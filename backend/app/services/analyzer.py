import os
import json
import zipfile
from datetime import datetime
from urllib.parse import urlparse
import requests
from pypdf import PdfReader
from app.services.taxonomy import CANONICAL_SKILLS, ROLE_PROFILES, ROADMAP_TEMPLATES

MAX_ZIP_BYTES = 15 * 1024 * 1024
ALLOWED_CODE_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".sql",
    ".md", ".txt", ".json", ".yml", ".yaml", ".toml", ".sh", ".env.example"
}

def _match_text_against_taxonomy(corpus: str, source_bucket: str, artifact_name: str, detected: dict):
    lowered = corpus.lower()
    for skill_name, meta in CANONICAL_SKILLS.items():
        hits = [kw for kw in meta["keywords"] if kw in lowered]
        if hits:
            entry = detected.setdefault(skill_name, {
                "signal_count": 0,
                "matched_keywords": set(),
                "artifacts": set(),
                "buckets": set()
            })
            entry["signal_count"] += len(hits)
            entry["matched_keywords"].update(hits[:6])
            entry["artifacts"].add(artifact_name)
            entry["buckets"].add(source_bucket)

def analyze_github_repo(repo_url: str) -> dict:
    parsed = urlparse(repo_url.strip())
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        raise ValueError("Security Policy: Only public https://github.com/<owner>/<repo> URLs are permitted.")
    parts = [p for p in parsed.path.strip("/").split("/") if p]
    if len(parts) < 2:
        raise ValueError("Invalid GitHub repository URL. Expected format: https://github.com/owner/repository")

    owner, repo = parts[0], parts[1].replace(".git", "")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "SkillGraph-MVP-Analyzer"}

    repo_api = f"https://api.github.com/repos/{owner}/{repo}"
    resp = requests.get(repo_api, headers=headers, timeout=10)
    if resp.status_code == 404:
        raise ValueError(f"Repository '{owner}/{repo}' was not found or is private. SkillGraph requires read-only public access.")
    if resp.status_code == 403:
        raise ValueError("GitHub API rate limit reached. Try uploading the repository ZIP archive directly.")
    if resp.status_code != 200:
        raise ValueError(f"GitHub inspection failed with HTTP {resp.status_code}.")

    repo_meta = resp.json()
    default_branch = repo_meta.get("default_branch", "main")
    description = repo_meta.get("description") or ""
    primary_lang = repo_meta.get("language") or "Unknown"

    detected = {}
    inspected_files = []
    languages_found = {}

    lang_resp = requests.get(f"{repo_api}/languages", headers=headers, timeout=8)
    if lang_resp.status_code == 200:
        languages_found = lang_resp.json()
        _match_text_against_taxonomy(" ".join(languages_found.keys()) + " " + description, "repo_metadata", f"{owner}/{repo} metadata", detected)

    tree_resp = requests.get(f"{repo_api}/git/trees/{default_branch}?recursive=1", headers=headers, timeout=10)
    tree_paths = []
    if tree_resp.status_code == 200:
        tree_data = tree_resp.json().get("tree", [])
        tree_paths = [item["path"] for item in tree_data if item.get("type") == "blob"]
        _match_text_against_taxonomy("\n".join(tree_paths), "file_structure", "Repository file tree", detected)

    priority_names = ("readme.md", "requirements.txt", "pyproject.toml", "package.json", "dockerfile", "docker-compose.yml", "pom.xml")
    target_files = [p for p in tree_paths if p.lower().split("/")[-1] in priority_names]
    code_candidates = [
        p for p in tree_paths
        if os.path.splitext(p)[1].lower() in {".py", ".ts", ".js", ".java", ".go", ".sql"}
        and p not in target_files
    ][:8]

    for rel_path in (target_files + code_candidates)[:14]:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{rel_path}"
        raw_resp = requests.get(raw_url, headers=headers, timeout=8)
        if raw_resp.status_code == 200 and len(raw_resp.text) < 200_000:
            inspected_files.append(rel_path)
            bucket = "documentation" if rel_path.lower().endswith(".md") else (
                "dependencies" if rel_path.lower().split("/")[-1] in priority_names else "source_code"
            )
            _match_text_against_taxonomy(raw_resp.text[:25000], bucket, rel_path, detected)

    serialized_skills = {
        s_name: {
            "signal_count": info["signal_count"],
            "matched_keywords": sorted(list(info["matched_keywords"])),
            "artifacts": sorted(list(info["artifacts"]))[:5],
            "buckets": sorted(list(info["buckets"]))
        }
        for s_name, info in detected.items()
    }

    summary = (
        f"Inspected {owner}/{repo} (branch: {default_branch}, primary: {primary_lang}). "
        f"Scanned {len(tree_paths)} repo paths and {len(inspected_files)} key code/config files; "
        f"extracted {len(serialized_skills)} canonical technical skills."
    )
    return {
        "title": f"GitHub: {owner}/{repo}",
        "summary": summary,
        "extracted_signals": {
            "languages": list(languages_found.keys()) or [primary_lang],
            "total_files": len(tree_paths),
            "inspected_files": inspected_files,
            "stars": repo_meta.get("stargazers_count", 0)
        },
        "detected_skills": serialized_skills
    }

def analyze_zip_archive(file_path: str, original_filename: str) -> dict:
    if os.path.getsize(file_path) > MAX_ZIP_BYTES:
        raise ValueError("File size exceeds 15 MB security limit.")
    if not zipfile.is_zipfile(file_path):
        raise ValueError("Uploaded file is not a valid ZIP archive.")

    detected = {}
    inspected_files = []
    total_files = 0

    with zipfile.ZipFile(file_path, "r") as zf:
        for member in zf.infolist():
            if member.is_dir():
                continue
            normalized = os.path.normpath(member.filename)
            if normalized.startswith("..") or os.path.isabs(normalized):
                raise ValueError("Malicious path traversal detected inside ZIP archive; ingestion blocked.")
            if any(skip in normalized.lower() for skip in ("node_modules/", ".git/", "__pycache__/", "venv/")):
                continue

            total_files += 1
            ext = os.path.splitext(normalized)[1].lower()
            base = os.path.basename(normalized).lower()
            _match_text_against_taxonomy(normalized, "file_structure", normalized, detected)

            if (ext in ALLOWED_CODE_EXTS or base == "dockerfile") and member.file_size < 180_000 and len(inspected_files) < 25:
                try:
                    content = zf.read(member).decode("utf-8", errors="ignore")
                    inspected_files.append(normalized)
                    bucket = "documentation" if ext == ".md" else (
                        "dependencies" if base in ("requirements.txt", "package.json", "pyproject.toml", "dockerfile") else "source_code"
                    )
                    _match_text_against_taxonomy(content[:25000], bucket, normalized, detected)
                except Exception:
                    continue

    serialized_skills = {
        s: {
            "signal_count": info["signal_count"],
            "matched_keywords": sorted(list(info["matched_keywords"])),
            "artifacts": sorted(list(info["artifacts"]))[:5],
            "buckets": sorted(list(info["buckets"]))
        }
        for s, info in detected.items()
    }
    return {
        "title": f"Project Archive: {original_filename}",
        "summary": f"Safely extracted and analyzed {len(inspected_files)} of {total_files} files from {original_filename}; mapped {len(serialized_skills)} skills.",
        "extracted_signals": {
            "total_files": total_files,
            "inspected_files": inspected_files
        },
        "detected_skills": serialized_skills
    }

def analyze_pdf_document(file_path: str, original_filename: str) -> dict:
    if os.path.getsize(file_path) > MAX_ZIP_BYTES:
        raise ValueError("PDF exceeds 15 MB upload limit.")
    reader = PdfReader(file_path)
    pages_text = [(page.extract_text() or "") for page in reader.pages[:20]]
    full_text = "\n".join(pages_text)
    if len(full_text.strip()) < 20:
        raise ValueError("PDF contains no extractable text (possibly a scanned image without OCR).")

    detected = {}
    _match_text_against_taxonomy(full_text[:40000], "documentation", original_filename, detected)
    serialized_skills = {
        s: {
            "signal_count": info["signal_count"],
            "matched_keywords": sorted(list(info["matched_keywords"])),
            "artifacts": [f"{original_filename} ({len(reader.pages)} pages)"],
            "buckets": ["documentation"]
        }
        for s, info in detected.items()
    }
    return {
        "title": f"Architecture / Report PDF: {original_filename}",
        "summary": f"Parsed {len(reader.pages)} pages ({len(full_text)} chars) from {original_filename}; identified {len(serialized_skills)} documented technical domains.",
        "extracted_signals": {
            "page_count": len(reader.pages),
            "character_count": len(full_text)
        },
        "detected_skills": serialized_skills
    }

def recalculate_user_profile(conn, user_id: int, trigger_reason: str = "Evidence update"):
    now = datetime.utcnow().isoformat() + "Z"
    cur = conn.cursor()

    cur.execute("SELECT * FROM skill_evaluations WHERE user_id = ?", (user_id,))
    previous_map = {row["skill_name"]: dict(row) for row in cur.fetchall()}

    cur.execute("SELECT * FROM evidence WHERE user_id = ?", (user_id,))
    evidence_rows = cur.fetchall()

    cur.execute("SELECT * FROM assessments WHERE user_id = ?", (user_id,))
    assessment_rows = cur.fetchall()
    best_assessments = {}
    for a in assessment_rows:
        pct = int(round((a["score"] / max(a["max_score"], 1)) * 100))
        if a["skill_name"] not in best_assessments or pct > best_assessments[a["skill_name"]]["pct"]:
            best_assessments[a["skill_name"]] = {"pct": pct, "score": a["score"], "max": a["max_score"]}

    aggregated = {skill: {
        "claimed": False,
        "code_signals": 0,
        "doc_signals": 0,
        "dep_signals": 0,
        "evidence_sources": [],
        "keywords": set()
    } for skill in CANONICAL_SKILLS}

    for ev in evidence_rows:
        source_type = ev["source_type"]
        title = ev["title"]
        detected = json.loads(ev["detected_skills"] or "{}")
        for skill_name, info in detected.items():
            if skill_name not in aggregated:
                continue
            bucket_entry = aggregated[skill_name]
            bucket_entry["evidence_sources"].append(title)
            bucket_entry["keywords"].update(info.get("matched_keywords", []))
            if source_type == "claimed":
                bucket_entry["claimed"] = True
            elif source_type == "pdf":
                bucket_entry["doc_signals"] += info.get("signal_count", 1)
            else:
                buckets = info.get("buckets", [])
                sig = info.get("signal_count", 1)
                if "source_code" in buckets:
                    bucket_entry["code_signals"] += sig
                if "dependencies" in buckets or "file_structure" in buckets:
                    bucket_entry["dep_signals"] += max(1, sig // 2)
                if "documentation" in buckets:
                    bucket_entry["doc_signals"] += 1

    for skill_name, meta in CANONICAL_SKILLS.items():
        agg = aggregated[skill_name]
        assess = best_assessments.get(skill_name)
        has_code = (agg["code_signals"] + agg["dep_signals"]) > 0
        has_docs = agg["doc_signals"] > 0
        has_claimed = agg["claimed"]
        unique_sources = sorted(list(set(agg["evidence_sources"])))
        kw_sample = ", ".join(sorted(list(agg["keywords"]))[:5])

        if assess and assess["pct"] >= 65:
            evidence_status = "assessment-validated"
            base_level = 3 if assess["pct"] >= 80 else 2
            if has_code and (agg["code_signals"] + agg["dep_signals"]) >= 4 and assess["pct"] >= 85:
                base_level = 4
            proficiency = base_level
            confidence = min(98, 72 + (len(unique_sources) * 6) + (assess["pct"] // 6))
            missing_flag = 0
            explanation = (
                f"Validated via practical coding assessment ({assess['score']}/{assess['max']} pts) "
                f"corroborated by {len(unique_sources)} evidence artifact(s) [{kw_sample or 'rubric passed'}]."
            )
        elif has_code:
            evidence_status = "project-supported"
            total_signals = agg["code_signals"] + agg["dep_signals"] + agg["doc_signals"]
            if total_signals >= 9 and len(unique_sources) >= 2:
                proficiency = 4
            elif total_signals >= 5:
                proficiency = 3
            elif total_signals >= 2:
                proficiency = 2
            else:
                proficiency = 1
            confidence = min(88, 52 + (total_signals * 4) + (len(unique_sources) * 7))
            missing_flag = 0
            explanation = (
                f"Verified across {len(unique_sources)} project artifact(s) with {total_signals} technical signals "
                f"(detected: {kw_sample}). Take a practical assessment to elevate confidence above 90%."
            )
        elif has_docs:
            evidence_status = "project-supported"
            proficiency = 2 if agg["doc_signals"] >= 3 else 1
            confidence = min(64, 40 + agg["doc_signals"] * 6)
            missing_flag = 1
            explanation = (
                f"Documented in written architecture/PDF reports ({kw_sample}), but executable code repositories "
                f"have not yet been inspected to verify implementation depth."
            )
        elif has_claimed:
            evidence_status = "claimed"
            proficiency = 1
            confidence = 22
            missing_flag = 1
            explanation = (
                "Self-declared by student without linked repository code or assessment proof. "
                "Distinguished as missing evidence rather than inability — capped at Level 1 until verified."
            )
        else:
            evidence_status = "missing"
            proficiency = 0
            confidence = 10
            missing_flag = 1
            explanation = "No submitted repositories, documentation, or self-claims demonstrate this skill yet."

        prev = previous_map.get(skill_name)
        if prev and (prev["proficiency_level"] != proficiency or abs(prev["confidence_score"] - confidence) >= 5):
            cur.execute('''
                INSERT INTO evaluation_history
                (user_id, skill_name, previous_level, new_level, previous_confidence, new_confidence, trigger_reason, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, skill_name, prev["proficiency_level"], proficiency, prev["confidence_score"], confidence, trigger_reason, now))

        cur.execute('''
            INSERT INTO skill_evaluations
            (user_id, skill_name, category, proficiency_level, evidence_status, confidence_score, explanation, supporting_evidence, missing_evidence_flag, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, skill_name) DO UPDATE SET
                proficiency_level=excluded.proficiency_level,
                evidence_status=excluded.evidence_status,
                confidence_score=excluded.confidence_score,
                explanation=excluded.explanation,
                supporting_evidence=excluded.supporting_evidence,
                missing_evidence_flag=excluded.missing_evidence_flag,
                updated_at=excluded.updated_at
        ''', (
            user_id, skill_name, meta["category"], proficiency, evidence_status,
            confidence, explanation, json.dumps(unique_sources), missing_flag, now
        ))

    cur.execute("SELECT target_role FROM users WHERE id = ?", (user_id,))
    user_row = cur.fetchone()
    target_role = user_row["target_role"] if user_row else "Backend Developer"
    role_spec = ROLE_PROFILES.get(target_role, ROLE_PROFILES["Backend Developer"])

    cur.execute("SELECT * FROM skill_evaluations WHERE user_id = ?", (user_id,))
    evals = {r["skill_name"]: dict(r) for r in cur.fetchall()}

    cur.execute("SELECT skill_name, status FROM roadmap_tasks WHERE user_id = ?", (user_id,))
    existing_statuses = {r["skill_name"]: r["status"] for r in cur.fetchall()}

    cur.execute("DELETE FROM roadmap_tasks WHERE user_id = ?", (user_id,))

    for req in role_spec["requirements"]:
        s_name = req["skill"]
        req_lvl = req["required_level"]
        ev = evals.get(s_name, {"proficiency_level": 0, "evidence_status": "missing"})
        cur_lvl = ev["proficiency_level"]
        gap = req_lvl - cur_lvl
        if gap > 0 or ev["evidence_status"] in ("claimed", "missing"):
            severity_score = max(1, gap) * req["importance"]
            priority = "Critical" if severity_score >= 0.25 or gap >= 2 else ("High" if severity_score >= 0.12 else "Recommended")
            tpl = ROADMAP_TEMPLATES[s_name]
            prev_status = existing_statuses.get(s_name, "pending")
            cur.execute('''
                INSERT INTO roadmap_tasks
                (user_id, skill_name, priority, title, project_activity, resource_label, resource_url, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, s_name, priority, tpl["title"], tpl["activity"], tpl["resource_label"], tpl["resource_url"], prev_status, now))

    conn.commit()
