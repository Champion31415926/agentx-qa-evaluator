import streamlit as st
import requests
import json
import re

st.set_page_config(page_title="AgentX: Multi-Agent Grading System", layout="wide", page_icon="🧠")

st.markdown("""
    <style>
    .stSlider { padding-bottom: 15px; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; }
    .agent-box { padding: 10px; border-radius: 5px; margin-bottom: 5px; font-size: 0.9em; }
    .thesis { background-color: #e3f2fd; border-left: 4px solid #2196f3; color: #0d47a1; }
    .antithesis { background-color: #ffebee; border-left: 4px solid #f44336; color: #b71c1c; }
    .synthesis { background-color: #e8f5e9; border-left: 4px solid #4caf50; color: #1b5e20; }
    .plan-card { background-color: #fff3cd; border: 1px solid #ffeeba; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if "rubric_rows" not in st.session_state:
    st.session_state.rubric_rows = [{"text": "", "score": 1.0}]
if "question_input" not in st.session_state:
    st.session_state.question_input = ""
if "answer_input" not in st.session_state:
    st.session_state.answer_input = ""

st.title("🧠 AgentX: Dialectical Evaluation Engine")
st.caption("Powered by Multi-Agent Debate Logic (Thesis-Antithesis-Synthesis)")

with st.sidebar:
    st.header("🎛️ Agent Configuration")
    api_url = st.text_input("Backend Endpoint", value="http://localhost:8000/evaluate")
    
    st.divider()
    
    subject = st.selectbox(
        "Domain Context",
        ("Mechanical Engineering", "Medical Science", "Law & Jurisprudence", 
         "Computer Science", "Humanities", "Business & Finance", "General Science"),
        index=6
    )
    
    strictness = st.slider("⚖️ Rigor Level", 0.0, 1.0, 0.7)
    tone = st.slider("📢 Tone (Coach ↔ Critic)", 0.0, 1.0, 0.5)
    audience = st.slider("👥 Audience (Layman ↔ Expert)", 0.0, 1.0, 0.6)

    st.markdown("---")
    st.markdown("🎯 **Focus Dimensions**")
    
    all_dimensions = ["Accuracy", "Reasoning", "Terminology", "Completeness", "Safety"]
    focus_areas = []
    
    col_a, col_b = st.columns(2)
    for i, dim in enumerate(all_dimensions):
        with col_a if i % 2 == 0 else col_b:
            is_checked = dim in ["Accuracy", "Reasoning"]
            if st.checkbox(dim, value=is_checked):
                focus_areas.append(dim)

    st.divider()
    
    _, center_col, _ = st.columns([1, 3, 1])
    with center_col:
        if st.button("🧹 Clear Session"):
            st.session_state.rubric_rows = [{"text": "", "score": 1.0}]
            st.session_state.answer_input = ""
            st.session_state.result = None
            st.rerun()

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1️⃣ Assessment Criteria")
    
    question = st.text_area(
        "Problem Statement", 
        value=st.session_state.question_input, 
        height=100,
        placeholder="Enter the exam question here..."
    )
    
    st.markdown("###### Rubric Points")
    
    def add_row():
        st.session_state.rubric_rows.append({"text": "", "score": 1.0})

    for i, row in enumerate(st.session_state.rubric_rows):
        c1, c2 = st.columns([4, 1])
        st.session_state.rubric_rows[i]["text"] = c1.text_input(
            f"Point {i+1}", 
            value=row["text"], 
            key=f"rubric_txt_{i}", 
            label_visibility="collapsed",
            placeholder="Key concept required..."
        )
        st.session_state.rubric_rows[i]["score"] = c2.number_input(
            f"Max {i+1}", 
            value=float(row["score"]), 
            step=0.5, 
            key=f"rubric_sc_{i}", 
            label_visibility="collapsed"
        )

    st.button("➕ Add Criterion", on_click=add_row)

with col2:
    st.subheader("2️⃣ Candidate Response")
    student_answer = st.text_area(
        "Student Answer", 
        value=st.session_state.answer_input, 
        height=350,
        placeholder="Paste the student's response here..."
    )
    
    if st.button("🚀 Run Multi-Agent Evaluation", type="primary", use_container_width=True):
        reference_answers = [
            {"text": r["text"], "max_score": r["score"]} 
            for r in st.session_state.rubric_rows if r["text"].strip()
        ]
        
        if not reference_answers:
            st.error("Please define at least one rubric point.")
        else:
            payload = {
                "task_id": "live_demo",
                "question": question,
                "reference_answers": reference_answers,
                "purple_answer": student_answer,
                "subject": subject,
                "strictness": strictness,
                "tone": tone,
                "audience": audience,
                "focus_areas": focus_areas
            }

            with st.spinner("🤖 Agents are debating (Thesis vs. Antithesis)..."):
                try:
                    response = requests.post(api_url, json=payload, timeout=120)
                    if response.status_code == 200:
                        st.session_state.result = response.json()
                    else:
                        st.error(f"Server Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection Failed: {e}")

def parse_debate_log(log_text):
    t_match = re.search(r'THESIS[:\s]*(.*?)(?=ANTITHESIS|SYNTHESIS|$)', log_text, re.IGNORECASE | re.DOTALL)
    a_match = re.search(r'ANTITHESIS[:\s]*(.*?)(?=SYNTHESIS|THESIS|$)', log_text, re.IGNORECASE | re.DOTALL)
    if not a_match:
        a_match = re.search(r'ANTI[:\s]*(.*?)(?=SYNTHESIS|THESIS|$)', log_text, re.IGNORECASE | re.DOTALL)
    s_match = re.search(r'SYNTHESIS[:\s]*(.*?)(?=THESIS|ANTITHESIS|$)', log_text, re.IGNORECASE | re.DOTALL)
    
    return {
        "THESIS": t_match.group(1).strip().replace("*", "") if t_match else "No thesis found.",
        "ANTITHESIS": a_match.group(1).strip().replace("*", "") if a_match else "No antithesis found.",
        "SYNTHESIS": s_match.group(1).strip().replace("*", "") if s_match else "No synthesis found."
    }

if 'result' in st.session_state and st.session_state.result:
    res = st.session_state.result
    st.markdown("---")
    
    st.header("📊 Evaluation Report")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Final Grade", f"{res['score']*100:.1f}%")
    m2.metric("Points Awarded", f"{res['awarded_score']} / {res['max_score']}")
    m3.metric("Logic Mode", "Dialectical")
    m4.metric("Subject Context", subject)
    
    st.progress(min(1.0, max(0.0, float(res['score']))))

    meta = res.get('metadata', {})
    breakdown = meta.get('breakdown', [])
    study_plan = meta.get('study_plan', {})

    tab_audit, tab_debate, tab_plan = st.tabs(["📝 Detailed Audit", "⚔️ Agent Debate Logs", "📅 Adaptive Study Plan"])
    
    with tab_audit:
        st.info(meta.get('feedback', ''))
        for idx, item in enumerate(breakdown):
            with st.expander(f"{idx+1}. {item['rubric_point']} ({item['awarded_score']}/{item['max_score']})", expanded=True):
                status_color = "green" if item['status'] == "match" else ("orange" if item['status'] == "partial" else "red")
                st.markdown(f"**Status:** :{status_color}[{item['status'].upper()}]")
                st.markdown(f"**Evidence:** `{item['evidence_found']}`")
                st.markdown(f"**Expert Comment:** {item['comment']}")

    with tab_debate:
        st.markdown("### Internal Cognitive Process")
        st.caption("Visualizing the Thesis-Antithesis-Synthesis logic chain.")
        
        for idx, item in enumerate(breakdown):
            st.markdown(f"**Criterion {idx+1}: {item['rubric_point']}**")
            log_content = item.get('reflexion_log', '')
            phases = parse_debate_log(log_content)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="agent-box thesis"><b>🔹 THESIS (Recognize)</b><br>{phases["THESIS"]}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="agent-box antithesis"><b>🔸 ANTITHESIS (Critique)</b><br>{phases["ANTITHESIS"]}</div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="agent-box synthesis"><b>✅ SYNTHESIS (Resolve)</b><br>{phases["SYNTHESIS"]}</div>', unsafe_allow_html=True)
            st.divider()

    with tab_plan:
        if study_plan and any(study_plan.values()):
            st.markdown(f'''
                <div class="plan-card">
                    <h3 style="color: #856404; margin-top: 0;">🎯 Tailored Improvement Plan</h3>
                    <div style="margin-bottom: 15px;">
                        <b style="color: #856404;">⚠️ Critical Gap Identified:</b><br>
                        <span style="color: #333;">{study_plan.get('identified_gap', 'No specific gap identified.')}</span>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <b style="color: #856404;">🔭 Recommended Focus:</b><br>
                        <span style="color: #333;">{study_plan.get('recommended_focus', 'Review core concepts related to this criterion.')}</span>
                    </div>
                    <div>
                        <b style="color: #856404;">⚡ Immediate Action Item:</b><br>
                        <span style="color: #333;">{study_plan.get('action_item', 'Consult textbook section on this topic for precise terminology.')}</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.info("No specific study plan generated for this response.")