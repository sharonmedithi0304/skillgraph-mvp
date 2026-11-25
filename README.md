🧠 SkillGraphStudents list skills. We check the evidence.AI-Powered Evidence-Based Skill Intelligence PlatformBuilt by Team Kaizen (Sharon & Santhosh) · Prasunex Innovathon 2026🚀 Launch Live Production MVP →⚡ The Problem We SolveEveryone lists skills on a resume. Nobody checks the proof.Resumes & Certificates ≠ Capability: Listing "Python, Docker, REST APIs" or finishing a video course proves attendance—not engineering competence.Scattered Role Expectations: Students don't know how their existing GitHub projects map to industry competency bars across target roles.No Actionable Closing Loop: Existing quiz sites test trivia instead of real repositories, and generic course recommenders ignore what a student has already built.SkillGraph bridges the gap between Claimed Skills (A), Demonstrated Competence (B), and Target Role Requirements (C)—turning raw repositories, project archives, technical write-ups, and practical coding rubrics into an explainable, audit-logged role-readiness graph.🎯 90-Second Judge Walkthrough (Live Production)No setup required. Open https://skillgraph-mvp-henna.vercel.app and test both portals live:RoleAccess MethodCredentialsWhat to Experience🎓 Student Portal1-Click Judge Demo Buttonalex.rivera@kaizen.eduInspect 0–4 skill scores, submit a live GitHub repo or ZIP, pass a practical coding rubric, and watch role readiness recalculate in real time.🧑‍🏫 Faculty & Mentor PortalStandard Logindr.mehta@kaizen.eduMentor2026!Inspect submitted student artifacts, verify code evidence, endorse validated skills, and monitor cohort gap trends.💡 Demo Tip: Our backend runs on Render's free tier (https://skillgraph-api-n7i9.onrender.com). If idle for 15+ minutes, allow ~30–45 seconds on the first request for cold-start wake-up.🔥 Core Capabilities & Innovations1. Multi-Source Evidence Ingestion + Security Trust GateLive GitHub Repository Inspection: Analyzes repository file trees, commit depth, dependencies, and source structure via read-only access (repository ownership ≠ proficiency).Project ZIP Archive Analysis: Deep AST/static scanning protected by a Zip-Slip path-traversal guard (os.path.realpath boundary enforcement).PDF Reports & Lab Write-Ups: Extracts technical architecture signals from project documentation.Prompt-Injection Isolation: Repository files and README.md contents are strictly treated as untrusted data, never as model instructions.2. Three-Axis Explainable Evaluation EngineUnlike black-box scores, SkillGraph separates every skill into three orthogonal signals:Proficiency Level (0–4): 0 Not Demonstrated · 1 Beginner (Claimed Only — Capped) · 2 Developing (Project-Supported) · 3 Proficient (Multi-Signal) · 4 Advanced (Assessment-Validated).Evidence Status: Claimed vs. Project-Supported vs. Assessment-Validated.Confidence Score (10% – 98%): Reflects source reliability and corroboration across multiple artifacts.3. Fair & Non-Offsetting Role Gap Matrix (6 Career Pathways)Benchmarks student evidence against weighted competency profiles for Backend Developer, Frontend Developer, Full Stack Developer, Data Analyst, AI/ML Engineer, and Python Developer:Weighted Readiness Formula:
$$\text{Role Match} = \frac{\sum w_i \cdot \min(\text{student}_i,\, \text{required}_i)}{\sum w_i \cdot \text{required}_i}$$Non-Offsetting Rule: A surplus in Git (+1) never hides a critical P1 gap in SQL, Docker, or Testing.Fairness Rule (Unassessed ≠ Unable): Missing evidence is flagged for verification alongside an explicit Evidence Coverage ratio—never punished as zero ability.4. Closed-Loop Practical Assessments & RoadmapRanked P1 / P2 engineering tasks generated directly from top role gaps.Interactive Practical Code Rubrics (no trivial MCQs) that promote skills to Assessment-Validated and immediately update the Progress Ledger and Audit Log.🏗️ System Architecture┌─────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER (Vercel)                      │
│        React 18 · Vite · Tailwind CSS · Recharts · 1-Click Demo         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTPS / REST (JWT + RBAC)
┌────────────────────────────────────▼────────────────────────────────────┐
│                       APPLICATION LAYER (Render)                        │
│       FastAPI · Pydantic Validation · PBKDF2-SHA256 Auth · CORS         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                      SKILL INTELLIGENCE MONOLITH                        │
│  ┌───────────────────┐  ┌────────────────────┐  ┌────────────────────┐  │
│  │  Evidence Vault   │  │  8-Stage Analyzer  │  │  Gap & Roadmap     │  │
│  │  GitHub · ZIP ·   │─▶│  AST · Taxonomy ·  │─▶│  Weighted Matrix · │  │
│  │  PDF · Trust Gate │  │  0–4 + Confidence  │  │  Rubrics · Ledger  │  │
│  └───────────────────┘  └────────────────────┘  └────────────────────┘  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ SQLAlchemy ORM
┌────────────────────────────────────▼────────────────────────────────────┐
│                         PERSISTENCE LAYER                               │
│     SQLite (WAL Mode) + Persisted Artifacts  ──▶  Scale-Out: PG + S3    │
└─────────────────────────────────────────────────────────────────────────┘
💻 Local Development SetupPrerequisitesPython 3.11+Node.js 18+1. Clone the Repositorygit clone https://github.com/Sharonmedithi0304/skillgraph-mvp.git
cd skillgraph-mvp
2. Start the FastAPI Backendcd backend
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
Interactive Swagger API Docs will be available at: http://localhost:8000/docs3. Start the React + Vite Frontendcd ../frontend
npm install
npm run dev
Open http://localhost:5173 in your browser and click One-Click Judge Student Demo (Alex Rivera).📂 Repository Structureskillgraph-mvp/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint, CORS, startup DB seeding
│   │   ├── models.py            # SQLAlchemy relational schema & audit logs
│   │   ├── schemas.py           # Typed Pydantic request/response contracts
│   │   ├── security.py          # PBKDF2-SHA256 hashing & JWT RBAC guards
│   │   ├── routers/             # Auth, evidence, skills, roles, assessments, mentor
│   │   └── services/
│   │       ├── analyzer.py      # GitHub, Zip-Slip safe archive & PDF extractor
│   │       ├── taxonomy.py      # Standardized skill catalog & 6 role benchmarks
│   │       └── assessment.py    # 0–4 scoring, confidence & gap prioritization
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api.js               # Typed API client bound to VITE_API_URL
│   │   ├── App.jsx              # Student & Mentor dashboards, charts, rubrics
│   │   └── main.jsx
│   └── package.json
└── README.md
🗺️ Roadmap: From Live MVP to Campus Scale✅ Phase 1 — Live MVP (Shipped): Full-stack Student & Mentor portals, GitHub/ZIP/PDF ingestion, Trust Gate security, 0–4 explainable scoring, weighted gap matrix across 6 roles, practical coding rubrics, and audit-logged reassessment.🔜 Phase 2 — Campus & Placement Scale: Consent-scoped Placement Cell cohort analytics, PostgreSQL + S3 artifact storage, Celery + Redis async worker queues, and Sentence-Transformer semantic alignment with ESCO / O*NET.🔭 Phase 3 — Verifiable Ecosystem: Cryptographically signed SkillGraph Evidence Passport, additional engineering disciplines, and human-in-the-loop rubric calibration.Built with conviction by Team Kaizen (Sharon & Santhosh)Don't just list your skills. Prove them. Improve them.
