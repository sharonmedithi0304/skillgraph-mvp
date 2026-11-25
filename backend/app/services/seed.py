import hashlib
import os
import json
from datetime import datetime, timedelta
from app.database import get_db
from app.services.analyzer import recalculate_user_profile

def hash_password(password: str, salt: str = None) -> str:
    if not salt:
        salt = os.urandom(16).hex()
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${dk.hex()}"

def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _ = stored.split("$", 1)
        return hash_password(password, salt) == stored
    except Exception:
        return False

def seed_demo_data():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM users")
    if cur.fetchone()["cnt"] > 0:
        conn.close()
        return

    now = datetime.utcnow()
    t1 = (now - timedelta(days=5)).isoformat() + "Z"
    t2 = (now - timedelta(days=2)).isoformat() + "Z"
    t3 = (now - timedelta(hours=6)).isoformat() + "Z"

    cur.execute('''
        INSERT INTO users (name, email, password_hash, role, education, institution, target_role, faculty_consent, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        "Alex Rivera (Judge Demo)",
        "alex.rivera@kaizen.edu",
        hash_password("Kaizen2026!"),
        "student",
        "B.Tech Computer Science (Final Year)",
        "Kaizen Institute of Technology",
        "Backend Developer",
        1,
        t1
    ))
    alex_id = cur.lastrowid

    cur.execute('''
        INSERT INTO users (name, email, password_hash, role, education, institution, target_role, faculty_consent, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        "Priya Nair",
        "priya.nair@kaizen.edu",
        hash_password("Student2026!"),
        "student",
        "B.Tech Information Technology (3rd Year)",
        "Kaizen Institute of Technology",
        "Backend Developer",
        1,
        t1
    ))
    priya_id = cur.lastrowid

    cur.execute('''
        INSERT INTO users (name, email, password_hash, role, education, institution, target_role, faculty_consent, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        "Dr. Arvind Mehta",
        "dr.mehta@kaizen.edu",
        hash_password("Mentor2026!"),
        "faculty",
        "Professor & Placement Lead, Dept. of CSE",
        "Kaizen Institute of Technology",
        "Backend Developer",
        1,
        t1
    ))

    ev_items = [
        (
            alex_id,
            "github",
            "GitHub: alex-dev/fastapi-inventory-core",
            "https://github.com/tiangolo/fastapi",
            1,
            "analyzed",
            "Inspected FastAPI REST service with Pydantic schemas, SQLAlchemy models, JWT auth middleware, and modular routers.",
            json.dumps({"languages": ["Python", "SQL"], "total_files": 24, "inspected_files": ["app/main.py", "app/routers/items.py", "app/models.py", "requirements.txt", "README.md"]}),
            json.dumps({
                "Python": {"signal_count": 7, "matched_keywords": ["python", "pydantic", "asyncio", "requirements.txt", "venv"], "artifacts": ["app/main.py", "requirements.txt"], "buckets": ["source_code", "dependencies"]},
                "REST APIs & Backend Frameworks": {"signal_count": 8, "matched_keywords": ["fastapi", "router", "endpoint", "uvicorn", "middleware", "rest"], "artifacts": ["app/main.py", "app/routers/items.py"], "buckets": ["source_code", "dependencies"]},
                "SQL & Relational Databases": {"signal_count": 6, "matched_keywords": ["sqlalchemy", "postgresql", "schema", "foreign key", "orm"], "artifacts": ["app/models.py"], "buckets": ["source_code", "dependencies"]},
                "Authentication & Security": {"signal_count": 4, "matched_keywords": ["jwt", "bcrypt", "token", "authorization"], "artifacts": ["app/auth.py"], "buckets": ["source_code"]},
                "Git & Collaborative Workflow": {"signal_count": 3, "matched_keywords": ["readme", "gitignore", "license"], "artifacts": ["README.md"], "buckets": ["documentation", "file_structure"]}
            }),
            t1
        ),
        (
            alex_id,
            "pdf",
            "Architecture & Report PDF: Distributed_Order_Engine_Design.pdf",
            "uploads/Distributed_Order_Engine_Design.pdf",
            1,
            "analyzed",
            "Parsed 8-page system architecture spec detailing Redis caching, rate limiting, and PostgreSQL read replicas.",
            json.dumps({"page_count": 8, "character_count": 14200}),
            json.dumps({
                "System Design & Caching": {"signal_count": 4, "matched_keywords": ["redis", "rate limit", "architecture", "caching"], "artifacts": ["Distributed_Order_Engine_Design.pdf"], "buckets": ["documentation"]},
                "SQL & Relational Databases": {"signal_count": 3, "matched_keywords": ["postgresql", "schema", "migration"], "artifacts": ["Distributed_Order_Engine_Design.pdf"], "buckets": ["documentation"]}
            }),
            t2
        ),
        (
            alex_id,
            "claimed",
            "Self-Declared Skill: Docker & Cloud Deployment",
            "self-declaration",
            1,
            "analyzed",
            "Student listed Docker & Cloud Deployment on profile; awaiting Dockerfile or deployment evidence.",
            json.dumps({"source": "Student Profile Declaration"}),
            json.dumps({
                "Docker & Cloud Deployment": {"signal_count": 1, "matched_keywords": ["docker"], "artifacts": ["Self-Declared Profile"], "buckets": ["claimed"]}
            }),
            t2
        )
    ]

    for row in ev_items:
        cur.execute('''
            INSERT INTO evidence (user_id, source_type, title, reference_uri, consent_confirmed, status, summary, extracted_signals, detected_skills, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', row)

    recalculate_user_profile(conn, alex_id, "Initial repository & architecture PDF ingestion")

    cur.execute('''
        INSERT INTO assessments (user_id, skill_name, score, max_score, feedback, submitted_code, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        alex_id,
        "SQL & Relational Databases",
        92,
        100,
        "Passed all 3 rubric criteria: eliminated N+1 query with explicit JOIN + GROUP BY and added B-Tree index.",
        "CREATE INDEX idx_evidence_user ON evidence(user_id); SELECT u.name, COUNT(e.id) FROM users u JOIN evidence e ON u.id = e.user_id GROUP BY u.id;",
        t3
    ))

    recalculate_user_profile(conn, alex_id, "Completed Practical SQL Optimization Assessment (92/100)")

    cur.execute('''
        INSERT INTO mentor_feedback (student_id, mentor_name, evidence_title, comment, endorsement_tag, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        alex_id,
        "Dr. Arvind Mehta (Placement & Backend Mentor)",
        "GitHub: alex-dev/fastapi-inventory-core",
        "Strong API modularization and SQL indexing proof. Add a multi-stage Dockerfile and pytest suite before final placement interviews to close your remaining Backend Developer gaps.",
        "Placement Ready — Shortlist Track",
        t3
    ))

    cur.execute('''
        INSERT INTO evidence (user_id, source_type, title, reference_uri, consent_confirmed, status, summary, extracted_signals, detected_skills, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        priya_id,
        "github",
        "GitHub: priya-codes/student-portal-api",
        "https://github.com/pallets/flask",
        1,
        "analyzed",
        "Inspected Flask API project with Python endpoints and basic SQLite persistence.",
        json.dumps({"languages": ["Python"], "total_files": 11}),
        json.dumps({
            "Python": {"signal_count": 5, "matched_keywords": ["python", "requirements.txt"], "artifacts": ["app.py"], "buckets": ["source_code"]},
            "REST APIs & Backend Frameworks": {"signal_count": 4, "matched_keywords": ["flask", "endpoint", "api"], "artifacts": ["app.py"], "buckets": ["source_code"]}
        }),
        t2
    ))
    recalculate_user_profile(conn, priya_id, "Initial repository sync")

    conn.commit()
    conn.close()
