"""Tab 3 (OPTIONAL extension): Resource Request simulation."""

import tkinter as tk
from tkinter import ttk

from banker import request_resources
from banker.data import fmt, resource_name

from .ui_helpers import (BORDER, FONT, GRAY, GREEN, LIGHT_BG, MAX_VALUE, MONO, NAVY,
                         RED, TEXT, build_entry_grid, clear_children, make_section,
                         parse_int)


class RequestTab:

    def __init__(self, parent, app, input_tab):
        self.parent = parent
        self.app = app
        self.input_tab = input_tab
        self.request_vars = []
        self.build()

    # -----------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------
    def build(self):
        wrapper = tk.Frame(self.parent, bg=LIGHT_BG, padx=14, pady=12)
        wrapper.pack(fill="both", expand=True)

        # ---- Inputs ----
        body = make_section(wrapper, "SECTION 5 · Resource Request Simulation")
        tk.Label(body,
                 text="Choose a process and the extra resources it is asking for. The "
                      "simulator checks Request ≤ Need, then Request ≤ Available, then "
                      "tries the allocation and re-runs the safety algorithm.",
                 bg="white", fg=GRAY, font=(FONT, 9), wraplength=1050, justify="left"
                 ).pack(anchor="w", pady=(0, 8))

        row = tk.Frame(body, bg="white")
        row.pack(anchor="w")
        tk.Label(row, text="Process:", bg="white", fg=TEXT,
                 font=(FONT, 10, "bold")).pack(side="left", padx=(0, 8))
        self.process_box = ttk.Combobox(row, state="readonly", width=6)
        self.process_box.pack(side="left", padx=(0, 24))
        tk.Label(row, text="Request vector:", bg="white", fg=TEXT,
                 font=(FONT, 10, "bold")).pack(side="left", padx=(0, 8))
        self.entry_frame = tk.Frame(row, bg="white")
        self.entry_frame.pack(side="left", padx=(0, 24))
        ttk.Button(row, text="CHECK REQUEST", style="Primary.TButton",
                   command=self.check_request).pack(side="left")

        # ---- Results ----
        body = make_section(wrapper, "Request Result and Explanation", pady=(0, 0))
        self.banner = tk.Label(body, text="No request checked yet", bg=GRAY, fg="white",
                               font=(FONT, 18, "bold"), pady=12)
        self.banner.pack(fill="x")

        text_frame = tk.Frame(body, bg="white")
        text_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.text = tk.Text(text_frame, height=18, wrap="word", bg="#FAFCFF",
                            relief="flat", font=(MONO, 10), padx=10, pady=8,
                            highlightbackground=BORDER, highlightthickness=1,
                            state="disabled")
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        self.text.tag_configure("heading", foreground=NAVY, font=(MONO, 10, "bold"),
                                spacing1=10, spacing3=2)
        self.text.tag_configure("pass", foreground=GREEN, font=(MONO, 10, "bold"))
        self.text.tag_configure("fail", foreground=RED, font=(MONO, 10, "bold"))
        self.text.tag_configure("text", foreground=TEXT)

    # -----------------------------------------------------------------
    # Called by the main window when the tables are (re)generated
    # -----------------------------------------------------------------
    def update_widgets(self, n, m):
        """Refresh the process dropdown and the request boxes for an n × m system."""
        self.process_box["values"] = [f"P{i}" for i in range(n)]
        if n:
            self.process_box.current(0)
        clear_children(self.entry_frame)
        self.request_vars = build_entry_grid(self.entry_frame, "", ["Request"], m)[0]
        for var in self.request_vars:
            var.set("0")
        self.reset_display()

    def clear(self):
        for var in self.request_vars:
            var.set("0")
        self.reset_display()

    def reset_display(self):
        self.banner.configure(text="No request checked yet", bg=GRAY)
        self.show_log([])

    def show_log(self, log):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        for style_name, line in log:
            self.text.insert("end", line + "\n", style_name)
        self.text.configure(state="disabled")

    # -----------------------------------------------------------------
    # CHECK REQUEST
    # -----------------------------------------------------------------
    def check_request(self):
        data = self.input_tab.read_system_data()
        if data is None:
            return
        total, allocation, maximum = data

        pid = self.process_box.current()
        if pid < 0:
            self.app.show_errors(["Please select a process for the request."])
            return

        errors = []
        request = [parse_int(var.get(), f"Request[{resource_name(j)}]", errors,
                             maximum=MAX_VALUE)
                   for j, var in enumerate(self.request_vars)]
        if errors:
            self.app.show_errors(errors, "Invalid Request")
            return
        if len(request) != len(total):
            self.app.show_errors(["The request vector has the wrong length. "
                                  "Click GENERATE MATRIX."], "Invalid Request")
            return

        result = request_resources(total, allocation, maximum, pid, request)

        # Banner
        self.banner.configure(text=f"P{pid} requests {fmt(request)}  →  {result.decision}",
                              bg=GREEN if result.decision == "GRANTED" else RED)
        log = list(result.log)

        if result.decision == "GRANTED":
            self.input_tab.set_allocation(result.new_allocation)
            log.append(("text", ""))
            log.append(("pass", "The Allocation table on the Input tab was updated and "
                                "the Results tab was refreshed."))
            self.app.run_simulation(switch_tab=False)
            self.app.set_status(f"Request GRANTED for P{pid}. Allocation updated.", "ok")
        else:
            self.app.set_status(f"Request {result.decision} for P{pid}. "
                                f"Original data unchanged.", "error")

        self.show_log(log)
