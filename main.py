"""Banker's Algorithm Simulator"""

import sys

def main():
    try:
        import tkinter as tk
    except ImportError:
        print("Tkinter is not installed.\n"
              "  Ubuntu/Debian : sudo apt install python3-tk\n"
              "  Fedora        : sudo dnf install python3-tkinter\n"
              "  Windows/macOS : reinstall Python from python.org (Tcl/Tk is included)")
        sys.exit(1)

    from gui import BankerGUI

    root = tk.Tk()
    BankerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
