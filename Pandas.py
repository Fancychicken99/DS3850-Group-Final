# ============================================================
# DS3850 — Group Project - Pandas.py
# Name: Brodi Remick
# Section: 001
# Date: 04/29/2026
# ============================================================

import sqlite3
import pandas as pd

DBNAME = "nba_league.db"


# Shared helpers
# These utilities keep report formatting consistent across the module.
def clean_number(value):
    if float(value).is_integer():
        return int(value)

    return value


# Data loading
# This pulls the player and team data from SQLite into one pandas DataFrame.
def load_player_report():
    conn = sqlite3.connect(DBNAME)

    query = """
        SELECT 
            nba_players.id,
            nba_players.name AS Player_Name,
            nba_players.position,
            nba_players.salary,
            nba_players.injury_status,
            nba_players.pts,
            nba_players.reb,
            nba_players.ast,
            nba_teams.name AS Team_Name,
            nba_teams.city,
            nba_teams.conference,
            nba_teams.division,
            nba_teams.coach,
            nba_teams.owner,
            nba_teams.budget
        FROM nba_players
        JOIN nba_teams
            ON nba_players.team_id = nba_teams.id
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df


# Dropdown options
# The UI can use this list to fill the position filter dropdown.
def available_positions():
    df = load_player_report()

    return sorted(df["position"].dropna().unique())


# Player report
# Returns a summary first, then the filtered player list for the UI table.
def player_report(position=None):
    df = load_player_report()
    selected_position = position if position and position != "All" else "All"

    if position and position != "All":
        df = df[df["position"].str.lower() == position.lower()]

    summary = pd.DataFrame(
        [
            {
                "Position": selected_position,
                "Player_Count": len(df),
                "Avg_Points": round(float(df["pts"].mean()), 1) if not df.empty else 0,
                "Avg_Rebounds": (
                    round(float(df["reb"].mean()), 1) if not df.empty else 0
                ),
                "Avg_Assists": round(float(df["ast"].mean()), 1) if not df.empty else 0,
            }
        ]
    )

    players = (
        df[
            [
                "Player_Name",
                "position",
                "injury_status",
                "pts",
                "reb",
                "ast",
                "Team_Name",
            ]
        ]
        .sort_values(["position", "Team_Name", "Player_Name"])
        .reset_index(drop=True)
    )

    return {"summary": summary, "players": players}


# Team summary
# Use team_summary() for all teams, or team_summary(team_name) for one selected team.
def team_summary(team_name=None):
    df = load_player_report()

    summary = df.groupby(["Team_Name"], as_index=False).agg(
        Player_Count=("Player_Name", "count"),
        Avg_Points=("pts", "mean"),
        Avg_Rebounds=("reb", "mean"),
        Avg_Assists=("ast", "mean"),
        Injured_Players=("injury_status", lambda status: (status == "Y").sum()),
    )

    top_scorers = df.loc[
        df.groupby("Team_Name")["pts"].idxmax(), ["Team_Name", "Player_Name", "pts"]
    ].rename(columns={"Player_Name": "Top_Scorer", "pts": "Top_Scorer_Points"})

    summary = summary.merge(top_scorers, on="Team_Name")

    average_columns = ["Avg_Points", "Avg_Rebounds", "Avg_Assists", "Top_Scorer_Points"]

    summary[average_columns] = summary[average_columns].round(1)

    summary = summary.rename(columns={"Team_Name": "Team"})

    summary = summary[
        [
            "Team",
            "Player_Count",
            "Injured_Players",
            "Avg_Points",
            "Avg_Rebounds",
            "Avg_Assists",
            "Top_Scorer",
            "Top_Scorer_Points",
        ]
    ]

    if team_name:
        summary = summary[summary["Team"].str.lower() == team_name.lower()].reset_index(
            drop=True
        )

    return summary


# Clicked team details
# The UI can call team_clicked(team_name) when a team row/button is selected.
def selected_team_data(team_name):
    team_data = team_summary(team_name)

    if team_data.empty:
        return None, pd.DataFrame()

    players = load_player_report()
    players = (
        players[players["Team_Name"].str.lower() == team_name.lower()][
            ["Player_Name", "position", "injury_status", "pts", "reb", "ast"]
        ]
        .sort_values("pts", ascending=False)
        .reset_index(drop=True)
    )

    return team_data.iloc[0], players


def format_selected_team_summary(team_name):
    team_data, players = selected_team_data(team_name)

    if team_data is None:
        return f"No team found for: {team_name}"

    player_lines = []
    for _, player in players.iterrows():
        injury_note = "Injured" if player["injury_status"] == "Y" else "Active"
        player_lines.append(
            f"- {player['Player_Name']} ({player['position']}): "
            f"{player['pts']} PTS, {player['reb']} REB, {player['ast']} AST, "
            f"{injury_note}"
        )

    return f"""
{team_data['Team']} Team Summary
Players: {team_data['Player_Count']}
Injured Players: {team_data['Injured_Players']}
Average Points: {team_data['Avg_Points']}
Average Rebounds: {team_data['Avg_Rebounds']}
Average Assists: {team_data['Avg_Assists']}
Top Scorer: {team_data['Top_Scorer']} ({team_data['Top_Scorer_Points']} PPG)

Roster:
{chr(10).join(player_lines)}
""".strip()


def team_clicked(team_name):
    return format_selected_team_summary(team_name)


# League summary
# This returns overall leaders first, followed by league totals and averages.
def league_summary():
    df = load_player_report()

    def highest_stat_row(stat_name, column_name):
        player = df.loc[df[column_name].idxmax()]
        return {
            "Stat": stat_name,
            "Player": player["Player_Name"],
            "Value": round(float(player[column_name]), 2),
        }

    summary_rows = [
        {"Stat": "Total Teams", "Value": df["Team_Name"].nunique(), "Player": ""},
        {"Stat": "Total Players", "Value": len(df), "Player": ""},
        {
            "Stat": "Injured Players",
            "Value": int((df["injury_status"] == "Y").sum()),
            "Player": "",
        },
        {
            "Stat": "Average Points",
            "Value": round(float(df["pts"].mean()), 2),
            "Player": "",
        },
        {
            "Stat": "Average Rebounds",
            "Value": round(float(df["reb"].mean()), 2),
            "Player": "",
        },
        {
            "Stat": "Average Assists",
            "Value": round(float(df["ast"].mean()), 2),
            "Player": "",
        },
    ]

    highest_stats = [
        highest_stat_row("Highest Points", "pts"),
        highest_stat_row("Highest Rebounds", "reb"),
        highest_stat_row("Highest Assists", "ast"),
    ]

    summary = pd.DataFrame(highest_stats + summary_rows)[["Stat", "Value", "Player"]]
    summary["Value"] = pd.Series(
        [clean_number(value) for value in summary["Value"]], dtype=object
    )

    return summary


# CSV export
# This exports the current full player report for download or sharing.
def export_report_to_csv():
    df = player_report()["players"]
    df.to_csv("nba_player_report.csv", index=False)
    return "nba_player_report.csv"
