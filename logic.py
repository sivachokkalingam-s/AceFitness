import sqlite3
from datetime import datetime

DB_NAME = "aceest_fitness.db"

PROGRAMS = {
    "Fat Loss (FL)": {"factor": 22},
    "Muscle Gain (MG)": {"factor": 35},
    "Beginner (BG)": {"factor": 26}
}


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            weight REAL,
            program TEXT,
            calories INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            week TEXT,
            adherence INTEGER
        )
    """)

    conn.commit()
    conn.close()


def save_client(name, age, weight, program):
    if not name or not program:
        raise ValueError("Name and Program required")

    calories = int(weight * PROGRAMS[program]["factor"])

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO clients
        (name, age, weight, program, calories)
        VALUES (?, ?, ?, ?, ?)
    """, (name, age, weight, program, calories))

    conn.commit()
    conn.close()

    return calories


def load_client(name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT * FROM clients WHERE name=?", (name,))
    row = cur.fetchone()

    conn.close()

    if not row:
        return None

    _, name, age, weight, program, calories = row

    return {
        "name": name,
        "age": age,
        "weight": weight,
        "program": program,
        "calories": calories
    }


def save_progress(name, adherence):
    week = datetime.now().strftime("Week %U - %Y")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO progress (client_name, week, adherence)
        VALUES (?, ?, ?)
    """, (name, week, adherence))

    conn.commit()
    conn.close()