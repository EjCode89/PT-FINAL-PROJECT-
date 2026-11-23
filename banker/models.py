"""Plain data containers"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class SafetyStep:
    """One comparison made by the safety algorithm (successful OR failed)."""
    number: int                      # running step number: 1, 2, 3 ...
    process: int                     # which process Pi was checked
    need: List[int]                  # Need[i]
    work_before: List[int]           # Work before the check
    can_run: bool                    # result of  Need[i] <= Work
    released: Optional[List[int]]    # Allocation[i] given back (only if can_run)
    work_after: List[int]            # Work after the check
    finish_after: List[bool]         # snapshot of the whole Finish vector
    explanation: str                 # plain-English explanation


@dataclass
class SafetyResult:
    """Everything the safety algorithm discovers."""
    safe: bool
    sequence: List[int]              # safe sequence (process indexes)
    steps: List[SafetyStep]          # every comparison, in order
    need: List[List[int]]
    available: List[int]
    unfinished: List[int]            # processes that never finished
    final_work: List[int]
    blocked_reasons: Dict[int, str]  # {process index: why it cannot run}


@dataclass
class RequestResult:
    """Outcome of a resource request."""
    decision: str                    # GRANTED / NOT GRANTED / WAIT / REJECTED
    message: str                     # one-line summary
    log: List[Tuple[str, str]]       # (style, text) lines describing each check
    safety: Optional[SafetyResult]
    new_allocation: List[List[int]]  # differs from the original ONLY if GRANTED
