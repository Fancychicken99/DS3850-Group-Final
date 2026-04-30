# main.py

import tkinter as tk
from Database import createTables, seedData
from report_panel import ReportPanel

createTables()
seedData()

root = tk.Tk()
root.title("NBA App")

panel = ReportPanel(root)
panel.pack(fill="both", expand=True)

root.mainloop()