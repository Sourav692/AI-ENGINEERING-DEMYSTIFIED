# main.py - Resume AI Toolkit
import streamlit as st
import os
import tempfile
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

# ───────────────────────────────────────────────
# CONFIG (shared across all tools)
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Genie",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

from PIL import Image

logo = Image.open("assets/logo.png")
st.sidebar.image(logo, width=80)

st.sidebar.markdown("**Resume Genie**")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ **GROQ_API_KEY missing**. Add to your `.env` file.")
    st.stop()

@st.cache_resource(show_spinner="🔄 Initializing model...")
def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
    )

llm = get_llm()

# ───────────────────────────────────────────────
# SHARED PDF LOADER
# ───────────────────────────────────────────────
@st.cache_data
def extract_resume_text(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    try:
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        text = "\n\n".join(doc.page_content for doc in docs)
        return text
    finally:
        os.unlink(tmp_path)

# ───────────────────────────────────────────────
# PROMPTS (synced with notebook logic)
# ───────────────────────────────────────────────
COVER_LETTER_PROMPT = PromptTemplate.from_template("""
Write a professional, compelling cover letter (300-450 words) tailored
specifically to the job description below.

Emphasize the candidate's most relevant experience, skills, achievements and
qualifications that directly match or exceed the job requirements.
Use concrete examples from the resume where possible.
Show enthusiasm for the role and company without fabricating information.
Structure the letter in standard business format:
- Header (date, employer's contact if known, or just salutation)
- Opening paragraph: state the position and how you found it + brief why
  you're a strong fit
- 1-2 body paragraphs: highlight strongest matching qualifications with evidence
- Closing paragraph: reiterate interest, call to action, thanks

Job Description:
{job_description}

Candidate's Resume:
{resume_text}

Do not invent any experience, skills or facts not present in the resume.
""")

RESUME_SCORER_PROMPT = """You are an expert resume scorer and ATS optimization specialist with deep
knowledge of recruitment practices across industries.

Task: Carefully analyze how well the candidate's resume matches the job
description below. Base EVERY statement, score, and suggestion strictly and
exclusively on the content actually present in the provided resume and job
description. Do NOT invent, assume, or add any experience, skills, tools,
achievements, or facts that are not explicitly written in the resume.

Job Description:
{job_description}

Candidate's Resume:
{context}

Produce the analysis using exactly the following structure and headings:

Score: [integer]/100
Overall Match: [integer]%

Keywords matched:
- [bullet list of important keywords/phrases from JD that DO appear in the resume]

Missing keywords:
- [bullet list of important/hard-required keywords/phrases from JD that are
  completely absent or extremely weakly represented in the resume]

Readability Score: [integer]/100
ATS Compatibility Score: [integer]/100

2-liner summary:
[One strong sentence summarizing the overall fit]
[One strong sentence naming the single biggest current weakness]

Skill gap analysis:
- [Bullet points - clear skill/tool/experience gaps]
- Focus on the most impactful gaps only (4-8 bullets max)

Overall improvement suggestions:
- [Prioritized, actionable bullet points]
- Include both content and formatting/ATS tips

Industry specific feedback:
- [2-5 bullets tailored to this role's industry/function]

Scoring rubrics:
- Score (0-100): weighted combination of keyword presence, skill relevance,
  experience recency & level, achievements quantification, role progression
- Overall Match %: estimated chance of passing initial ATS + recruiter screen
- Readability: clarity, grammar, formatting, length, action verbs
- ATS Compatibility: standard section headings, keyword density, no
  tables/graphics, machine-readable layout

Be honest, direct, and constructive.
"""

RESUME_CHECKER_PROMPT = PromptTemplate.from_template("""
    You are an advanced resume evaluation assistant. Analyze the provided
    resume in the context document and score it out of 100 based on the
    following criteria: clarity, relevance, format, comprehensiveness,
    and keywords.

    Your response should be structured as follows:

    1. **Score**: Provide the score out of 100.
    2. **Strengths**: List at least three strengths found in the resume.
    3. **Weaknesses**: List at least three weaknesses or areas for
       improvement in the resume.
    4. **Skills Mentioned**: Identify and list the skills that are
       explicitly mentioned in the resume.
    5. **Recommended Skills**: Suggest additional skills that could
       enhance the resume's effectiveness.
    6. **Next Career Path**: Suggest what should be the next career
       paths for this candidate.

    Please ensure your analysis is clear and concise, providing
    actionable insights for improvement.

    Resume:
    {context}
""")

# ───────────────────────────────────────────────
# MAIN UI
# ───────────────────────────────────────────────
st.title("🚀 Resume Genie")
st.markdown("""
**Powered by Groq (llama-3.3-70b-versatile)** • Your all-in-one solution for job applications
""")

# ─── LEFT SIDEBAR: Tool Selector ───
st.sidebar.title("🛠️ Select Tool")
tool = st.sidebar.radio("Choose a service:", [
    "✉️ Cover Letter Generator",
    "📊 Resume-JD Matcher",
    "🔍 Resume Checker",
    "💬 Career Coach Chat"
], index=0, horizontal=False)

# Shared inputs (positioned based on tool)
if tool in ["✉️ Cover Letter Generator", "📊 Resume-JD Matcher"]:
    st.sidebar.subheader("📤 Inputs")
    job_desc = st.sidebar.text_area("Job Description", height=200, key="jd_shared")
    resume_file = st.sidebar.file_uploader("Resume PDF", type="pdf", key="resume_shared")

# ───────────────────────────────────────────────
# TOOL 1: COVER LETTER
# ───────────────────────────────────────────────
if tool == "✉️ Cover Letter Generator":
    st.header("✉️ AI Cover Letter Generator")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Job Description")
        job_description = st.text_area("Paste JD", value=job_desc or "", height=350, key="jd_cl")

    with col2:
        st.subheader("📄 Your Resume")
        uploaded_file = st.file_uploader("Upload PDF", type="pdf", key="cl_resume")
        if uploaded_file:
            if st.button("🔥 Generate Cover Letter", type="primary"):
                with st.spinner("Extracting → Generating..."):
                    resume_text = extract_resume_text(uploaded_file)
                    chain = COVER_LETTER_PROMPT | llm
                    full_response = ""
                    resp_container = st.empty()
                    for chunk in chain.stream({"job_description": job_description, "resume_text": resume_text}):
                        content = chunk.content if hasattr(chunk, "content") else str(chunk)
                        full_response += content
                        resp_container.markdown(full_response + "▌")
                    resp_container.markdown(full_response)
                    st.download_button("💾 Download .md", full_response, "cover_letter.md")

# ───────────────────────────────────────────────
# TOOL 2: RESUME SCORER/MATCHER
# ───────────────────────────────────────────────
elif tool == "📊 Resume-JD Matcher":
    st.header("📊 Resume vs Job Description Matcher")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Job Description")
        job_description = st.text_area("Paste full JD", value=job_desc or "", height=350, key="jd_scorer")

    with col2:
        st.subheader("📄 Resume")
        uploaded_file = st.file_uploader("Upload PDF", type="pdf", key="scorer_resume")
        if uploaded_file:
            st.success("✅ Resume loaded")
            if st.button("📈 Score Match", type="primary"):
                with st.spinner("Analyzing match..."):
                    context = extract_resume_text(uploaded_file)
                    prompt = RESUME_SCORER_PROMPT.format(job_description=job_description, context=context)
                    resp_container = st.empty()
                    full_response = ""
                    for chunk in llm.stream(prompt):
                        content = chunk.content if hasattr(chunk, "content") else str(chunk)
                        full_response += content
                        resp_container.markdown(full_response + "▌")
                    resp_container.markdown(full_response)
                    st.markdown("### 📊 **Analysis Complete**")

# ───────────────────────────────────────────────
# TOOL 3: RESUME CHECKER
# ───────────────────────────────────────────────
elif tool == "🔍 Resume Checker":
    st.header("🔍 Standalone Resume Evaluator")
    uploaded_file = st.file_uploader("Upload resume PDF", type="pdf", key="checker_resume")

    if uploaded_file and st.button("Evaluate Resume", type="primary"):
        with st.spinner("Evaluating..."):
            context = extract_resume_text(uploaded_file)
            chain = RESUME_CHECKER_PROMPT | llm
            resp_container = st.empty()
            full_response = ""
            for chunk in chain.stream({"context": context}):
                content = chunk.content if hasattr(chunk, "content") else str(chunk)
                full_response += content
                resp_container.markdown(full_response + "▌")
            resp_container.markdown(full_response)
            st.markdown("### 📋 **Detailed Evaluation**")

# ───────────────────────────────────────────────
# TOOL 4: CAREER COACH CHAT
# ───────────────────────────────────────────────
elif tool == "💬 Career Coach Chat":
    st.header("💬 Career Coach Chatbot")

    # Resume upload (session-persisted)
    if "resume_context" not in st.session_state:
        st.session_state.resume_context = None
        st.session_state.chat_history = []

    uploaded_file = st.file_uploader("Upload resume first", type="pdf", key="chat_resume")
    if uploaded_file and st.session_state.resume_context is None:
        context = extract_resume_text(uploaded_file)
        st.session_state.resume_context = context
        st.rerun()

    if not st.session_state.resume_context:
        st.warning("👆 Upload your resume to start chatting!")
        st.stop()

    # Layout: Left=Resume | Right=Chat
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("📄 Your Resume")
        with st.expander("View full text", expanded=True):
            st.text_area("", st.session_state.resume_context, height=500, disabled=True)

    with right_col:
        st.subheader("🤖 Career Coach")
        system_msg = SystemMessage(content=f"""
    You are a professional career coach and resume mentor.

    You help with:
    - Career Guidance
    - Resume Improvements
    - Interview Preparation
    - Job Search Strategy
    - Skill Gap Analysis

    Candidate Resume:
    {st.session_state.resume_context}
    """)

        # Chat history
        for msg in st.session_state.chat_history:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            with st.chat_message(role):
                st.markdown(msg.content)

        # Chat input
        if prompt := st.chat_input("Ask about career, resume, interviews..."):
            st.session_state.chat_history.append(HumanMessage(content=prompt))
            with st.chat_message("assistant"):
                messages = [system_msg] + st.session_state.chat_history
                resp_container = st.empty()
                full_resp = ""
                for chunk in llm.stream(messages):
                    full_resp += chunk.content
                    resp_container.markdown(full_resp + "▌")
                resp_container.markdown(full_resp)
            st.session_state.chat_history.append(AIMessage(content=full_resp))
            st.rerun()

# ───────────────────────────────────────────────
# FOOTER
# ───────────────────────────────────────────────
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.caption("✅ **Ready**: All 4 tools live")
with col2:
    st.caption("🔑 **API**: Groq (llama-3.3-70b-versatile)")

st.sidebar.markdown("---")
st.sidebar.caption("**Pro Tips**: Use sidebar to switch tools instantly ⚡")
