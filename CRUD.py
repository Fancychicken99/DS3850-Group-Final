# ============================================================
# DS3850 — Group Project - CRUD.py
# Name: Brody Mensonides
# Section: 001
# Date: 04/29/2026
# ============================================================

from Database import getDBConnection


# TEAMS CRUD


def getAllTeams():
    # Return all teams from the database
    conn = getDBConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nba_teams ORDER BY name")
    teams = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return teams


def addTeam(name, city, conference, division="", coach="", owner="", budget=0.0):
    # Create a new team
    conn = getDBConnection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO teams (name, city, conference, division, coach, owner, budget)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (name, city, conference, division, coach, owner, budget),
    )
    conn.commit()
    newID = cursor.lastrowid
    conn.close()
    return newID


def updateTeam(teamID, name, city, conference, division, coach, owner, budget):
    # Update an existing team
    conn = getDBConnection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE teams 
        SET name=?, city=?, conference=?, division=?, coach=?, owner=?, budget=?
        WHERE id=?
    """,
        (name, city, conference, division, coach, owner, budget, teamID),
    )
    conn.commit()
    conn.close()


def deleteTeam(teamID):
    # Delete a team (players will also be deleted)
    conn = getDBConnection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM nba_teams WHERE id=?", (teamID,))
    conn.commit()
    conn.close()


# PLAYERS CRUD


def getPlayersByTeam(teamID):
    # Get all players belonging to a specific team
    conn = getDBConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nba_players WHERE team_id = ? ORDER BY name", (teamID,))
    players = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return players


def addPlayer(
    teamID,
    name,
    number=None,
    salary=0.0,
    injuryStatus="N",
    position="",
    pts=0.0,
    reb=0.0,
    ast=0.0,
):
    # Create a new player
    conn = getDBConnection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO players 
        (team_id, name, number, salary, injury_status, position, pts, reb, ast)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (teamID, name, number, salary, injuryStatus, position, pts, reb, ast),
    )
    conn.commit()
    conn.close()


def updatePlayer(playerID, name, number, salary, injuryStatus, position, pts, reb, ast):
    # Update an existing player
    conn = getDBConnection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE players 
        SET name=?, number=?, salary=?, injury_status=?, position=?, pts=?, reb=?, ast=?
        WHERE id=?
    """,
        (name, number, salary, injuryStatus, position, pts, reb, ast, playerID),
    )
    conn.commit()
    conn.close()


def deletePlayer(playerID):
    # Delete a single player
    conn = getDBConnection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM nba_players WHERE id=?", (playerID,))
    conn.commit()
    conn.close()
