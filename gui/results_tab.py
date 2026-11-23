"""Tab 2: everything that is shown after RUN SAFETY ALGORITHM."""

import tkinter as tk
from tkinter import ttk

from banker.data import fmt, fmt_finish, resource_name

from .ui_helpers import (BLUE, FONT, GRAY, GREEN, GREEN_LIGHT, LIGHT_BG, MONO, NAVY,
                         RED, RED_LIGHT, TEXT, HorizontalScrollArea, clear_children,
                         make_section, make_table)


class ResultsTab:

    def __init__(self, scroll_frame):
        self.scroll = scroll_frame
        self.inner = scroll_frame.inner
        self.reset()

    def reset(self):
        clear_children(self.inner)
        tk.Label(self.inner,
                 text="No results yet.\n\nEnter your data on the first tab and "
                      "click  RUN SAFETY ALGORITHM.",
                 bg=LIGHT_BG, fg=GRAY, font=(FONT, 14), pady=80).pack(fill="x")
        self.scroll.scroll_to_top()

    def show(self, data, result):
        total, allocation, maximum = data
        clear_children(self.inner)
        wrapper = tk.Frame(self.inner, bg=LIGHT_BG, padx=14, pady=12)
        wrapper.pack(fill="both", expand=True)

        self.show_system_info(wrapper, total, allocation, maximum, result)
        self.show_need_matrix(wrapper, allocation, maximum, result)
        self.show_execution_steps(wrapper, result)
        self.show_safe_sequence(wrapper, result)
        self.show_final_status(wrapper, result)
        self.scroll.scroll_to_top()

    # -----------------------------------------------------------------
    # A. System information
    # -----------------------------------------------------------------
    def show_system_info(self, parent, total, allocation, maximum, result):
        """Section A. Row 1: Total + Available vectors. Row 2: Allocation, Max, Need."""
        n, m = len(allocation), len(total)
        names = [resource_name(j) for j in range(m)]
        process_labels = [f"P{i}" for i in range(n)]
        body = make_section(parent, "A · System Information")

        area = HorizontalScrollArea(body)
        area.pack(fill="x")

        # Row 1 – vector information 
        self.add_table_row(area.inner, names, [
            ("Total Resources Vector", ["Value"], [total], ""),
            ("Available Vector", ["Value"], [result.available], ""),
        ], pady=(0, 14))

        # Row 2 – matrix information 
        self.add_table_row(area.inner, names, [
            ("Allocation Matrix", process_labels, allocation, "Process"),
            ("Max Matrix", process_labels, maximum, "Process"),
            ("Need Matrix", process_labels, result.need, "Process"),
        ])

        column_sums = [sum(row[j] for row in allocation) for j in range(m)]
        tk.Label(body,
                 text=f"Available = Total − Σ Allocation = {fmt(total)} − "
                      f"{fmt(column_sums)} = {fmt(result.available)}",
                 bg="white", fg=TEXT, font=(MONO, 10, "bold")).pack(anchor="w", pady=(10, 0))

    def add_table_row(self, parent, column_names, tables, pady=0):
   
        row = tk.Frame(parent, bg="white")
        row.pack(fill="x", pady=pady)
        for column, (title, row_labels, rows, corner) in enumerate(tables):
            row.columnconfigure(column, weight=1, uniform="tables") 
            box = make_table(row, title, column_names, row_labels, rows, corner,
                             stretch=True)
            gap = 16 if column < len(tables) - 1 else 0             
            box.grid(row=0, column=column, sticky="nsew", padx=(0, gap))

    # -----------------------------------------------------------------
    # B. Need matrix
    # -----------------------------------------------------------------
    def show_need_matrix(self, parent, allocation, maximum, result):
        n, m = len(allocation), len(allocation[0])
        names = [resource_name(j) for j in range(m)]
        body = make_section(parent, "B · Need Matrix   (Need = Max − Allocation)")

        row = tk.Frame(body, bg="white")
        row.pack(anchor="w")
        make_table(row, "Need Matrix", names, [f"P{i}" for i in range(n)],
                   result.need, "Process").pack(side="left", anchor="n", padx=(0, 40))
        lines = [f"P{i}: {fmt(maximum[i])} − {fmt(allocation[i])} = {fmt(result.need[i])}"
                 for i in range(n)]
        tk.Label(row, text="Calculation for every process:\n\n" + "\n".join(lines),
                 bg="white", fg=TEXT, font=(MONO, 10), justify="left"
                 ).pack(side="left", anchor="n")

    # -----------------------------------------------------------------
    # C. Step-by-step execution
    # -----------------------------------------------------------------
    def show_execution_steps(self, parent, result):
        body = make_section(parent, "C · Step-by-Step Algorithm Execution")
        n = len(result.need)

        tk.Label(body,
                 text=f"Initialization:  Work = Available = {fmt(result.available)}    |    "
                      f"Finish = {fmt_finish([False] * n)}    |    Safe Sequence = [ ]",
                 bg="white", fg=NAVY, font=(MONO, 10, "bold")).pack(anchor="w")
        tk.Label(body,
                 text="The algorithm scans P0, P1, … in order and checks Need ≤ Work for "
                      "each unfinished process. It repeats the scan until no process can "
                      "be completed. Failed checks are shown too.",
                 bg="white", fg=GRAY, font=(FONT, 9), wraplength=1050, justify="left"
                 ).pack(anchor="w", pady=(4, 8))

        columns = ("step", "process", "need", "before", "check", "released",
                   "after", "finish", "vector", "why")
        headings = ("Step", "Process", "Need", "Work Before", "Need ≤ Work?",
                    "Allocation Released", "Work After", "Finish[i]",
                    "Finish Vector", "Explanation")
        widths = (45, 65, 90, 95, 95, 115, 95, 70, 125, 330)

        frame = tk.Frame(body, bg="white")
        frame.pack(fill="x")
        tree = ttk.Treeview(frame, columns=columns, show="headings",
                            style="Steps.Treeview",
                            height=min(max(len(result.steps), 1), 22))
        for column, heading, width in zip(columns, headings, widths):
            tree.heading(column, text=heading)
            tree.column(column, width=width, minwidth=width,
                        anchor="w" if column == "why" else "center",
                        stretch=(column == "why"))
        tree.column("why", minwidth=300)
        tree.tag_configure("ok", background=GREEN_LIGHT)
        tree.tag_configure("fail", background=RED_LIGHT)

        for s in result.steps:
            tree.insert("", "end", tags=("ok" if s.can_run else "fail",), values=(
                s.number, f"P{s.process}", fmt(s.need), fmt(s.work_before),
                "TRUE" if s.can_run else "FALSE",
                fmt(s.released) if s.released else "—",
                fmt(s.work_after),
                "True" if s.can_run else "False",
                fmt_finish(s.finish_after), s.explanation))

        vertical = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        horizontal = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)

        detail = tk.Label(body, text="Click a row to read its full explanation here.",
                          bg="white", fg=TEXT, font=(FONT, 10), wraplength=1050,
                          justify="left", anchor="w")
        detail.pack(fill="x", pady=(8, 0))

        def show_detail(_event):
            selected = tree.selection()
            if selected:
                values = tree.item(selected[0], "values")
                detail.configure(text=f"Step {values[0]} ({values[1]}):  {values[9]}")

        tree.bind("<<TreeviewSelect>>", show_detail)

        legend = tk.Frame(body, bg="white")
        legend.pack(anchor="w", pady=(8, 0))
        tk.Label(legend, text=" TRUE — process can finish ", bg=GREEN_LIGHT, fg=GREEN,
                 font=(FONT, 9, "bold")).pack(side="left", padx=(0, 8))
        tk.Label(legend, text=" FALSE — process must wait ", bg=RED_LIGHT, fg=RED,
                 font=(FONT, 9, "bold")).pack(side="left")

    # -----------------------------------------------------------------
    # D. Safe sequence
    # -----------------------------------------------------------------
    def show_safe_sequence(self, parent, result):
        body = make_section(parent, "D · Safe Sequence Visualization")
        if result.safe:
            row = tk.Frame(body, bg="white")
            row.pack(anchor="w", pady=4)
            for k, process in enumerate(result.sequence):
                tk.Label(row, text=f"P{process}", bg=BLUE, fg="white",
                         font=(FONT, 16, "bold"), padx=18, pady=10).pack(side="left")
                if k < len(result.sequence) - 1:
                    tk.Label(row, text="→", bg="white", fg=NAVY,
                             font=(FONT, 20, "bold"), padx=8).pack(side="left")
            tk.Label(body, text="The processes can finish in this order without causing "
                                "a deadlock.", bg="white", fg=GRAY,
                     font=(FONT, 9)).pack(anchor="w", pady=(6, 0))
        else:
            tk.Label(body, text="No complete safe sequence exists for this state.",
                     bg="white", fg=RED, font=(FONT, 13, "bold")).pack(anchor="w")
            if result.sequence:
                partial = " → ".join(f"P{p}" for p in result.sequence)
                tk.Label(body, text=f"Processes that could finish before the algorithm "
                                    f"got stuck: {partial}",
                         bg="white", fg=GRAY, font=(FONT, 10)).pack(anchor="w", pady=(4, 0))

    # -----------------------------------------------------------------
    # E. Final status
    # -----------------------------------------------------------------
    def show_final_status(self, parent, result):
        n = len(result.need)
        color = GREEN if result.safe else RED
        body = make_section(parent, "E · Final Result Summary")

        banner = tk.Frame(body, bg=color, padx=22, pady=16)
        banner.pack(fill="x")

        indicator = tk.Canvas(banner, width=64, height=64, bg=color, highlightthickness=0)
        indicator.create_oval(4, 4, 60, 60, fill="white", outline="")
        indicator.create_text(32, 32, text="✓" if result.safe else "✗", fill=color,
                              font=(FONT, 28, "bold"))
        indicator.pack(side="left", padx=(0, 20))

        text = tk.Frame(banner, bg=color)
        text.pack(side="left", anchor="w")

        def line(message, size=13, bold=False, pady=0):
            tk.Label(text, text=message, bg=color, fg="white",
                     font=(FONT, size, "bold" if bold else "normal")
                     ).pack(anchor="w", pady=pady)

        if result.safe:
            sequence = " → ".join(f"P{p}" for p in result.sequence)
            line("SYSTEM STATUS: SAFE STATE", size=22, bold=True)
            line(f"Safe sequence: {sequence}")
            line(f"Processes completed: {len(result.sequence)} of {n}")
        else:
            unfinished = ", ".join(f"P{p}" for p in result.unfinished)
            line("SYSTEM STATUS: UNSAFE STATE", size=22, bold=True)
            line(f"Unfinished processes: {unfinished}")
            line(f"Processes completed: {len(result.sequence)} of {n}")
            line("The current resource allocation cannot guarantee a safe "
                 "execution sequence.", size=12, bold=True, pady=(4, 0))

            tk.Label(body, text="Why these processes cannot proceed:", bg="white",
                     fg=NAVY, font=(FONT, 11, "bold")).pack(anchor="w", pady=(12, 4))
            for process in result.unfinished:
                tk.Label(body, text="• " + result.blocked_reasons[process], bg="white",
                         fg=RED, font=(FONT, 10), wraplength=1050, justify="left"
                         ).pack(anchor="w")
