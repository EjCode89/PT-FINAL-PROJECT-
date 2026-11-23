"""OPTIONAL extension: the Resource-Request algorithm.

To remove this feature: delete this file, remove its import from
banker/__init__.py, and delete gui/request_tab.py (see README).
"""

from typing import List, Tuple

from .algorithm import BankerAlgorithm
from .data import fmt, resource_name
from .models import RequestResult


def request_resources(total, allocation, maximum, pid, request) -> RequestResult:

    n, m = len(allocation), len(total)
    if not 0 <= pid < n:
        raise ValueError(f"Process index {pid} is out of range (0..{n - 1}).")
    if len(request) != m:
        raise ValueError(f"The request vector must have {m} values.")
    if any(v < 0 for v in request):
        raise ValueError("The request vector cannot contain negative values.")

    original_alloc = [row[:] for row in allocation]            # untouched copy
    need = BankerAlgorithm.calculate_need(maximum, allocation)
    available = BankerAlgorithm.calculate_available(total, allocation)
    log: List[Tuple[str, str]] = []

    # ---- Check 1: Request <= Need -------------------------------------
    log.append(("heading", f"CHECK 1 — Is Request ≤ Need[P{pid}] ?"))
    log.append(("text", f"Request = {fmt(request)}    Need[P{pid}] = {fmt(need[pid])}"))
    over_need = [j for j in range(m) if request[j] > need[pid][j]]
    if over_need:
        why = ", ".join(f"{resource_name(j)}: {request[j]} > {need[pid][j]}"
                        for j in over_need)
        log.append(("fail", f"FALSE ({why})"))
        msg = (f"P{pid} asked for more than its declared maximum remaining "
               f"need, so the request is rejected.")
        log.append(("fail", "DECISION: REJECTED — " + msg))
        return RequestResult("REJECTED", msg, log, None, original_alloc)
    log.append(("pass", "TRUE — the request is within the declared maximum need."))

    # ---- Check 2: Request <= Available --------------------------------
    log.append(("heading", "CHECK 2 — Is Request ≤ Available ?"))
    log.append(("text", f"Request = {fmt(request)}    Available = {fmt(available)}"))
    over_avail = [j for j in range(m) if request[j] > available[j]]
    if over_avail:
        why = ", ".join(f"{resource_name(j)}: {request[j]} > {available[j]}"
                        for j in over_avail)
        log.append(("fail", f"FALSE ({why})"))
        msg = (f"The requested resources are not currently available, "
               f"so P{pid} must WAIT.")
        log.append(("fail", "DECISION: WAIT — " + msg))
        return RequestResult("WAIT", msg, log, None, original_alloc)
    log.append(("pass", "TRUE — the resources are currently available."))

    # ---- Step 3: pretend to allocate (copies only) --------------------
    new_alloc = [row[:] for row in allocation]
    new_alloc[pid] = [new_alloc[pid][j] + request[j] for j in range(m)]
    new_available = [available[j] - request[j] for j in range(m)]
    new_need_pid = [need[pid][j] - request[j] for j in range(m)]

    log.append(("heading", "STEP 3 — Tentative (pretend) allocation"))
    log.append(("text", f"Available       : {fmt(available)} − {fmt(request)} = {fmt(new_available)}"))
    log.append(("text", f"Allocation[P{pid}] : {fmt(allocation[pid])} + {fmt(request)} = {fmt(new_alloc[pid])}"))
    log.append(("text", f"Need[P{pid}]       : {fmt(need[pid])} − {fmt(request)} = {fmt(new_need_pid)}"))

    # ---- Step 4: run the safety algorithm on the tentative state ------
    safety = BankerAlgorithm.safety_algorithm(total, new_alloc, maximum)
    log.append(("heading", "STEP 4 — Safety test on the tentative state"))
    for s in safety.steps:
        verdict = "TRUE" if s.can_run else "FALSE"
        log.append(("text", f"Step {s.number}: P{s.process}  Need {fmt(s.need)} ≤ "
                            f"Work {fmt(s.work_before)} ?  {verdict}"))
        log.append(("pass" if s.can_run else "fail", "      " + s.explanation))

    # ---- Step 5 / 6: grant, or roll back ------------------------------
    if safety.safe:
        seq = " → ".join(f"P{p}" for p in safety.sequence)
        msg = f"The tentative state is SAFE (sequence: {seq}). Request GRANTED."
        log.append(("heading", "STEP 5 — Final decision"))
        log.append(("pass", "DECISION: GRANTED — " + msg))
        log.append(("pass", "The new allocation is kept."))
        return RequestResult("GRANTED", msg, log, safety, new_alloc)

    msg = "The tentative state is UNSAFE. Request NOT GRANTED and rolled back."
    log.append(("heading", "STEP 6 — Final decision"))
    log.append(("fail", "DECISION: NOT GRANTED — " + msg))
    log.append(("fail", "Rollback complete: Available, Allocation and Need are "
                        "restored to their original values."))
    return RequestResult("NOT GRANTED", msg, log, safety, original_alloc)
