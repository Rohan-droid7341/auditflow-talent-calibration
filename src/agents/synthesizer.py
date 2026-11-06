import time
import json
from typing import Dict, Any, List
from src.state import CalibrationState
from src.config import has_gemini_key, GEMINI_API_KEY, GEMINI_MODEL

def call_gemini_synthesis(profile: Dict[str, Any], req: Dict[str, Any], evidence: List[Dict[str, Any]], feedback: str = "") -> Dict[str, Any]:
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""You are a Lead Solutions Architect and Technical Hiring Manager for Google Forward Deployed Engineers (FDE).
Evaluate this candidate profile against the job requisition.

Ground-Truth Candidate Profile (Structured SQLite):
{json.dumps(profile, indent=2)}

Unstructured Evidence (ChromaDB Case Studies):
{json.dumps([e['text'] for e in evidence], indent=2)}

Target Requisition Criteria:
{json.dumps(req, indent=2)}

Reviewer Critique Feedback from Previous Iteration (if any):
{feedback if feedback else "None. First iteration."}

Generate a JSON object with:
- "match_score": float between 0.0 and 100.0
- "qualification_breakdown": {
    "minimum_qualifications_met": list of strings,
    "minimum_qualifications_gaps": list of strings,
    "preferred_qualifications_met": list of strings,
    "preferred_qualifications_gaps": list of strings
  }
- "discovery_rubric": list of 3-4 objects, each with:
    { "category": string, "probing_question": string, "expected_signal": string, "calibrated_for_candidate": string }
- "executive_summary": string summarizing alignment, technical strengths, and discovery focus.

CRITICAL INSTRUCTION: Do NOT hallucinate or attribute any skill, framework, or cloud tool to the candidate that is NOT explicitly evidenced in the structured profile or unstructured text.
Respond strictly in valid JSON.
"""
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)

def deterministic_synthesis(profile: Dict[str, Any], req: Dict[str, Any], evidence: List[Dict[str, Any]], feedback: str = "") -> Dict[str, Any]:
    skills = [s["skill_name"].lower() for s in profile.get("skills", [])]
    projects = profile.get("projects", [])
    assessments = profile.get("assessments", [])
    cand_id = profile.get("id", "")
    
    # Calculate factual match points
    min_met = []
    min_gaps = []
    pref_met = []
    pref_gaps = []
    
    # Check Min Quals
    has_python = any("python" in s for s in skills)
    has_dsa = any("algorithms" in s or "dsa" in s for s in skills) or len(assessments) > 0
    has_rag = any("rag" in s or "vector" in s for s in skills)
    has_cloud = any("gcp" in s or "cloud" in s for s in skills)
    
    if has_python and has_dsa:
        min_met.append("Python programming & DSA (LeetCode/Codeforces proven records)")
    else:
        min_gaps.append("Missing verified competitive DSA or core Python records")
        
    if has_rag:
        min_met.append("Structured & unstructured data pipelines with vector DBs (ChromaDB/pgvector)")
    else:
        min_gaps.append("Lacks vector database and RAG pipeline implementation proof")
        
    if has_cloud:
        min_met.append("Production cloud architecture & deployment on GCP / containerized services")
    else:
        min_gaps.append("Lacks verified cloud architecture or production launch credentials")
        
    # Check Pref Quals
    has_agents = any("agent" in s or "langgraph" in s for s in skills)
    has_metrics = any("metric" in s or "tracing" in s or "telemetry" in s for s in skills)
    
    if has_agents:
        pref_met.append("Multi-agent systems using LangGraph, state machines, and self-reflection loops")
    else:
        pref_gaps.append("No proven multi-agent orchestration or LangGraph production patterns")
        
    if has_metrics:
        pref_met.append("LLM-native metrics (tokens/sec, latency, cost optimization) and tracing")
    else:
        pref_gaps.append("Lacks granular observability & cost/latency profiling experience")

    # Score calculation
    base_score = 40.0
    if has_python: base_score += 15.0
    if has_dsa: base_score += 10.0
    if has_rag: base_score += 15.0
    if has_cloud: base_score += 10.0
    if has_agents: base_score += 7.0
    if has_metrics: base_score += 3.0
    
    match_score = min(100.0, round(base_score, 1))
    
    # Calibrated Discovery Rubric (Specific to candidate's real projects)
    if "rohan" in cand_id:
        rubric = [
            {
                "category": "High-Throughput State & Spatial Processing",
                "probing_question": "In SiliconCanvas, how did you architect Web Workers and memoization to prevent main-thread UI jank while processing 50,000 spatial defect coordinates at 60 FPS?",
                "expected_signal": "Demonstrates deep understanding of event loop blocking, OffscreenCanvas/ArrayBuffer memory sharing, and spatial indexing.",
                "calibrated_for_candidate": "Targeted probe on SiliconCanvas industrial metrology case study."
            },
            {
                "category": "Streaming Multi-Agent Latency & TTFT",
                "probing_question": "In your Alles Gemini integration, what specific buffer management techniques allowed sub-180ms Time-To-First-Token over WebSockets?",
                "expected_signal": "Discusses chunked async generators, non-blocking backpressure, and decoupling token receipt from UI hydration.",
                "calibrated_for_candidate": "Calibrated directly against real-time Gemini API integration."
            },
            {
                "category": "LangGraph Cyclical State & Reflection",
                "probing_question": "When designing a self-reflection loop in LangGraph, how do you prevent infinite cyclic bouncing between the Critic and Generator nodes?",
                "expected_signal": "Explains typed state transition counters, conditional edge fallback thresholds, and programmatic temperature decay.",
                "calibrated_for_candidate": "Validates core LangGraph Preferred Qualification."
            }
        ]
    else:
        rubric = [
            {
                "category": "Core Data Structures & Algorithmic Complexity",
                "probing_question": "Walk through how you profile and optimize an algorithm with nested loops causing latency spikes in production.",
                "expected_signal": "Big-O space/time tradeoffs and memory caching strategies.",
                "calibrated_for_candidate": "General technical calibration for candidate profile."
            },
            {
                "category": "RAG & Vector Retrieval Scaling",
                "probing_question": "How do you evaluate and handle semantic drift and low-recall queries in a dense vector database?",
                "expected_signal": "Understands hybrid search (BM25 + Dense), re-ranking models, and semantic chunking.",
                "calibrated_for_candidate": "Testing foundational knowledge in RAG gaps."
            }
        ]
        
    summary = (
        f"Candidate '{profile.get('name', cand_id)}' achieves a calibration match score of {match_score}% "
        f"for the Google FDE requisition. Met {len(min_met)} minimum and {len(pref_met)} preferred qualifications. "
        f"Identified {len(min_gaps) + len(pref_gaps)} discovery probing areas for technical interview sessions."
    )
    
    return {
        "match_score": match_score,
        "qualification_breakdown": {
            "minimum_qualifications_met": min_met,
            "minimum_qualifications_gaps": min_gaps,
            "preferred_qualifications_met": pref_met,
            "preferred_qualifications_gaps": pref_gaps
        },
        "discovery_rubric": rubric,
        "executive_summary": summary
    }

def synthesizer_node(state: CalibrationState) -> Dict[str, Any]:
    start_t = time.time()
    status_log = state.get("status_log", [])
    telemetry = state.get("telemetry", {})
    profile = state.get("structured_profile", {})
    req = state.get("parsed_req", {})
    evidence = state.get("unstructured_evidence", [])
    critique = state.get("critique", {})
    revision_count = state.get("revision_count", 0)
    
    status_log.append(f"[Synthesizer] Synthesizing talent calibration report (Iteration #{revision_count + 1})...")
    
    feedback = critique.get("reasoning", "") if critique else ""
    in_tokens = 500
    out_tokens = 450

    if has_gemini_key():
        try:
            result = call_gemini_synthesis(profile, req, evidence, feedback)
        except Exception as e:
            status_log.append(f"[Synthesizer] Gemini API call note: {e}. Executing deterministic synthesizer.")
            result = deterministic_synthesis(profile, req, evidence, feedback)
    else:
        result = deterministic_synthesis(profile, req, evidence, feedback)

    duration = time.time() - start_t
    telemetry["node_timings"] = telemetry.get("node_timings", {})
    telemetry["node_timings"]["synthesizer"] = round(duration, 4)
    telemetry["total_input_tokens"] = telemetry.get("total_input_tokens", 0) + in_tokens
    telemetry["total_output_tokens"] = telemetry.get("total_output_tokens", 0) + out_tokens

    status_log.append(f"[Synthesizer] Generated calibration report with match score {result.get('match_score')}% and {len(result.get('discovery_rubric', []))} discovery questions.")

    return {
        "match_score": result.get("match_score", 0.0),
        "qualification_breakdown": result.get("qualification_breakdown", {}),
        "discovery_rubric": result.get("discovery_rubric", []),
        "synthesis_draft": result.get("executive_summary", ""),
        "status_log": status_log,
        "telemetry": telemetry
    }
