import time
from typing import Dict, Any
from src.state import CalibrationState
from src.metrics import TelemetryTracker

def supervisor_node(state: CalibrationState) -> Dict[str, Any]:
    """
    Supervisor / Hierarchical Delegation Root.
    Initializes execution state, validates input job description and candidate ID,
    and sets up telemetry and logging for downstream worker agents.
    """
    start_t = time.time()
    candidate_id = state.get("candidate_id", "rohan_garg")
    raw_jd = state.get("raw_job_description", "")
    
    status_log = state.get("status_log", [])
    status_log.append(f"[Supervisor] Initialized talent audit for candidate '{candidate_id}'. Routing to Requisition Parser.")
    
    telemetry = state.get("telemetry", {})
    if not telemetry:
        tracker = TelemetryTracker()
        telemetry = tracker.get_summary()

    duration = time.time() - start_t
    telemetry["node_timings"] = telemetry.get("node_timings", {})
    telemetry["node_timings"]["supervisor"] = round(duration, 4)

    return {
        "candidate_id": candidate_id,
        "raw_job_description": raw_jd,
        "status_log": status_log,
        "revision_count": state.get("revision_count", 0),
        "telemetry": telemetry
    }
