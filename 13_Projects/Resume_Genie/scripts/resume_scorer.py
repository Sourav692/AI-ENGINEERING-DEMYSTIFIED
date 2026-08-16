import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ───────────────────────────────────────────────
#   CONFIG
# ───────────────────────────────────────────────
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found. Please set it in your .env file.")
    st.stop()

PROMPT_TEMPLATE = """You are an expert resume scorer and ATS optimization specialist with deep
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

# ───────────────────────────────────────────────
#   STREAMLIT APP
# ───────────────────────────────────────────────

st.set_page_config(page_title="Resume Scorer", layout="wide")

st.title("📄 Resume Matcher & Scorer")
st.markdown("Upload your resume (PDF) and paste the job description to get a detailed match analysis.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Job Description")
    job_description = st.text_area(
        "Paste the full job description here",
        height=320,
        placeholder="Responsibilities...\nRequirements...\nSkills...\n",
        key="jd_input"
    )

with col2:
    st.subheader("Your Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"], key="resume_uploader")

    if uploaded_file is not None:
        st.success("Resume uploaded ✓")

# ── Analyze button ────────────────────────────────────────

if st.button("Analyze Resume Match", type="primary", disabled=not (uploaded_file and job_description.strip())):

    with st.spinner("Extracting resume text..."):
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            loader = PyPDFLoader(tmp_path)
            documents = loader.load()
            context = "\n\n".join(doc.page_content for doc in documents)

            os.unlink(tmp_path)  # clean up

        except Exception as e:
            st.error(f"Could not read the PDF: {e}")
            st.stop()

    if not context.strip():
        st.error("No readable text found in the resume PDF.")
        st.stop()

    # Build final prompt
    prompt = PROMPT_TEMPLATE.format(
        job_description=job_description.strip(),
        context=context.strip()
    )

    with st.spinner("Analyzing resume match..."):
        try:
            chat = ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=GROQ_API_KEY,
            )

            # Stream the response
            st.subheader("📊 Resume Analysis Result")
            response_container = st.empty()
            full_response = ""

            for chunk in chat.stream(prompt):
                content = chunk.content if hasattr(chunk, "content") else str(chunk)
                full_response += content
                response_container.markdown(full_response + "▌")

            response_container.markdown(full_response)

        except Exception as e:
            st.error(f"API error: {str(e)}")
            if "rate limit" in str(e).lower():
                st.warning("Rate limit reached — please wait a few minutes and try again.")

# Footer
st.markdown("---")
st.caption("Powered by Groq (llama-3.3-70b-versatile)")
