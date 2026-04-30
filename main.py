# ============================================================
# DS3850 — Group Project - Main.py
# Name: Connor Beck
# Section: 001
# Date: 04/29/2026
# ============================================================

import tkinter as tk
from Database import createTables, seedData
from ReportPanel import ReportPanel

createTables()
seedData()

root = tk.Tk()
root.title("NBA App")

panel = ReportPanel(root)
panel.pack(fill="both", expand=True)

root.mainloop()
