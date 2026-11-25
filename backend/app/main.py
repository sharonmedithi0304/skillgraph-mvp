import os
import json
import shutil
import secrets
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.database import get_db, init_db
from app.services.seed import seed_demo_data, hash_password, verify_password
from app.services.taxonomy import CANONICAL_SKILLS, ROLE_PROFILES, PRACTICAL_ASSESSMENTS
from app.services.analyzer import (
    analyze_github_repo,
    analyze_zip_archive,
    analyze_pdf_document,
    recalculate_user_profile,
)

app = FastAPI(title="SkillGraph Evidence-Based Skill Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ACTIVE_SESSIONS = {}

@app.on_event("startup")
def startup_event():
    init_db()
    seed_demo_data()

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "").strip()
    user_id = ACTIVE_SESSIONS.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired. Please sign in again.")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(user)

class RegisterReq(BaseModel):
    name: str
    email: str
    password: str
    role: str = "student"
    education: str = "B.Tech Computer Science"
    institution: str = "Kaizen Institute of Technology"
    target_role: str = "Backend Developer"

class LoginReq(BaseModel):
    email: str
    password: str

class ProfileUpdateReq(BaseModel):
    name: str
    education: str
    institution: str
    target_role: str
    faculty_consent: bool

class GitHubSubmitReq(BaseModel):
    repo_url: str
    consent_confirmed: bool

class ClaimSkillReq(BaseModel):
    skill_name: str
    notes: Optional[str] = ""

class AssessmentSubmitReq(BaseModel):
    assessment_id: str
    submitted_code: str

class RoadmapStatusReq(BaseModel):
    status: str

class MentorFeedbackReq(BaseModel):
    student_id: int
    evidence_title: str
    comment: str
    endorsement_tag: str

@app.post("/api/auth/register")
def register(req: RegisterReq):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = ?", (req.email.lower().strip(),))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email is already registered.")
    now = datetime.utcnow().isoformat() + "Z"
    cur.execute('''
        INSERT INTO users (name, email, password_hash, role, education, institution, target_role, faculty_consent, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        req.name.strip(),
        req.email.lower().strip(),
        hash_password(req.password),
        req.role,
        req.education.strip(),
        req.institution.strip(),
        req.target_role,
        1,
        now
    ))
    user_id = cur.lastrowid
    recalculate_user_profile(conn, user_id, "Account created")
    conn.commit()
    conn.close()
    token = secrets.token_urlsafe(24)
    ACTIVE_SESSIONS[token] = user_id
    return {"token": token, "user_id": user_id}

@app.post("/api/auth/login")
def login(req: LoginReq):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (req.email.lower().strip(),))
    row = cur.fetchone()
    conn.close()
    if not row or not verify_password(req.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    token = secrets.token_urlsafe(24)
    ACTIVE_SESSIONS[token] = row["id"]
    user_dict = dict(row)
    user_dict.pop("password_hash", None)
    return {"token": token, "user": user_dict}

@app.post("/api/auth/logout")
def logout(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip()
        ACTIVE_SESSIONS.pop(token, None)
    return {"status": "logged_out"}

@app.put("/api/user/profile")
def update_user_profile(req: ProfileUpdateReq, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        UPDATE users
        SET name = ?, education = ?, institution = ?, target_role = ?, faculty_consent = ?
        WHERE id = ?
    ''', (req.name.strip(), req.education.strip(), req.institution.strip(), req.target_role, 1 if req.faculty_consent else 0, user["id"]))
    recalculate_user_profile(conn, user["id"], f"Target role updated to {req.target_role}")
    conn.commit()
    conn.close()
    return {"status": "updated"}

@app.get("/api/student/overview")
def get_student_overview(authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    user.pop("password_hash", None)
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM evidence WHERE user_id = ? ORDER BY created_at DESC", (user["id"],))
    evidence = []
    for r in cur.fetchall():
        d = dict(r)
        d["extracted_signals"] = json.loads(d["extracted_signals"] or "{}")
        d["detected_skills"] = json.loads(d["detected_skills"] or "{}")
        evidence.append(d)

    cur.execute("SELECT * FROM skill_evaluations WHERE user_id = ? ORDER BY proficiency_level DESC, confidence_score DESC", (user["id"],))
    skills = []
    for r in cur.fetchall():
        d = dict(r)
        d["supporting_evidence"] = json.loads(d["supporting_evidence"] or "[]")
        skills.append(d)

    cur.execute("SELECT * FROM roadmap_tasks WHERE user_id = ? ORDER BY CASE priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 ELSE 3 END", (user["id"],))
    roadmap = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT * FROM evaluation_history WHERE user_id = ? ORDER BY recorded_at DESC LIMIT 20", (user["id"],))
    history = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT * FROM assessments WHERE user_id = ? ORDER BY created_at DESC", (user["id"],))
    assessments = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT * FROM mentor_feedback WHERE student_id = ? ORDER BY created_at DESC", (user["id"],))
    feedback = [dict(r) for r in cur.fetchall()]

    conn.close()

    target_role = user.get("target_role", "Backend Developer")
    role_spec = ROLE_PROFILES.get(target_role, ROLE_PROFILES["Backend Developer"])
    skill_map = {s["skill_name"]: s for s in skills}

    weighted_match_sum = 0.0
    verified_weight_sum = 0.0
    total_weight = sum(r["importance"] for r in role_spec["requirements"])
    gap_analysis = []

    for req in role_spec["requirements"]:
        s_name = req["skill"]
        req_lvl = req["required_level"]
        imp = req["importance"]
        ev = skill_map.get(s_name, {
            "proficiency_level": 0,
            "evidence_status": "missing",
            "confidence_score": 10,
            "explanation": "No evidence submitted yet.",
            "supporting_evidence": []
        })
        cur_lvl = ev["proficiency_level"]
        ratio = min(1.0, cur_lvl / max(req_lvl, 1))
        weighted_match_sum += ratio * imp

        if ev["evidence_status"] in ("project-supported", "assessment-validated"):
            verified_weight_sum += imp

        gap_delta = max(0, req_lvl - cur_lvl)
        if gap_delta == 0 and ev["evidence_status"] in ("project-supported", "assessment-validated"):
            classification = "Met & Verified"
        elif cur_lvl > 0 and gap_delta > 0:
            classification = "Partially Developed"
        else:
            classification = "Lacking Evidence"

        severity = round(gap_delta * imp * 100, 1)
        gap_analysis.append({
            "skill_name": s_name,
            "criticality": req["criticality"],
            "importance_pct": int(round(imp * 100)),
            "required_level": req_lvl,
            "current_level": cur_lvl,
            "gap_delta": gap_delta,
            "severity_score": severity,
            "evidence_status": ev["evidence_status"],
            "confidence_score": ev["confidence_score"],
            "classification": classification,
            "explanation": ev["explanation"],
            "supporting_evidence": ev["supporting_evidence"]
        })

    gap_analysis.sort(key=lambda x: (-x["severity_score"], -x["importance_pct"]))
    role_match_score = int(round((weighted_match_sum / max(total_weight, 0.01)) * 100))
    evidence_coverage_score = int(round((verified_weight_sum / max(total_weight, 0.01)) * 100))

    return {
        "user": user,
        "evidence": evidence,
        "skills": skills,
        "role_profile": {
            "role_name": target_role,
            "description": role_spec["description"],
            "role_match_score": role_match_score,
            "evidence_coverage_score": evidence_coverage_score,
            "available_roles": list(ROLE_PROFILES.keys())
        },
        "gap_analysis": gap_analysis,
        "roadmap": roadmap,
        "history": history,
        "assessments": assessments,
        "available_assessments": PRACTICAL_ASSESSMENTS,
        "mentor_feedback": feedback,
        "taxonomy_skills": list(CANONICAL_SKILLS.keys())
    }

@app.post("/api/evidence/github")
def submit_github_evidence(req: GitHubSubmitReq, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    if not req.consent_confirmed:
        raise HTTPException(status_code=400, detail="Explicit student consent is required for read-only repository inspection.")
    try:
        result = analyze_github_repo(req.repo_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Repository analysis failed: {str(e)}")

    conn = get_db()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat() + "Z"
    cur.execute('''
        INSERT INTO evidence (user_id, source_type, title, reference_uri, consent_confirmed, status, summary, extracted_signals, detected_skills, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user["id"], "github", result["title"], req.repo_url.strip(), 1, "analyzed",
        result["summary"], json.dumps(result["extracted_signals"]), json.dumps(result["detected_skills"]), now
    ))
    recalculate_user_profile(conn, user["id"], f"Analyzed {result['title']}")
    conn.commit()
    conn.close()
    return {"status": "analyzed", "result": result}

@app.post("/api/evidence/upload")
async def upload_file_evidence(
    file: UploadFile = File(...),
    source_kind: str = Form("zip"),
    authorization: Optional[str] = Header(None)
):
    user = get_current_user(authorization)
    filename = os.path.basename(file.filename or "upload.bin")
    ext = os.path.splitext(filename)[1].lower()
    if ext not in (".zip", ".pdf"):
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload a .ZIP project archive or .PDF documentation.")

    safe_path = os.path.join(UPLOAD_DIR, f"u{user['id']}_{secrets.token_hex(6)}_{filename}")
    with open(safe_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        if ext == ".zip":
            result = analyze_zip_archive(safe_path, filename)
            s_type = "zip"
        else:
            result = analyze_pdf_document(safe_path, filename)
            s_type = "pdf"
    except ValueError as e:
        if os.path.exists(safe_path):
            os.remove(safe_path)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if os.path.exists(safe_path):
            os.remove(safe_path)
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

    conn = get_db()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat() + "Z"
    cur.execute('''
        INSERT INTO evidence (user_id, source_type, title, reference_uri, consent_confirmed, status, summary, extracted_signals, detected_skills, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user["id"], s_type, result["title"], filename, 1, "analyzed",
        result["summary"], json.dumps(result["extracted_signals"]), json.dumps(result["detected_skills"]), now
    ))
    recalculate_user_profile(conn, user["id"], f"Uploaded {result['title']}")
    conn.commit()
    conn.close()
    return {"status": "analyzed", "result": result}

@app.post("/api/evidence/claim")
def add_claimed_skill(req: ClaimSkillReq, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    if req.skill_name not in CANONICAL_SKILLS:
        raise HTTPException(status_code=400, detail="Skill not found in canonical taxonomy.")
    conn = get_db()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat() + "Z"
    detected = {
        req.skill_name: {
            "signal_count": 1,
            "matched_keywords": ["self-declared"],
            "artifacts": ["Student Skill Declaration"],
            "buckets": ["claimed"]
        }
    }
    cur.execute('''
        INSERT INTO evidence (user_id, source_type, title, reference_uri, consent_confirmed, status, summary, extracted_signals, detected_skills, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user["id"],
        "claimed",
        f"Self-Declared Skill: {req.skill_name}",
        req.notes or "Self-declaration",
        1,
        "analyzed",
        f"Claimed {req.skill_name}. Marked as unverified until linked repository or practical assessment proof is provided.",
        json.dumps({"notes": req.notes}),
        json.dumps(detected),
        now
    ))
    recalculate_user_profile(conn, user["id"], f"Added self-declared skill: {req.skill_name}")
    conn.commit()
    conn.close()
    return {"status": "claimed"}

@app.delete("/api/evidence/{evidence_id}")
def delete_evidence(evidence_id: int, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT title FROM evidence WHERE id = ? AND user_id = ?", (evidence_id, user["id"]))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Evidence item not found.")
    title = row["title"]
    cur.execute("DELETE FROM evidence WHERE id = ? AND user_id = ?", (evidence_id, user["id"]))
    recalculate_user_profile(conn, user["id"], f"Removed evidence: {title}")
    conn.commit()
    conn.close()
    return {"status": "deleted"}

@app.post("/api/assessments/submit")
def submit_assessment(req: AssessmentSubmitReq, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    spec = next((a for a in PRACTICAL_ASSESSMENTS if a["id"] == req.assessment_id), None)
    if not spec:
        raise HTTPException(status_code=404, detail="Assessment challenge not found.")

    code_lower = req.submitted_code.lower()
    if len(code_lower.strip()) < 25:
        raise HTTPException(status_code=400, detail="Submission is too brief to evaluate against the rubric.")

    matched = [kw for kw in spec["rubric_keywords"] if kw in code_lower]
    raw_ratio = len(matched) / max(len(spec["rubric_keywords"]), 1)
    score = int(round(40 + raw_ratio * 60)) if matched else 30
    passed = score >= 65

    feedback = (
        f"{'PASSED' if passed else 'NEEDS REVISION'} ({score}/100): Matched {len(matched)}/{len(spec['rubric_keywords'])} rubric indicators "
        f"({', '.join(matched) if matched else 'none'}). "
        + ("Skill upgraded to Assessment-Validated." if passed else "Review the rubric criteria and resubmit.")
    )

    conn = get_db()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat() + "Z"
    cur.execute('''
        INSERT INTO assessments (user_id, skill_name, score, max_score, feedback, submitted_code, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user["id"], spec["skill_name"], score, 100, feedback, req.submitted_code, now))

    recalculate_user_profile(conn, user["id"], f"Practical Assessment ({spec['skill_name']}): {score}/100")
    conn.commit()
    conn.close()
    return {"score": score, "passed": passed, "feedback": feedback}

@app.patch("/api/roadmap/{task_id}")
def update_roadmap_status(task_id: int, req: RoadmapStatusReq, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    if req.status not in ("pending", "in_progress", "completed"):
        raise HTTPException(status_code=400, detail="Invalid task status.")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE roadmap_tasks SET status = ? WHERE id = ? AND user_id = ?", (req.status, task_id, user["id"]))
    conn.commit()
    conn.close()
    return {"status": "updated"}

@app.get("/api/faculty/insights")
def get_faculty_insights(authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, education, institution, target_role FROM users WHERE role = 'student' AND faculty_consent = 1")
    students = [dict(r) for r in cur.fetchall()]

    cohort_profiles = []
    skill_totals = {s: [] for s in CANONICAL_SKILLS}

    for st in students:
        cur.execute("SELECT * FROM skill_evaluations WHERE user_id = ?", (st["id"],))
        evals = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT id, source_type, title, summary, created_at FROM evidence WHERE user_id = ?", (st["id"],))
        evs = [dict(r) for r in cur.fetchall()]

        verified_count = sum(1 for e in evals if e["evidence_status"] in ("project-supported", "assessment-validated"))
        avg_prof = round(sum(e["proficiency_level"] for e in evals) / max(len(evals), 1), 2)
        for e in evals:
            if e["skill_name"] in skill_totals:
                skill_totals[e["skill_name"]].append(e["proficiency_level"])

        cohort_profiles.append({
            **st,
            "verified_skills_count": verified_count,
            "average_proficiency": avg_prof,
            "skills": evals,
            "evidence": evs
        })

    aggregate_gaps = []
    for s_name, levels in skill_totals.items():
        avg = round(sum(levels) / max(len(levels), 1), 2)
        aggregate_gaps.append({
            "skill_name": s_name,
            "cohort_avg_level": avg,
            "benchmark_level": 3.0,
            "cohort_gap": round(max(0.0, 3.0 - avg), 2)
        })
    aggregate_gaps.sort(key=lambda x: -x["cohort_gap"])
    conn.close()
    return {
        "viewer": user["name"],
        "students": cohort_profiles,
        "aggregate_gaps": aggregate_gaps
    }

@app.post("/api/faculty/feedback")
def post_mentor_feedback(req: MentorFeedbackReq, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    conn = get_db()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat() + "Z"
    cur.execute('''
        INSERT INTO mentor_feedback (student_id, mentor_name, evidence_title, comment, endorsement_tag, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (req.student_id, user["name"], req.evidence_title, req.comment.strip(), req.endorsement_tag.strip(), now))
    conn.commit()
    conn.close()
    return {"status": "submitted"}
