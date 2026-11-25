import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skillgraph.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        education TEXT DEFAULT 'B.Tech Computer Science & IT',
        institution TEXT DEFAULT 'Kaizen Institute of Technology',
        target_role TEXT DEFAULT 'Backend Developer',
        faculty_consent INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS evidence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        source_type TEXT NOT NULL,
        title TEXT NOT NULL,
        reference_uri TEXT,
        consent_confirmed INTEGER DEFAULT 1,
        status TEXT DEFAULT 'analyzed',
        summary TEXT,
        extracted_signals TEXT,
        detected_skills TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS skill_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        category TEXT NOT NULL,
        proficiency_level INTEGER DEFAULT 0,
        evidence_status TEXT DEFAULT 'claimed',
        confidence_score INTEGER DEFAULT 15,
        explanation TEXT,
        supporting_evidence TEXT,
        missing_evidence_flag INTEGER DEFAULT 0,
        updated_at TEXT NOT NULL,
        UNIQUE(user_id, skill_name),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS evaluation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        previous_level INTEGER,
        new_level INTEGER,
        previous_confidence INTEGER,
        new_confidence INTEGER,
        trigger_reason TEXT,
        recorded_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS roadmap_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        priority TEXT NOT NULL,
        title TEXT NOT NULL,
        project_activity TEXT NOT NULL,
        resource_label TEXT NOT NULL,
        resource_url TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        score INTEGER NOT NULL,
        max_score INTEGER NOT NULL,
        feedback TEXT NOT NULL,
        submitted_code TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS mentor_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        mentor_name TEXT NOT NULL,
        evidence_title TEXT,
        comment TEXT NOT NULL,
        endorsement_tag TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(student_id) REFERENCES users(id)
    );
    ''')
    conn.commit()
    conn.close()
