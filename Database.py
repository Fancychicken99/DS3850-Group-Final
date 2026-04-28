# database.py
# This file handles database connection, table creation, and seed data

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
    cursor.execute('''
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
    ''')

    # Players Table - Secondary table with Foreign Key to teams
    cursor.execute('''
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
    ''')

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
        ("Los Angeles Lakers", "Los Angeles", "Western", "Pacific", "JJ Redick", "Jeanie Buss", 145.8),
        ("Golden State Warriors", "San Francisco", "Western", "Pacific", "Steve Kerr", "Joe Lacob", 132.4),
        ("Boston Celtics", "Boston", "Eastern", "Atlantic", "Joe Mazzulla", "Wyc Grousbeck", 138.9),
        ("New York Knicks", "New York", "Eastern", "Atlantic", "Tom Thibodeau", "James Dolan", 125.6),
        ("Miami Heat", "Miami", "Eastern", "Southeast", "Erik Spoelstra", "Micky Arison", 118.3),
        ("Dallas Mavericks", "Dallas", "Western", "Southwest", "Jason Kidd", "Mark Cuban", 140.2),
    ]

    cursor.executemany('''
        INSERT INTO nba_teams (name, city, conference, division, coach, owner, budget)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', teams)

    # Get team IDs to assign players correctly
    cursor.execute("SELECT id, name FROM nba_teams")
    teamMap = {name: tid for tid, name in cursor.fetchall()}

    # Insert sample Players using funny names
    players = [
        (teamMap["Los Angeles Lakers"], "Jangledangle Smith", 23, 48.7, 'N', 'SF', 25.4, 7.2, 8.1),
        (teamMap["Los Angeles Lakers"], "Clarence Almond", 11, 12.5, 'N', 'PG', 14.8, 3.1, 6.4),
        (teamMap["Los Angeles Lakers"], "Yamzy Sparkles", 3, 8.9, 'Y', 'SG', 11.2, 2.8, 3.9),
        (teamMap["Golden State Warriors"], "Nesquick Rodriguez", 30, 35.2, 'N', 'PG', 28.5, 5.1, 9.3),
        (teamMap["Golden State Warriors"], "Albert Sweatstein", 5, 22.1, 'N', 'SF', 19.7, 6.4, 4.2),
        (teamMap["Boston Celtics"], "Randilyn Becktwain", 7, 18.4, 'N', 'PF', 16.3, 8.9, 2.1),
        (teamMap["Boston Celtics"], "Choopie Mcdoogie", 42, 9.8, 'N', 'C', 12.5, 10.2, 1.8),
        (teamMap["New York Knicks"], "Fresno Squeeps", 8, 25.6, 'N', 'SG', 22.1, 4.3, 5.7),
        (teamMap["Miami Heat"], "Jefranklin Maggert", 22, 14.7, 'Y', 'PF', 13.9, 7.1, 3.4),
        (teamMap["Miami Heat"], "Jacubahn Hasbro", 45, 6.3, 'N', 'C', 8.4, 9.5, 1.2),
        (teamMap["Dallas Mavericks"], "JaQuantavious Brown", 77, 31.2, 'N', 'SF', 27.8, 6.8, 4.9),
        (teamMap["Dallas Mavericks"], "Alexington Smurthens", 12, 16.8, 'N', 'PG', 15.2, 3.9, 7.1),
        (teamMap["Los Angeles Lakers"], "Carloftus Hatzmazotray", 9, 7.5, 'N', 'SG', 10.1, 2.5, 2.8),
        (teamMap["Golden State Warriors"], "Dexter Lester", 4, 19.3, 'N', 'PF', 17.6, 8.2, 2.9),
        (teamMap["Boston Celtics"], "Mooratum Bindiferus", 33, 11.2, 'N', 'C', 9.8, 11.4, 1.5),
        (teamMap["New York Knicks"], "Crusty Pete", 6, 24.1, 'N', 'SG', 21.3, 4.7, 6.2),
        (teamMap["Miami Heat"], "Spangy Nutballs", 13, 5.9, 'Y', 'PG', 7.4, 2.1, 4.8),
        (teamMap["Dallas Mavericks"], "Pablo Seasame", 21, 14.2, 'N', 'SF', 13.5, 5.6, 3.7),
    ]

    cursor.executemany('''
        INSERT INTO nba_players (team_id, name, number, salary, injury_status, position, pts, reb, ast)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', players)

    conn.commit()
    conn.close()
    print("Seed data loaded successfully.")