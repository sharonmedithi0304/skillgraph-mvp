# SkillGraph — Evidence-Based Skill Intelligence Platform
**Team Kaizen** | *Students list skills. We check the evidence.*

SkillGraph is a complete, runnable full-stack MVP built with **FastAPI + SQLite + React + Tailwind + Recharts** designed to run directly in **VS Code**.

## Quick Start in VS Code

### Terminal 1 — Backend (FastAPI + Real GitHub, ZIP & PDF Analyzer)
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — Frontend (React + Vite + Tailwind)
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173** and click **"One-Click Judge Student Demo (Alex Rivera)"** or **"Faculty & Placement Mentor View"**.

### Included Demo Credentials
- **Judge Student Demo:** `alex.rivera@kaizen.edu` / `Kaizen2026!`
- **Faculty & Placement Lead:** `dr.mehta@kaizen.edu` / `Mentor2026!`
- **Sample Test ZIP for Upload:** `backend/sample_projects/sample_docker_pytest_microservice.zip`
