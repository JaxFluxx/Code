#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统流程：
任务到达 -> 大中小任务 → 按目标时长切分成子任务；

挑最空的 GPU，用 （SRPT+老化+回填）把合适的子任务塞进去；

子任务经历传输→执行；

同一父任务全部子任务完成后，进入 CPU 汇总；

有 GPU/CPU 故障？→ 释放→修复→重分配；

如果利用率低或任务池浅 → 自动补货，系统一直跑。
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多NPU并发度模拟（任务可拆分为子任务）
- 设备：1×CPU + 3×NPU
- 调度：SRPT + Aging + 回填 + 退火算法
- 容错：CPU/NPU 三态（N 正常 / F 临时故障 / D 永久故障-吸收态）
      · N→F：瞬时可修复故障；F→N：修复计时后恢复；N→D：永久损坏（吸收）
      · 若 CPU 进入 F 或 D：系统算力归零，所有NPU子任务回滚至最近检查点并重排队
      · 若 NPU 进入 F 或 D：该卡上的子任务回滚至最近检查点并重排队
- 带宽模型：多通路带宽 + 协议开销 + 分配权重 + I/O-计算重叠度ρ；Roofline口径：C_task = min(C_hw, B_eff*OI) * (1 - sched_overhead)
- 功率模型：P(u) = P_idle + (P_tdp - P_idle) * u^beta
- 检查点：子任务运行中周期性做检查点；故障发生时，从最近检查点恢复，丢失该间隔内的进度，传输需重来
- 持续下发：池浅+利用率低时补货，目标维持 70%~85% 区间
- 汇总：父任务全部子任务完成后进入 CPU 汇总（并行上限=CPU_MAX_PARALLEL），CPU 工作按 β 计
- 日志CSV：每 10 秒记录一行（time, utilization(%), ACC(TFLOPS), cap_tflops(TFLOPS), NPU0_tasks, NPU1_tasks, NPU2_tasks）
"""

import sys
import time
import random
import threading
from collections import deque
from dataclasses import dataclass, field
from math import ceil
from typing import List, Tuple, Dict, Optional

# ======= 可视化依赖 =======
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
from PyQt5.QtCore import QTimer
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FC
from matplotlib import gridspec

import numpy as np  # <<< 新增：用于 Dirichlet 切分

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

# ------------------------ 全局随机种子（便于复现实验） ------------------------
random.seed(25)

# ======================== 核心可调参数 ========================
SAMPLE_EVERY = 1       # 采样间隔（仿真秒）
REFRESH_MS   = 15      # 画面刷新间隔（毫秒）
MAX_POINTS   = 400     # 曲线最多保留的“最近时间点”数量
TICK_SLEEP   = 0.01    # “1 仿真秒”的真实睡眠时间（秒）
MAX_QUEUE_LEGEND = 20  # 队列图最多展示的图例条目

# ======================== 硬件与系统参数（NPU 口径） =======================
NPU_COUNT = 3
NPU_CAPACITY = 8.00             # 每卡可并发槽位
NPU_MIN_FREE = 0.50             # 预留，避免满槽导致碎片
NPU_TFLOPS_PER_UNIT = 5.0       # 1 槽位≈ 5 TFLOPS（等效）

NPU_VRAM_GB = 8.0               # 每卡显存（GB）
NPU_VRAM_PER_RES = 1.0          # 每1槽位显存占用（GB）

# 效率项
NPU_ETA_SCAL   = 0.92
NPU_ETA_SCHED  = 0.93
NPU_ETA_JITTER = 0.85
NPU_EFF = NPU_ETA_SCAL * NPU_ETA_SCHED * NPU_ETA_JITTER  # ≈ 0.728

# ================= CPU 峰值与有效折算 =================
CPU_PEAK_TFLOPS = 5.0          # 标称/理论峰值（FP32 等效）
# —— 以下为折算因子（建议根据机房功耗/温度与基准测试校准）——
CPU_DELTA_PT      = 0.95       # δ_cpu(P,T)：功率/温度降额（长期负载下的可持续占比）
CPU_ETA_SCHED_CPU = 0.95       # η_sched^cpu：调度/上下文切换效率（OS/线程切换开销）
CPU_ETA_DMR       = 0.98       # η_dmr：冗余/容错开销（无则设 1.0）
CPU_Q_CPU         = 0.98       # q_cpu：有效指令占比（分支/流水线乱序等导致的无效槽位）
CPU_GAMMA_STATE   = 0.97       # Γ_cpu：状态加权（满载/降速/失效稳态概率的综合）
# 得到 CPU 的可持续有效算力：
CPU_TFLOPS = (CPU_PEAK_TFLOPS * CPU_DELTA_PT * CPU_ETA_SCHED_CPU *
              CPU_ETA_DMR * CPU_Q_CPU * CPU_GAMMA_STATE)

CPU_MAX_PARALLEL = 2
BETA = 0.05                    # NPU:CPU = 20:1 的校验/汇总开销（β=1/20）


# 带宽模型（多通路 + 协议开销 + 分配占比）
# (B_theo_GBs, protocol_eff_delta, share_gamma)
B_PATHS = [
    (16.0, 0.85, 0.6),
    (32.0, 0.90, 0.4),
]
UPSTREAM_DROP_RATIO = 0.0
IO_OVERLAP_K = 2
SCHED_OVERHEAD_BASE = 0.05

# SRPT + Aging
AGE_BOOST_PER_SEC = 0.02

# ==================== 可靠性三态马尔可夫（N/F/D） =========================
from random import expovariate
HOUR = 3600.0
# NPU
NPU_LAMBDA_NF = 0.00200 / HOUR
NPU_MU_FN     = 1.00000 / HOUR
NPU_LAMBDA_ND = 4.57e-5 / HOUR
NPU_LAMBDA_FD = 2.00e-4 / HOUR
# CPU（整机域）
CPU_LAMBDA_NF = 1.00e-3 / HOUR
CPU_MU_FN     = 0.50    / HOUR
CPU_LAMBDA_ND = 1.00e-4 / HOUR
CPU_LAMBDA_FD = 1.00e-4 / HOUR

# -------------------- 高区分度的颜色（避开灰度系） -------------------------
BRIGHT_PALETTE = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#17becf",
    "#bcbd22", "#ff1493", "#00ced1", "#ffa500",
    "#228b22", "#4169e1", "#ff6347", "#00bcd4",
    "#8a2be2", "#20b2aa", "#ffd700", "#7b68ee"
]

# ============================== 数据结构 ===================================
@dataclass
class SubTask:
    pid: int
    part_idx: int
    parts_total: int
    res: float
    exec_total: float
    tx_total: float
    oi_flop_per_byte: float
    exec_left: float
    tx_left: float
    state: str = "queued"           # queued / transferring / running / done
    npu: Optional[int] = None
    submit_ts: int = 0

    def label(self) -> str:
        return f"{self.pid}-{self.part_idx+1}/{self.parts_total}"

@dataclass
class ParentTask:
    pid: int
    total_res: float
    total_exec: int
    submit_ts: int
    oi_flop_per_byte: float
    parts: List[SubTask] = field(default_factory=list)
    remaining_parts: int = 0

@dataclass
class NPUNodes:
    nid: int
    capacity: float = NPU_CAPACITY
    used: float = 0.0
    vram_used: float = 0.0
    transferring: List[SubTask] = field(default_factory=list)
    running: List[SubTask] = field(default_factory=list)
    up: bool = True

    def free_res(self) -> float:
        return self.capacity - self.used

    def free_vram(self) -> float:
        return max(0.0, NPU_VRAM_GB - self.vram_used)

# ============================== 马尔可夫单元 ================================
class MarkovUnit:
    """连续时间马尔可夫三态：N / F / D（吸收）"""
    def __init__(self, name: str, rates: Dict[str, Dict[str, float]]):
        self.name = name
        self.rates = rates
        self.state = "N"
        self.next_ts = 0
        self.next_to = None
        self._schedule(0)

    def _schedule(self, now: int):
        out = self.rates.get(self.state, {})
        lam = sum(v for v in out.values())
        if lam <= 0.0:
            self.next_ts = 10**18
            self.next_to = None
            return
        dt = max(1, int(round(expovariate(lam))))
        r = random.random() * lam
        acc = 0.0
        to_state = None
        for k, v in out.items():
            acc += v
            if r <= acc:
                to_state = k
                break
        self.next_ts = now + dt
        self.next_to = to_state

    def step(self, now: int) -> Optional[Tuple[str, str]]:
        if now >= self.next_ts and self.next_to is not None:
            old = self.state
            self.state = self.next_to
            if self.state == "D":
                self.next_ts = 10**18
                self.next_to = None
            else:
                self._schedule(now)
            return (old, self.state)
        return None

def make_cpu_markov() -> MarkovUnit:
    rates = {"N": {"F": CPU_LAMBDA_NF, "D": CPU_LAMBDA_ND},
             "F": {"N": CPU_MU_FN,     "D": CPU_LAMBDA_FD},
             "D": {}}
    return MarkovUnit("CPU", rates)

def make_npu_markov(nid: int) -> MarkovUnit:
    rates = {"N": {"F": NPU_LAMBDA_NF, "D": NPU_LAMBDA_ND},
             "F": {"N": NPU_MU_FN,     "D": NPU_LAMBDA_FD},
             "D": {}}
    return MarkovUnit(f"NPU{nid}", rates)

# =========================== 功率、带宽、Roofline ============================
def effective_bandwidth(paths: List[Tuple[float, float, float]], drop_ratio: float = 0.0) -> float:
    agg = 0.0
    for B_theo, delta, gamma in paths:
        agg += gamma * delta * B_theo
    agg *= (1.0 - drop_ratio)
    return max(0.0, agg)

def rho_overlap(Tio: float, Tcomp: float, k: int) -> float:
    if Tio <= 0 or Tcomp <= 0:
        return 1.0
    if Tio <= Tcomp:
        return 1.0
    return max(0.0, min(1.0, (Tcomp + (k - 1) * min(Tio, Tcomp)) / (k * Tio)))

def roofline_cap(C_hw: float, B_eff: float, OI: float, sched_overhead: float) -> float:
    return max(0.0, min(C_hw, B_eff * OI) * (1.0 - sched_overhead))

def dynamic_sched_overhead(pool_len: int, total_concurrency: int) -> float:
    extra = 0.0
    extra += min(0.10, 0.002 * pool_len)                       # 队列压力
    extra += min(0.08, 0.005 * max(0, total_concurrency - NPU_COUNT))  # 并发超卡数
    return min(0.25, SCHED_OVERHEAD_BASE + extra)

# =============================== 任务生成/切分 ================================
def split_parent_into_subtasks(pid: int, total_res: float, total_exec: int, submit_ts: int, oi: float) -> List[SubTask]:
    """
    允许切分为多片（>3），并有少量“更大任务”。
    """
    base_pieces = max(1, int(total_exec / 240))
    if random.random() < 0.35:
        scale = random.randint(2, 4)
        base_pieces *= scale
    g = max(1, min(24, base_pieces))

    total_exec = max(240, total_exec)
    parts_ratio = list(np.random.dirichlet([1.0] * g))
    exec_parts = [max(60, int(round(total_exec * r))) for r in parts_ratio]

    res_per = max(1.0, total_res / g)
    parts = []
    for k in range(g):
        tx = random.randint(40, 80)
        res_k = max(0.5, round(res_per * random.uniform(0.8, 1.2), 2))
        parts.append(SubTask(pid=pid, part_idx=k, parts_total=g,
                             res=res_k,
                             exec_total=float(exec_parts[k]), tx_total=float(tx),
                             oi_flop_per_byte=oi,
                             exec_left=float(exec_parts[k]), tx_left=float(tx),
                             submit_ts=submit_ts))
    return parts

def gen_parent_batch(next_pid: int, k: int, now_ts: int) -> Tuple[List[ParentTask], int]:
    parents=[]
    for _ in range(k):
        total_res = random.uniform(5.0, 10.0)
        total_exec = random.randint(480, 1200)
        oi = random.choice([150.0, 300.0, 600.0])
        p = ParentTask(pid=next_pid, total_res=total_res, total_exec=total_exec,
                       submit_ts=now_ts, oi_flop_per_byte=oi)
        p.parts = split_parent_into_subtasks(next_pid, total_res, total_exec, now_ts, oi)
        p.remaining_parts = len(p.parts)
        parents.append(p)
        next_pid += 1
    return parents, next_pid

# =========================== 仿真核心（后台线程） =============================
class Simulator(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        # 设备
        self.npus = [NPUNodes(i) for i in range(NPU_COUNT)]
        self.npu_markovs = [make_npu_markov(i) for i in range(NPU_COUNT)]
        self.cpu_markov = make_cpu_markov()
        # 队列
        self.pool = deque()
        self.parents: Dict[int, ParentTask] = {}
        self.cpu_running = []      # [{'pid':int, 'work_left':float}]
        self.cpu_queue = deque()
        # 指标
        self.now_ts = 0
        self.sum_TC = 0.0
        self.stop_flag = False
        # 初始任务
        self.next_pid = 0
        init_parents, self.next_pid = gen_parent_batch(self.next_pid, 6, self.now_ts)
        for p in init_parents:
            self.parents[p.pid] = p
            for st in p.parts:
                self.pool.append(st)
        # 带宽基线
        self.B_base = effective_bandwidth(B_PATHS, drop_ratio=UPSTREAM_DROP_RATIO)
        # 共享可视化缓冲（UI 读）
        self.data_lock = threading.Lock()
        self.series_time = []          # x 轴：时间（秒）
        self.series_ACC = []           # y1：ACC（TFLOPS，平均算力）
        self.series_UTIL = []          # y2：总体瞬时利用率（%）
        # 每张 NPU 的利用率曲线
        self.series_UTIL_NPUs = [[], [], []]  # 百分比
        # 当前时刻每张 NPU 的任务构成（单位：槽位数）
        self.cur_stack = [[], [], []]  # 每项为 [(pid, units), ...]
        # 队列池：单列竖向堆叠柱（[(pid, pct), ...]）
        self.cur_pool_stack_all = []
        # 当前值（用于窗口标题）
        self.cur_inst = 0.0
        self.cur_util = 0.0
        self.cur_cap  = 0.0
        self.cur_tasks = ["-", "-", "-"]
        # 颜色映射
        self._task_color: Dict[int, Tuple[float,float,float,float]] = {}

    def get_task_color(self, pid: int):
        if pid not in self._task_color:
            self._task_color[pid] = BRIGHT_PALETTE[pid % len(BRIGHT_PALETTE)]
        return self._task_color[pid]

    # ---- 调度：SRPT + Aging + 回填 ----
    def pick_best_task_for_npu(self, npu: NPUNodes, tnow: int) -> Optional[SubTask]:
        cands = [st for st in self.pool
                 if (npu.free_res()-NPU_MIN_FREE) >= st.res
                 and (npu.free_vram() >= st.res*NPU_VRAM_PER_RES)]
        if not cands:
            return None
        def score(st: SubTask):
            rem = st.tx_left + st.exec_left
            age = tnow - st.submit_ts
            return max(0.0, rem - AGE_BOOST_PER_SEC * age)
        cands.sort(key=lambda s: (score(s), s.res))  # 同分优先小任务（回填）
        return cands[0]

    def try_assign(self, tnow: int):
        while True:
            choices = [g for g in self.npus if g.up and (g.free_res()-NPU_MIN_FREE) > 0.0 and g.free_vram()>0.0]
            if not choices:
                break
            npu = max(choices, key=lambda x: (x.free_res(), x.free_vram()))
            best = self.pick_best_task_for_npu(npu, tnow)
            if not best:
                break
            self.pool.remove(best)
            best.npu = npu.nid
            best.state = "transferring"
            npu.transferring.append(best)
            npu.used += best.res
            npu.vram_used += best.res * NPU_VRAM_PER_RES

    def release_npu_tasks(self, nid: int):
        npu = self.npus[nid]
        for st in list(npu.transferring):
            npu.transferring.remove(st)
            npu.used -= st.res
            npu.vram_used -= st.res * NPU_VRAM_PER_RES
            st.state = "queued"; st.npu = None
            st.tx_left = st.tx_total; st.exec_left = st.exec_total
            self.pool.appendleft(st)
        for st in list(npu.running):
            npu.running.remove(st)
            npu.used -= st.res
            npu.vram_used -= st.res * NPU_VRAM_PER_RES
            st.state = "queued"; st.npu = None
            st.tx_left = st.tx_total; st.exec_left = st.exec_total
            self.pool.appendleft(st)

    def release_all_for_cpu_fault(self):
        for nid in range(NPU_COUNT):
            self.release_npu_tasks(nid)

    def utilization_snapshot(self, cpu_ok: bool):
        cap_tflops = sum(max(0.0, (g.capacity - NPU_MIN_FREE)) * NPU_TFLOPS_PER_UNIT * NPU_EFF
                         for g, m in zip(self.npus, self.npu_markovs) if g.up and m.state == "N")
        used_units = sum(sum(st.res for st in g.running)
                         for g, m in zip(self.npus, self.npu_markovs) if g.up and m.state == "N")
        used_tflops = used_units * NPU_TFLOPS_PER_UNIT * NPU_EFF
        cpu_used_tflops = CPU_TFLOPS if (self.cpu_running and cpu_ok) else 0.0
        return cap_tflops, used_tflops, cpu_used_tflops

    def _trim_window(self):
        if len(self.series_time) > MAX_POINTS:
            self.series_time = self.series_time[-MAX_POINTS:]
            self.series_ACC = self.series_ACC[-MAX_POINTS:]
            self.series_UTIL = self.series_UTIL[-MAX_POINTS:]
            for i in range(NPU_COUNT):
                self.series_UTIL_NPUs[i] = self.series_UTIL_NPUs[i][-MAX_POINTS:]

    def run(self):
        self.try_assign(self.now_ts)

        while not self.stop_flag:
            # 1) 马尔可夫演化
            cpu_event = self.cpu_markov.step(self.now_ts)
            if cpu_event:
                old, new = cpu_event
                if new in ("F", "D"):
                    self.release_all_for_cpu_fault()

            for nid, (npu, mk) in enumerate(zip(self.npus, self.npu_markovs)):
                ev = mk.step(self.now_ts)
                if ev:
                    old, new = ev
                    if new in ("F", "D"):
                        self.release_npu_tasks(nid)
                        npu.up = False
                    elif old == "F" and new == "N":
                        npu.up = True

            cpu_ok = (self.cpu_markov.state == "N")

            # 2) 推进与统计
            cap_tflops, used_tflops, cpu_used_tflops = self.utilization_snapshot(cpu_ok)
            delivered = (used_tflops + cpu_used_tflops) if cpu_ok else 0.0
            self.sum_TC += delivered
            acc = (self.sum_TC / max(1, self.now_ts)) if self.now_ts > 0 else 0.0

            # 3) 传输与执行推进
            if cpu_ok:
                total_conc = sum(len(g.running) + len(g.transferring) for g in self.npus if g.up)
                sched_over = dynamic_sched_overhead(len(self.pool), total_conc)
                B_base = self.B_base

                for g, mk in zip(self.npus, self.npu_markovs):
                    if not g.up or mk.state != "N":
                        continue
                    for st in list(g.transferring):
                        st.tx_left -= 1.0
                        if st.tx_left <= 0:
                            g.transferring.remove(st)
                            st.state = "running"
                            g.running.append(st)
                    for st in list(g.running):
                        C_hw = st.res * NPU_TFLOPS_PER_UNIT * NPU_EFF
                        flops_per_sec = C_hw
                        data_per_sec = flops_per_sec / max(1.0, st.oi_flop_per_byte)
                        theo_agg = sum(gamma*delta*B for (B, delta, gamma) in B_PATHS)
                        Tio = data_per_sec / max(1e-6, theo_agg)
                        Tcomp = 1.0
                        rho = rho_overlap(Tio, Tcomp, IO_OVERLAP_K)
                        B_eff = B_base * rho
                        deliver = roofline_cap(C_hw, B_eff, st.oi_flop_per_byte, sched_over)
                        eq_seconds = max(0.05, min(1.0, deliver / max(1e-6, C_hw)))
                        st.exec_left -= eq_seconds
                        if st.exec_left <= 0:
                            g.running.remove(st)
                            g.used -= st.res
                            g.vram_used -= st.res * NPU_VRAM_PER_RES
                            st.state = "done"

            # 4) 父任务完成 -> CPU 汇总排队
            for p in self.parents.values():
                done_cnt = sum(1 for st in p.parts if st.state == "done")
                p.remaining_parts = len(p.parts) - done_cnt
            for p in list(self.parents.values()):
                if p.remaining_parts == 0:
                    if not any(item['pid']==p.pid for item in self.cpu_running) and not any(pid==p.pid for pid,_ in self.cpu_queue):
                        total_work_units = sum(part.res * part.exec_total for part in p.parts)
                        cpu_work = max(1.0, BETA * total_work_units * NPU_TFLOPS_PER_UNIT)
                        self.cpu_queue.append((p.pid, cpu_work))

            # 5) CPU 汇总推进
            if cpu_ok:
                while len(self.cpu_running) < CPU_MAX_PARALLEL and self.cpu_queue:
                    pid, work = self.cpu_queue.popleft()
                    self.cpu_running.append({"pid": pid, "work_left": work})
                if self.cpu_running:
                    per_group = CPU_TFLOPS / len(self.cpu_running)
                    for item in list(self.cpu_running):
                        item["work_left"] -= per_group
                        if item["work_left"] <= 0:
                            self.cpu_running.remove(item)

            # 6) 分配（SRPT + Aging + 回填）
            if cpu_ok:
                self.try_assign(self.now_ts)

            # 7) 低水位补货（稳态运行）
            util_total = (used_tflops / cap_tflops) if (cap_tflops>0) else 0.0  # 0~1
            POOL_LOW_WM  = NPU_COUNT * 6
            POOL_HIGH_WM = NPU_COUNT * 12
            UTIL_LOW = 0.70
            if len(self.pool) < POOL_LOW_WM and util_total < UTIL_LOW:
                want = min(POOL_HIGH_WM - len(self.pool), POOL_LOW_WM)
                if want > 0:
                    k = max(3, ceil(want / NPU_COUNT))
                    new_parents, self.next_pid = gen_parent_batch(self.next_pid, k, self.now_ts)
                    for p in new_parents:
                        self.parents[p.pid] = p
                        for st in p.parts:
                            self.pool.append(st)
                    if cpu_ok:
                        self.try_assign(self.now_ts)

            # 8) 可视化缓冲
            with self.data_lock:
                self.cur_inst = delivered
                self.cur_util = util_total * 100.0
                self.cur_cap = cap_tflops

                tasks_short = []
                for g in self.npus:
                    if g.running:
                        tasks_short.append(g.running[0].label())
                    elif g.transferring:
                        tasks_short.append(g.transferring[0].label())
                    else:
                        tasks_short.append("-")
                self.cur_tasks = tasks_short[:3]

                # 每张 NPU 的任务构成（单位：槽位）
                stacks = [[], [], []]
                util_npux = [0.0, 0.0, 0.0]
                for i, g in enumerate(self.npus):
                    used_units = 0.0
                    comp = []
                    for st in g.running:
                        units = max(0.0, st.res)
                        if units > 0:
                            comp.append((st.pid, units))
                            used_units += units
                    util_npux[i] = max(0.0, min(100.0, (used_units / max(1.0, NPU_CAPACITY - NPU_MIN_FREE)) * 100.0))
                    stacks[i] = comp
                self.cur_stack = stacks

                # 队列池：单列（全量队列合并）
                pool_list = list(self.pool)
                if pool_list:
                    total_sec = sum((s.tx_left + s.exec_left) for s in pool_list) or 1.0
                    segs = []
                    for s in sorted(pool_list, key=lambda x: (x.tx_left + x.exec_left), reverse=True):
                        segs.append((s.pid, (s.tx_left + s.exec_left)/total_sec * 100.0))
                    self.cur_pool_stack_all = segs
                else:
                    self.cur_pool_stack_all = []

                if self.now_ts % SAMPLE_EVERY == 0:
                    self.series_time.append(self.now_ts)
                    self.series_ACC.append(acc)                          # 平均算力（TFLOPS）
                    self.series_UTIL.append(util_total * 100.0)          # 瞬时利用率（%）
                    for j in range(NPU_COUNT):
                        self.series_UTIL_NPUs[j].append(util_npux[j])
                    self._trim_window()

            self.now_ts += 1
            time.sleep(TICK_SLEEP)

# ================================ UI 部分 =====================================
class RealtimeACC(QWidget):
    def __init__(self, sim: Simulator, refresh_ms: int = REFRESH_MS):
        super().__init__()
        self.sim = sim
        self.refresh_ms = refresh_ms
        self.init_ui()

    def init_ui(self):
        self.resize(1400, 780)
        self.setWindowTitle("Realtime Charts (Simulating…)")  # 原：实时曲线（仿真中…）

        plt.rcParams['font.sans-serif'] = ['SimHei', 'PingFang SC', 'STHeiti']
        plt.rcParams['axes.unicode_minus'] = False

        # 2 行 3 列
        self.fig = plt.figure(constrained_layout=True)
        gs = gridspec.GridSpec(2, 3, figure=self.fig, height_ratios=[2, 2], width_ratios=[3, 2, 2])

        # 顶部主图（平均算力占用率 + 瞬时算力占用率）
        self.ax1 = self.fig.add_subplot(gs[0, 0:2])  # 左轴：ACC
        self.ax2 = self.ax1.twinx()                  # 右轴：总体利用率%
        self.ax1.set_xlabel("Time (s)")              # 原：时间（秒）
        self.ax1.set_ylabel("ACC (TFLOPS)")          # 原：ACC（TFLOPS）
        self.ax2.set_ylabel("Overall Utilization (%)")  # 原：总体利用率（%）
        (self.line_acc,)  = self.ax1.plot([], [], linewidth=1.0, marker='o', label="Average Compute Capacity")
        (self.line_util,) = self.ax2.plot([], [], linewidth=1.2, linestyle='--', marker='s', color='r', label="Instantaneous Utilization (%)")

        # 底部左：三条折线（NPU0/1/2 利用率）
        self.ax3 = self.fig.add_subplot(gs[1, 0])
        self.ax3.set_xlabel("Time (s)")             # 原：时间（秒）
        self.ax3.set_ylabel("NPU Utilization (%)")  # 原：NPU 利用率（%）
        self.lines_npu = []
        colors = ['tab:blue', 'tab:orange', 'tab:green']
        labels = ['NPU0 Utilization', 'NPU1 Utilization', 'NPU2 Utilization']  # 原：NPU0/1/2 利用率
        for c, lb in zip(colors, labels):
            (ln,) = self.ax3.plot([], [], linewidth=1.4, label=lb, color=c)
            self.lines_npu.append(ln)
        self.ax3.set_ylim(0, 100)
        self.ax3.grid(True, linestyle='--', alpha=0.3)
        self.ax3.legend(loc="upper left")

        # 底部中：当前时刻的堆叠柱（3 根）——纵轴 0~8 槽位
        self.ax4 = self.fig.add_subplot(gs[1, 1])
        self.ax4.set_title("Current NPU Task Composition (stacked, slots)")  # 原：当前时刻：各 NPU 任务构成（堆叠，单位：槽位数）
        self.ax4.set_ylabel("Slots (0–8)")                                    # 原：槽位（0-8）
        self.ax4.set_ylim(0, NPU_CAPACITY)

        # 右侧整列：任务队列池（单根竖向堆叠柱）
        self.ax5 = self.fig.add_subplot(gs[:, 2])
        self.ax5.set_title("Task Queue Pool (vertical stacked: runtime share)")   # 原：任务队列池（竖向堆叠：相对预计执行时间占比）
        self.ax5.set_ylabel("Relative Estimated Runtime (%)")                    # 原：相对预计执行时间（占比 %）
        self.ax5.set_ylim(0, 100)

        self.canvas = FC(self.fig)
        lay = QVBoxLayout()
        lay.addWidget(self.canvas)
        self.setLayout(lay)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(self.refresh_ms)

    def _draw_stackbars(self, ax, stacks):
        """3 根堆叠柱；空闲灰色；纵轴 0~8 槽位。"""
        ax.cla()
        ax.set_title("Current NPU Task Composition (stacked, slots)")
        ax.set_ylabel("Slots (0–8)")
        ax.set_ylim(0, NPU_CAPACITY)

        x = [0, 1, 2]
        ax.set_xticks(x)
        ax.set_xticklabels(["NPU0", "NPU1", "NPU2"])

        handles = []
        labels = []
        for i, comp in enumerate(stacks):
            bottom = 0.0
            for pid, units in comp:
                color = self.sim.get_task_color(pid)
                rects = ax.bar(i, units, bottom=bottom, color=color, edgecolor='white', linewidth=0.3)
                bottom += units
                if len(labels) < MAX_QUEUE_LEGEND:
                    handles.append(rects[0]); labels.append(f"Task {pid}")  # 原：任务{pid}
            idle = max(0.0, NPU_CAPACITY - bottom)
            if idle > 0:
                ax.bar(i, idle, bottom=bottom, color='#DDDDDD', edgecolor='white', linewidth=0.3, label=None)

        if handles:
            seen = set(); uniq_h, uniq_l = [], []
            for h, l in zip(handles, labels):
                if l not in seen:
                    uniq_h.append(h); uniq_l.append(l); seen.add(l)
            ax.legend(uniq_h, uniq_l, loc="upper right", fontsize=8, framealpha=0.6)

    def _draw_queue_singlebar(self, ax, segments):
        """
        单根竖向堆叠柱：segments = [(pid, pct), ...]，pct 为队列内相对预计执行时间占比。
        """
        ax.cla()
        ax.set_title("Task Queue Pool (vertical stacked: runtime share)")
        ax.set_ylabel("Relative Estimated Runtime (%)")
        ax.set_ylim(0, 100)
        ax.set_xticks([0])
        ax.set_xticklabels(["Task Queue"])  # 原：任务队列池

        if not segments:
            ax.text(0.5, 0.5, "Queue Empty", ha='center', va='center', transform=ax.transAxes, alpha=0.6)  # 原：队列为空
            return

        bottom = 0.0
        handles, labels = [], []
        for pid, pct in segments:
            color = self.sim.get_task_color(pid)
            rects = ax.bar(0, pct, bottom=bottom, color=color, edgecolor='white', linewidth=0.3)
            bottom += pct
            if len(labels) < MAX_QUEUE_LEGEND:
                handles.append(rects[0]); labels.append(f"Task {pid}")  # 原：任务{pid}

        if handles:
            seen = set(); uniq_h, uniq_l = [], []
            for h, l in zip(handles, labels):
                if l not in seen:
                    uniq_h.append(h); uniq_l.append(l); seen.add(l)
            ax.legend(uniq_h, uniq_l, loc="upper right", fontsize=8, framealpha=0.6)

        ax.grid(True, axis='y', linestyle='--', alpha=0.3)

    def update_plot(self):
        with self.sim.data_lock:
            x = list(self.sim.series_time)
            y_acc  = list(self.sim.series_ACC)   # 平均算力（TFLOPS）
            y_util = list(self.sim.series_UTIL)  # 瞬时利用率（%）
            y_npux = [list(self.sim.series_UTIL_NPUs[i]) for i in range(3)]
            stacks = [list(self.sim.cur_stack[i]) for i in range(3)]
            seg_all = list(self.sim.cur_pool_stack_all)
            inst = self.sim.cur_inst
            util = self.sim.cur_util
            cap  = self.sim.cur_cap
            n0, n1, n2 = self.sim.cur_tasks

        if not x:
            return

        x_max = x[-1]
        x_min = max(0, x_max - MAX_POINTS)
        self.ax1.set_xlim(x_min, x_min + MAX_POINTS)

        # 顶部曲线（图例英文）
        self.line_acc.set_data(x, y_acc)
        self.line_util.set_data(x, y_util)
        self.ax1.set_ylim(0, 100)
        self.ax2.set_ylim(0, 100)
        self.ax1.grid(True, linestyle='--', alpha=0.3)
        lines_main = [self.line_acc, self.line_util]
        labels_main = [l.get_label() for l in lines_main]
        self.ax1.legend(lines_main, labels_main, loc="upper left")

        # 底部左：NPU 利用率折线
        self.ax3.set_xlim(x_min, x_min + MAX_POINTS)
        for i in range(3):
            self.lines_npu[i].set_data(x, y_npux[i])

        # 底部中：NPU 构成堆叠柱（单位：槽位）
        self._draw_stackbars(self.ax4, stacks)

        # 右侧整列：单根竖向堆叠柱（队列池）
        self._draw_queue_singlebar(self.ax5, seg_all)

        # 窗口标题（英文）
        avg_now = y_acc[-1] if y_acc else 0.0
        self.setWindowTitle(
            f"Realtime Charts | Inst. Compute ≈ {inst:.2f} TFLOPS | Avg ACC ≈ {avg_now:.2f} TFLOPS | Overall Util ≈ {util:.0f}% | Capacity ≈ {cap:.2f} TFLOPS | NPU Tasks: [{n0}] [{n1}] [{n2}]"
        )

        self.canvas.draw()

# ================================== 入口 =====================================
def main():
    # 启动仿真线程
    sim = Simulator()
    sim.start()

    # 启动 UI
    app = QApplication(sys.argv)
    w = RealtimeACC(sim, refresh_ms=REFRESH_MS)
    w.show()

    # 优雅退出
    ret = app.exec_()
    sim.stop_flag = True
    sys.exit(ret)

if __name__ == "__main__":
    main()
