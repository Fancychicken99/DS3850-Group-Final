# ============================================================
# DS3850 — Group Project - Database.py
# Name: Brody Mensonides
# Section: 001
# Date: 04/29/2026
# ============================================================

import sqlite3

DBNAME = "nba_league.db"


def getDBConnection():
    # Create and return a new database connection
    # row_factory allows us to access columns by name (like a dictionary)
    conn = sqlite3.connect(DBNAME)
    conn.row_factory = sqlite3.Row
    return conn


def createTables():
    # Create the two required tables with foreign key relationship
    conn = getDBConnection()
    cursor = conn.cursor()

    # Teams Table - Primary table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nba_teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            conference TEXT NOT NULL,
            division TEXT,
            coach TEXT,
            owner TEXT,
            budget REAL DEFAULT 0.0
        )
    """
    )

    # Players Table - Secondary table with Foreign Key to teams
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nba_players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            number INTEGER,
            salary REAL DEFAULT 0.0,
            injury_status TEXT DEFAULT 'N',
            position TEXT,
            pts REAL DEFAULT 0.0,
            reb REAL DEFAULT 0.0,
            ast REAL DEFAULT 0.0,
            FOREIGN KEY (team_id) REFERENCES nba_teams(id) ON DELETE CASCADE
        )
    """
    )

    conn.commit()
    conn.close()
    print("Tables created successfully.")


def seedData():
    # Load sample data only on first launch (when tables are empty)
    conn = getDBConnection()
    cursor = conn.cursor()

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM nba_teams")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    print("Seeding initial data...")

    # Insert sample Teams
    teams = [
        (
            "Los Angeles Lakers",
            "Los Angeles",
            "Western",
            "Pacific",
            "JJ Redick",
            "Jeanie Buss",
            145.8,
        ),
        (
            "Golden State Warriors",
            "San Francisco",
            "Western",
            "Pacific",
            "Steve Kerr",
            "Joe Lacob",
            132.4,
        ),
        (
            "Boston Celtics",
            "Boston",
            "Eastern",
            "Atlantic",
            "Joe Mazzulla",
            "Wyc Grousbeck",
            138.9,
        ),
        (
            "New York Knicks",
            "New York",
            "Eastern",
            "Atlantic",
            "Tom Thibodeau",
            "James Dolan",
            125.6,
        ),
        (
            "Miami Heat",
            "Miami",
            "Eastern",
            "Southeast",
            "Erik Spoelstra",
            "Micky Arison",
            118.3,
        ),
        (
            "Dallas Mavericks",
            "Dallas",
            "Western",
            "Southwest",
            "Jason Kidd",
            "Mark Cuban",
            140.2,
        ),
        (
            "Seattle Supersonics",
            "Seattle",
            "Western",
            "Northwest",
            "John Weaver",
            "Susan Wells",
            110.0,
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO nba_teams (name, city, conference, division, coach, owner, budget)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        teams,
    )

    # Get team IDs to assign players correctly
    cursor.execute("SELECT id, name FROM nba_teams")
    teamMap = {name: tid for tid, name in cursor.fetchall()}

    # Insert sample Players using funny names
    players = [
        (
            teamMap["Los Angeles Lakers"],
            "Jangledangle Smith",
            23,
            48.7,
            "N",
            "SF",
            28.5,
            9.2,
            10.1,
        ),
        (
            teamMap["Los Angeles Lakers"],
            "Clarence Almond",
            11,
            12.5,
            "N",
            "PG",
            22.8,
            5.1,
            12.4,
        ),
        (
            teamMap["Los Angeles Lakers"],
            "Yamzy Sparkles",
            3,
            8.9,
            "Y",
            "SG",
            18.2,
            4.8,
            6.9,
        ),
        (
            teamMap["Golden State Warriors"],
            "Phil Oldham",
            23,
            24.5,
            "N",
            "PF",
            19.0,
            8.9,
            7.1,
        ),
        (
            teamMap["Golden State Warriors"],
            "Nesquick Rodriguez",
            30,
            35.2,
            "N",
            "PG",
            31.5,
            8.1,
            11.3,
        ),
        (
            teamMap["Golden State Warriors"],
            "Albert Sweatstein",
            5,
            22.1,
            "N",
            "SF",
            27.7,
            10.4,
            8.2,
        ),
        (
            teamMap["Boston Celtics"],
            "Randilyn Becktwain",
            7,
            18.4,
            "N",
            "PF",
            26.3,
            12.9,
            6.1,
        ),
        (
            teamMap["Boston Celtics"],
            "Choopie Mcdoogie",
            42,
            9.8,
            "N",
            "C",
            20.5,
            11.2,
            4.8,
        ),
        (
            teamMap["New York Knicks"],
            "Fresno Squeeps",
            8,
            25.6,
            "N",
            "SG",
            21.1,
            6.3,
            8.7,
        ),
        (
            teamMap["Miami Heat"],
            "Jefranklin Maggert",
            22,
            14.7,
            "Y",
            "PF",
            19.9,
            8.1,
            5.4,
        ),
        (teamMap["Miami Heat"], "Jacubahn Hasbro", 45, 6.3, "N", "C", 18.4, 10.5, 4.2),
        (
            teamMap["Dallas Mavericks"],
            "JaQuantavious Brown",
            77,
            31.2,
            "N",
            "SF",
            32.8,
            10.8,
            8.9,
        ),
        (
            teamMap["Dallas Mavericks"],
            "Alexington Smurthens",
            12,
            16.8,
            "N",
            "PG",
            25.2,
            7.9,
            11.1,
        ),
        (
            teamMap["Seattle Supersonics"],
            "Awesome Eagle",
            99,
            9.5,
            "N",
            "PG",
            24.0,
            12.8,
            10.3,
        ),
        (
            teamMap["Seattle Supersonics"],
            "Brody Mensonides",
            88,
            4.3,
            "Y",
            "C",
            22.2,
            13.9,
            5.0,
        ),
        (
            teamMap["Seattle Supersonics"],
            "Brodi Remick",
            77,
            12.8,
            "N",
            "SF",
            28.5,
            8.2,
            9.6,
        ),
        (
            teamMap["Seattle Supersonics"],
            "Isaac Waycott",
            55,
            18.6,
            "N",
            "SG",
            29.3,
            7.5,
            9.1,
        ),
        (
            teamMap["Seattle Supersonics"],
            "Connor Beck",
            66,
            7.9,
            "N",
            "PF",
            26.8,
            10.7,
            7.4,
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO nba_players (team_id, name, number, salary, injury_status, position, pts, reb, ast)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        players,
    )

    conn.commit()
    conn.close()
    print("Seed data loaded successfully.")
