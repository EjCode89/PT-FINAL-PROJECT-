"""Banker's Algorithm Simulator"""

def main():
    import tkinter as tk
    from gui import BankerGUI

    root = tk.Tk()
    BankerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
