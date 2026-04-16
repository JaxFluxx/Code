
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

import time
import random
import csv
from collections import deque
from math import ceil, exp
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
from random import expovariate

# ------------------------ 全局随机种子（便于复现实验） ------------------------
random.seed(23)

# ======================== 硬件与系统参数（可按平台替换） =======================
NPU_COUNT = 3
NPU_CAPACITY = 8.00              # 每卡可并发“资源单位”（抽象成算力并发槽位）
NPU_MIN_FREE = 0.50              # 每卡预留余量，避免满槽导致碎片
NPU_TFLOPS_PER_UNIT = 5.0        # 1“资源单位”≈ 5 TFLOPS（按实际卡型修改）

NPU_VRAM_GB = 8.0                # 每卡显存容量（GB）
NPU_VRAM_PER_RES = 1.0           # 每1“资源单位”约占用显存（GB），仿真用

# NPU效率项（示例常量，真实系统可按测量/模型动态化）
NPU_ETA_SCAL   = 0.92            # 并行扩展效率
NPU_ETA_SCHED  = 0.93            # 调度效率
NPU_ETA_JITTER = 0.85            # 抖动/最慢者效应
NPU_EFF = NPU_ETA_SCAL * NPU_ETA_SCHED * NPU_ETA_JITTER  # ≈ 0.728

# CPU“汇总/校验”算力（TFLOPS）与并行组上限
CPU_TFLOPS = 1.00
CPU_MAX_PARALLEL = 2
BETA = 0.05                      # CPU per NPU result：每1单位NPU结果，CPU需0.05单位计算

# 功率曲线参数（示例；可替换为实测/厂商数据）
NPU_POWER_TDP = 220.0            # W（示例）
NPU_POWER_IDLE = 35.0            # W
NPU_POWER_BETA = 1.2
CPU_POWER_TDP = 150.0            # W
CPU_POWER_IDLE = 25.0            # W
CPU_POWER_BETA = 1.1

# 带宽模型：多通路 + 协议开销 + 分配占比（可按平台替换）
# (B_theo_GBs, protocol_eff_delta, share_gamma)
B_PATHS = [
    (16.0, 0.85, 0.6),           # PCIe 4.0 x16：理论16GB/s，协议效率0.85，分配0.6
    (32.0, 0.90, 0.4),           # 本地直通/缓存：32GB/s，协议效率0.9，分配0.4
]
UPSTREAM_DROP_RATIO = 0.0        # 上游剔除率（如FPGA预处理掉无效数据），0~1
IO_OVERLAP_K = 2                 # I/O-计算重叠的“多缓冲路数” k
SCHED_OVERHEAD_BASE = 0.05       # 基础调度折损（其上叠加队列/并发引起的额外折损）

# 退火（降火）参数：周期性轻量邻域搜索，微调“已在途分配”
ANNEAL_PERIOD = 30               # 每隔多少“仿真秒”触发一次退火
SA_T0 = 1.3
SA_ALPHA = 0.996
SA_STEPS = 300

# 运行/打印控制
HEARTBEAT_EVERY = 50             # 心跳打印周期（仿真秒）
TICK_SLEEP = 0.02                # 每个仿真秒的真实睡眠（秒）

# 持续下发（维持目标利用率窗口）
POOL_LOW_WM  = NPU_COUNT * 6     # 子任务池低水位
POOL_HIGH_WM = NPU_COUNT * 12    # 一次最多补货的子任务量
UTIL_LOW  = 0.70                 # 低于则补货
UTIL_HIGH = 0.85                 # 高于则暂缓

# SRPT + Aging
AGE_BOOST_PER_SEC = 0.02

# CSV 日志文件
LOG_CSV_PATH = "system_log.csv"

# ----------------------- 可靠性三态马尔可夫（N/F/D） ---------------------------
# 速率单位：/秒；以下示例基于常见星载/数据中心经验值换算（可替换为文档表格标定值）
# NPU（每卡）：
#   N -> F：临时故障速率（约 0.002 /小时）
#   F -> N：修复速率（约 1 /小时）
#   N -> D：永久损坏速率（约 4.57e-5 /小时）
#   F -> D：临时变永久的速率（小概率）
HOUR = 3600.0
NPU_LAMBDA_NF = 0.00200 / HOUR
NPU_MU_FN     = 1.00000 / HOUR
NPU_LAMBDA_ND = 4.57e-5 / HOUR
NPU_LAMBDA_FD = 2.00e-4 / HOUR

# CPU（整机视作一个“域”）：数值可更保守
CPU_LAMBDA_NF = 1.00e-3 / HOUR
CPU_MU_FN     = 0.50    / HOUR
CPU_LAMBDA_ND = 1.00e-4 / HOUR
CPU_LAMBDA_FD = 1.00e-4 / HOUR

class MarkovUnit:
    """
    连续时间马尔可夫三态：N（正常）/F（临时故障）/D（永久故障，吸收态）
    - 用指数分布采样下一次转移时间；在转移瞬时选择去向（按相对速率权重）。
    """
    def __init__(self, name: str, rates: Dict[str, Dict[str, float]]):
        self.name = name
        self.rates = rates
        self.state = "N"
        self.next_ts = 0
        self.next_to = None
        self._schedule(0)

    def _schedule(self, now: int):
        """在当前状态下安排下一次转移事件。"""
        out = self.rates.get(self.state, {})
        lam = sum(v for v in out.values())
        if lam <= 0.0:
            self.next_ts = 10**18
            self.next_to = None
            return
        dt = max(1, int(round(expovariate(lam))))  # 按秒取整，至少1秒
        # 随机选择去向
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
        """
        推进一步：若到达转移时刻，则切换状态并重新安排下一事件。
        返回 (old_state, new_state) 或 None。
        """
        if now >= self.next_ts and self.next_to is not None:
            old = self.state
            self.state = self.next_to
            # D 是吸收态：不再安排未来事件
            if self.state == "D":
                self.next_ts = 10**18
                self.next_to = None
            else:
                self._schedule(now)
            return (old, self.state)
        return None

def make_cpu_markov() -> MarkovUnit:
    rates = {
        "N": {"F": CPU_LAMBDA_NF, "D": CPU_LAMBDA_ND},
        "F": {"N": CPU_MU_FN,     "D": CPU_LAMBDA_FD},
        "D": {},
    }
    return MarkovUnit("CPU", rates)

def make_npu_markov(nid: int) -> MarkovUnit:
    rates = {
        "N": {"F": NPU_LAMBDA_NF, "D": NPU_LAMBDA_ND},
        "F": {"N": NPU_MU_FN,     "D": NPU_LAMBDA_FD},
        "D": {},
    }
    return MarkovUnit(f"NPU{nid}", rates)

# ============================== 数据结构定义 ===================================
@dataclass
class SubTask:
    pid: int
    part_idx: int
    parts_total: int
    # 资源/时间
    res: float                      # 该份占用的“资源单位”
    exec_total: float               # 该份“纯计算时间”（秒，忽略带宽时）
    tx_total: float                 # 该份“传输时间”（秒）
    # 带宽口径
    oi_flop_per_byte: float         # 该份的 OI（FLOP/B），供 Roofline 使用
    # 运行态
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
    up: bool = True                # 设备物理开/关（F/D 时 up=False；N 时 up=True）

    def free_res(self) -> float:
        return self.capacity - self.used

    def free_vram(self) -> float:
        return max(0.0, NPU_VRAM_GB - self.vram_used)

# ============================== 打印/工具函数 ===================================
def ts(t: int) -> str:
    return f"时间[{t}]"

def print_assign(t, st, npu):
    print(f"{ts(t)} 任务 {st.label()} 分配到NPU{npu.nid}，开始传输。（资源：{st.res:.2f}，时间：{st.exec_total:.0f}，NPU剩余资源：{npu.free_res():.2f}，显存剩余：{npu.free_vram():.1f}GB）")

def print_tx_done(t, st, npu):
    print(f"{ts(t)} 任务 {st.label()} 在NPU{npu.nid} 上传输完成，开始执行")

def print_finish(t, st, npu):
    print(f"{ts(t)} 任务 {st.label()} 在NPU{npu.nid} 执行完成")

def print_cpu_group_start(t, pid, cpu_dt, eta_ts):
    print(f"{ts(t)} 任务组 {pid} NPU阶段完成 → 进入CPU汇总（≈{cpu_dt:.1f}s），预计完成到 {eta_ts}")

def print_cpu_group_done(t, pid):
    print(f"{ts(t)} 任务组 {pid} CPU汇总完成")

def print_heartbeat(t, cpu_state, npu_markovs, cap_tflops, used_tflops, cpu_used_tflops, avg_perf_per_w, acc_tflops):
    npu_states = ", ".join([f"{m.name[-1]}:{m.state}" for m in npu_markovs])  # '0:N, 1:F, 2:N' 等
    util = (used_tflops / cap_tflops * 100.0) if cap_tflops>0 else 0.0
    print(f"{ts(t)} [心跳] CPU={cpu_state} | NPU[{npu_states}] | NPU占用≈{used_tflops:.2f} TFLOPS | CPU≈{cpu_used_tflops:.2f} TFLOPS | 上限≈{cap_tflops:.2f} TFLOPS | 利用率≈{util:.0f}% | Perf/W≈{avg_perf_per_w:.3f} | ACC≈{acc_tflops:.2f} TFLOPS")

def device_power(u: float, p_idle: float, p_tdp: float, beta: float) -> float:
    """P(u) = P_idle + (P_tdp - P_idle) * u^beta，u ∈ [0,1]"""
    u = max(0.0, min(1.0, u))
    return p_idle + (p_tdp - p_idle) * (u ** beta)

def npu_tasks_str(npu: NPUNodes) -> str:
    """把一个 NPU 上正在执行的任务编号拼成字符串（空则为 '-'）。"""
    if not npu.running:
        return "-"
    return "|".join(st.label() for st in npu.running)

# =========================== 功率、带宽与 Roofline =============================
def effective_bandwidth(paths: List[Tuple[float, float, float]], drop_ratio: float = 0.0) -> float:
    """多通路有效带宽 B_eff = (1 - drop_ratio) * Σ (gamma * delta * B_theo)  [GB/s]"""
    agg = 0.0
    for B_theo, delta, gamma in paths:
        agg += gamma * delta * B_theo
    agg *= (1.0 - drop_ratio)
    return max(0.0, agg)

def rho_overlap(Tio: float, Tcomp: float, k: int) -> float:
    """
    I/O-计算重叠度 ρ：
      - 若 Tio <= Tcomp，则 ρ = 1（完全重叠）
      - 若 Tio > Tcomp，则 ρ = [Tcomp + (k-1)*min(Tio, Tcomp)] / (k * Tio)
    """
    if Tio <= 0 or Tcomp <= 0:
        return 1.0
    if Tio <= Tcomp:
        return 1.0
    return max(0.0, min(1.0, (Tcomp + (k - 1) * min(Tio, Tcomp)) / (k * Tio)))

def roofline_cap(C_hw: float, B_eff: float, OI: float, sched_overhead: float) -> float:
    """Roofline：C_task = min(C_hw, B_eff * OI) * (1 - sched_overhead)"""
    return max(0.0, min(C_hw, B_eff * OI) * (1.0 - sched_overhead))

def dynamic_sched_overhead(pool_len: int, total_concurrency: int) -> float:
    """
    动态调度折损：基础值 + 队列压力项 + 并发项，避免>25%
    - 队列越深/并发越高 → 调度/同步开销越大
    """
    extra = 0.0
    extra += min(0.10, 0.002 * pool_len)           # 队列压力
    extra += min(0.08, 0.005 * max(0, total_concurrency - NPU_COUNT))  # 并发超卡数
    return min(0.25, SCHED_OVERHEAD_BASE + extra)

# =============================== 任务生成/切分 ================================
def split_parent_into_subtasks(pid: int, total_res: float, total_exec: int, submit_ts: int, oi: float) -> List[SubTask]:
    """
    把父任务拆为 g 份，使每份执行时间≈240s；均分资源/时间；每份携带 OI 档位
    """
    g = max(1, min(NPU_COUNT, round(total_exec / 240)))
    res_per = max(1.0, total_res / g)
    exec_per = max(60, int(total_exec / g))
    parts = []
    for k in range(g):
        tx = random.randint(40, 80)
        parts.append(SubTask(
            pid=pid, part_idx=k, parts_total=g,
            res=round(res_per, 2),
            exec_total=float(exec_per), tx_total=float(tx),
            oi_flop_per_byte=oi,
            exec_left=float(exec_per), tx_left=float(tx),
            submit_ts=submit_ts
        ))
    return parts

def gen_parent_batch(next_pid: int, k: int, now_ts: int) -> Tuple[List[ParentTask], int]:
    """生成 k 个父任务（随机资源/时长/OI档位）"""
    parents=[]
    for _ in range(k):
        total_res = random.uniform(5.0, 10.0)
        total_exec = random.randint(480, 1200)
        oi = random.choice([150.0, 300.0, 600.0])  # FLOP/B 的三档
        p = ParentTask(pid=next_pid, total_res=total_res, total_exec=total_exec, submit_ts=now_ts, oi_flop_per_byte=oi)
        p.parts = split_parent_into_subtasks(next_pid, total_res, total_exec, now_ts, oi)
        p.remaining_parts = len(p.parts)
        parents.append(p)
        next_pid += 1
    return parents, next_pid

# ============================== 降火（模拟退火） ===============================
def anneal_adjust_assignment(npus: List[NPUNodes], pool: deque, temp: float,
                             cap_tflops: float, cpu_busy: bool,
                             B_eff: float, sched_overhead: float) -> None:
    """
    对“已在途（running/transferring）+ 池中队列”做轻量邻域：
    - 邻域1：把一个 transferring 子任务换到“更空”的另一卡（满足显存/资源）
    - 邻域2：从 pool 拉一个短任务替换某卡上的长任务（回填）
    目标：min(总时长) + λ_power·功耗 - λ_eff·Perf/W
    """
    if temp <= 1e-6:
        return

    L_PWR = 0.5
    L_EFF = 1.0

    def snapshot():
        info = []
        for n in npus:
            if not n.up:
                info.append((n.nid, 0.0, 0.0, 0.0))
                continue
            # 忙碌度：运行 + 0.5*传输
            busy_units = sum(st.res for st in n.running) + 0.5 * sum(st.res for st in n.transferring)
            # 计算侧上限：乘以 e_npu
            eff_hw = busy_units * NPU_TFLOPS_PER_UNIT * NPU_EFF
            if len(n.running) + len(n.transferring) > 0:
                avg_oi = sum(st.oi_flop_per_byte for st in (n.running + n.transferring)) / (len(n.running)+len(n.transferring))
            else:
                avg_oi = 300.0
            deliver = roofline_cap(eff_hw, B_eff, avg_oi, sched_overhead)
            todo_sec = sum(st.exec_left + st.tx_left for st in (n.running + n.transferring))
            rate_units_per_sec = (deliver / max(1e-9, (NPU_TFLOPS_PER_UNIT * NPU_EFF))) if deliver>0 else 1e-6
            n_time = todo_sec / max(1e-6, rate_units_per_sec)
            info.append((n.nid, deliver, n_time, busy_units))
        total_deliver = sum(d for _, d, _, _ in info)
        # 功率估算
        P_npu = 0.0
        for _, _, _, busy_units in info:
            u = min(1.0, busy_units / max(1.0, NPU_CAPACITY - NPU_MIN_FREE))
            P_npu += device_power(u, NPU_POWER_IDLE, NPU_POWER_TDP, NPU_POWER_BETA)
        P_cpu = device_power(1.0 if cpu_busy else 0.0, CPU_POWER_IDLE, CPU_POWER_TDP, CPU_POWER_BETA)
        P_total = P_npu + P_cpu
        perf_per_w = (total_deliver / P_total) if P_total>0 else 0.0
        total_time = max(n_time for _, _, n_time, _ in info) if info else 0.0
        cost = total_time + L_PWR*P_total - L_EFF*perf_per_w
        return cost, info, perf_per_w, P_total

    base_cost, _, _, _ = snapshot()

    def propose():
        # 邻域1：转移一个 transferring 子任务
        cand = [(n, st) for n in npus if n.up for st in n.transferring]
        if cand:
            n, st = random.choice(cand)
            others = [x for x in npus if x.up and x.nid != n.nid
                      and (x.free_res()-NPU_MIN_FREE) >= st.res
                      and (x.free_vram() >= st.res*NPU_VRAM_PER_RES)]
            if others:
                dst = max(others, key=lambda x: x.free_res())
                n.transferring.remove(st); n.used -= st.res; n.vram_used -= st.res*NPU_VRAM_PER_RES
                st.npu = dst.nid; dst.transferring.append(st)
                dst.used += st.res; dst.vram_used += st.res*NPU_VRAM_PER_RES
                return ("move", (n, dst, st))
        # 邻域2：回填替换（pool中短任务替换某卡长任务）
        running_cand = [(n, st) for n in npus if n.up for st in n.running]
        if pool and running_cand:
            n, st = random.choice(running_cand)
            short_pool = sorted([x for x in pool if (n.free_res()-NPU_MIN_FREE)>=x.res
                                 and n.free_vram()>=x.res*NPU_VRAM_PER_RES],
                                key=lambda x: (x.exec_left + x.tx_left, x.res))
            if short_pool:
                new_st = short_pool[0]
                n.running.remove(st); n.used -= st.res; n.vram_used -= st.res*NPU_VRAM_PER_RES
                st.state = "queued"; st.npu = None
                pool.appendleft(st)
                pool.remove(new_st)
                new_st.npu = n.nid; new_st.state = "transferring"
                n.transferring.append(new_st); n.used += new_st.res; n.vram_used += new_st.res*NPU_VRAM_PER_RES
                return ("swap", (n, st, new_st))
        return ("none", None)

    action, payload = propose()
    if action == "none":
        return

    new_cost, _, _, _ = snapshot()
    delta = new_cost - base_cost
    # Metropolis 接受准则
    if delta < 0.0 or random.random() < exp(-delta / temp):
        return  # 接受
    # 否则回滚
    if action == "move":
        n, dst, st = payload
        dst.transferring.remove(st); dst.used -= st.res; dst.vram_used -= st.res*NPU_VRAM_PER_RES
        st.npu = n.nid; n.transferring.append(st); n.used += st.res; n.vram_used += st.res*NPU_VRAM_PER_RES
    elif action == "swap":
        n, st_old, st_new = payload
        n.transferring.remove(st_new); n.used -= st_new.res; n.vram_used -= st_new.res*NPU_VRAM_PER_RES
        st_new.state = "queued"; st_new.npu = None; pool.appendleft(st_new)
        pool.remove(st_old); st_old.npu = n.nid; st_old.state = "running"
        n.running.append(st_old); n.used += st_old.res; n.vram_used += st_old.res*NPU_VRAM_PER_RES

# ================================== 主流程 ====================================
def main():
    # 设备与马尔可夫单元
    npus = [NPUNodes(i) for i in range(NPU_COUNT)]
    npu_markovs = [make_npu_markov(i) for i in range(NPU_COUNT)]
    cpu_markov = make_cpu_markov()

    # 子任务池、父任务、CPU汇总队列
    pool = deque()
    parents: Dict[int, ParentTask] = {}
    cpu_running = []            # [{'pid':int, 'work_left':float}]
    cpu_queue = deque()

    # 初始任务
    next_pid = 0
    now_ts = 0
    init_parents, next_pid = gen_parent_batch(next_pid, 6, now_ts)
    for p in init_parents:
        parents[p.pid] = p
        for st in p.parts:
            pool.append(st)

    # 累计指标
    sum_TC = 0.0                # Σ（每秒“NPU交付算力 + CPU算力”）

    # 设备侧固定带宽（可随时间/负载更改，此处为常数基线）
    B_raw = effective_bandwidth(B_PATHS, drop_ratio=UPSTREAM_DROP_RATIO)

    # CSV 文件初始化
    csv_file = open(LOG_CSV_PATH, "w", newline="", encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        "time",                   # 时间（秒）
        "utilization_percent",    # 利用率（%）
        "ACC_TFLOPS",             # 累计平均算力 ACC（TFLOPS）
        "cap_tflops_TFLOPS",      # 当前系统上限算力（TFLOPS）
        "NPU0_tasks",             # NPU0 正在跑的任务
        "NPU1_tasks",
        "NPU2_tasks",
    ])
    csv_file.flush()

    # ---- 调度：SRPT + Aging + 回填 ----
    def pick_best_task_for_npu(npu: NPUNodes, tnow: int) -> Optional[SubTask]:
        # 资源/显存约束
        candidates = [st for st in pool
                      if (npu.free_res()-NPU_MIN_FREE) >= st.res
                      and (npu.free_vram() >= st.res*NPU_VRAM_PER_RES)]
        if not candidates:
            return None
        def score(st: SubTask):
            # 剩余“壁钟时间”（传输+执行），等待越久越优先
            rem = st.tx_left + st.exec_left
            age = tnow - st.submit_ts
            return max(0.0, rem - AGE_BOOST_PER_SEC * age)
        candidates.sort(key=lambda s: (score(s), s.res))  # 同分时小任务回填
        return candidates[0]

    def try_assign(tnow: int):
        """尽可能把子任务塞进“最空”的NPU（预留余量），直到无法分配。"""
        assigned = False
        while True:
            choices = [n for n in npus if n.up and (n.free_res()-NPU_MIN_FREE) > 0.0 and n.free_vram()>0.0]
            if not choices:
                break
            npu = max(choices, key=lambda x: (x.free_res(), x.free_vram()))
            best = pick_best_task_for_npu(npu, tnow)
            if not best:
                break
            pool.remove(best)
            best.npu = npu.nid
            best.state = "transferring"
            npu.transferring.append(best)
            npu.used += best.res
            npu.vram_used += best.res * NPU_VRAM_PER_RES
            print_assign(tnow, best, npu)
            assigned = True
        return assigned

    def release_npu_tasks(nid: int, tnow: int, reason: str = "回滚"):
        """释放某卡的在途任务（传输/运行），回滚到检查点并回队等待。"""
        npu = npus[nid]
        for st in list(npu.transferring):
            npu.transferring.remove(st)
            npu.used -= st.res
            npu.vram_used -= st.res * NPU_VRAM_PER_RES
            st.state = "queued"; st.npu = None
            st.tx_left = st.tx_total; st.exec_left = st.exec_total
            pool.appendleft(st)
        for st in list(npu.running):
            npu.running.remove(st)
            npu.used -= st.res
            npu.vram_used -= st.res * NPU_VRAM_PER_RES
            st.state = "queued"; st.npu = None
            st.tx_left = st.tx_total; st.exec_left = st.exec_total
            pool.appendleft(st)

    def release_all_for_cpu_fault(tnow: int):
        """CPU进入故障态：系统算力归零，所有NPU在途任务回滚并回队。"""
        for nid in range(NPU_COUNT):
            release_npu_tasks(nid, tnow, reason="CPU故障")

    # 利用率/功率/ACC 统计
    def utilization_power_acc(now_ts: int, cpu_ok: bool):
        # 可用上限（仅可用NPU参与）
        cap_tflops = sum(max(0.0, (n.capacity - NPU_MIN_FREE)) * NPU_TFLOPS_PER_UNIT * NPU_EFF
                         for n, m in zip(npus, npu_markovs) if n.up and m.state == "N")
        # 实际占用（仅“运行中”的资源单位）
        used_units = sum(sum(st.res for st in n.running) for n, m in zip(npus, npu_markovs) if n.up and m.state == "N")
        used_tflops = used_units * NPU_TFLOPS_PER_UNIT * NPU_EFF
        # 功率估算：NPU 按每卡利用率；CPU 按是否在做汇总
        P_npu = 0.0
        for n, m in zip(npus, npu_markovs):
            if not n.up or m.state != "N":
                P_npu += device_power(0.0, NPU_POWER_IDLE, NPU_POWER_TDP, NPU_POWER_BETA)
            else:
                u = min(1.0, (sum(st.res for st in n.running) / max(1.0, n.capacity - NPU_MIN_FREE)))
                P_npu += device_power(u, NPU_POWER_IDLE, NPU_POWER_TDP, NPU_POWER_BETA)
        cpu_used_tflops = CPU_TFLOPS if (cpu_running and cpu_ok) else 0.0
        P_cpu = device_power(1.0 if (cpu_running and cpu_ok) else 0.0, CPU_POWER_IDLE, CPU_POWER_TDP, CPU_POWER_BETA)
        P_total = P_npu + P_cpu
        acc = (sum_TC / max(1, now_ts)) if now_ts > 0 else 0.0
        return cap_tflops, used_tflops, cpu_used_tflops, P_total, acc

    # 初始一次分配
    try_assign(now_ts)

    try:
        # ============================== 主循环 ==============================
        while True:
            # ---- 1) 三态马尔可夫演化（可能引发回滚/下线/修复/下发） ----
            # CPU 演化
            cpu_event = cpu_markov.step(now_ts)
            if cpu_event:
                old, new = cpu_event
                if new in ("F", "D"):
                    # 系统算力归零：回滚所有NPU在途任务
                    release_all_for_cpu_fault(now_ts)
                elif old in ("F",) and new == "N":
                    # CPU修复：允许继续调度
                    pass

            # NPU 演化
            for nid, (npu, mk) in enumerate(zip(npus, npu_markovs)):
                ev = mk.step(now_ts)
                if ev:
                    old, new = ev
                    if new in ("F", "D"):
                        # 故障/永久下线：释放该卡任务，标记不可用
                        release_npu_tasks(nid, now_ts, reason="NPU故障/下线")
                        npu.up = False
                    elif old in ("F",) and new == "N":
                        # 修复：恢复可用
                        npu.up = True

            cpu_ok = (cpu_markov.state == "N")

            # ---- 2) 心跳/功率/Perf-W/ACC ----
            cap_tflops, used_tflops, cpu_used_tflops, P_total, acc = utilization_power_acc(now_ts, cpu_ok)
            # 本秒交付算力（若CPU故障，NPU算力也视为0，因为我们已回滚在途并暂停推进）
            delivered = (used_tflops + cpu_used_tflops) if cpu_ok else 0.0
            sum_TC += delivered
            perf_per_w = delivered / P_total if P_total > 0 else 0.0

            if now_ts == 1 or now_ts % HEARTBEAT_EVERY == 0:
                print_heartbeat(now_ts, cpu_markov.state, npu_markovs, cap_tflops, used_tflops if cpu_ok else 0.0, cpu_used_tflops if cpu_ok else 0.0, perf_per_w, acc)

            # === 每 10 秒写一行 CSV ===
            if now_ts > 0 and now_ts % 10 == 0:
                util_percent = (used_tflops / cap_tflops * 100.0) if cap_tflops > 0 else 0.0
                row = [
                    now_ts,
                    round(util_percent, 2),
                    round(acc, 6),
                    round(cap_tflops, 6),
                    npu_tasks_str(npus[0]),
                    npu_tasks_str(npus[1]),
                    npu_tasks_str(npus[2]),
                ]
                csv_writer.writerow(row)
                csv_file.flush()

            # ---- 3) 传输与执行推进（仅当CPU可用时才推进） ----
            if cpu_ok:
                # 动态调度折损（随队列/并发变化）
                total_conc = sum(len(n.running) + len(n.transferring) for n in npus if n.up)
                sched_over = dynamic_sched_overhead(len(pool), total_conc)
                # 设备侧 B_eff（叠加 ρ）
                B_base = effective_bandwidth(B_PATHS, drop_ratio=UPSTREAM_DROP_RATIO)

                for n, mk in zip(npus, npu_markovs):
                    if not n.up or mk.state != "N":
                        continue

                    # --- 传输推进 ---
                    for st in list(n.transferring):
                        st.tx_left -= 1.0
                        if st.tx_left <= 0:
                            n.transferring.remove(st)
                            st.state = "running"
                            print_tx_done(now_ts, st, n)
                            n.running.append(st)

                    # --- 执行推进（Roofline + e_npu） ---
                    for st in list(n.running):
                        # 计算侧上限：资源单位 × 每单位TFLOPS × e_npu
                        C_hw = st.res * NPU_TFLOPS_PER_UNIT * NPU_EFF

                        # 估算 I/O/Compute 比例以求 ρ（数量级近似）
                        flops_per_sec = C_hw
                        data_per_sec = flops_per_sec / max(1.0, st.oi_flop_per_byte)  # B/s（近似）
                        theo_agg = sum(gamma*delta*B for (B, delta, gamma) in B_PATHS)
                        Tio = data_per_sec / max(1e-6, theo_agg)  # 相对尺度
                        Tcomp = 1.0
                        rho = rho_overlap(Tio, Tcomp, IO_OVERLAP_K)

                        B_eff = B_base * rho
                        deliver = roofline_cap(C_hw, B_eff, st.oi_flop_per_byte, sched_over)

                        # 用“等效推进秒数”扣减：deliver/C_hw ∈ (0,1]
                        eq_seconds = max(0.05, min(1.0, deliver / max(1e-6, C_hw)))
                        st.exec_left -= eq_seconds
                        if st.exec_left <= 0:
                            n.running.remove(st)
                            n.used -= st.res
                            n.vram_used -= st.res * NPU_VRAM_PER_RES
                            st.state = "done"
                            print_finish(now_ts, st, n)

            # ---- 4) 父任务完成→进入CPU汇总（只入队一次） ----
            # 刷新每个父任务剩余份数
            for p in parents.values():
                done_cnt = sum(1 for st in p.parts if st.state == "done")
                p.remaining_parts = len(p.parts) - done_cnt
            # 入队新完结的父任务
            for p in list(parents.values()):
                if p.remaining_parts == 0:
                    if not any(item['pid']==p.pid for item in cpu_running) and not any(pid==p.pid for pid,_ in cpu_queue):
                        total_work_units = sum(part.res * part.exec_total for part in p.parts)
                        cpu_work = max(1.0, BETA * total_work_units * NPU_TFLOPS_PER_UNIT)  # TFLOPS·s@1TFLOPS
                        cpu_queue.append((p.pid, cpu_work))

            # ---- 5) CPU并行汇总（仅在CPU正常时推进） ----
            if cpu_ok:
                # 启动新的汇总（并发上限）
                while len(cpu_running) < CPU_MAX_PARALLEL and cpu_queue:
                    pid, work = cpu_queue.popleft()
                    parallel_n = max(1, len(cpu_running) + 1)
                    est_dt = work / (CPU_TFLOPS / parallel_n)
                    eta = now_ts + ceil(est_dt)
                    print_cpu_group_start(now_ts, pid, est_dt, eta_ts=eta)
                    cpu_running.append({"pid": pid, "work_left": work})

                # 扣减工作量
                if cpu_running:
                    per_group = CPU_TFLOPS / len(cpu_running)
                    for item in list(cpu_running):
                        item["work_left"] -= per_group
                        if item["work_left"] <= 0:
                            print_cpu_group_done(now_ts, item["pid"])
                            cpu_running.remove(item)

            # ---- 6) 快速分配（SRPT + Aging + 回填；仅CPU正常时尝试） ----
            if cpu_ok:
                try_assign(now_ts)

            # ---- 7) 周期降火（模拟退火）微调（仅CPU正常时） ----
            if cpu_ok and now_ts % ANNEAL_PERIOD == 0 and now_ts > 0:
                # 退火温度递降
                sa_temp = SA_T0
                # 选择一个固定的 B_eff 与调度折损快照（近似）
                total_conc = sum(len(n.running) + len(n.transferring) for n in npus if n.up)
                sched_over = dynamic_sched_overhead(len(pool), total_conc)
                B_base = effective_bandwidth(B_PATHS, drop_ratio=UPSTREAM_DROP_RATIO)
                for _ in range(SA_STEPS):
                    anneal_adjust_assignment(npus, pool, sa_temp, cap_tflops, bool(cpu_running), B_base, sched_over)
                    sa_temp *= SA_ALPHA

            # ---- 8) 持续下发（池浅 & 利用率低 → 补货） ----
            util = (used_tflops / cap_tflops) if (cap_tflops>0) else 0.0
            if len(pool) < POOL_LOW_WM and util < UTIL_LOW:
                want = min(POOL_HIGH_WM - len(pool), POOL_LOW_WM)
                if want > 0:
                    k = max(3, ceil(want / NPU_COUNT))
                    new_parents, next_pid = gen_parent_batch(next_pid, k, now_ts)
                    for p in new_parents:
                        parents[p.pid] = p
                        for st in p.parts:
                            pool.append(st)
                    print(f"{ts(now_ts)} 新任务批次到达，共 {k} 个父任务（拆分后 {sum(len(p.parts) for p in new_parents)} 个子任务）；开始分配")
                    if cpu_ok:
                        try_assign(now_ts)

            # ---- 9) 推进时间（放慢打印） ----
            now_ts += 1
            if TICK_SLEEP > 0:
                time.sleep(TICK_SLEEP)
    except KeyboardInterrupt:
        print("\n收到中断信号，准备退出并关闭日志文件。")
    finally:
        try:
            csv_file.close()
        except Exception:
            pass

# 入口
if __name__ == "__main__":
    main()
