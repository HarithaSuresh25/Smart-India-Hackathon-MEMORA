import sqlite3
from datetime import datetime

DB_NAME = "cognitive.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            game_type TEXT,
            timestamp TEXT,
            difficulty_level INTEGER,
            correct_count INTEGER,
            wrong_count INTEGER,
            domain TEXT,
            score REAL,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            title TEXT,
            time_of_day TEXT,
            is_done INTEGER DEFAULT 0,
            date_created TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS known_people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            name TEXT,
            relationship TEXT,
            image_path TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)
    conn.commit()
    conn.close()

def add_patient(name):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("INSERT INTO patients (name) VALUES (?)", (name,))
    conn.commit()
    patient_id = c.lastrowid
    conn.close()
    return patient_id

def log_session(patient_id, game_type, difficulty_level, correct_count, wrong_count, domain, score):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("""
        INSERT INTO sessions (patient_id, game_type, timestamp, difficulty_level, correct_count, wrong_count, domain, score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (patient_id, game_type, datetime.now().isoformat(), difficulty_level, correct_count, wrong_count, domain, score))
    conn.commit()
    conn.close()

def get_sessions(patient_id, domain=None):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    if domain:
        c.execute("SELECT * FROM sessions WHERE patient_id = ? AND domain = ? ORDER BY timestamp", (patient_id, domain))
    else:
        c.execute("SELECT * FROM sessions WHERE patient_id = ? ORDER BY timestamp", (patient_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_patients():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("SELECT * FROM patients")
    rows = c.fetchall()
    conn.close()
    return rows
def add_reminder(patient_id, title, time_of_day):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("""
        INSERT INTO reminders (patient_id, title, time_of_day, is_done, date_created)
        VALUES (?, ?, ?, 0, ?)
    """, (patient_id, title, time_of_day, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_reminders(patient_id):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("SELECT * FROM reminders WHERE patient_id = ? ORDER BY time_of_day", (patient_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def mark_reminder_done(reminder_id, is_done):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("UPDATE reminders SET is_done = ? WHERE id = ?", (1 if is_done else 0, reminder_id))
    conn.commit()
    conn.close()

def add_known_person(patient_id, name, relationship, image_path):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("""
        INSERT INTO known_people (patient_id, name, relationship, image_path)
        VALUES (?, ?, ?, ?)
    """, (patient_id, name, relationship, image_path))
    conn.commit()
    conn.close()

def get_known_people(patient_id):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("SELECT * FROM known_people WHERE patient_id = ?", (patient_id,))
    rows = c.fetchall()
    conn.close()
    return rows