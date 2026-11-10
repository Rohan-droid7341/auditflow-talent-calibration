import time
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.state import CalibrationState
from src.agents.supervisor import supervisor_node
from src.agents.req_parser import req_parser_node
from src.agents.portfolio_retriever import portfolio_retriever_node
from src.agents.synthesizer import synthesizer_node
from src.agents.critic import critic_node

def should_revise(state: CalibrationState) -> Literal["synthesizer", "__end__"]:
    """
    Conditional Reflection Edge:
    Evaluates Critic Agent feedback. If unsupported claims or contradictions are found
    and the retry limit (< 2) has not been exceeded, loops back to the Synthesizer.
    Otherwise, terminates graph execution at END.
    """
    critique = state.get("critique", {})
    status = critique.get("status", "PASS")
    revision_count = state.get("revision_count", 0)
    
    if status == "REVISE" and revision_count < 2:
        return "synthesizer"
    return END

def build_calibration_graph():
    """
    Constructs the LangGraph StateGraph with hierarchical delegation and cyclic reflection.
    """
    workflow = StateGraph(CalibrationState)
    
    # 1. Register Nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("req_parser", req_parser_node)
    workflow.add_node("portfolio_retriever", portfolio_retriever_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("critic", critic_node)
    
    # 2. Register Deterministic Edges
    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "req_parser")
    workflow.add_edge("req_parser", "portfolio_retriever")
    workflow.add_edge("portfolio_retriever", "synthesizer")
    workflow.add_edge("synthesizer", "critic")
    
    # 3. Register Conditional Self-Reflection Edge
    workflow.add_conditional_edges(
        "critic",
        should_revise,
        {
            "synthesizer": "synthesizer",
            END: END
        }
    )
    
    # In-memory checkpointer for state persistence
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app

def run_calibration_pipeline(candidate_id: str, raw_job_description: str) -> Dict[str, Any]:
    """
    Executes the full multi-agent pipeline and returns complete deliverables with telemetry.
    """
    start_t = time.time()
    app = build_calibration_graph()
    
    initial_state: CalibrationState = {
        "candidate_id": candidate_id,
        "raw_job_description": raw_job_description,
        "status_log": [],
        "revision_count": 0,
        "telemetry": {
            "start_time": start_t,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "node_timings": {}
        }
    }
    
    config = {"configurable": {"thread_id": f"talent_audit_{candidate_id}_{int(start_t)}"}}
    final_state = app.invoke(initial_state, config=config)
    
    # Finalize Telemetry calculations
    total_duration = max(0.001, time.time() - start_t)
    telem = final_state.get("telemetry", {})
    in_tok = telem.get("total_input_tokens", 0)
    out_tok = telem.get("total_output_tokens", 0)
    total_tok = in_tok + out_tok
    
    telem["total_latency_seconds"] = round(total_duration, 3)
    telem["total_tokens"] = total_tok
    telem["tokens_per_second"] = round(total_tok / total_duration, 2)
    telem["simulated_cost_usd"] = round(
        (in_tok / 1_000_000) * 0.075 + (out_tok / 1_000_000) * 0.30, 6
    )
    telem["actual_cost"] = "$0.00 (Free Tier / Local Execution)"
    final_state["telemetry"] = telem
    
    return final_state
