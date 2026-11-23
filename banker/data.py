"""
Section 1: LOAD SAMPLE DATA button
Section 2: tiny formatting helpers
"""

# =====================================================================
# 1. SAMPLE DATA 
# =====================================================================

SAMPLE_DATA = {
    "total": [10, 5, 7],
    "allocation": [
        [0, 1, 0],   # P0
        [2, 0, 0],   # P1
        [3, 0, 2],   # P2
        [2, 1, 1],   # P3
        [0, 0, 2],   # P4
    ],
    "maximum": [
        [7, 5, 3],   # P0
        [3, 2, 2],   # P1
        [9, 0, 2],   # P2
        [2, 2, 2],   # P3
        [4, 3, 3],   # P4
    ],
}

# =====================================================================
# 2. FORMATTING HELPERS
# =====================================================================

def resource_name(index: int) -> str:
    return chr(ord("A") + index)

def process_name(index: int) -> str:
    return f"P{index}"

def fmt(vector) -> str:
    return "[" + ", ".join(str(v) for v in vector) + "]"

def fmt_finish(finish) -> str:
    return "[" + ", ".join("T" if f else "F" for f in finish) + "]"
