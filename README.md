# Banker's Algorithm Simulator

**Course:** PT 101 – Platform Technologies  
**Project Topic:** Topic 4 – Deadlock Avoidance: Banker's Algorithm  
**Programming Language:** Python  
**Graphical User Interface:** Tkinter and ttk

## 1. Project Overview

The Banker's Algorithm Simulator is a desktop application that demonstrates how an operating system can avoid deadlock by checking whether a resource-allocation state is safe. Users can enter the total number of instances of each resource type, the current Allocation matrix, and the Max matrix. The program calculates the Need matrix and Available vector, then performs the Banker's Safety Algorithm and displays the checking process and final result.

The application also includes an optional Resource-Request feature. It checks whether a process's request is within its remaining Need and the currently Available resources, then tests whether granting the request would leave the system in a safe state.

## 2. Project Features

- Set the number of processes and resource types and generate the input matrices.
- Enter the Total resource vector, Allocation matrix, and Max matrix.
- Load the built-in sample data to try the classic Banker's Algorithm example.
- Validate input values and matrix dimensions before running the algorithm.
- Calculate Need and Available automatically.
- Display each process comparison of `Need <= Work`, the Work update, and Finish flags.
- Display a safe sequence when the state is safe, or identify processes that cannot finish when the state is unsafe.
- Test an additional resource request using the optional Resource-Request algorithm.
- Reset simulation results or clear the input fields.

## 3. Requirements

- Python 3
- Tkinter (normally included with standard Python installations)

No third-party Python packages are required by the application.

## 4. Project Structure

```text
PT-FINAL-PROJECT--main/
├── banker/
│   ├── __init__.py       # Exposes the algorithm, data, and result classes
│   ├── algorithm.py      # Validation, Need/Available calculations, safety algorithm
│   ├── data.py           # Built-in sample data and formatting helpers
│   ├── models.py         # Data classes for algorithm steps and results
│   └── request.py        # Optional resource-request checking algorithm
├── gui/
│   ├── __init__.py
│   ├── app.py            # Main application window and navigation
│   ├── input_tab.py      # System configuration and matrix input
│   ├── results_tab.py    # Safety algorithm results and execution trace
│   ├── request_tab.py    # Optional resource-request interface
│   └── ui_helpers.py     # Shared styles, widgets, and input helpers
├── main.py               # Application entry point
└── README.md
```

## 5. How to Run the Program

1. Make sure Python 3 is installed on your computer.
2. Extract or clone the project folder.
3. Open a terminal or command prompt in the project folder (the folder containing `main.py`).
4. Run:

   ```bash
   python main.py
   ```

   On some systems, use `python3 main.py` instead.
5. The Banker's Algorithm Simulator window will open.

## 6. How to Use the Simulator

### A. Enter the system configuration

1. Open the **Input & Controls** tab.
2. Enter the **Number of Processes** and **Number of Resource Types**.
3. Click **GENERATE MATRIX** to create the input fields.
4. Enter the **Total Resources Vector**. Each value represents the total number of instances of a resource type in the system.

The application supports 1–10 processes and 1–8 resource types. Resource types are labeled A, B, C, and so on.

### B. Enter the Allocation and Max matrices

- **Allocation Matrix:** The number of instances of each resource type currently allocated to each process.
- **Max Matrix:** The maximum number of instances of each resource type that each process may need to complete.

Each row represents a process (P0, P1, P2, and so on), while each column represents a resource type.

Input values must be whole numbers from 0 to 9999. Allocation cannot be greater than Max for a process/resource pair, and the sum allocated for a resource cannot exceed its Total value. The program checks these conditions before running the simulation.

### C. Run the Safety Algorithm

1. Click **RUN SAFETY ALGORITHM**.
2. The application calculates the Need matrix and Available vector.
3. The **Simulation Results** tab displays the calculated values and the algorithm's execution trace.
4. Review the comparisons, Work updates, Finish flags, and final state.

You can click **LOAD SAMPLE DATA** to fill the fields with the built-in five-process, three-resource example. Click **RESET SIMULATION** to clear displayed results while keeping the input data, or **CLEAR ALL** to clear the input fields and results.

## 7. Banker's Safety Algorithm and Output Interpretation

The program follows the required safety-checking procedure:

1. **Calculate Need:** `Need = Max - Allocation` for every process and resource type.
2. **Calculate Available:** `Available = Total - column sums of Allocation`.
3. **Initialize Work:** `Work = Available`.
4. **Initialize Finish:** Set `Finish[i] = False` for every process.
5. Find an unfinished process whose Need is less than or equal to Work for every resource type.
6. If such a process is found, assume it finishes, release its allocated resources back to the system, and update `Work = Work + Allocation[i]`. Set its Finish flag to True.
7. Continue checking unfinished processes until all processes finish or a complete scan finds no process that can proceed.

**How to interpret the result:**

- **SAFE STATE:** All processes can finish. The program displays a safe sequence showing one possible order in which they can complete.
- **UNSAFE STATE:** At least one process cannot finish under the simulated resource availability. The program displays the processes that remain unfinished and the reasons they are blocked.
- **Need <= Work:** The comparison is performed for every resource type, not just one column. A process can proceed only when all its Need values are less than or equal to the corresponding Work values.
- **Work update:** When a process finishes, its currently allocated resources are returned to Work. This is a simulation used to determine whether the state is safe.
- **Finish flags:** `T` means the process can finish in the simulated sequence; `F` means it has not finished.

The order in which the program scans processes is P0 through the last process. The safe sequence shown is a valid sequence found by that scan order; other safe sequences may also exist.

## 8. Optional Resource-Request Feature

The **Resource Request** tab is an extension to the required Safety Algorithm. It lets the user select a process and enter the additional resources it is requesting.

The program checks the request in this order:

1. **Request <= Need:** The request must not exceed the process's remaining declared maximum need. Otherwise, the request is **REJECTED**.
2. **Request <= Available:** The requested resources must currently be available. Otherwise, the process must **WAIT**.
3. **Tentative allocation:** If both checks pass, the program temporarily applies the request to copied allocation data and runs the Safety Algorithm on the tentative state.
4. **Safety result:** If the tentative state is safe, the request is **GRANTED**. If it is unsafe, the request is **NOT GRANTED**, and the original allocation is retained (rollback).

The request check does not permanently change the original input matrices when it is rejected, must wait, or would create an unsafe state.

## 9. Input Validation

The application checks for common input errors, including:

- Missing or non-integer values.
- Negative resource values.
- Invalid process or resource counts.
- Matrix dimensions that do not match the selected counts.
- Allocation values greater than the corresponding Max values.
- Total allocated resources greater than the system's Total resources.
- Invalid process selection or request-vector length in the Resource Request tab.

Correct the displayed input errors before running the simulation.

## 10. Testing

Before submission and demonstration, test the program with at least three different cases. For each case, record the input values, expected result, actual result, and attach a screenshot of the program output.

Suggested test scenarios:

| Test case | Input/scenario | Expected result |
|---|---|---|
| TC-01 – Safe state | Use the built-in sample data. | The program reports a SAFE STATE and displays a safe sequence. |
| TC-02 – Unsafe state | Use Total `[3]`, Allocation `[[1], [1]]`, and Max `[[3], [3]]`. | The program reports an UNSAFE STATE because neither process can satisfy its remaining Need with the available Work. |
| TC-03 – Invalid allocation | Enter an Allocation value greater than the corresponding Max value. | The program displays an input validation error and does not run the safety simulation. |

For the optional Resource Request feature, also test a request that is within Need and Available and results in a safe tentative state, a request greater than Need, and a request greater than Available. Record the actual result shown by the application.

**Important:** The testing evidence submitted to the instructor should contain screenshots and the actual results observed when the group runs the program. Do not treat the expected results in this guide as a substitute for running and documenting each test.




