import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "candidate.db"
DOCS_DIR = BASE_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

SCHEMA_PATH = BASE_DIR / "schema.sql"

def init_sqlite_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())
    
    # Candidate 1: Rohan Garg (Google FDE Aligned Candidate)
    cursor.execute("""
    INSERT INTO candidates (id, name, university, degree, gpa, grad_year, target_role)
    VALUES ('rohan_garg', 'Rohan Garg', 'IIIT Lucknow', 'B.Tech Computer Science', 9.1, 2026, 'Google Forward Deployed Engineer / AI Engineer')
    """)
    
    rohan_skills = [
        ('rohan_garg', 'Language', 'Python', 'Expert', 1, 'Production FastAPI, AsyncIO, PyTorch, Scripting'),
        ('rohan_garg', 'Language', 'C++', 'Proficient', 1, 'C++17 Rubiks solver with IDA* heuristic search'),
        ('rohan_garg', 'Language', 'SQL', 'Proficient', 1, 'PostgreSQL, SQLite, complex relational joins and indexing'),
        ('rohan_garg', 'AI/ML', 'RAG & Vector Databases', 'Expert', 1, 'ChromaDB, pgvector, hybrid BM25 + dense search'),
        ('rohan_garg', 'AI/ML', 'Multi-Agent Frameworks', 'Expert', 1, 'LangGraph, state machines, self-reflection loops'),
        ('rohan_garg', 'AI/ML', 'LLM Metrics & Tracing', 'Proficient', 1, 'Tokens/sec, TTFT, cost optimization, OpenTelemetry/Langfuse'),
        ('rohan_garg', 'Cloud/Infra', 'Google Cloud Platform (GCP)', 'Proficient', 1, 'Cloud Run, Vertex AI API, Cloud SQL, Docker'),
        ('rohan_garg', 'Algorithms', 'Data Structures & Algorithms', 'Expert', 1, 'LeetCode Knight (Rating 1850+, Top 4%), 1000+ solved')
    ]
    cursor.executemany("""
    INSERT INTO skills (candidate_id, category, skill_name, proficiency_level, verified, proof_details)
    VALUES (?, ?, ?, ?, ?, ?)
    """, rohan_skills)
    
    rohan_projects = [
        ('rohan_garg', 'SiliconCanvas', 'React 18, TypeScript, HTML5 Canvas, Web Workers', 'Microsecond wafer defect metrology engine rendering 50,000+ spatial data points at 60 FPS', 1, 'github.com/Rohan-droid7341/silicon-canvas'),
        ('rohan_garg', 'Internship Engine India', 'Python, FastAPI, Playwright, MongoDB, Docker', 'Distributed web scraping & ETL pipeline ingesting 15,000+ postings with async rate-limiting', 1, 'github.com/Rohan-droid7341/internship-engine'),
        ('rohan_garg', 'Alles AI Social Ecosystem', 'Next.js, Node.js, MongoDB, Socket.io, Gemini API', 'Real-time collaborative workspace with streaming multimodal Gemini integration under 180ms TTFT', 1, 'github.com/Rohan-droid7341/alles-platform'),
        ('rohan_garg', 'LogiSync AI Logistics', 'Python, PyTorch, RL (PPO), XGBoost, LightGBM', 'Supply chain routing digital twin cutting simulated delivery delay by 22% using PPO policy networks', 1, 'github.com/Rohan-droid7341/logisync-rl')
    ]
    cursor.executemany("""
    INSERT INTO projects (candidate_id, title, primary_stack, metrics_summary, is_production, repo_url)
    VALUES (?, ?, ?, ?, ?, ?)
    """, rohan_projects)
    
    rohan_assessments = [
        ('rohan_garg', 'DSA', 'LeetCode Knight (1850+ Rating, Top ~4%)', 96.2, 1000),
        ('rohan_garg', 'DSA', 'Codeforces Specialist (Peak 1441)', 88.0, 300),
        ('rohan_garg', 'Hackathon', 'Monad BlitZ Global Hackathon (2nd Place / 250+ Teams)', 99.2, 0)
    ]
    cursor.executemany("""
    INSERT INTO assessments (candidate_id, domain, metric_label, score_percentile, problems_solved)
    VALUES (?, ?, ?, ?, ?)
    """, rohan_assessments)
    
    rohan_exp = [
        ('rohan_garg', 'Gurukul Code', 'Frontend Engineering Intern', 'May 2025 - July 2025', 'Built high-throughput data grid and visual dashboards with Web Workers and memoization; eliminated UI freeze on large datasets.')
    ]
    cursor.executemany("""
    INSERT INTO experience (candidate_id, company, role, duration, highlights)
    VALUES (?, ?, ?, ?, ?)
    """, rohan_exp)
    
    # Candidate 2: Jordan Taylor (Junior Full-Stack, Gaps in AI/Cloud)
    cursor.execute("""
    INSERT INTO candidates (id, name, university, degree, gpa, grad_year, target_role)
    VALUES ('jordan_taylor', 'Jordan Taylor', 'State University', 'B.S. Information Technology', 3.4, 2026, 'Software Engineer')
    """)
    jordan_skills = [
        ('jordan_taylor', 'Language', 'JavaScript', 'Proficient', 1, 'ES6+, React, Node.js'),
        ('jordan_taylor', 'Language', 'Python', 'Working', 1, 'Basic scripts and Flask APIs'),
        ('jordan_taylor', 'Language', 'SQL', 'Working', 1, 'Basic CRUD queries on MySQL'),
        ('jordan_taylor', 'Algorithms', 'Data Structures & Algorithms', 'Working', 1, 'LeetCode 150 solved')
    ]
    cursor.executemany("INSERT INTO skills (candidate_id, category, skill_name, proficiency_level, verified, proof_details) VALUES (?, ?, ?, ?, ?, ?)", jordan_skills)
    
    # Candidate 3: Priya Sharma (Academic ML Researcher, Gaps in Multi-Agent & Production Cloud)
    cursor.execute("""
    INSERT INTO candidates (id, name, university, degree, gpa, grad_year, target_role)
    VALUES ('priya_sharma', 'Priya Sharma', 'Tech Institute', 'M.S. Computer Science', 3.8, 2026, 'Machine Learning Engineer')
    """)
    priya_skills = [
        ('priya_sharma', 'Language', 'Python', 'Expert', 1, 'NumPy, Pandas, PyTorch research papers'),
        ('priya_sharma', 'AI/ML', 'Classical ML & Deep Learning', 'Expert', 1, 'CNNs, Transformers fine-tuning on PyTorch'),
        ('priya_sharma', 'Algorithms', 'Data Structures & Algorithms', 'Proficient', 1, 'LeetCode 450 solved')
    ]
    cursor.executemany("INSERT INTO skills (candidate_id, category, skill_name, proficiency_level, verified, proof_details) VALUES (?, ?, ?, ?, ?, ?)", priya_skills)
    
    conn.commit()
    conn.close()
    print("Database candidate.db seeded successfully.")

def write_unstructured_docs():
    # 1. Target Job Description (Google FDE Role from prompt)
    jd_content = """# Role: AI Solutions Engineer / Forward Deployed Engineer (FDE)

## Minimum Qualifications:
- Currently pursuing a Bachelor's or Master's degree in Computer Science, Engineering, or a related technical field.
- Enrolled in the penultimate academic year of a Bachelor's or Master's degree.
- Experience in Python programming language, and data structures and algorithms.
- Experience taking production-grade AI-driven solutions from conception to launch and architecting AI systems on cloud platforms (e.g., Google Cloud Platform).
- Experience building pipelines for structured and unstructured data using both vector databases and RAG-like architectures to power enterprise AI solutions.

## Preferred Qualifications:
- Experience implementing multi-agent systems using frameworks (e.g., LangGraph, CrewAI, ADK) and complex patterns (e.g., ReAct, self-reflection, hierarchical delegation).
- Experience leading technical discovery sessions.
- Knowledge of Large Language Model (LLM) native metrics (e.g., tokens/sec, cost-per-request) and techniques for optimizing state management and granular tracing.
"""
    with open(DOCS_DIR / "google_fde_requisition.md", "w", encoding="utf-8") as f:
        f.write(jd_content)

    # 2. Rohan Garg Project Case Studies (Unstructured deep-dive)
    rohan_docs = """# Candidate Dossier: Rohan Garg (IIIT Lucknow)

## Architectural Case Study 1: Alles Multimodal AI Platform
Rohan architected a collaborative AI platform integrating Google's Gemini API with real-time WebSockets.
- Built a hybrid RAG pipeline using ChromaDB and sentence transformers to store and retrieve user session memory and contextual files.
- Optimized latency down to sub-180ms Time-To-First-Token (TTFT) by chunking streaming token buffers and maintaining asynchronous state transitions.
- Deployed microservices using Docker on cloud platforms, with integrated health-checks and rate-limiting to prevent quota exhaustion.

## Architectural Case Study 2: LogiSync & Distributed ETL Engine
- Designed an autonomous data ingestion pipeline parsing over 15,000 structured and unstructured company postings.
- Implemented reinforcement learning (PPO) and gradient boosted trees to model risk scores and optimize routing paths.
- Demonstrated end-to-end telemetry: instrumented structured logging capturing request latency, database query times, and pipeline throughput.

## Technical Discovery & Collaboration
- Acted as GDG (Google Developer Groups) Coordinator, leading technical discovery workshops, hackathon mentorship sessions, and architecture whiteboarding for 200+ engineering students.
"""
    with open(DOCS_DIR / "rohan_garg_dossier.md", "w", encoding="utf-8") as f:
        f.write(rohan_docs)

    # 3. Jordan Taylor Dossier
    jordan_docs = """# Candidate Dossier: Jordan Taylor
Jordan has built web dashboards using Node.js, Express, and React.
- Has not worked with vector databases or retrieval-augmented generation (RAG).
- Has basic Python familiarity for small utility scripts, but no production experience with LangGraph, multi-agent frameworks, or cloud infrastructure like GCP.
"""
    with open(DOCS_DIR / "jordan_taylor_dossier.md", "w", encoding="utf-8") as f:
        f.write(jordan_docs)

    # 4. Priya Sharma Dossier
    priya_docs = """# Candidate Dossier: Priya Sharma
Priya is an academic ML researcher with multiple publications on transformer fine-tuning in PyTorch.
- Strong in statistical modeling and data preprocessing with Pandas and NumPy.
- Has built prototype RAG notebooks using LangChain, but has not architected production multi-agent systems, cyclic graphs with self-reflection, or deployed systems on GCP Cloud Run.
"""
    with open(DOCS_DIR / "priya_sharma_dossier.md", "w", encoding="utf-8") as f:
        f.write(priya_docs)

    print("Unstructured documentation dossiers created.")

if __name__ == "__main__":
    init_sqlite_db()
    write_unstructured_docs()
