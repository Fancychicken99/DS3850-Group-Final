import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog

import pandas as pd
import numpy as np

from Database import createTables, seedData, getDBConnection
from CRUD import (
    getAllTeams,
    addTeam,
    updateTeam,
    deleteTeam,
    getPlayersByTeam,
    addPlayer,
    updatePlayer,
    deletePlayer,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BasketballApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Basketball League Management System")
        self.geometry("1200x700")

        createTables()
        seedData()

        self.selected_team_id = None
        self.selected_player_id = None
        self.selected_player_team_id = None
        self.team_name_to_id = {}
        self.team_id_to_name = {}
        self.player_row_team_ids = {}
        self.report_df = pd.DataFrame()

        self.create_layout()
        self.load_teams()

    def create_layout(self):
        title = ctk.CTkLabel(
            self,
            text="Basketball League Dashboard",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=20)

        self.tabs = ctk.CTkTabview(self, width=1150, height=600)
        self.tabs.pack(padx=20, pady=10, fill="both", expand=True)

        self.teams_tab = self.tabs.add("Teams")
        self.players_tab = self.tabs.add("Players")
        self.reports_tab = self.tabs.add("Reports")

        self.build_teams_tab()
        self.build_players_tab()
        self.build_reports_tab()

    # ---------------- TEAMS TAB ----------------
    def build_teams_tab(self):
        form_frame = ctk.CTkFrame(self.teams_tab)
        form_frame.pack(padx=15, pady=15, fill="x")

        self.team_name_entry = self.create_labeled_entry(form_frame, "Team Name", 0, 0)
        self.city_entry = self.create_labeled_entry(form_frame, "City", 0, 1)
        self.conference_entry = self.create_labeled_entry(form_frame, "Conference", 0, 2)
        self.division_entry = self.create_labeled_entry(form_frame, "Division", 2, 0)
        self.coach_entry = self.create_labeled_entry(form_frame, "Coach", 2, 1)
        self.owner_entry = self.create_labeled_entry(form_frame, "Owner", 2, 2)
        self.budget_entry = self.create_labeled_entry(form_frame, "Budget", 4, 0)

        button_frame = ctk.CTkFrame(self.teams_tab)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Add Team", command=self.add_team).grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="Update Team", command=self.update_team).grid(row=0, column=1, padx=10)
        ctk.CTkButton(button_frame, text="Delete Team", command=self.delete_team).grid(row=0, column=2, padx=10)
        ctk.CTkButton(button_frame, text="Clear Fields", command=self.clear_team_fields).grid(row=0, column=3, padx=10)

        search_frame = ctk.CTkFrame(self.teams_tab)
        search_frame.pack(padx=15, pady=10, fill="x")

        ctk.CTkLabel(search_frame, text="Search Teams:").pack(side="left", padx=10)
        self.team_search_entry = ctk.CTkEntry(search_frame, width=250)
        self.team_search_entry.pack(side="left", padx=10)

        ctk.CTkButton(search_frame, text="Search", command=self.search_teams).pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="View All", command=self.load_teams).pack(side="left", padx=10)

        self.teams_tree = self.create_treeview(
            self.teams_tab,
            columns=("ID", "Name", "City", "Conference", "Division", "Coach", "Owner", "Budget")
        )

        self.teams_tree.bind("<<TreeviewSelect>>", self.select_team)

    # ---------------- PLAYERS TAB ----------------
    def build_players_tab(self):
        form_frame = ctk.CTkFrame(self.players_tab)
        form_frame.pack(padx=15, pady=15, fill="x")

        team_label = ctk.CTkLabel(form_frame, text="Team Name")
        team_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        self.player_team_dropdown = ctk.CTkComboBox(form_frame, values=[], width=220, state="readonly")
        self.player_team_dropdown.grid(row=1, column=0, padx=10, pady=(0, 10))

        self.player_name_entry = self.create_labeled_entry(form_frame, "Player Name", 0, 1)
        self.number_entry = self.create_labeled_entry(form_frame, "Number", 0, 2)
        self.salary_entry = self.create_labeled_entry(form_frame, "Salary", 2, 0)
        self.injury_status_entry = self.create_labeled_entry(form_frame, "Injury Status Y/N", 2, 1)
        self.position_entry = self.create_labeled_entry(form_frame, "Position", 2, 2)
        self.pts_entry = self.create_labeled_entry(form_frame, "Points", 4, 0)
        self.reb_entry = self.create_labeled_entry(form_frame, "Rebounds", 4, 1)
        self.ast_entry = self.create_labeled_entry(form_frame, "Assists", 4, 2)

        button_frame = ctk.CTkFrame(self.players_tab)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Add Player", command=self.add_player).grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="Update Player", command=self.update_player).grid(row=0, column=1, padx=10)
        ctk.CTkButton(button_frame, text="Delete Player", command=self.delete_player).grid(row=0, column=2, padx=10)

        ctk.CTkLabel(button_frame, text="View:").grid(row=0, column=3, padx=(20, 5))
        self.player_filter_dropdown = ctk.CTkComboBox(button_frame, values=["All Players"], width=220, state="readonly")
        self.player_filter_dropdown.grid(row=0, column=4, padx=5)
        self.player_filter_dropdown.set("All Players")

        ctk.CTkButton(button_frame, text="View Players", command=self.load_players).grid(row=0, column=5, padx=10)
        ctk.CTkButton(button_frame, text="Clear Fields", command=self.clear_player_fields).grid(row=0, column=6, padx=10)

        search_frame = ctk.CTkFrame(self.players_tab)
        search_frame.pack(padx=15, pady=10, fill="x")

        ctk.CTkLabel(search_frame, text="Search Players:").pack(side="left", padx=10)
        self.player_search_entry = ctk.CTkEntry(search_frame, width=250)
        self.player_search_entry.pack(side="left", padx=10)

        ctk.CTkButton(search_frame, text="Search", command=self.search_players).pack(side="left", padx=10)

        self.players_tree = self.create_treeview(
            self.players_tab,
            columns=("ID", "Team Name", "Name", "Number", "Salary", "Injury", "Position", "PTS", "REB", "AST")
        )

        self.players_tree.bind("<<TreeviewSelect>>", self.select_player)

    # ---------------- REPORTS TAB ----------------
    def build_reports_tab(self):
        top_frame = ctk.CTkFrame(self.reports_tab)
        top_frame.pack(padx=15, pady=15, fill="x")

        ctk.CTkButton(top_frame, text="Generate Report", command=self.generate_report).grid(row=0, column=0, padx=10, pady=8)
        ctk.CTkButton(top_frame, text="Export CSV", command=self.export_csv).grid(row=0, column=1, padx=10, pady=8)

        ctk.CTkLabel(top_frame, text="Team:").grid(row=1, column=0, padx=10, pady=(10, 2), sticky="w")
        self.report_team_dropdown = ctk.CTkComboBox(top_frame, values=[], width=240, state="readonly")
        self.report_team_dropdown.grid(row=2, column=0, padx=10, pady=(0, 10))
        ctk.CTkButton(top_frame, text="Show Team Summary", command=self.show_selected_team_summary).grid(row=2, column=1, padx=10, pady=(0, 10))

        ctk.CTkLabel(top_frame, text="Position:").grid(row=1, column=2, padx=10, pady=(10, 2), sticky="w")
        self.report_position_dropdown = ctk.CTkComboBox(top_frame, values=["All"], width=180, state="readonly")
        self.report_position_dropdown.grid(row=2, column=2, padx=10, pady=(0, 10))
        self.report_position_dropdown.set("All")
        ctk.CTkButton(top_frame, text="Show Position Summary", command=self.show_position_summary).grid(row=2, column=3, padx=10, pady=(0, 10))

        self.report_text = ctk.CTkTextbox(self.reports_tab, width=1000, height=450)
        self.report_text.pack(padx=15, pady=15, fill="both", expand=True)

    # ---------------- HELPER METHODS ----------------
    def create_labeled_entry(self, parent, label_text, row, column):
        label = ctk.CTkLabel(parent, text=label_text)
        label.grid(row=row, column=column, padx=10, pady=(10, 0), sticky="w")

        entry = ctk.CTkEntry(parent, width=220)
        entry.grid(row=row + 1, column=column, padx=10, pady=(0, 10))

        return entry
    
    def format_millions(self, value):
        try:
            number = float(value)
            return f"${number:.1f}M"
        except (ValueError, TypeError):
            return value

    def clean_millions_input(self, value):
        return str(value).replace("$", "").replace("M", "").replace("m", "").strip()

    def load_report_dropdowns(self):
        if not hasattr(self, "report_team_dropdown") or not hasattr(self, "report_position_dropdown"):
            return

        team_names = [team["name"] for team in getAllTeams()]
        self.report_team_dropdown.configure(values=team_names)

        if team_names and not self.report_team_dropdown.get():
            self.report_team_dropdown.set(team_names[0])

        conn = getDBConnection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT position FROM nba_players ORDER BY position")
        positions = [row[0] for row in cursor.fetchall()]
        conn.close()

        position_options = ["All"] + positions
        self.report_position_dropdown.configure(values=position_options)

        if self.report_position_dropdown.get() not in position_options:
            self.report_position_dropdown.set("All")

    def get_report_dataframe(self):
        conn = getDBConnection()
        query = """
        SELECT
            nba_teams.name AS team_name,
            nba_players.name AS player_name,
            nba_players.salary,
            nba_players.pts,
            nba_players.reb,
            nba_players.ast,
            nba_players.position,
            nba_players.injury_status
        FROM nba_teams
        JOIN nba_players
            ON nba_teams.id = nba_players.team_id
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def create_treeview(self, parent, columns):
                tree_frame = ctk.CTkFrame(parent)
                tree_frame.pack(padx=15, pady=15, fill="both", expand=True)

                tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)

                column_widths = {
                    "ID": 60,
                    "Team ID": 80,
                    "Team Name": 220,
                    "Name": 260,
                    "Number": 80,
                    "Salary": 100,
                    "Injury": 80,
                    "Position": 100,
                    "PTS": 80,
                    "REB": 80,
                    "AST": 80,
                    "City": 130,
                    "Conference": 130,
                    "Division": 130,
                    "Coach": 180,
                    "Owner": 180,
                    "Budget": 120,
        }


                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=column_widths.get(col, 120), minwidth=60, anchor="center")

                x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
                y_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)

                tree.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

                tree.grid(row=0, column=0, sticky="nsew")
                y_scrollbar.grid(row=0, column=1, sticky="ns")
                x_scrollbar.grid(row=1, column=0, sticky="ew")

                tree_frame.grid_rowconfigure(0, weight=1)
                tree_frame.grid_columnconfigure(0, weight=1)

                return tree

    # ---------------- TEAM FUNCTIONS ----------------
    def add_team(self):
        try:
            name = self.team_name_entry.get().strip()
            city = self.city_entry.get().strip()
            conference = self.conference_entry.get().strip()
            division = self.division_entry.get().strip()
            coach = self.coach_entry.get().strip()
            owner = self.owner_entry.get().strip()
            budget = float(self.clean_millions_input(self.budget_entry.get()))

            if not name or not city or not conference or not division or not coach or not owner:
                messagebox.showerror("Error", "Please fill out all team fields.")
                return

            addTeam(name, city, conference, division, coach, owner, budget)
            self.load_teams()
            self.clear_team_fields()
            messagebox.showinfo("Success", "Team added successfully.")

        except ValueError:
            messagebox.showerror("Error", "Budget must be a valid number.")


    def update_team(self):
        if self.selected_team_id is None:
            messagebox.showerror("Error", "Please select a team to update.")
            return

        try:
            name = self.team_name_entry.get().strip()
            city = self.city_entry.get().strip()
            conference = self.conference_entry.get().strip()
            division = self.division_entry.get().strip()
            coach = self.coach_entry.get().strip()
            owner = self.owner_entry.get().strip()
            budget = float(self.clean_millions_input(self.budget_entry.get()))

            if not name or not city or not conference or not division or not coach or not owner:
                messagebox.showerror("Error", "Please fill out all team fields.")
                return

            updateTeam(self.selected_team_id, name, city, conference, division, coach, owner, budget)
            self.load_teams()
            self.clear_team_fields()
            self.selected_team_id = None
            messagebox.showinfo("Success", "Team updated successfully.")

        except ValueError:
            messagebox.showerror("Error", "Budget must be a valid number.")


    def delete_team(self):
        if self.selected_team_id is None:
            messagebox.showerror("Error", "Please select a team to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this team? This may also delete players connected to this team."
        )

        if confirm:
            deleteTeam(self.selected_team_id)
            self.load_teams()
            self.load_players()
            self.clear_team_fields()
            self.selected_team_id = None
            messagebox.showinfo("Success", "Team deleted successfully.")

    def load_teams(self):
        teams = getAllTeams()

        for item in self.teams_tree.get_children():
            self.teams_tree.delete(item)

        for team in teams:
            self.teams_tree.insert(
                "",
                "end",
                values=(
                    team["id"],
                    team["name"],
                    team["city"],
                    team["conference"],
                    team["division"],
                    team["coach"],
                    team["owner"],
                    self.format_millions(team["budget"])
            )
        )
        self.load_team_dropdown()
        self.load_report_dropdowns()

    def load_team_dropdown(self):
        teams = getAllTeams()

        self.team_name_to_id = {}
        self.team_id_to_name = {}
        team_names = []

        for team in teams:
            team_name = team["name"]
            team_id = team["id"]

            self.team_name_to_id[team_name] = team_id
            self.team_id_to_name[team_id] = team_name
            team_names.append(team_name)

        self.player_team_dropdown.configure(values=team_names)

        if team_names:
            self.player_team_dropdown.set(team_names[0])
        else:
            self.player_team_dropdown.set("")

        self.load_player_filter_dropdown(team_names)

    def load_player_filter_dropdown(self, team_names):
        filter_options = ["All Players"] + team_names
        self.player_filter_dropdown.configure(values=filter_options)

        current_filter = self.player_filter_dropdown.get()
        if current_filter not in filter_options:
            self.player_filter_dropdown.set("All Players")

    def search_teams(self):
        search_text = self.team_search_entry.get().strip().lower()

        for item in self.teams_tree.get_children():
            self.teams_tree.delete(item)

        teams = getAllTeams()

        for team in teams:
            if (
                search_text in team["name"].lower()
                or search_text in team["city"].lower()
                or search_text in team["conference"].lower()
                or search_text in team["division"].lower()
                or search_text in team["coach"].lower()
                or search_text in team["owner"].lower()
            ):
                self.teams_tree.insert(
                    "",
                    "end",
                    values=(
                        team["id"],
                        team["name"],
                        team["city"],
                        team["conference"],
                        team["division"],
                        team["coach"],
                        team["owner"],
                        self.format_millions(team["budget"])
                    )
                )

    def select_team(self, event):
        selected = self.teams_tree.focus()

        if selected:
            values = self.teams_tree.item(selected, "values")

            self.clear_team_fields()

            self.selected_team_id = values[0]
            self.player_filter_dropdown.set(values[1])

            self.team_name_entry.insert(0, values[1])
            self.city_entry.insert(0, values[2])
            self.conference_entry.insert(0, values[3])
            self.division_entry.insert(0, values[4])
            self.coach_entry.insert(0, values[5])
            self.owner_entry.insert(0, values[6])
            self.budget_entry.insert(0, self.clean_millions_input(values[7]))

    def clear_team_fields(self):
        self.team_name_entry.delete(0, "end")
        self.city_entry.delete(0, "end")
        self.conference_entry.delete(0, "end")
        self.division_entry.delete(0, "end")
        self.coach_entry.delete(0, "end")
        self.owner_entry.delete(0, "end")
        self.budget_entry.delete(0, "end")
        self.selected_team_id = None

    # ---------------- PLAYER FUNCTIONS ----------------
    def add_player(self):
        selected_team_name = self.player_team_dropdown.get()

        if selected_team_name not in self.team_name_to_id:
            messagebox.showerror("Error", "Please select an existing team.")
            return

        try:
            team_id = self.team_name_to_id[selected_team_name]
            name = self.player_name_entry.get().strip()
            number = int(self.number_entry.get().strip())
            salary = float(self.clean_millions_input(self.salary_entry.get()))
            injury_status = self.injury_status_entry.get().strip()
            position = self.position_entry.get().strip()
            pts = float(self.pts_entry.get().strip())
            reb = float(self.reb_entry.get().strip())
            ast = float(self.ast_entry.get().strip())

            if not name or not injury_status or not position:
                messagebox.showerror("Error", "Please fill out all player fields.")
                return

            addPlayer(team_id, name, number, salary, injury_status, position, pts, reb, ast)
            self.load_players()
            self.clear_player_fields()
            messagebox.showinfo("Success", "Player added successfully.")

        except ValueError:
            messagebox.showerror(
                "Error",
                "Number must be whole number. Salary, points, rebounds, and assists must be valid numbers."
            )

    def update_player(self):
        if self.selected_player_id is None:
            messagebox.showerror("Error", "Please select a player to update.")
            return

        try:
            name = self.player_name_entry.get().strip()
            number = int(self.number_entry.get().strip())
            salary = float(self.clean_millions_input(self.salary_entry.get()))
            injury_status = self.injury_status_entry.get().strip()
            position = self.position_entry.get().strip()
            pts = float(self.pts_entry.get().strip())
            reb = float(self.reb_entry.get().strip())
            ast = float(self.ast_entry.get().strip())

            if not name or not injury_status or not position:
                messagebox.showerror("Error", "Please fill out all player fields.")
                return

            updatePlayer(self.selected_player_id, name, number, salary, injury_status, position, pts, reb, ast)
            self.load_players()
            self.clear_player_fields()
            self.selected_player_id = None
            messagebox.showinfo("Success", "Player updated successfully.")

        except ValueError:
            messagebox.showerror(
                "Error",
                "Number must be whole number. Salary, points, rebounds, and assists must be valid numbers."
            )


    def delete_player(self):
        if self.selected_player_id is None:
            messagebox.showerror("Error", "Please select a player to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this player?")

        if confirm:
            deletePlayer(self.selected_player_id)
            self.load_players()
            self.clear_player_fields()
            self.selected_player_id = None
            messagebox.showinfo("Success", "Player deleted successfully.")

    def load_players(self):
        selected_filter = self.player_filter_dropdown.get()

        if selected_filter == "All Players" or selected_filter == "":
            conn = getDBConnection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM nba_players ORDER BY name")
            players = [dict(row) for row in cursor.fetchall()]
            conn.close()
        else:
            team_id = self.team_name_to_id.get(selected_filter)

            if team_id is None:
                messagebox.showerror("Error", "Please select a valid team.")
                return

            players = getPlayersByTeam(team_id)

        for item in self.players_tree.get_children():
            self.players_tree.delete(item)
        self.player_row_team_ids = {}
        for player in players:
            team_id = player["team_id"]
            team_name = self.team_id_to_name.get(team_id, f"Team {team_id}")

            item_id = self.players_tree.insert(
                "",
                "end",
                values=(
                    player["id"],
                    team_name,
                    player["name"],
                    player["number"],
                    self.format_millions(player["salary"]),
                    player["injury_status"],
                    player["position"],
                    player["pts"],
                    player["reb"],
                    player["ast"]
                )
            )
            self.player_row_team_ids[item_id] = team_id

    def search_players(self):
        search_text = self.player_search_entry.get().strip().lower()

        for item in self.players_tree.get_children():
            self.players_tree.delete(item)
        self.player_row_team_ids = {}

        conn = getDBConnection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nba_players ORDER BY name")
        players = [dict(row) for row in cursor.fetchall()]
        conn.close()

        for player in players:
            team_id = player["team_id"]
            team_name = self.team_id_to_name.get(team_id, f"Team {team_id}")

            if (
                search_text in player["name"].lower()
                or search_text in team_name.lower()
                or search_text in player["position"].lower()
                or search_text in player["injury_status"].lower()
                or search_text in str(player["number"])
                or search_text in str(team_id)
            ):
                item_id = self.players_tree.insert(
                    "",
                    "end",
                    values=(
                        player["id"],
                        team_name,
                        player["name"],
                        player["number"],
                        self.format_millions(player["salary"]),
                        player["injury_status"],
                        player["position"],
                        player["pts"],
                        player["reb"],
                        player["ast"]
                    )
                )
                self.player_row_team_ids[item_id] = team_id

    def select_player(self, event):
        selected = self.players_tree.focus()

        if selected:
            values = self.players_tree.item(selected, "values")

            self.clear_player_fields()

            self.selected_player_id = values[0]
            self.selected_player_team_id = self.player_row_team_ids.get(selected)

            team_name = values[1]
            self.player_team_dropdown.set(team_name)
            self.player_name_entry.insert(0, values[2])
            self.number_entry.insert(0, values[3])
            self.salary_entry.insert(0, self.clean_millions_input(values[4]))
            self.injury_status_entry.insert(0, values[5])
            self.position_entry.insert(0, values[6])
            self.pts_entry.insert(0, values[7])
            self.reb_entry.insert(0, values[8])
            self.ast_entry.insert(0, values[9])

    def clear_player_fields(self):
        if self.team_name_to_id:
            first_team_name = list(self.team_name_to_id.keys())[0]
            self.player_team_dropdown.set(first_team_name)
        else:
            self.player_team_dropdown.set("")
        self.player_name_entry.delete(0, "end")
        self.number_entry.delete(0, "end")
        self.salary_entry.delete(0, "end")
        self.injury_status_entry.delete(0, "end")
        self.position_entry.delete(0, "end")
        self.pts_entry.delete(0, "end")
        self.reb_entry.delete(0, "end")
        self.ast_entry.delete(0, "end")
        self.selected_player_id = None
        self.selected_player_team_id = None

    def league_summary(self):
        df = self.report_df
        return (
            f"Top Scorer: {df.loc[df['pts'].idxmax(), 'player_name']}\n"
            f"Top Rebounder: {df.loc[df['reb'].idxmax(), 'player_name']}\n"
            f"Top Assist Leader: {df.loc[df['ast'].idxmax(), 'player_name']}\n"
        )

    def team_summary(self):
        df = self.report_df
        grouped = df.groupby("team_name")

        summary = ""
        for team, group in grouped:
            top_scorer = group.loc[group['pts'].idxmax(), 'player_name']
            summary += (
                f"{team}:\n"
                f"  Players: {len(group)}\n"
                f"  Avg Points: {group['pts'].mean():.1f}\n"
                f"  Top Scorer: {top_scorer}\n\n"
            )
        return summary

    def player_report(self):
        df = self.report_df
        grouped = df.groupby("position")

        report = ""
        for pos, group in grouped:
            report += f"{pos}: {len(group)} players\n"
        return report

    def selected_team_data(self, team_name):
        df = self.report_df
        return df[df["team_name"] == team_name]

    def format_selected_team_summary(self, team_name):
        team_df = self.selected_team_data(team_name)
        if team_df.empty:
            return "No data for selected team."

        return (
            f"Team: {team_name}\n"
            f"Players: {len(team_df)}\n"
            f"Avg Points: {team_df['pts'].mean():.1f}\n"
            f"Total Salary: ${team_df['salary'].sum():.1f}M\n"
        )

    # ---------------- REPORT FUNCTIONS ----------------
    def generate_report(self):
        conn = getDBConnection()

        query = """
        SELECT
            nba_teams.name AS team_name,
            nba_players.name AS player_name,
            nba_players.salary,
            nba_players.pts,
            nba_players.reb,
            nba_players.ast,
            nba_players.position,
            nba_players.injury_status
        FROM nba_teams
        JOIN nba_players
            ON nba_teams.id = nba_players.team_id
        """

        self.report_df = pd.read_sql_query(query, conn)
        conn.close()

        self.report_text.delete("1.0", "end")

        if self.report_df.empty:
            messagebox.showwarning("No Data", "No report data found.")
            return

        avg_salary = np.mean(self.report_df["salary"])
        max_salary = np.max(self.report_df["salary"])
        avg_points = np.mean(self.report_df["pts"])
        max_points = np.max(self.report_df["pts"])
        avg_rebounds = np.mean(self.report_df["reb"])
        avg_assists = np.mean(self.report_df["ast"])

        salary_by_team = self.report_df.groupby("team_name")["salary"].sum()
        avg_points_by_team = self.report_df.groupby("team_name")["pts"].mean()
        avg_rebounds_by_team = self.report_df.groupby("team_name")["reb"].mean()
        avg_assists_by_team = self.report_df.groupby("team_name")["ast"].mean()
        injured_count = self.report_df[self.report_df["injury_status"].str.upper() == "Y"].shape[0]

        self.report_text.insert("end", "BASKETBALL LEAGUE REPORT\n")
        self.report_text.insert("end", "=" * 35 + "\n\n")

        self.report_text.insert("end", "League Summary Statistics\n")
        self.report_text.insert("end", "-" * 25 + "\n")
        self.report_text.insert("end", f"Average Salary: ${avg_salary:.1f}M\n")
        self.report_text.insert("end", f"Highest Salary: ${max_salary:.1f}M\n")
        self.report_text.insert("end", f"Average Points: {avg_points:.2f}\n")
        self.report_text.insert("end", f"Highest Points: {max_points:.2f}\n")
        self.report_text.insert("end", f"Average Rebounds: {avg_rebounds:.2f}\n")
        self.report_text.insert("end", f"Average Assists: {avg_assists:.2f}\n")
        self.report_text.insert("end", f"Injured Players Count: {injured_count}\n\n")

        self.report_text.insert("end", "Total Salary by Team\n")
        self.report_text.insert("end", "-" * 20 + "\n")
        self.report_text.insert("end", salary_by_team.rename_axis(None).to_string())
        self.report_text.insert("end", "\n\n")

        self.report_text.insert("end", "Average Points by Team\n")
        self.report_text.insert("end", "-" * 22 + "\n")
        self.report_text.insert("end", avg_points_by_team.rename_axis(None).to_string(float_format=lambda x: f"{x:.1f}"))
        self.report_text.insert("end", "\n\n")

        self.report_text.insert("end", "Average Rebounds by Team\n")
        self.report_text.insert("end", "-" * 24 + "\n")
        self.report_text.insert("end", avg_rebounds_by_team.rename_axis(None).to_string(float_format=lambda x: f"{x:.1f}"))
        self.report_text.insert("end", "\n\n")

        self.report_text.insert("end", "Average Assists by Team\n")
        self.report_text.insert("end", "-" * 23 + "\n")
        self.report_text.insert("end", avg_assists_by_team.rename_axis(None).to_string(float_format=lambda x: f"{x:.1f}"))
        self.report_text.insert("end", "\n\n")

        # League Summary
        self.report_text.insert("end", "League Leaders\n")
        self.report_text.insert("end", "-" * 20 + "\n")
        self.report_text.insert("end", self.league_summary())
        self.report_text.insert("end", "\n")

        # Team Summary
        self.report_text.insert("end", "Team Summary\n")
        self.report_text.insert("end", "-" * 20 + "\n")
        self.report_text.insert("end", self.team_summary())

        # Player Position Report
        self.report_text.insert("end", "Players by Position\n")
        self.report_text.insert("end", "-" * 20 + "\n")
        self.report_text.insert("end", self.player_report())

    def show_selected_team_summary(self):
        team_name = self.report_team_dropdown.get()

        if not team_name:
            messagebox.showwarning("No Team Selected", "Please select a team first.")
            return

        df = self.get_report_dataframe()
        team_df = df[df["team_name"] == team_name]

        self.report_df = team_df
        self.report_text.delete("1.0", "end")

        if team_df.empty:
            self.report_text.insert("end", f"No data found for {team_name}.")
            return

        top_scorer = team_df.loc[team_df["pts"].idxmax()]
        injured_count = team_df[team_df["injury_status"].str.upper() == "Y"].shape[0]

        self.report_text.insert("end", f"{team_name} Team Summary\n")
        self.report_text.insert("end", "=" * 30 + "\n\n")
        self.report_text.insert("end", f"Players: {len(team_df)}\n")
        self.report_text.insert("end", f"Injured Players: {injured_count}\n")
        self.report_text.insert("end", f"Average Salary: ${team_df['salary'].mean():.1f}M\n")
        self.report_text.insert("end", f"Total Salary: ${team_df['salary'].sum():.1f}M\n")
        self.report_text.insert("end", f"Average Points: {team_df['pts'].mean():.1f}\n")
        self.report_text.insert("end", f"Average Rebounds: {team_df['reb'].mean():.1f}\n")
        self.report_text.insert("end", f"Average Assists: {team_df['ast'].mean():.1f}\n")
        self.report_text.insert("end", f"Top Scorer: {top_scorer['player_name']} ({top_scorer['pts']:.1f} PPG)\n\n")

        self.report_text.insert("end", "Roster\n")
        self.report_text.insert("end", "-" * 15 + "\n")

        roster = team_df[["player_name", "position", "injury_status", "pts", "reb", "ast"]].sort_values("pts", ascending=False)

        for _, player in roster.iterrows():
            injury_status = "Injured" if str(player["injury_status"]).upper() == "Y" else "Active"
            self.report_text.insert(
                "end",
                f"• {player['player_name']} ({player['position']}) - "
                f"{player['pts']:.1f} PTS, {player['reb']:.1f} REB, {player['ast']:.1f} AST - "
                f"{injury_status}\n"
            )

    def show_position_summary(self):
        position = self.report_position_dropdown.get()
        df = self.get_report_dataframe()

        if position and position != "All":
            df = df[df["position"].str.lower() == position.lower()]

        self.report_df = df
        self.report_text.delete("1.0", "end")

        if df.empty:
            self.report_text.insert("end", "No players found for this position.")
            return

        title_position = position if position else "All"

        self.report_text.insert("end", f"{title_position} Position Summary\n")
        self.report_text.insert("end", "=" * 30 + "\n\n")
        self.report_text.insert("end", f"Player Count: {len(df)}\n")
        self.report_text.insert("end", f"Average Salary: ${df['salary'].mean():.1f}M\n")
        self.report_text.insert("end", f"Average Points: {df['pts'].mean():.1f}\n")
        self.report_text.insert("end", f"Average Rebounds: {df['reb'].mean():.1f}\n")
        self.report_text.insert("end", f"Average Assists: {df['ast'].mean():.1f}\n\n")

        self.report_text.insert("end", "Players\n")
        self.report_text.insert("end", "-" * 15 + "\n")

        players = df[["player_name", "team_name", "position", "injury_status", "pts", "reb", "ast"]].sort_values(["position", "team_name", "player_name"])

        for _, player in players.iterrows():
            injury_status = "Injured" if str(player["injury_status"]).upper() == "Y" else "Active"
            self.report_text.insert(
                "end",
                f"• {player['player_name']} - {player['team_name']} ({player['position']}) - "
                f"{player['pts']:.1f} PTS, {player['reb']:.1f} REB, {player['ast']:.1f} AST - "
                f"{injury_status}\n"
            )

    def export_csv(self):
        if self.report_df.empty:
            messagebox.showwarning("No Data", "Generate the report first before exporting.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="basketball_report.csv"
        )

        if file_path:
            export_df = self.report_df.copy()
            export_df["salary"] = export_df["salary"].apply(self.format_millions)
            export_df.to_csv(file_path, index=False)
            messagebox.showinfo("Success", "CSV exported successfully.")


if __name__ == "__main__":
    app = BasketballApp()
    app.mainloop()