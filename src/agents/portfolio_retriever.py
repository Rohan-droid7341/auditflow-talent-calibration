import time
from typing import Dict, Any, List
from src.state import CalibrationState
from src.db import get_candidate_profile
from src.vector_store import query_candidate_evidence

def portfolio_retriever_node(state: CalibrationState) -> Dict[str, Any]:
    """
    Hybrid Data Pipeline Layer:
    Executes relational database queries (SQLite) for verified candidate skills/projects
    and dense vector semantic search (ChromaDB + HuggingFace API) for unstructured architectural case studies.
    """
    start_t = time.time()
    candidate_id = state.get("candidate_id", "rohan_garg")
    status_log = state.get("status_log", [])
    telemetry = state.get("telemetry", {})
    
    status_log.append(f"[PortfolioRetriever] Fetching structured ground truth from SQLite for candidate '{candidate_id}'...")
    structured_profile = get_candidate_profile(candidate_id)
    if not structured_profile:
        status_log.append(f"[PortfolioRetriever] Warning: Candidate '{candidate_id}' not found in SQLite. Using fallback.")
        structured_profile = {"id": candidate_id, "name": candidate_id, "skills": [], "projects": [], "assessments": []}

    status_log.append(f"[PortfolioRetriever] Executing vector similarity search across unstructured project case studies in ChromaDB...")
    query_topics = [
        "AI multi-agent LangGraph architecture",
        "RAG vector database pipelines",
        "Cloud production deployment and telemetry metrics",
        "Technical discovery and system design"
    ]
    
    unstructured_evidence = []
    for topic in query_topics:
        matches = query_candidate_evidence(candidate_id, topic, n_results=2)
        for m in matches:
            # Deduplicate by text content
            if not any(e["text"] == m["text"] for e in unstructured_evidence):
                unstructured_evidence.append(m)

    duration = time.time() - start_t
    telemetry["node_timings"] = telemetry.get("node_timings", {})
    telemetry["node_timings"]["portfolio_retriever"] = round(duration, 4)

    status_log.append(
        f"[PortfolioRetriever] Retrieved {len(structured_profile.get('skills', []))} structured skills and "
        f"{len(unstructured_evidence)} unstructured case study chunks."
    )

    return {
        "structured_profile": structured_profile,
        "unstructured_evidence": unstructured_evidence,
        "status_log": status_log,
        "telemetry": telemetry
    }
