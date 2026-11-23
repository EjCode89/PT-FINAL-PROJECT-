"""
The Banker's Safety Algorithm.
"""

from typing import List

from .data import fmt, resource_name
from .models import SafetyResult, SafetyStep


class BankerAlgorithm:

    # -----------------------------------------------------------------
    # Validation of the system state
    # -----------------------------------------------------------------
    @staticmethod
    def validate_state(total, allocation, maximum) -> List[str]:
        """Return a list of error messages (an empty list means: valid)."""
        errors: List[str] = []
        n, m = len(allocation), len(total)

        if n < 1:
            errors.append("The number of processes must be at least 1.")
        if m < 1:
            errors.append("The number of resource types must be at least 1.")
        if errors:
            return errors

        if (len(maximum) != n
                or any(len(row) != m for row in allocation)
                or any(len(row) != m for row in maximum)):
            return ["Matrix dimensions do not match the number of processes "
                    "and resource types."]

        if any(v < 0 for v in total):
            errors.append("Total resources cannot be negative.")
        if any(v < 0 for row in allocation for v in row):
            errors.append("Allocation values cannot be negative.")
        if any(v < 0 for row in maximum for v in row):
            errors.append("Max values cannot be negative.")
        if errors:
            return errors


        for i in range(n):
            for j in range(m):
                if allocation[i][j] > maximum[i][j]:
                    errors.append(
                        f"P{i}: Allocation of {resource_name(j)} "
                        f"({allocation[i][j]}) is greater than its Max "
                        f"({maximum[i][j]}).")


        for j in range(m):
            allocated = sum(allocation[i][j] for i in range(n))
            if allocated > total[j]:
                errors.append(
                    f"Resource {resource_name(j)}: total allocated ({allocated}) "
                    f"is more than the total resources ({total[j]}).")
        return errors

    # -----------------------------------------------------------------
    # STEP 1:  Need = Max - Allocation
    # -----------------------------------------------------------------
    @staticmethod
    def calculate_need(maximum, allocation) -> List[List[int]]:
        return [[mx - al for mx, al in zip(max_row, alloc_row)]
                for max_row, alloc_row in zip(maximum, allocation)]

    # -----------------------------------------------------------------
    # STEP 2:  Available = Total - (column sums of Allocation)
    # -----------------------------------------------------------------
    @staticmethod
    def calculate_available(total, allocation) -> List[int]:
        return [total[j] - sum(row[j] for row in allocation)
                for j in range(len(total))]

    # -----------------------------------------------------------------
    # STEPS 3-7:  the Safety Algorithm
    # -----------------------------------------------------------------
    @staticmethod
    def safety_algorithm(total, allocation, maximum) -> SafetyResult:
        n, m = len(allocation), len(total)

        need = BankerAlgorithm.calculate_need(maximum, allocation)
        available = BankerAlgorithm.calculate_available(total, allocation)

        # Step 3: Work = Available, Finish[i] = False for every process
        work = available[:]
        finish = [False] * n
        sequence: List[int] = []
        steps: List[SafetyStep] = []
        step_number = 0

        # Steps 4-6: keep scanning P0..Pn-1 until a full scan finishes nobody
        progress = True
        while progress:
            progress = False
            for i in range(n):
                if finish[i]:
                    continue                   

                step_number += 1
                work_before = work[:]

                # Component-wise test:  Need[i] <= Work
                too_big = [j for j in range(m) if need[i][j] > work[j]]

                if not too_big:
                    # Step 5: Pi can finish -> it releases its allocation
                    released = allocation[i][:]
                    work = [work[j] + released[j] for j in range(m)]
                    finish[i] = True
                    sequence.append(i)
                    progress = True
                    explanation = (
                        f"Need ≤ Work on every resource, so P{i} can finish and "
                        f"releases {fmt(released)}. "
                        f"Work: {fmt(work_before)} + {fmt(released)} = {fmt(work)}.")
                    steps.append(SafetyStep(step_number, i, need[i][:], work_before,
                                            True, released, work[:], finish[:],
                                            explanation))
                else:
                    reasons = ", ".join(
                        f"{resource_name(j)} (needs {need[i][j]} > work {work[j]})"
                        for j in too_big)
                    explanation = (f"Cannot run now. Need exceeds Work for: "
                                   f"{reasons}. P{i} must wait.")
                    steps.append(SafetyStep(step_number, i, need[i][:], work_before,
                                            False, None, work[:], finish[:],
                                            explanation))

        # Step 7: decide the final result
        unfinished = [i for i in range(n) if not finish[i]]
        blocked = {}
        for i in unfinished:
            short = [f"{resource_name(j)} (needs {need[i][j]}, only {work[j]} free)"
                     for j in range(m) if need[i][j] > work[j]]
            blocked[i] = (f"P{i} needs {fmt(need[i])} but only {fmt(work)} can ever "
                          f"become free. Short on: " + ", ".join(short) + ".")

        return SafetyResult(safe=(len(unfinished) == 0), sequence=sequence,
                            steps=steps, need=need, available=available,
                            unfinished=unfinished, final_work=work,
                            blocked_reasons=blocked)
