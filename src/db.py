import sqlite3
from typing import Dict, Any, List, Optional
from pathlib import Path
from src.config import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def list_candidate_ids() -> List[Dict[str, str]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, target_role, university FROM candidates")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r["id"], "name": r["name"], "target_role": r["target_role"], "university": r["university"]} for r in rows]

def get_candidate_profile(candidate_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Basic Info
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    cand = cursor.fetchone()
    if not cand:
        conn.close()
        return None
    
    profile = {
        "id": cand["id"],
        "name": cand["name"],
        "university": cand["university"],
        "degree": cand["degree"],
        "gpa": cand["gpa"],
        "grad_year": cand["grad_year"],
        "target_role": cand["target_role"],
        "skills": [],
        "projects": [],
        "assessments": [],
        "experience": []
    }
    
    # 2. Skills
    cursor.execute("SELECT category, skill_name, proficiency_level, verified, proof_details FROM skills WHERE candidate_id = ?", (candidate_id,))
    for row in cursor.fetchall():
        profile["skills"].append({
            "category": row["category"],
            "skill_name": row["skill_name"],
            "proficiency_level": row["proficiency_level"],
            "verified": bool(row["verified"]),
            "proof_details": row["proof_details"]
        })
        
    # 3. Projects
    cursor.execute("SELECT title, primary_stack, metrics_summary, is_production, repo_url FROM projects WHERE candidate_id = ?", (candidate_id,))
    for row in cursor.fetchall():
        profile["projects"].append({
            "title": row["title"],
            "primary_stack": row["primary_stack"],
            "metrics_summary": row["metrics_summary"],
            "is_production": bool(row["is_production"]),
            "repo_url": row["repo_url"]
        })
        
    # 4. Assessments
    cursor.execute("SELECT domain, metric_label, score_percentile, problems_solved FROM assessments WHERE candidate_id = ?", (candidate_id,))
    for row in cursor.fetchall():
        profile["assessments"].append({
            "domain": row["domain"],
            "metric_label": row["metric_label"],
            "score_percentile": row["score_percentile"],
            "problems_solved": row["problems_solved"]
        })
        
    # 5. Experience
    cursor.execute("SELECT company, role, duration, highlights FROM experience WHERE candidate_id = ?", (candidate_id,))
    for row in cursor.fetchall():
        profile["experience"].append({
            "company": row["company"],
            "role": row["role"],
            "duration": row["duration"],
            "highlights": row["highlights"]
        })
        
    conn.close()
    return profile
