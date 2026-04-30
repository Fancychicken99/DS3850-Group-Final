# report_panel.py

import tkinter as tk
from tkinter import messagebox
import pandas as pd
import numpy as np

from Database import getDBConnection


class ReportPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.df = pd.DataFrame()

        tk.Label(self, text="NBA Report Panel", font=("Arial", 16, "bold")).pack(pady=10)

        tk.Button(self, text="Load Report", command=self.load_report).pack(pady=5)
        tk.Button(self, text="Export to CSV", command=self.export_csv).pack(pady=5)

        self.output = tk.Text(self, width=100, height=25)
        self.output.pack(pady=10)

    def load_report(self):
        conn = getDBConnection()

        query = """
        SELECT
            nba_teams.name AS team_name,
            nba_players.name AS player_name,
            nba_players.salary,
            nba_players.pts,
            nba_players.reb,
            nba_players.ast
        FROM nba_teams
        JOIN nba_players
            ON nba_teams.id = nba_players.team_id
        """

        self.df = pd.read_sql_query(query, conn)
        conn.close()

        if self.df.empty:
            messagebox.showwarning("No Data", "No data found.")
            return

        # NumPy calculations
        avg_salary = np.mean(self.df["salary"])
        max_salary = np.max(self.df["salary"])
        avg_points = np.mean(self.df["pts"])
        max_points = np.max(self.df["pts"])

        # Groupby summaries
        salary_by_team = self.df.groupby("team_name")["salary"].sum()
        points_by_team = self.df.groupby("team_name")["pts"].mean()

        self.output.delete("1.0", tk.END)

        self.output.insert(tk.END, "=== NBA REPORT ===\n\n")

        self.output.insert(tk.END, "NumPy Stats:\n")
        self.output.insert(tk.END, f"Average Salary: {avg_salary:.2f}\n")
        self.output.insert(tk.END, f"Max Salary: {max_salary:.2f}\n")
        self.output.insert(tk.END, f"Average Points: {avg_points:.2f}\n")
        self.output.insert(tk.END, f"Max Points: {max_points:.2f}\n\n")

        self.output.insert(tk.END, "Total Salary by Team:\n")
        self.output.insert(tk.END, salary_by_team.to_string())
        self.output.insert(tk.END, "\n\n")

        self.output.insert(tk.END, "Average Points by Team:\n")
        self.output.insert(tk.END, points_by_team.to_string())
        self.output.insert(tk.END, "\n\n")

    def export_csv(self):
        if self.df.empty:
            messagebox.showwarning("No Data", "Load report first.")
            return

        self.df.to_csv("nba_report_export.csv", index=False)
        messagebox.showinfo("Success", "CSV exported!")