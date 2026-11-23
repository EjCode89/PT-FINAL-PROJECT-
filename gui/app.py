"""Main Window"""

import tkinter as tk
import traceback
from tkinter import messagebox, ttk

from banker import BankerAlgorithm

from .input_tab import InputTab
from .request_tab import RequestTab
from .results_tab import ResultsTab
from .ui_helpers import (BORDER, FONT, GRAY, GREEN, LIGHT_BG, NAVY, RED,
                         ScrollableFrame, apply_styles)


class BankerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Banker's Algorithm Simulator — Deadlock Avoidance")
        root.geometry("1240x820")
        root.minsize(1000, 650)
        root.configure(bg=LIGHT_BG)

        self.status_var = tk.StringVar()

        apply_styles(root)
        self.create_widgets()

        self.input_tab.generate_tables()
        self.set_status("Ready. Fill in the tables, or click LOAD SAMPLE DATA to try "
                        "the classic example.", "info")

        # Mouse-wheel scrolling + friendly handling of unexpected errors
        root.bind_all("<MouseWheel>", self.on_mousewheel)
        root.bind_all("<Button-4>", self.on_mousewheel)     # Linux scroll up
        root.bind_all("<Button-5>", self.on_mousewheel)     # Linux scroll down
        root.report_callback_exception = self.on_unexpected_error

    # -----------------------------------------------------------------
    # Building the window
    # -----------------------------------------------------------------
    def create_widgets(self):
        self.create_header()
        self.create_status_bar()     

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(10, 6))

        # One page per tab
        self.input_page = ScrollableFrame(self.notebook, LIGHT_BG)
        self.results_page = ScrollableFrame(self.notebook, LIGHT_BG)
        self.request_page = tk.Frame(self.notebook, bg=LIGHT_BG)
        self.notebook.add(self.input_page, text="  1 · Input & Controls  ")
        self.notebook.add(self.results_page, text="  2 · Simulation Results  ")
        self.notebook.add(self.request_page, text="  3 · Resource Request  ")

        # The three tab objects 
        self.input_tab = InputTab(self.input_page.inner, self)
        self.results_tab = ResultsTab(self.results_page)
        self.request_tab = RequestTab(self.request_page, self, self.input_tab)

    def create_header(self):
        header = tk.Frame(self.root, bg=NAVY, padx=24, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="BANKER'S ALGORITHM SIMULATOR", bg=NAVY, fg="white",
                 font=(FONT, 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Operating Systems – Deadlock Avoidance", bg=NAVY,
                 fg="#9EC5FF", font=(FONT, 12, "bold")).pack(anchor="w")
        tk.Label(header,
                 text="Enter the system's resources, allocation and maximum demand. "
                      "The simulator calculates Need and Available, runs the safety "
                      "algorithm step by step, and can test new resource requests.",
                 bg=NAVY, fg="#D6E4FA", font=(FONT, 10), wraplength=1100,
                 justify="left").pack(anchor="w", pady=(4, 0))

    def create_status_bar(self):
        bar = tk.Frame(self.root, bg="white", highlightbackground=BORDER,
                       highlightthickness=1)
        bar.pack(side="bottom", fill="x")
        self.status_label = tk.Label(bar, textvariable=self.status_var, bg="white",
                                     fg=GRAY, font=(FONT, 10), anchor="w",
                                     padx=14, pady=6)
        self.status_label.pack(fill="x")

    # -----------------------------------------------------------------
    # Services used by the tabs
    # -----------------------------------------------------------------
    def set_status(self, text, kind="info"):
        """Show a message in the status bar"""
        colors = {"info": GRAY, "ok": GREEN, "error": RED}
        self.status_var.set(text)
        self.status_label.configure(fg=colors.get(kind, GRAY))

    def show_errors(self, errors, title="Invalid Input"):
        shown = errors[:10]
        text = "\n".join("• " + e for e in shown)
        if len(errors) > len(shown):
            text += f"\n… and {len(errors) - len(shown)} more problem(s)."
        self.set_status(f"{title}: {errors[0]}", "error")
        messagebox.showerror(title, text)

    def show_tab(self, name):
        """Switch tab"""
        pages = {"input": self.input_page, "results": self.results_page,
                 "request": self.request_page}
        self.notebook.select(pages[name])

    def on_tables_generated(self, n, m):
        self.results_tab.reset()
        self.request_tab.update_widgets(n, m)
        self.set_status(f"Generated empty tables for {n} processes and {m} resource types.",
                        "info")

    # -----------------------------------------------------------------
    # Button actions
    # -----------------------------------------------------------------
    def run_simulation(self, switch_tab=True):
        """RUN SAFETY ALGORITHM."""
        data = self.input_tab.read_system_data()
        if data is None:
            self.results_tab.reset()      # never keep results of old / invalid data
            return

        total, allocation, maximum = data
        result = BankerAlgorithm.safety_algorithm(total, allocation, maximum)
        self.results_tab.show(data, result)
        if switch_tab:
            self.show_tab("results")

        if result.safe:
            sequence = " → ".join(f"P{p}" for p in result.sequence)
            self.set_status(f"SAFE STATE. Safe sequence: {sequence}", "ok")
        else:
            unfinished = ", ".join(f"P{p}" for p in result.unfinished)
            self.set_status(f"UNSAFE STATE. Processes that cannot finish: {unfinished}",
                            "error")

    def reset_simulation(self):
        self.results_tab.reset()
        self.request_tab.reset_display()
        self.set_status("Simulation reset. Your input data was kept.", "info")

    def clear_inputs(self):
        self.input_tab.clear()
        self.request_tab.clear()
        self.results_tab.reset()
        self.show_tab("input")
        self.set_status("All input fields cleared.", "info")

    # -----------------------------------------------------------------
    # Mouse wheel + error safety net
    # -----------------------------------------------------------------
    def on_mousewheel(self, event):
        try:
            widget = self.root.winfo_containing(event.x_root, event.y_root)
        except (KeyError, tk.TclError):
            return                 

        if event.num == 4:              # Linux: wheel up
            units = -3
        elif event.num == 5:            # Linux: wheel down
            units = 3
        else:                           # Windows / macOS
            units = -3 if event.delta > 0 else 3

        while widget is not None:
            if isinstance(widget, (ttk.Treeview, tk.Text)):
                return          
            if isinstance(widget, ScrollableFrame):
                widget.scroll(units)
                return
            widget = widget.master

    def on_unexpected_error(self, exc_type, exc_value, exc_traceback):
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        message = f"{exc_type.__name__}: {exc_value}"
        self.set_status(f"Unexpected error: {message}", "error")
        messagebox.showerror("Unexpected Error",
                             f"Something went wrong, but the program is still running.\n\n"
                             f"{message}")
