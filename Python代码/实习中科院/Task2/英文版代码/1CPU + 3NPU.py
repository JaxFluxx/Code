#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
System workflow:
Task arrives -> classified into large/medium/small -> split into subtasks by target duration;
Pick the emptiest GPU; pack suitable subtasks using (SRPT + Aging + Backfill);
Each subtask experiences Transfer -> Execute;
When all subtasks of a parent are done -> CPU aggregation;
GPU/CPU fault? -> release -> repair -> reschedule;
If utilization is low or pool becomes shallow -> auto-replenish; system keeps running.
"""

import time
import random
import csv
from collections import deque
from math import ceil, exp
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
from random import expovariate

# ------------------------ Global random seed (for reproducibility) ------------------------
random.seed(23)

# ======================== Hardware & system parameters (customize) =======================
NPU_COUNT = 3
NPU_CAPACITY = 8.00              # concurrent "resource units" per card (abstract compute slots)
NPU_MIN_FREE = 0.50              # reserve to avoid fragmentation
NPU_TFLOPS_PER_UNIT = 5.0        # 1 "resource unit" ≈ 5 TFLOPS

NPU_VRAM_GB = 8.0                # VRAM per card (GB)
NPU_VRAM_PER_RES = 1.0           # VRAM per resource unit (GB), for simulation

# NPU efficiencies (example constants)
NPU_ETA_SCAL   = 0.92            # scaling efficiency
NPU_ETA_SCHED  = 0.93            # scheduling efficiency
NPU_ETA_JITTER = 0.85            # jitter/straggler effect
NPU_EFF = NPU_ETA_SCAL * NPU_ETA_SCHED * NPU_ETA_JITTER  # ≈ 0.728

# CPU aggregation capacity (TFLOPS) & parallel limit
CPU_TFLOPS = 1.00
CPU_MAX_PARALLEL = 2
BETA = 0.05                      # CPU work per NPU result

# Power curve parameters (example; replace with measured/vendor data)
NPU_POWER_TDP = 220.0            # W
NPU_POWER_IDLE = 35.0            # W
NPU_POWER_BETA = 1.2
CPU_POWER_TDP = 150.0            # W
CPU_POWER_IDLE = 25.0            # W
CPU_POWER_BETA = 1.1

# Bandwidth model: multi-path + protocol overhead + share
# (B_theo_GBs, protocol_eff_delta, share_gamma)
B_PATHS = [
    (16.0, 0.85, 0.6),           # PCIe 4.0 x16: 16 GB/s, protocol eff 0.85, share 0.6
    (32.0, 0.90, 0.4),           # local/fast path: 32 GB/s, eff 0.9, share 0.4
]
UPSTREAM_DROP_RATIO = 0.0        # upstream data drop ratio (e.g., prefiltering), 0~1
IO_OVERLAP_K = 2                 # number of buffering pipelines for IO-Compute overlap
SCHED_OVERHEAD_BASE = 0.05       # base scheduling overhead

# Simulated annealing (lightweight neighbor search for "in-flight" assignments)
ANNEAL_PERIOD = 30               # trigger every simulated seconds
SA_T0 = 1.3
SA_ALPHA = 0.996
SA_STEPS = 300

# Run/print control
HEARTBEAT_EVERY = 50             # heartbeat print interval (sim seconds)
TICK_SLEEP = 0.02                # real sleep per simulated second

# Continuous dispatch (keep target utilization window)
POOL_LOW_WM  = NPU_COUNT * 6     # low watermark for subtask pool
POOL_HIGH_WM = NPU_COUNT * 12    # max batch replenish size
UTIL_LOW  = 0.70                 # replenish when below
UTIL_HIGH = 0.85                 # hold when above

# SRPT + Aging
AGE_BOOST_PER_SEC = 0.02

# CSV log file
LOG_CSV_PATH = "system_log.csv"

# ----------------------- Reliability: CTMC 3-state (N/F/D) ---------------------------
HOUR = 3600.0
# NPU
NPU_LAMBDA_NF = 0.00200 / HOUR
NPU_MU_FN     = 1.00000 / HOUR
NPU_LAMBDA_ND = 4.57e-5 / HOUR
NPU_LAMBDA_FD = 2.00e-4 / HOUR
# CPU
CPU_LAMBDA_NF = 1.00e-3 / HOUR
CPU_MU_FN     = 0.50    / HOUR
CPU_LAMBDA_ND = 1.00e-4 / HOUR
CPU_LAMBDA_FD = 1.00e-4 / HOUR

class MarkovUnit:
    """Continuous-time Markov 3-state: N (normal) / F (temporary fault) / D (permanent, absorbing)."""
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
        dt = max(1, int(round(expovariate(lam))))  # integral seconds, at least 1
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

# ============================== Data structures ===================================
@dataclass
class SubTask:
    pid: int
    part_idx: int
    parts_total: int
    # resources / time
    res: float
    exec_total: float
    tx_total: float
    # bandwidth metric
    oi_flop_per_byte: float
    # runtime
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

# ============================== Print / utilities ===================================
def ts(t: int) -> str:
    return f"Time[{t}]"

def print_assign(t, st, npu):
    print(f"{ts(t)} Task {st.label()} assigned to NPU{npu.nid}, starting TRANSFER. "
          f"(res={st.res:.2f}, exec={st.exec_total:.0f}s, "
          f"NPU free res={npu.free_res():.2f}, VRAM free={npu.free_vram():.1f}GB)")

def print_tx_done(t, st, npu):
    print(f"{ts(t)} Task {st.label()} on NPU{npu.nid} finished TRANSFER → start EXECUTE")

def print_finish(t, st, npu):
    print(f"{ts(t)} Task {st.label()} finished on NPU{npu.nid}")

def print_cpu_group_start(t, pid, cpu_dt, eta_ts):
    print(f"{ts(t)} Parent {pid} completed NPU stage → enter CPU aggregation (~{cpu_dt:.1f}s), ETA {eta_ts}")

def print_cpu_group_done(t, pid):
    print(f"{ts(t)} Parent {pid} CPU aggregation DONE")

def print_heartbeat(t, cpu_state, npu_markovs, cap_tflops, used_tflops, cpu_used_tflops, avg_perf_per_w, acc_tflops):
    npu_states = ", ".join([f"{m.name[-1]}:{m.state}" for m in npu_markovs])
    util = (used_tflops / cap_tflops * 100.0) if cap_tflops>0 else 0.0
    print(
        f"{ts(t)} [Heartbeat] CPU={cpu_state} | NPU[{npu_states}] | "
        f"NPU_used≈{used_tflops:.2f} TFLOPS | CPU≈{cpu_used_tflops:.2f} TFLOPS | "
        f"Cap≈{cap_tflops:.2f} TFLOPS | Util≈{util:.0f}% | Perf/W≈{avg_perf_per_w:.3f} | "
        f"ACC≈{acc_tflops:.2f} TFLOPS"
    )

def device_power(u: float, p_idle: float, p_tdp: float, beta: float) -> float:
    """P(u) = P_idle + (P_tdp - P_idle) * u^beta, u in [0,1]"""
    u = max(0.0, min(1.0, u))
    return p_idle + (p_tdp - p_idle) * (u ** beta)

def npu_tasks_str(npu: NPUNodes) -> str:
    if not npu.running:
        return "-"
    return "|".join(st.label() for st in npu.running)

# =========================== Power, bandwidth & Roofline =============================
def effective_bandwidth(paths: List[Tuple[float, float, float]], drop_ratio: float = 0.0) -> float:
    """B_eff = (1 - drop_ratio) * Σ (gamma * delta * B_theo)  [GB/s]"""
    agg = 0.0
    for B_theo, delta, gamma in paths:
        agg += gamma * delta * B_theo
    agg *= (1.0 - drop_ratio)
    return max(0.0, agg)

def rho_overlap(Tio: float, Tcomp: float, k: int) -> float:
    """IO-Compute overlap ρ."""
    if Tio <= 0 or Tcomp <= 0:
        return 1.0
    if Tio <= Tcomp:
        return 1.0
    return max(0.0, min(1.0, (Tcomp + (k - 1) * min(Tio, Tcomp)) / (k * Tio)))

def roofline_cap(C_hw: float, B_eff: float, OI: float, sched_overhead: float) -> float:
    """C_task = min(C_hw, B_eff * OI) * (1 - sched_overhead)"""
    return max(0.0, min(C_hw, B_eff * OI) * (1.0 - sched_overhead))

def dynamic_sched_overhead(pool_len: int, total_concurrency: int) -> float:
    """Dynamic scheduling overhead: base + queue pressure + concurrency term (capped at 25%)."""
    extra = 0.0
    extra += min(0.10, 0.002 * pool_len)
    extra += min(0.08, 0.005 * max(0, total_concurrency - NPU_COUNT))
    return min(0.25, SCHED_OVERHEAD_BASE + extra)

# =============================== Task gen / split ================================
def split_parent_into_subtasks(pid: int, total_res: float, total_exec: int, submit_ts: int, oi: float) -> List[SubTask]:
    """Split parent into g parts so each part is ≈240s; evenly divide res/time; carry OI."""
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
    """Generate k parent tasks with random res/duration/OI tiers."""
    parents=[]
    for _ in range(k):
        total_res = random.uniform(5.0, 10.0)
        total_exec = random.randint(480, 1200)
        oi = random.choice([150.0, 300.0, 600.0])  # FLOP/B tiers
        p = ParentTask(pid=next_pid, total_res=total_res, total_exec=total_exec, submit_ts=now_ts, oi_flop_per_byte=oi)
        p.parts = split_parent_into_subtasks(next_pid, total_res, total_exec, now_ts, oi)
        p.remaining_parts = len(p.parts)
        parents.append(p)
        next_pid += 1
    return parents, next_pid

# ============================== Simulated annealing ===============================
def anneal_adjust_assignment(npus: List[NPUNodes], pool: deque, temp: float,
                             cap_tflops: float, cpu_busy: bool,
                             B_eff: float, sched_overhead: float) -> None:
    """
    Lightweight neighbors over in-flight (running/transferring) + queued pool:
    N1: move a transferring subtask to a "emptier" card (if res/VRAM allow);
    N2: backfill swap: replace a long running task with a short queued one.
    Objective: min(total_time) + λ_power·Power - λ_eff·Perf/W.
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
            busy_units = sum(st.res for st in n.running) + 0.5 * sum(st.res for st in n.transferring)
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
        # power
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
        # N1: move a transferring task
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
        # N2: backfill swap
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
    # Metropolis criterion
    if delta < 0.0 or random.random() < exp(-delta / temp):
        return  # accept
    # rollback
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

# ================================== Main ====================================
def main():
    # devices & Markov units
    npus = [NPUNodes(i) for i in range(NPU_COUNT)]
    npu_markovs = [make_npu_markov(i) for i in range(NPU_COUNT)]
    cpu_markov = make_cpu_markov()

    # pools & queues
    pool = deque()
    parents: Dict[int, ParentTask] = {}
    cpu_running = []            # [{'pid':int, 'work_left':float}]
    cpu_queue = deque()

    # initial tasks
    next_pid = 0
    now_ts = 0
    init_parents, next_pid = gen_parent_batch(next_pid, 6, now_ts)
    for p in init_parents:
        parents[p.pid] = p
        for st in p.parts:
            pool.append(st)

    # accumulators
    sum_TC = 0.0                # sum over time of delivered compute (NPU+CPU)

    # fixed bandwidth baseline (can be dynamic)
    B_raw = effective_bandwidth(B_PATHS, drop_ratio=UPSTREAM_DROP_RATIO)

    # CSV init
    csv_file = open(LOG_CSV_PATH, "w", newline="", encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        "time",
        "utilization_percent",
        "ACC_TFLOPS",
        "cap_tflops_TFLOPS",
        "NPU0_tasks",
        "NPU1_tasks",
        "NPU2_tasks",
    ])
    csv_file.flush()

    # ---- scheduling: SRPT + Aging + Backfill ----
    def pick_best_task_for_npu(npu: NPUNodes, tnow: int) -> Optional[SubTask]:
        candidates = [st for st in pool
                      if (npu.free_res()-NPU_MIN_FREE) >= st.res
                      and (npu.free_vram() >= st.res*NPU_VRAM_PER_RES)]
        if not candidates:
            return None
        def score(st: SubTask):
            rem = st.tx_left + st.exec_left
            age = tnow - st.submit_ts
            return max(0.0, rem - AGE_BOOST_PER_SEC * age)
        candidates.sort(key=lambda s: (score(s), s.res))
        return candidates[0]

    def try_assign(tnow: int):
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

    def release_npu_tasks(nid: int, tnow: int, reason: str = "rollback"):
        """Release tasks on a given NPU (rollback to last checkpoint and requeue)."""
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
        """CPU fault: set system compute to zero by rolling back all NPU in-flight tasks."""
        for nid in range(NPU_COUNT):
            release_npu_tasks(nid, tnow, reason="CPU fault")

    # utilization / power / ACC
    def utilization_power_acc(now_ts: int, cpu_ok: bool):
        cap_tflops = sum(max(0.0, (n.capacity - NPU_MIN_FREE)) * NPU_TFLOPS_PER_UNIT * NPU_EFF
                         for n, m in zip(npus, npu_markovs) if n.up and m.state == "N")
        used_units = sum(sum(st.res for st in n.running) for n, m in zip(npus, npu_markovs) if n.up and m.state == "N")
        used_tflops = used_units * NPU_TFLOPS_PER_UNIT * NPU_EFF
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

    # initial assignment
    try_assign(now_ts)

    try:
        # ============================== Main loop ==============================
        while True:
            # ---- 1) CTMC evolution (may trigger rollback/offline/repair) ----
            cpu_event = cpu_markov.step(now_ts)
            if cpu_event:
                old, new = cpu_event
                if new in ("F", "D"):
                    release_all_for_cpu_fault(now_ts)
                elif old in ("F",) and new == "N":
                    pass

            for nid, (npu, mk) in enumerate(zip(npus, npu_markovs)):
                ev = mk.step(now_ts)
                if ev:
                    old, new = ev
                    if new in ("F", "D"):
                        release_npu_tasks(nid, now_ts, reason="NPU fault/offline")
                        npu.up = False
                    elif old in ("F",) and new == "N":
                        npu.up = True

            cpu_ok = (cpu_markov.state == "N")

            # ---- 2) Heartbeat / power / Perf-W / ACC ----
            cap_tflops, used_tflops, cpu_used_tflops, P_total, acc = utilization_power_acc(now_ts, cpu_ok)
            delivered = (used_tflops + cpu_used_tflops) if cpu_ok else 0.0
            sum_TC += delivered
            perf_per_w = delivered / P_total if P_total > 0 else 0.0

            if now_ts == 1 or now_ts % HEARTBEAT_EVERY == 0:
                print_heartbeat(now_ts, cpu_markov.state, npu_markovs, cap_tflops, used_tflops if cpu_ok else 0.0, cpu_used_tflops if cpu_ok else 0.0, perf_per_w, acc)

            # === CSV every 10s ===
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

            # ---- 3) Advance transfer/execute (only when CPU is OK) ----
            if cpu_ok:
                total_conc = sum(len(n.running) + len(n.transferring) for n in npus if n.up)
                sched_over = dynamic_sched_overhead(len(pool), total_conc)
                B_base = effective_bandwidth(B_PATHS, drop_ratio=UPSTREAM_DROP_RATIO)

                for n, mk in zip(npus, npu_markovs):
                    if not n.up or mk.state != "N":
                        continue

                    # --- transfer ---
                    for st in list(n.transferring):
                        st.tx_left -= 1.0
                        if st.tx_left <= 0:
                            n.transferring.remove(st)
                            st.state = "running"
                            print_tx_done(now_ts, st, n)
                            n.running.append(st)

                    # --- execute (Roofline + e_npu) ---
                    for st in list(n.running):
                        C_hw = st.res * NPU_TFLOPS_PER_UNIT * NPU_EFF
                        flops_per_sec = C_hw
                        data_per_sec = flops_per_sec / max(1.0, st.oi_flop_per_byte)  # B/s approx
                        theo_agg = sum(gamma*delta*B for (B, delta, gamma) in B_PATHS)
                        Tio = data_per_sec / max(1e-6, theo_agg)
                        Tcomp = 1.0
                        rho = rho_overlap(Tio, Tcomp, IO_OVERLAP_K)

                        B_eff = B_base * rho
                        deliver = roofline_cap(C_hw, B_eff, st.oi_flop_per_byte, sched_over)

                        eq_seconds = max(0.05, min(1.0, deliver / max(1e-6, C_hw)))
                        st.exec_left -= eq_seconds
                        if st.exec_left <= 0:
                            n.running.remove(st)
                            n.used -= st.res
                            n.vram_used -= st.res * NPU_VRAM_PER_RES
                            st.state = "done"
                            print_finish(now_ts, st, n)

            # ---- 4) Parent finished -> CPU aggregation (enqueue once) ----
            for p in parents.values():
                done_cnt = sum(1 for st in p.parts if st.state == "done")
                p.remaining_parts = len(p.parts) - done_cnt
            for p in list(parents.values()):
                if p.remaining_parts == 0:
                    if not any(item['pid']==p.pid for item in cpu_running) and not any(pid==p.pid for pid,_ in cpu_queue):
                        total_work_units = sum(part.res * part.exec_total for part in p.parts)
                        cpu_work = max(1.0, BETA * total_work_units * NPU_TFLOPS_PER_UNIT)  # TFLOPS·s @1TFLOPS
                        cpu_queue.append((p.pid, cpu_work))

            # ---- 5) CPU parallel aggregation (only when CPU is OK) ----
            if cpu_ok:
                while len(cpu_running) < CPU_MAX_PARALLEL and cpu_queue:
                    pid, work = cpu_queue.popleft()
                    parallel_n = max(1, len(cpu_running) + 1)
                    est_dt = work / (CPU_TFLOPS / parallel_n)
                    eta = now_ts + ceil(est_dt)
                    print_cpu_group_start(now_ts, pid, est_dt, eta_ts=eta)
                    cpu_running.append({"pid": pid, "work_left": work})

                if cpu_running:
                    per_group = CPU_TFLOPS / len(cpu_running)
                    for item in list(cpu_running):
                        item["work_left"] -= per_group
                        if item["work_left"] <= 0:
                            print_cpu_group_done(now_ts, item["pid"])
                            cpu_running.remove(item)

            # ---- 6) Fast assign (SRPT + Aging + Backfill; only when CPU is OK) ----
            if cpu_ok:
                try_assign(now_ts)

            # ---- 7) Periodic annealing (only when CPU is OK) ----
            if cpu_ok and now_ts % ANNEAL_PERIOD == 0 and now_ts > 0:
                sa_temp = SA_T0
                total_conc = sum(len(n.running) + len(n.transferring) for n in npus if n.up)
                sched_over = dynamic_sched_overhead(len(pool), total_conc)
                B_base = effective_bandwidth(B_PATHS, drop_ratio=UPSTREAM_DROP_RATIO)
                for _ in range(SA_STEPS):
                    anneal_adjust_assignment(npus, pool, sa_temp, cap_tflops, bool(cpu_running), B_base, sched_over)
                    sa_temp *= SA_ALPHA

            # ---- 8) Continuous dispatch (replenish when pool shallow & util low) ----
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
                    print(f"{ts(now_ts)} New batch arrived: {k} parents "
                          f"({sum(len(p.parts) for p in new_parents)} subtasks). Dispatching...")
                    if cpu_ok:
                        try_assign(now_ts)

            # ---- 9) advance time ----
            now_ts += 1
            if TICK_SLEEP > 0:
                time.sleep(TICK_SLEEP)
    except KeyboardInterrupt:
        print("\nInterrupted by user. Closing logs and exiting.")
    finally:
        try:
            csv_file.close()
        except Exception:
            pass

# entry
if __name__ == "__main__":
    main()
