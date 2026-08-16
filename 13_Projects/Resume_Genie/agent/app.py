import os
import sys

# Ensure the project root is on sys.path so `agent` package is importable
# when Streamlit runs this file directly (e.g. `streamlit run agent/app.py`)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
from PIL import Image

from agent.graph import build_graph, TOOL_LABELS
from agent.pdf_utils import extract_resume_text

load_dotenv()

# ─────────────────────────────────────────────
# Page config (must be first Streamlit command)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Genie",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Session state initialization
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "job_description" not in st.session_state:
    st.session_state.job_description = None

# ─────────────────────────────────────────────
# LLM + Graph (cached)
# ─────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


@st.cache_resource(show_spinner=False)
def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
    )


@st.cache_resource(show_spinner=False)
def get_graph():
    return build_graph(get_llm())


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    logo = Image.open("assets/logo.png")
    st.image(logo, width=80)
    st.markdown("### Resume Genie")
    st.caption("Chat-first AI agent for your career")
    st.markdown("---")

    # Resume upload
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
    if uploaded_file:
        if st.session_state.resume_text is None:
            with st.spinner("Extracting resume text..."):
                st.session_state.resume_text = extract_resume_text(uploaded_file)
            st.success(f"Resume loaded!")
        else:
            st.success("Resume loaded!")

    if st.session_state.resume_text:
        with st.expander("View resume text", expanded=False):
            st.text_area(
                "", st.session_state.resume_text, height=300, disabled=True
            )

    st.markdown("---")

    # Job description input
    jd = st.text_area(
        "Job Description (optional)",
        height=200,
        key="jd_input",
        placeholder="Paste a job description here to enable\nresume scoring and cover letter generation...",
    )
    if jd.strip():
        st.session_state.job_description = jd.strip()
    else:
        st.session_state.job_description = None

    st.markdown("---")

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

    st.caption("Powered by Groq (llama-3.3-70b-versatile)")

# ─────────────────────────────────────────────
# API key check
# ─────────────────────────────────────────────
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found. Please set it in your `.env` file.")
    st.stop()

# ─────────────────────────────────────────────
# Main chat area
# ─────────────────────────────────────────────
st.title("🚀 Resume Genie")
st.markdown(
    "Chat naturally — I'll auto-detect what you need and run the right tools. "
    "Try: *\"Check my resume\"*, *\"Score against this JD\"*, *\"Write a cover letter\"*, "
    "*\"Give me a full analysis\"*, or *\"Help me prep for interviews\"*."
)

# Render chat history
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# Gate: need resume first
if not st.session_state.resume_text:
    st.info("👈 Upload your resume in the sidebar to get started.")
    st.stop()

# ─────────────────────────────────────────────
# Chat input + graph execution
# ─────────────────────────────────────────────
if user_input := st.chat_input(
    "Ask about your resume, career, interviews..."
):
    user_msg = HumanMessage(content=user_input)
    st.session_state.messages.append(user_msg)

    with st.chat_message("user"):
        st.markdown(user_input)

    # Build graph state from session
    state = {
        "messages": list(st.session_state.messages),
        "resume_text": st.session_state.resume_text,
        "job_description": st.session_state.job_description,
        "tool_choice": None,
        "tool_chain": None,
        "tool_outputs": None,
    }

    with st.chat_message("assistant"):
        status_container = st.empty()
        result_container = st.empty()

        status_container.markdown("🤔 *Thinking...*")

        # Stream the graph node-by-node
        ai_message = None
        for event in get_graph().stream(state, stream_mode="updates"):
            for node_name, node_output in event.items():
                # Show status for tool nodes
                if node_name in TOOL_LABELS:
                    label = TOOL_LABELS[node_name]
                    status_container.markdown(f"⚙️ *Running {label}...*")

                if node_name == "career_coach":
                    status_container.markdown("💬 *Coaching...*")

                # Capture the final AI message
                if "messages" in node_output:
                    for msg in node_output["messages"]:
                        if isinstance(msg, AIMessage):
                            ai_message = msg

        # Clear status and show result
        status_container.empty()

        if ai_message:
            result_container.markdown(ai_message.content)
            st.session_state.messages.append(ai_message)
        else:
            result_container.markdown(
                "I couldn't process that request. Please try again."
            )

    st.rerun()
