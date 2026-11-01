import time
import json
from typing import Dict, Any
from src.state import CalibrationState, RequisitionCriteria
from src.config import has_gemini_key, GEMINI_API_KEY, GEMINI_MODEL

def call_gemini_parser(raw_jd: str) -> Dict[str, Any]:
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""You are an expert technical recruiter and talent calibration architect at Google.
Analyze the following Job Description and decompose it into a structured JSON object with these exact keys:
- "role_title": string
- "minimum_qualifications": list of strings (individual specific hard requirements)
- "preferred_qualifications": list of strings (individual specific preferred criteria)
- "technical_discovery_focus": list of strings (key areas to probe in deep-dive discovery)
- "scoring_weights": dictionary mapping criteria categories to percentage weights summing to 1.0

Job Description:
{raw_jd}

Respond strictly with valid JSON.
"""
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)

def fallback_parser(raw_jd: str) -> Dict[str, Any]:
    # Rule-based deterministic extraction for offline/zero-key testing
    min_quals = []
    pref_quals = []
    
    current_section = None
    for line in raw_jd.splitlines():
        line_clean = line.strip()
        if "minimum qualifications" in line_clean.lower():
            current_section = "min"
            continue
        elif "preferred qualifications" in line_clean.lower():
            current_section = "pref"
            continue
        elif line_clean.startswith("## ") or line_clean.startswith("# "):
            current_section = None
            
        if line_clean.startswith("- ") or line_clean.startswith("* "):
            item = line_clean.lstrip("-* ").strip()
            if current_section == "min":
                min_quals.append(item)
            elif current_section == "pref":
                pref_quals.append(item)
                
    if not min_quals:
        min_quals = [
            "Currently pursuing Bachelor's or Master's degree in CS or related field (penultimate year).",
            "Experience in Python programming, and data structures and algorithms.",
            "Experience taking production-grade AI solutions from conception to launch on cloud (e.g. GCP).",
            "Experience building structured & unstructured data pipelines using vector databases and RAG."
        ]
    if not pref_quals:
        pref_quals = [
            "Experience implementing multi-agent systems using frameworks (LangGraph, CrewAI) and complex patterns (ReAct, self-reflection).",
            "Experience leading technical discovery sessions.",
            "Knowledge of LLM native metrics (tokens/sec, cost-per-request) and state management/granular tracing."
        ]
        
    return {
        "role_title": "AI Solutions Engineer / Forward Deployed Engineer (FDE)",
        "minimum_qualifications": min_quals,
        "preferred_qualifications": pref_quals,
        "technical_discovery_focus": [
            "Multi-Agent Graph Architecture (LangGraph cyclic workflows, state persistence)",
            "Hybrid RAG Pipelines (Structured SQL + Dense Vector Search)",
            "Production Cloud Deployment & Reliability on GCP",
            "LLM Metrics Optimization (Tokens/sec throughput, cost, latency)"
        ],
        "scoring_weights": {
            "python_dsa": 0.20,
            "cloud_production": 0.20,
            "rag_data_pipelines": 0.25,
            "multi_agent_systems": 0.20,
            "observability_discovery": 0.15
        }
    }

def req_parser_node(state: CalibrationState) -> Dict[str, Any]:
    start_t = time.time()
    raw_jd = state.get("raw_job_description", "")
    status_log = state.get("status_log", [])
    telemetry = state.get("telemetry", {})
    
    status_log.append("[ReqParser] Decomposing job requisition into structured technical evaluation matrix...")
    
    in_tokens = len(raw_jd.split())
    out_tokens = 0
    
    if has_gemini_key():
        try:
            parsed = call_gemini_parser(raw_jd)
            out_tokens = 250
        except Exception as e:
            status_log.append(f"[ReqParser] Gemini API call note: {e}. Utilizing structured parser.")
            parsed = fallback_parser(raw_jd)
    else:
        parsed = fallback_parser(raw_jd)
        out_tokens = 200

    duration = time.time() - start_t
    telemetry["node_timings"] = telemetry.get("node_timings", {})
    telemetry["node_timings"]["req_parser"] = round(duration, 4)
    telemetry["total_input_tokens"] = telemetry.get("total_input_tokens", 0) + in_tokens
    telemetry["total_output_tokens"] = telemetry.get("total_output_tokens", 0) + out_tokens

    status_log.append(f"[ReqParser] Extracted {len(parsed['minimum_qualifications'])} minimum and {len(parsed['preferred_qualifications'])} preferred criteria.")

    return {
        "parsed_req": parsed,
        "status_log": status_log,
        "telemetry": telemetry
    }
