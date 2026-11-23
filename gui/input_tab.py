"""Tab 1: system configuration"""

import tkinter as tk
from tkinter import ttk

from banker import SAMPLE_DATA, BankerAlgorithm
from banker.data import resource_name

from .ui_helpers import (FONT, GRAY, LIGHT_BG, MAX_PROCESSES, MAX_RESOURCES,
                         MAX_VALUE, NAVY, TEXT, build_entry_grid, clear_children,
                         make_section, parse_int)


class InputTab:

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

        self.n = 0     # number of processes in the tables currently on screen
        self.m = 0     # number of resource types in the tables currently on screen
        self.total_vars = []
        self.alloc_vars = []
        self.max_vars = []

        self.process_count_var = tk.StringVar(value="5")
        self.resource_count_var = tk.StringVar(value="3")

        self.build()

    # -----------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------
    def build(self):
        wrapper = tk.Frame(self.parent, bg=LIGHT_BG, padx=14, pady=12)
        wrapper.pack(fill="both", expand=True)
        self.build_configuration(wrapper)
        self.build_matrices(wrapper)
        self.build_controls(wrapper)

    def build_configuration(self, wrapper):

        body = make_section(wrapper, "SECTION 1 · System Configuration")
        row = tk.Frame(body, bg="white")
        row.pack(fill="x")

        tk.Label(row, text="Number of Processes:", bg="white", fg=TEXT,
                 font=(FONT, 10, "bold")).pack(side="left")
        ttk.Entry(row, textvariable=self.process_count_var, width=6, justify="center",
                  style="Cell.TEntry").pack(side="left", padx=(8, 24))
        tk.Label(row, text="Number of Resource Types:", bg="white", fg=TEXT,
                 font=(FONT, 10, "bold")).pack(side="left")
        ttk.Entry(row, textvariable=self.resource_count_var, width=6, justify="center",
                  style="Cell.TEntry").pack(side="left", padx=(8, 24))
        ttk.Button(row, text="GENERATE MATRIX", style="Primary.TButton",
                   command=self.generate_tables).pack(side="left")
        tk.Label(row, text=f"   (1–{MAX_PROCESSES} processes, 1–{MAX_RESOURCES} "
                           f"resource types: A, B, C …)",
                 bg="white", fg=GRAY, font=(FONT, 9)).pack(side="left")

        tk.Label(body, text="Total Resources Vector (total instances of each resource type):",
                 bg="white", fg=TEXT, font=(FONT, 10, "bold")).pack(anchor="w", pady=(14, 4))
        self.total_frame = tk.Frame(body, bg="white")
        self.total_frame.pack(anchor="w")

    def build_matrices(self, wrapper):

        body = make_section(wrapper, "SECTION 2 · Resource Allocation Input")
        panels = tk.Frame(body, bg="white")
        panels.pack(anchor="w")

        left = tk.Frame(panels, bg="white")
        left.pack(side="left", anchor="n", padx=(0, 40))
        right = tk.Frame(panels, bg="white")
        right.pack(side="left", anchor="n")

        tk.Label(left, text="Allocation Matrix (currently allocated)", bg="white",
                 fg=NAVY, font=(FONT, 10, "bold")).pack(anchor="w", pady=(0, 4))
        self.alloc_frame = tk.Frame(left, bg="white")
        self.alloc_frame.pack(anchor="w")

        tk.Label(right, text="Max Matrix (maximum demand)", bg="white", fg=NAVY,
                 font=(FONT, 10, "bold")).pack(anchor="w", pady=(0, 4))
        self.max_frame = tk.Frame(right, bg="white")
        self.max_frame.pack(anchor="w")

    def build_controls(self, wrapper):
        
        body = make_section(wrapper, "SECTION 3 · Simulation Controls")
        row = tk.Frame(body, bg="white")
        row.pack(fill="x")
        ttk.Button(row, text="RUN SAFETY ALGORITHM", style="Primary.TButton",
                   command=self.app.run_simulation).pack(side="left", padx=(0, 10))
        ttk.Button(row, text="LOAD SAMPLE DATA", style="Secondary.TButton",
                   command=self.load_sample_data).pack(side="left", padx=(0, 10))
        ttk.Button(row, text="RESET SIMULATION", style="Secondary.TButton",
                   command=self.app.reset_simulation).pack(side="left", padx=(0, 10))
        ttk.Button(row, text="CLEAR ALL", style="Danger.TButton",
                   command=self.app.clear_inputs).pack(side="left")

    # -----------------------------------------------------------------
    # Generating the tables
    # -----------------------------------------------------------------
    def read_counts(self):
        """Return (processes, resource types) or None (after showing the errors)."""
        errors = []
        n = parse_int(self.process_count_var.get(), "Number of Processes", errors,
                      minimum=1, maximum=MAX_PROCESSES)
        m = parse_int(self.resource_count_var.get(), "Number of Resource Types", errors,
                      minimum=1, maximum=MAX_RESOURCES)
        if errors:
            self.app.show_errors(errors)
            return None
        return n, m

    def generate_tables(self):

        counts = self.read_counts()
        if counts is None:
            return False
        self.n, self.m = counts

        for frame in (self.total_frame, self.alloc_frame, self.max_frame):
            clear_children(frame)

        process_labels = [f"P{i}" for i in range(self.n)]
        self.total_vars = build_entry_grid(self.total_frame, "", ["Total"], self.m)[0]
        self.alloc_vars = build_entry_grid(self.alloc_frame, "Process", process_labels, self.m)
        self.max_vars = build_entry_grid(self.max_frame, "Process", process_labels, self.m)

        self.app.on_tables_generated(self.n, self.m)
        return True

    # -----------------------------------------------------------------
    # Reading + validating
    # -----------------------------------------------------------------
    def read_system_data(self):

        if self.n == 0:
            self.app.show_errors(["Please click GENERATE MATRIX first."])
            return None

        errors = []
        n = parse_int(self.process_count_var.get(), "Number of Processes", errors,
                      minimum=1, maximum=MAX_PROCESSES)
        m = parse_int(self.resource_count_var.get(), "Number of Resource Types", errors,
                      minimum=1, maximum=MAX_RESOURCES)
        if errors:
            self.app.show_errors(errors)
            return None
        if (n, m) != (self.n, self.m):
            self.app.show_errors([
                f"The counts ({n} processes, {m} resource types) do not match the "
                f"tables on screen ({self.n} × {self.m}). Click GENERATE MATRIX."])
            return None

        total = [parse_int(var.get(), f"Total Resources [{resource_name(j)}]",
                           errors, maximum=MAX_VALUE)
                 for j, var in enumerate(self.total_vars)]
        allocation = [[parse_int(var.get(), f"Allocation[P{i}][{resource_name(j)}]",
                                 errors, maximum=MAX_VALUE)
                       for j, var in enumerate(row)]
                      for i, row in enumerate(self.alloc_vars)]
        maximum = [[parse_int(var.get(), f"Max[P{i}][{resource_name(j)}]",
                              errors, maximum=MAX_VALUE)
                    for j, var in enumerate(row)]
                   for i, row in enumerate(self.max_vars)]
        if errors:
            self.app.show_errors(errors)
            return None

        logic_errors = BankerAlgorithm.validate_state(total, allocation, maximum)
        if logic_errors:
            self.app.show_errors(logic_errors)
            return None
        return total, allocation, maximum

    # -----------------------------------------------------------------
    # Filling / emptying the boxes
    # -----------------------------------------------------------------
    def load_sample_data(self):
        self.process_count_var.set(str(len(SAMPLE_DATA["allocation"])))
        self.resource_count_var.set(str(len(SAMPLE_DATA["total"])))
        if not self.generate_tables():
            return
        for j, value in enumerate(SAMPLE_DATA["total"]):
            self.total_vars[j].set(str(value))
        self.set_allocation(SAMPLE_DATA["allocation"])
        for i in range(self.n):
            for j in range(self.m):
                self.max_vars[i][j].set(str(SAMPLE_DATA["maximum"][i][j]))
        self.app.show_tab("input")
        self.app.set_status("Sample data loaded (classic textbook example). "
                            "Click RUN SAFETY ALGORITHM.", "ok")

    def set_allocation(self, matrix):

        for i in range(self.n):
            for j in range(self.m):
                self.alloc_vars[i][j].set(str(matrix[i][j]))

    def clear(self):

        for var in self.total_vars:
            var.set("")
        for row in self.alloc_vars + self.max_vars:
            for var in row:
                var.set("")
