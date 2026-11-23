import re
import tkinter as tk
from tkinter import ttk

from banker.data import resource_name

# =====================================================================
# 1. THEME: COLOURS, FONTS AND ttk STYLES
# =====================================================================

# ---- Colour palette ----
NAVY = "#0B2E5C"            # app header and section headers
BLUE = "#1F6FD1"            # primary buttons, process cards
BLUE_DARK = "#1559AB"
LIGHT_BG = "#EEF3FA"        # window background
TABLE_HEADER_BG = "#DCE8F8"
BORDER = "#C3D3EA"
TEXT = "#1B2A41"
GRAY = "#6B7A90"
GREEN = "#1E8E3E"
GREEN_LIGHT = "#E6F4EA"
RED = "#C62828"
RED_LIGHT = "#FDECEA"

# ---- Fonts ----
FONT = "Segoe UI"
MONO = "Courier New"


def apply_styles(root):
    """Configure every ttk style once, at start-up."""
    style = ttk.Style(root)
    style.theme_use("clam")      # 'clam' lets us colour buttons on every OS

    # Tabs
    style.configure("TNotebook", background=LIGHT_BG, borderwidth=0)
    style.configure("TNotebook.Tab", padding=(22, 10), background="#D3E0F4",
                    foreground=NAVY, font=(FONT, 11, "bold"))
    style.map("TNotebook.Tab",
              background=[("selected", BLUE)],
              foreground=[("selected", "white")])

    # Buttons
    style.configure("Primary.TButton", background=BLUE, foreground="white",
                    font=(FONT, 11, "bold"), padding=(20, 10), borderwidth=0,
                    focusthickness=0)
    style.map("Primary.TButton", background=[("active", BLUE_DARK)])
    style.configure("Secondary.TButton", background=TABLE_HEADER_BG, foreground=NAVY,
                    font=(FONT, 10, "bold"), padding=(16, 9), borderwidth=0,
                    focusthickness=0)
    style.map("Secondary.TButton", background=[("active", "#C5D8F2")])
    style.configure("Danger.TButton", background=RED_LIGHT, foreground=RED,
                    font=(FONT, 10, "bold"), padding=(16, 9), borderwidth=0,
                    focusthickness=0)
    style.map("Danger.TButton", background=[("active", "#F8D0CC")])

    # Input boxes
    style.configure("Cell.TEntry", padding=4, fieldbackground="white")
    style.configure("TCombobox", padding=4)

    # Step table
    def fixed_map(option):
        return [entry for entry in style.map("Treeview", query_opt=option)
                if entry[:2] != ("!disabled", "!selected")]

    style.map("Treeview", foreground=fixed_map("foreground"),
              background=fixed_map("background"))
    style.configure("Steps.Treeview", rowheight=28, font=(FONT, 10),
                    background="white", fieldbackground="white")
    style.configure("Steps.Treeview.Heading", background=NAVY, foreground="white",
                    font=(FONT, 10, "bold"), relief="flat", padding=6)
    style.map("Steps.Treeview.Heading", background=[("active", NAVY)])

# =====================================================================
# 2. INPUT PARSING AND VALIDATION
# =====================================================================

MAX_PROCESSES = 10
MAX_RESOURCES = 8
MAX_VALUE = 9999

def parse_int(text, label, errors, minimum=0, maximum=None):
    text = text.strip()
    if text == "":
        errors.append(f"{label}: the field is empty.")
        return None
    if not re.fullmatch(r"[+-]?\d+", text):
        errors.append(f"{label}: '{text}' is not a whole number.")
        return None

    value = int(text)
    if value < minimum:
        if minimum == 0:
            errors.append(f"{label}: negative values are not allowed ({value}).")
        else:
            errors.append(f"{label}: must be at least {minimum} (got {value}).")
        return None
    if maximum is not None and value > maximum:
        errors.append(f"{label}: must not be more than {maximum} (got {value}).")
        return None
    return value

# =====================================================================
# 3. REUSABLE WIDGETS
# =====================================================================

def clear_children(widget):
    """Destroy everything inside `widget`."""
    for child in list(widget.winfo_children()):
        child.destroy()


class ScrollableFrame(tk.Frame):

    def __init__(self, parent, bg):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, yscrollincrement=20)
        self.vbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vbar.set)
        self.vbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=bg)
        self.window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._update_inner_width)

    def _update_scroll_region(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _update_inner_width(self, event):
        self.canvas.itemconfigure(self.window, width=event.width)

    def scroll(self, units):
        first, last = self.canvas.yview()
        if first > 0.0 or last < 1.0:
            self.canvas.yview_scroll(units, "units")

    def scroll_to_top(self):
        self.canvas.yview_moveto(0)


class HorizontalScrollArea(tk.Frame):

    def __init__(self, parent, bg="white"):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, height=1)
        self.hbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.hbar.set)
        self.canvas.pack(fill="x")

        self.inner = tk.Frame(self.canvas, bg=bg)
        self.window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._update_layout)
        self.canvas.bind("<Configure>", self._update_layout)

    def _update_layout(self, _event=None):
        needed_width = self.inner.winfo_reqwidth()      # width the content needs
        visible_width = self.canvas.winfo_width()       # width we actually have
        self.canvas.itemconfigure(self.window, width=max(needed_width, visible_width))
        self.canvas.configure(scrollregion=self.canvas.bbox("all"),
                              height=self.inner.winfo_reqheight())
        if needed_width > visible_width > 1:
            self.hbar.pack(fill="x")                 
        else:
            self.hbar.pack_forget()

def make_section(parent, title, pady=(0, 14)):
    
    card = tk.Frame(parent, bg="white", highlightbackground=BORDER, highlightthickness=1)
    card.pack(fill="x", pady=pady)
    tk.Label(card, text=title, bg=NAVY, fg="white", font=(FONT, 12, "bold"),
             anchor="w", padx=14, pady=7).pack(fill="x")
    body = tk.Frame(card, bg="white", padx=16, pady=12)
    body.pack(fill="both", expand=True)
    return body


def make_table(parent, title, col_headers, row_labels, rows, corner="", stretch=False):

    box = tk.Frame(parent, bg="white")
    if stretch:
        tk.Label(box, text=title.upper(), bg=BLUE, fg="white", pady=5,
                 font=(FONT, 10, "bold")).pack(fill="x")
    else:
        tk.Label(box, text=title, bg="white", fg=NAVY,
                 font=(FONT, 10, "bold")).pack(anchor="w", pady=(0, 4))

    grid = tk.Frame(box, bg=BORDER, padx=1, pady=1)  
    if stretch:
        grid.pack(fill="both", expand=True)
        for col in range(len(col_headers) + 1):
            grid.columnconfigure(col, weight=1)  
    else:
        grid.pack(anchor="w")

    def cell(row, col, text, bg, fg, bold):
        tk.Label(grid, text=text, bg=bg, fg=fg, pady=4,
                 width=9 if col == 0 else 6,
                 font=(FONT, 10, "bold" if bold else "normal")
                 ).grid(row=row, column=col, padx=(0, 1), pady=(0, 1),
                        sticky="nsew" if stretch else "")

    cell(0, 0, corner, TABLE_HEADER_BG, NAVY, True)
    for j, header in enumerate(col_headers):
        cell(0, j + 1, header, TABLE_HEADER_BG, NAVY, True)
    for i, row in enumerate(rows):
        cell(i + 1, 0, row_labels[i], TABLE_HEADER_BG, NAVY, True)
        for j, value in enumerate(row):
            cell(i + 1, j + 1, str(value), "white", TEXT, False)
    return box


def build_entry_grid(parent, corner, row_labels, col_count):
 
    header_style = dict(bg=TABLE_HEADER_BG, fg=NAVY, font=(FONT, 10, "bold"), pady=5)
    tk.Label(parent, text=corner, width=9, **header_style).grid(
        row=0, column=0, padx=1, pady=1)
    for j in range(col_count):
        tk.Label(parent, text=resource_name(j), width=7, **header_style).grid(
            row=0, column=j + 1, padx=1, pady=1)

    all_vars, all_entries = [], []
    for i, label in enumerate(row_labels):
        tk.Label(parent, text=label, width=9, **header_style).grid(
            row=i + 1, column=0, padx=1, pady=1)
        row_vars, row_entries = [], []
        for j in range(col_count):
            var = tk.StringVar()
            entry = ttk.Entry(parent, textvariable=var, width=6,
                              justify="center", style="Cell.TEntry")
            entry.grid(row=i + 1, column=j + 1, padx=1, pady=1)
            row_vars.append(var)
            row_entries.append(entry)
        all_vars.append(row_vars)
        all_entries.append(row_entries)

    _bind_navigation(all_entries)
    return all_vars


def _bind_navigation(entries):

    row_count = len(entries)

    def move(row, col):
        if 0 <= row < row_count:
            entries[row][col].focus_set()
        return "break"

    def select_all(event):
        event.widget.after(1, lambda w=event.widget: w.select_range(0, "end"))

    for r, row in enumerate(entries):
        for c, entry in enumerate(row):
            entry.bind("<Down>", lambda e, r=r, c=c: move(r + 1, c))
            entry.bind("<Return>", lambda e, r=r, c=c: move(r + 1, c))
            entry.bind("<Up>", lambda e, r=r, c=c: move(r - 1, c))
            entry.bind("<FocusIn>", select_all)
