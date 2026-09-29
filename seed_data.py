import sqlite3
from datetime import datetime, timedelta
from database import init_db

init_db()

conn = sqlite3.connect("cognitive.db", timeout=10)
c = conn.cursor()

def add_patient_raw(name):
    c.execute("INSERT INTO patients (name) VALUES (?)", (name,))
    conn.commit()
    return c.lastrowid

def seed_patient(name, memory_scores, memory_difficulty, attention_scores, attention_difficulty, days_ago_start=20):
    patient_id = add_patient_raw(name)
    base_date = datetime.now() - timedelta(days=days_ago_start)

    for i, (score, diff) in enumerate(zip(memory_scores, memory_difficulty)):
        session_date = base_date + timedelta(days=i * 2)
        correct = int(score / 10)
        wrong = 10 - correct
        c.execute("""
            INSERT INTO sessions (patient_id, game_type, timestamp, difficulty_level, correct_count, wrong_count, domain, score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, "memory_recall", session_date.isoformat(), diff, correct, wrong, "memory", score))

    for i, (score, diff) in enumerate(zip(attention_scores, attention_difficulty)):
        session_date = base_date + timedelta(days=i * 2, hours=2)
        correct = int(score / 10)
        wrong = 10 - correct
        c.execute("""
            INSERT INTO sessions (patient_id, game_type, timestamp, difficulty_level, correct_count, wrong_count, domain, score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, "attention_focus", session_date.isoformat(), diff, correct, wrong, "attention", score))

    conn.commit()
    return patient_id

# Patient 1: Memory declining, attention stable
seed_patient(
    "Mrs. Rina Devi",
    memory_scores=[78, 82, 80, 85, 81, 79, 83, 68, 60, 52],
    memory_difficulty=[2, 2, 3, 3, 3, 3, 3, 2, 2, 1],
    attention_scores=[85, 88, 82, 90, 86, 89, 84, 87, 91, 88],
    attention_difficulty=[2, 2, 3, 3, 3, 3, 3, 3, 4, 4],
)

# Patient 2: Both domains stable/healthy
seed_patient(
    "Mr. Tenzin Norbu",
    memory_scores=[75, 78, 80, 77, 82, 79, 81, 80, 83, 82],
    memory_difficulty=[2, 2, 3, 3, 3, 3, 3, 3, 3, 3],
    attention_scores=[80, 82, 85, 83, 81, 86, 84, 87, 85, 88],
    attention_difficulty=[2, 3, 3, 3, 3, 3, 4, 4, 4, 4],
)

# Patient 3: Both domains declining
seed_patient(
    "Mrs. Lily Kharmawphlang",
    memory_scores=[70, 72, 68, 65, 60, 55, 50, 48, 42, 38],
    memory_difficulty=[2, 2, 2, 2, 1, 1, 1, 1, 1, 1],
    attention_scores=[75, 73, 70, 68, 65, 62, 58, 55, 50, 48],
    attention_difficulty=[2, 2, 2, 2, 2, 1, 1, 1, 1, 1],
)

# Default reminders for each patient
default_reminders = [
    ("Take morning medication", "8:00 AM"),
    ("Physiotherapy session", "11:00 AM"),
    ("Take afternoon medication", "2:00 PM"),
    ("Evening walk with caregiver", "5:30 PM"),
]

c.execute("SELECT id FROM patients")
all_patient_ids = [row[0] for row in c.fetchall()]

for pid in all_patient_ids:
    for title, time_of_day in default_reminders:
        c.execute("""
            INSERT INTO reminders (patient_id, title, time_of_day, is_done, date_created)
            VALUES (?, ?, ?, 0, ?)
        """, (pid, title, time_of_day, datetime.now().isoformat()))

conn.commit()
conn.close()

print(f"Seeded {len(all_patient_ids)} patients with sessions and reminders.")