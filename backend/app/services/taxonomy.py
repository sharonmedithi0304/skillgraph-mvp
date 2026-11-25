CANONICAL_SKILLS = {
    "Python": {
        "category": "Core Language",
        "keywords": ["python", ".py", "pytest", "pydantic", "asyncio", "pip", "pyproject.toml", "requirements.txt", "venv", "pandas", "numpy"]
    },
    "REST APIs & Backend Frameworks": {
        "category": "Backend Engineering",
        "keywords": ["fastapi", "flask", "django", "express", "nestjs", "spring boot", "router", "endpoint", "uvicorn", "api", "rest", "graphql", "middleware"]
    },
    "SQL & Relational Databases": {
        "category": "Data Persistence",
        "keywords": ["sql", "sqlite", "postgresql", "postgres", "mysql", "sqlalchemy", "prisma", "typeorm", "migration", "schema", "select ", "create table", "foreign key", "orm"]
    },
    "Authentication & Security": {
        "category": "Security & Trust",
        "keywords": ["jwt", "oauth", "bcrypt", "pbkdf2", "hash", "token", "rbac", "authorization", "authentication", "cors", "csrf", "helmet", "security", "encryption"]
    },
    "Docker & Cloud Deployment": {
        "category": "DevOps & Infrastructure",
        "keywords": ["docker", "dockerfile", "docker-compose", "kubernetes", "k8s", "nginx", "ci/cd", "github actions", "vercel", "aws", "render", "deployment", "container"]
    },
    "Automated Testing & QA": {
        "category": "Software Quality",
        "keywords": ["pytest", "unittest", "jest", "vitest", "mocha", "cypress", "test_", ".spec.", ".test.", "coverage", "mock", "assertion", "integration test"]
    },
    "System Design & Caching": {
        "category": "Architecture",
        "keywords": ["redis", "celery", "rabbitmq", "kafka", "rate limit", "load balancer", "microservice", "architecture", "scalability", "queue", "webhook", "caching"]
    },
    "Git & Collaborative Workflow": {
        "category": "Engineering Practices",
        "keywords": ["readme", "gitignore", "contributing", "pull request", "branch", "version control", "license", "changelog"]
    }
}

ROLE_PROFILES = {
    "Backend Developer": {
        "description": "Designs resilient APIs, relational data models, authentication pipelines, and containerized backend services.",
        "requirements": [
            {"skill": "Python", "required_level": 3, "importance": 0.18, "criticality": "Core"},
            {"skill": "REST APIs & Backend Frameworks", "required_level": 3, "importance": 0.22, "criticality": "Core"},
            {"skill": "SQL & Relational Databases", "required_level": 3, "importance": 0.20, "criticality": "Core"},
            {"skill": "Authentication & Security", "required_level": 3, "importance": 0.14, "criticality": "High"},
            {"skill": "Automated Testing & QA", "required_level": 2, "importance": 0.10, "criticality": "High"},
            {"skill": "Docker & Cloud Deployment", "required_level": 2, "importance": 0.08, "criticality": "Important"},
            {"skill": "System Design & Caching", "required_level": 2, "importance": 0.05, "criticality": "Important"},
            {"skill": "Git & Collaborative Workflow", "required_level": 2, "importance": 0.03, "criticality": "Baseline"}
        ]
    },
    "Full-Stack Engineer": {
        "description": "Builds end-to-end web products combining interactive UI engineering with reliable backend APIs and databases.",
        "requirements": [
            {"skill": "REST APIs & Backend Frameworks", "required_level": 3, "importance": 0.24, "criticality": "Core"},
            {"skill": "SQL & Relational Databases", "required_level": 3, "importance": 0.20, "criticality": "Core"},
            {"skill": "Authentication & Security", "required_level": 2, "importance": 0.16, "criticality": "High"},
            {"skill": "Python", "required_level": 2, "importance": 0.15, "criticality": "High"},
            {"skill": "Automated Testing & QA", "required_level": 2, "importance": 0.10, "criticality": "Important"},
            {"skill": "Docker & Cloud Deployment", "required_level": 2, "importance": 0.08, "criticality": "Important"},
            {"skill": "Git & Collaborative Workflow", "required_level": 2, "importance": 0.07, "criticality": "Baseline"}
        ]
    },
    "AI & Backend Systems Engineer": {
        "description": "Productionizes intelligent inference pipelines, FastAPI microservices, and scalable data workflows.",
        "requirements": [
            {"skill": "Python", "required_level": 4, "importance": 0.28, "criticality": "Core"},
            {"skill": "REST APIs & Backend Frameworks", "required_level": 3, "importance": 0.22, "criticality": "Core"},
            {"skill": "System Design & Caching", "required_level": 3, "importance": 0.18, "criticality": "High"},
            {"skill": "Docker & Cloud Deployment", "required_level": 3, "importance": 0.14, "criticality": "High"},
            {"skill": "SQL & Relational Databases", "required_level": 2, "importance": 0.10, "criticality": "Important"},
            {"skill": "Automated Testing & QA", "required_level": 2, "importance": 0.08, "criticality": "Important"}
        ]
    }
}

ROADMAP_TEMPLATES = {
    "Python": {
        "title": "Build Modular Async Python Service with Type Hints & Pydantic",
        "activity": "Refactor a script into a multi-module Python package with strict type annotations, custom exception hierarchies, and structured logging.",
        "resource_label": "Real Python — Clean Architecture & Typing Guide",
        "resource_url": "https://realpython.com/python-type-checking/"
    },
    "REST APIs & Backend Frameworks": {
        "title": "Architect a Versioned REST API with Dependency Injection & OpenAPI Docs",
        "activity": "Build a multi-resource FastAPI service with pagination, request validation, standardized error envelopes, and rate limiting.",
        "resource_label": "FastAPI Official — Bigger Applications & Routers",
        "resource_url": "https://fastapi.tiangolo.com/tutorial/bigger-applications/"
    },
    "SQL & Relational Databases": {
        "title": "Design Normalized 3NF Schema with Indexes & Transaction Safety",
        "activity": "Create a relational schema with foreign-key constraints, composite indexes, and an EXPLAIN QUERY PLAN benchmark in PostgreSQL/SQLite.",
        "resource_label": "Use The Index, Luke — SQL Indexing & Tuning",
        "resource_url": "https://use-the-index-luke.com/"
    },
    "Authentication & Security": {
        "title": "Implement Salted Password Hashing, JWT Refresh Rotation & RBAC",
        "activity": "Add role-based middleware guards, hashed credentials, and input sanitization to protect student/admin API endpoints.",
        "resource_label": "OWASP API Security Top 10 Checklist",
        "resource_url": "https://owasp.org/API-Security/"
    },
    "Docker & Cloud Deployment": {
        "title": "Containerize Backend + Database with Multi-Stage Dockerfile",
        "activity": "Write a production multi-stage Dockerfile and docker-compose.yml with healthchecks, non-root user, and environment variable injection.",
        "resource_label": "Docker Official — Best Practices for Writing Dockerfiles",
        "resource_url": "https://docs.docker.com/build/building/best-practices/"
    },
    "Automated Testing & QA": {
        "title": "Write Pytest Integration Suite with >80% Endpoint Coverage",
        "activity": "Create isolated test fixtures for auth, database CRUD, and error edge cases using pytest and FastAPI TestClient.",
        "resource_label": "FastAPI Testing Guide with Pytest",
        "resource_url": "https://fastapi.tiangolo.com/tutorial/testing/"
    },
    "System Design & Caching": {
        "title": "Add Redis Cache-Aside Pattern & Background Task Queue",
        "activity": "Implement TTL-based caching on expensive read endpoints and offload heavy analysis jobs to an async worker.",
        "resource_label": "System Design Primer — Caching & Scalability",
        "resource_url": "https://github.com/donnemartin/system-design-primer"
    },
    "Git & Collaborative Workflow": {
        "title": "Standardize Repository Hygiene, Architecture README & CI Checks",
        "activity": "Add architecture diagrams, setup commands, .gitignore rules, and a GitHub Actions lint/test workflow.",
        "resource_label": "GitHub Docs — Quickstart for Repositories",
        "resource_url": "https://docs.github.com/en/get-started"
    }
}

PRACTICAL_ASSESSMENTS = [
    {
        "id": "assess_sql_01",
        "skill_name": "SQL & Relational Databases",
        "difficulty": "Intermediate (Level 3 Benchmark)",
        "title": "Fix N+1 Query & Design Indexed Leaderboard Schema",
        "prompt": "A student submission endpoint runs 1 query per repository file, causing 400ms latency. Write a SQL query using JOIN and GROUP BY (with appropriate INDEX recommendations) to aggregate verified skill counts per student in a single query.",
        "starter_code": "-- Write your optimized SQL schema index and aggregation query below:\nCREATE INDEX idx_evidence_user ON evidence(user_id);\n\nSELECT u.name, COUNT(e.id) AS verified_items\nFROM users u\n-- Complete JOIN and GROUP BY\n",
        "rubric_keywords": ["join", "group by", "index", "on ", "count"],
        "rubric_criteria": [
            "Uses explicit JOIN instead of correlated subqueries (+35 pts)",
            "Includes GROUP BY aggregation on user identifier (+30 pts)",
            "Defines B-Tree INDEX on foreign key / lookup column (+35 pts)"
        ]
    },
    {
        "id": "assess_auth_01",
        "skill_name": "Authentication & Security",
        "difficulty": "Intermediate (Level 3 Benchmark)",
        "title": "Harden Repository Ingestion & Role Authorization Middleware",
        "prompt": "Write a Python verification function `validate_repo_and_role(url: str, user_role: str)` that prevents SSRF/non-GitHub URLs, enforces read-only public HTTPS links, and verifies `student` or `admin` role access.",
        "starter_code": "def validate_repo_and_role(url: str, user_role: str) -> bool:\n    # Enforce https://github.com/ prefix, block path traversal, and check role\n    pass\n",
        "rubric_keywords": ["https://github.com/", "startswith", "role", "raise", "return"],
        "rubric_criteria": [
            "Validates strict https://github.com/ origin to prevent SSRF (+40 pts)",
            "Checks authorized user role before processing (+30 pts)",
            "Returns explicit boolean or raises HTTPException/ValueError (+30 pts)"
        ]
    },
    {
        "id": "assess_docker_01",
        "skill_name": "Docker & Cloud Deployment",
        "difficulty": "Applied (Level 2–3 Benchmark)",
        "title": "Author a Secure Multi-Stage FastAPI Dockerfile",
        "prompt": "Write a Dockerfile for a Python FastAPI service that installs dependencies from requirements.txt, avoids running as root, exposes port 8000, and launches uvicorn.",
        "starter_code": "FROM python:3.11-slim\nWORKDIR /app\n# Copy requirements, install, add non-root user, and run uvicorn\n",
        "rubric_keywords": ["copy", "requirements.txt", "pip install", "user", "uvicorn", "8000"],
        "rubric_criteria": [
            "Leverages layer caching by copying requirements.txt first (+35 pts)",
            "Switches away from root via USER directive (+35 pts)",
            "Starts uvicorn server cleanly on port 8000 (+30 pts)"
        ]
    },
    {
        "id": "assess_test_01",
        "skill_name": "Automated Testing & QA",
        "difficulty": "Applied (Level 2–3 Benchmark)",
        "title": "Write Pytest Edge-Case Suite for Skill Evaluation Engine",
        "prompt": "Write two pytest unit tests verifying that: (1) a claimed-only skill never exceeds Proficiency Level 1, and (2) an assessment-validated skill upgrades evidence_status to 'assessment-validated'.",
        "starter_code": "import pytest\n\ndef test_claimed_skill_cap():\n    # Assert claimed-only skill proficiency <= 1\n    pass\n\ndef test_assessment_upgrade():\n    # Assert assessment upgrades status\n    pass\n",
        "rubric_keywords": ["def test_", "assert", "claimed", "assessment", "proficiency"],
        "rubric_criteria": [
            "Defines isolated pytest functions with clear assertions (+40 pts)",
            "Tests boundary condition on claimed-only proficiency cap (+30 pts)",
            "Verifies state transition to assessment-validated (+30 pts)"
        ]
    }
]
