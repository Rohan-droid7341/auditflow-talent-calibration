import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.db import list_candidate_ids, get_candidate_profile
from src.vector_store import init_vector_store, query_candidate_evidence
from src.graph import run_calibration_pipeline

def test_sqlite_layer():
    print("[TEST 1/5] Testing SQLite Structured Ground-Truth Layer...")
    candidates = list_candidate_ids()
    assert len(candidates) >= 3, f"Expected at least 3 seeded candidates, found {len(candidates)}"
    
    rohan = get_candidate_profile("rohan_garg")
    assert rohan is not None, "Candidate 'rohan_garg' not found in SQLite"
    assert len(rohan["skills"]) >= 5, "Expected at least 5 verified skills for Rohan Garg"
    assert len(rohan["projects"]) >= 3, "Expected at least 3 projects for Rohan Garg"
    print(f" -> PASS: SQLite loaded {len(candidates)} candidates. Rohan Garg profile verified.")

def test_vector_store_layer():
    print("[TEST 2/5] Testing ChromaDB Unstructured Vector Retrieval Layer...")
    collection = init_vector_store(force_reindex=True)
    count = collection.count()
    assert count > 0, "ChromaDB collection is empty after indexing"
    
    matches = query_candidate_evidence("rohan_garg", "LangGraph multi-agent architecture and Gemini API", n_results=2)
    assert len(matches) > 0, "Vector similarity search returned 0 matches for candidate query"
    print(f" -> PASS: ChromaDB indexed {count} document sections. Retrieved {len(matches)} matching evidence chunks.")

def test_langgraph_pipeline():
    print("[TEST 3/5] Testing LangGraph Multi-Agent State Machine End-to-End...")
    with open(PROJECT_ROOT / "data" / "docs" / "google_fde_requisition.md", "r", encoding="utf-8") as f:
        jd_text = f.read()
        
    result = run_calibration_pipeline("rohan_garg", jd_text)
    
    assert "match_score" in result, "Result missing match_score"
    assert "qualification_breakdown" in result, "Result missing qualification_breakdown"
    assert "discovery_rubric" in result, "Result missing discovery_rubric"
    assert len(result["discovery_rubric"]) >= 2, "Expected at least 2 tailored discovery questions"
    
    print(f" -> PASS: Graph executed successfully. Match Score: {result['match_score']}%.")
    print(f" -> Generated {len(result['discovery_rubric'])} discovery questions tailored to candidate.")

def test_self_reflection_loop():
    print("[TEST 4/5] Testing Self-Reflection & Anti-Hallucination Critic Node...")
    with open(PROJECT_ROOT / "data" / "docs" / "google_fde_requisition.md", "r", encoding="utf-8") as f:
        jd_text = f.read()

    # Test candidate with known skill gaps (Jordan Taylor)
    result = run_calibration_pipeline("jordan_taylor", jd_text)
    critique = result.get("critique", {})
    
    assert "status" in critique, "Critique node did not emit status"
    assert "reasoning" in critique, "Critique node did not emit reasoning"
    print(f" -> PASS: Self-Reflection Critic executed. Status: {critique['status']}. Iterations: {result['revision_count']}.")

def test_llm_native_metrics():
    print("[TEST 5/5] Testing LLM-Native Observability & Telemetry Metrics...")
    with open(PROJECT_ROOT / "data" / "docs" / "google_fde_requisition.md", "r", encoding="utf-8") as f:
        jd_text = f.read()

    result = run_calibration_pipeline("rohan_garg", jd_text)
    telem = result.get("telemetry", {})
    
    assert "total_latency_seconds" in telem and telem["total_latency_seconds"] > 0, "Invalid latency metric"
    assert "total_tokens" in telem and telem["total_tokens"] > 0, "Invalid token metric"
    assert "tokens_per_second" in telem, "Invalid tokens/sec metric"
    assert "simulated_cost_usd" in telem, "Invalid simulated cost metric"
    
    print(f" -> PASS: Telemetry captured:")
    print(f"    * Latency: {telem['total_latency_seconds']}s")
    print(f"    * Total Tokens: {telem['total_tokens']}")
    print(f"    * Throughput: {telem['tokens_per_second']} tokens/sec")
    print(f"    * Simulated Production Cost: ${telem['simulated_cost_usd']}")
    print(f"    * Actual Free-Tier Cost: {telem['actual_cost']}")

def run_all_tests():
    print("=================================================================")
    print("   ENTERPRISE TALENT CALIBRATION PLATFORM - VERIFICATION SUITE   ")
    print("=================================================================")
    try:
        test_sqlite_layer()
        test_vector_store_layer()
        test_langgraph_pipeline()
        test_self_reflection_loop()
        test_llm_native_metrics()
        print("=================================================================")
        print("   ALL 5 VERIFICATION TESTS PASSED SUCCESSFULLY!                ")
        print("=================================================================")
    except AssertionError as e:
        print(f"\n[FAIL] Assertion Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
