import streamlit as st
import time
import json
from pathlib import Path

# Setup Path
BASE_DIR = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(BASE_DIR))

from src.db import list_candidate_ids, get_candidate_profile
from src.vector_store import query_candidate_evidence, init_vector_store
from src.graph import run_calibration_pipeline
import src.config as config

st.set_page_config(
    page_title="AuditFlow — Google FDE Talent Calibration Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a73e8;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #5f6368;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1.2rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge-met {
        background-color: #e6f4ea;
        color: #137333;
        padding: 0.25rem 0.6rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-gap {
        background-color: #fef7e0;
        color: #b06000;
        padding: 0.25rem 0.6rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .stMetric {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Engine Configuration")
    
    # API Keys
    gemini_key_input = st.text_input(
        "Google Gemini API Key",
        value=config.GEMINI_API_KEY,
        type="password",
        help="Powers the 4 LangGraph agents. Free at https://aistudio.google.com/apikey"
    )
    if gemini_key_input:
        config.GEMINI_API_KEY = gemini_key_input
        
    hf_token_input = st.text_input(
        "Hugging Face Token (Read)",
        value=config.HF_TOKEN,
        type="password",
        help="Powers serverless embeddings via HF API. Free at https://huggingface.co/settings/tokens"
    )
    if hf_token_input:
        config.HF_TOKEN = hf_token_input

    st.markdown("---")
    st.markdown("### 📊 System Status")
    
    if config.has_gemini_key():
        st.success("🟢 Gemini API: Connected (Live)")
    else:
        st.info("🔵 Gemini API: Offline Test Mode (Deterministic)")

    if config.has_hf_token():
        st.success("🟢 Hugging Face API: Connected (Live)")
    else:
        st.info("🔵 HF API: Local Deterministic Embeddings")

    st.markdown("---")
    st.markdown("### 🎯 Architecture Highlights")
    st.markdown("""
    - **Structured Data:** SQLite relational store
    - **Unstructured Data:** ChromaDB vector store
    - **Orchestration:** LangGraph StateGraph
    - **Patterns:** ReAct, Hierarchical, Self-Reflection
    - **Target Role:** Google Forward Deployed Engineer
    """)

# Header
st.markdown('<div class="main-header">🎯 Enterprise Talent & Requisition Calibration Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-Agent AI System with Cyclic Self-Reflection, Hybrid RAG, and LLM-Native Telemetry</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Job Requisition", 
    "👤 Candidate Ground Truth", 
    "🤖 Multi-Agent Audit Run", 
    "💡 Technical Discovery Rubric",
    "📈 Observability & Telemetry"
])

# Default Requisition Text
default_jd_path = BASE_DIR / "data" / "docs" / "google_fde_requisition.md"
if default_jd_path.exists():
    with open(default_jd_path, "r", encoding="utf-8") as f:
        default_jd = f.read()
else:
    default_jd = "Requisition file not found."

with tab1:
    st.markdown("### Target Requisition Specification")
    st.info("Pre-loaded with the **Google Forward Deployed Engineer (FDE) / AI Engineer** job description.")
    jd_input = st.text_area("Job Description Content", value=default_jd, height=350)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Minimum Qualifications Highlighted:**")
        st.markdown("""
        * Penultimate academic year in CS / Engineering degree
        * Python programming, Data Structures & Algorithms
        * Production-grade AI solutions deployed on Cloud (e.g. GCP)
        * Structured & unstructured data pipelines (Vector DBs + RAG)
        """)
    with col_b:
        st.markdown("**Preferred Qualifications Highlighted:**")
        st.markdown("""
        * Multi-agent systems with **LangGraph / CrewAI**
        * Complex patterns: **ReAct, self-reflection, hierarchical delegation**
        * Leading technical discovery sessions
        * LLM-native metrics: **tokens/sec, cost-per-request, granular tracing**
        """)

with tab2:
    st.markdown("### Candidate Ground-Truth Profile (SQLite + ChromaDB)")
    candidates = list_candidate_ids()
    cand_options = {f"{c['name']} ({c['university']})": c['id'] for c in candidates}
    selected_label = st.selectbox("Select Candidate to Inspect:", list(cand_options.keys()))
    selected_id = cand_options[selected_label]
    
    profile = get_candidate_profile(selected_id)
    if profile:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Candidate Name", profile['name'])
        col2.metric("University", profile['university'])
        col3.metric("GPA / Performance", f"{profile['gpa']}" if profile['gpa'] else "N/A")
        col4.metric("Target Role", profile['target_role'])
        
        st.markdown("#### 1. Verified Structured Skills (SQLite)")
        skills_df = [
            {"Category": s["category"], "Skill": s["skill_name"], "Level": s["proficiency_level"], "Proof": s["proof_details"]}
            for s in profile.get("skills", [])
        ]
        st.dataframe(skills_df, use_container_width=True)
        
        st.markdown("#### 2. Production Projects & Architectural Highlights")
        for proj in profile.get("projects", []):
            with st.expander(f"📁 {proj['title']} — Stack: {proj['primary_stack']}"):
                st.write(f"**Impact Summary:** {proj['metrics_summary']}")
                st.write(f"**Repository:** `{proj['repo_url']}`")
                
        st.markdown("#### 3. Competitive Assessments & Problem Solving")
        for ass in profile.get("assessments", []):
            st.markdown(f"- **{ass['domain']}:** {ass['metric_label']} (Percentile: **{ass['score_percentile']}%**, Problems: **{ass['problems_solved']}**)")

with tab3:
    st.markdown("### Execute LangGraph Multi-Agent Calibration Audit")
    
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        target_cand = st.selectbox("Audit Candidate:", list(cand_options.keys()), key="audit_selector")
        target_id = cand_options[target_cand]
    with col_btn:
        st.write("")
        st.write("")
        run_btn = st.button("🚀 Run Multi-Agent Audit", type="primary", use_container_width=True)
        
    if run_btn:
        with st.spinner("Executing LangGraph StateGraph (Supervisor -> Parser -> Retriever -> Synthesizer -> Critic)..."):
            progress_bar = st.progress(0)
            time.sleep(0.1)
            progress_bar.progress(25)
            
            result = run_calibration_pipeline(target_id, jd_input)
            progress_bar.progress(100)
            st.session_state["last_result"] = result
            st.success("Calibration audit completed with self-reflection validation!")

    if "last_result" in st.session_state:
        res = st.session_state["last_result"]
        
        st.markdown("---")
        st.markdown("### 🏆 Calibration Audit Deliverable")
        
        score_col, status_col, iter_col = st.columns([1, 2, 1])
        with score_col:
            st.metric("Requisition Match Score", f"{res.get('match_score', 0)}%")
        with status_col:
            critique = res.get("critique", {})
            st.markdown(f"**Critic Status:** `{critique.get('status', 'PASS')}`")
            st.markdown(f"*{critique.get('reasoning', '')}*")
        with iter_col:
            st.metric("Reflection Loops", f"{res.get('revision_count', 1)} iteration(s)")

        st.markdown("#### Executive Summary")
        st.info(res.get("synthesis_draft", "No draft available."))
        
        st.markdown("#### Qualification Breakdown")
        breakdown = res.get("qualification_breakdown", {})
        col_m, col_p = st.columns(2)
        with col_m:
            st.markdown("**Minimum Qualifications:**")
            for m in breakdown.get("minimum_qualifications_met", []):
                st.markdown(f'<span class="badge-met">✓ MET</span> {m}', unsafe_allow_html=True)
            for g in breakdown.get("minimum_qualifications_gaps", []):
                st.markdown(f'<span class="badge-gap">⚠ GAP</span> {g}', unsafe_allow_html=True)
        with col_p:
            st.markdown("**Preferred Qualifications:**")
            for p in breakdown.get("preferred_qualifications_met", []):
                st.markdown(f'<span class="badge-met">✓ MET</span> {p}', unsafe_allow_html=True)
            for g in breakdown.get("preferred_qualifications_gaps", []):
                st.markdown(f'<span class="badge-gap">⚠ GAP</span> {g}', unsafe_allow_html=True)

        st.markdown("#### Agent Execution Event Trace")
        with st.expander("View LangGraph State Log"):
            for log_msg in res.get("status_log", []):
                st.markdown(f"`{log_msg}`")

with tab4:
    st.markdown("### 💡 Technical Discovery Rubric (FDE Interview Calibration)")
    st.info("These probing questions are autonomously generated by the Synthesizer and calibrated directly against the candidate's real project portfolio to test depth and eliminate resume inflation.")
    
    if "last_result" in st.session_state:
        rubric = st.session_state["last_result"].get("discovery_rubric", [])
        for idx, item in enumerate(rubric):
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <h4>#{idx + 1}: {item.get('category', 'Technical Probe')}</h4>
                    <p style="font-size: 1.05rem; font-weight: 500; color: #202124;">
                        <b>Probing Question:</b> "{item.get('probing_question', '')}"
                    </p>
                    <p style="color: #137333; margin-bottom: 0.3rem;">
                        <b>Expected Signal:</b> {item.get('expected_signal', '')}
                    </p>
                    <p style="color: #5f6368; font-size: 0.88rem;">
                        <i>Calibration Context: {item.get('calibrated_for_candidate', '')}</i>
                    </p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.write("Run the calibration audit in Tab 3 to generate the personalized technical discovery rubric.")

with tab5:
    st.markdown("### 📈 Observability & LLM-Native Telemetry Dashboard")
    st.info("Demonstrates granular tracking required by Google FDE teams: Latency, token throughput (tokens/sec), and simulated vs actual cost.")
    
    if "last_result" in st.session_state:
        telem = st.session_state["last_result"].get("telemetry", {})
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Latency", f"{telem.get('total_latency_seconds', 0)}s")
        m2.metric("Token Throughput", f"{telem.get('tokens_per_second', 0)} tok/s")
        m3.metric("Total Tokens", telem.get('total_tokens', 0))
        m4.metric("Simulated Prod Cost", f"${telem.get('simulated_cost_usd', 0)}")
        
        st.markdown("#### Node Latency Breakdown")
        timings = telem.get("node_timings", {})
        st.bar_chart(timings)
        
        st.markdown("#### Cost & Efficiency Summary")
        st.write(f"- **Input Tokens:** {telem.get('total_input_tokens', 0):,}")
        st.write(f"- **Output Tokens:** {telem.get('total_output_tokens', 0):,}")
        st.write(f"- **Simulated Cost (at $0.075/$0.30 per 1M):** ${telem.get('simulated_cost_usd', 0):.6f}")
        st.write(f"- **Actual Free-Tier Cost:** `{telem.get('actual_cost', '$0.00')}`")
    else:
        st.write("Run the audit in Tab 3 to view real-time latency and token observability metrics.")
