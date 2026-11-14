import time
from typing import Dict, Any, List

class TelemetryTracker:
    """
    Production-grade LLM Native Observability and Metrics Tracker.
    Measures tokens/sec, latency, cost per request, and state transition graph paths.
    """
    def __init__(self):
        self.start_time = time.time()
        self.node_timings: Dict[str, float] = {}
        self.node_tokens: Dict[str, Dict[str, int]] = {}
        self.state_transitions: List[Dict[str, Any]] = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        
        # Standard production pricing for Gemini 2.0 / 1.5 Flash (for simulated cost reporting)
        # $0.075 per 1M input tokens, $0.30 per 1M output tokens
        self.COST_PER_MILLION_INPUT = 0.075
        self.COST_PER_MILLION_OUTPUT = 0.30

    def record_node_start(self, node_name: str):
        self.state_transitions.append({
            "node": node_name,
            "timestamp": time.time(),
            "event": "START"
        })

    def record_node_end(self, node_name: str, duration: float, input_tokens: int = 0, output_tokens: int = 0):
        self.node_timings[node_name] = round(duration, 3)
        self.node_tokens[node_name] = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.state_transitions.append({
            "node": node_name,
            "timestamp": time.time(),
            "duration": round(duration, 3),
            "event": "END"
        })

    def get_summary(self) -> Dict[str, Any]:
        total_duration = max(0.001, time.time() - self.start_time)
        total_tokens = self.total_input_tokens + self.total_output_tokens
        tokens_per_sec = round(total_tokens / total_duration, 2)
        
        simulated_cost = (
            (self.total_input_tokens / 1_000_000) * self.COST_PER_MILLION_INPUT +
            (self.total_output_tokens / 1_000_000) * self.COST_PER_MILLION_OUTPUT
        )
        
        return {
            "total_latency_seconds": round(total_duration, 3),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": total_tokens,
            "tokens_per_second": tokens_per_sec,
            "simulated_cost_usd": round(simulated_cost, 6),
            "free_tier_actual_cost": 0.0,
            "node_timings": self.node_timings,
            "node_tokens": self.node_tokens,
            "state_transition_count": len(self.state_transitions)
        }
