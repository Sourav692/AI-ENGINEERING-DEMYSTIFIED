import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
import tempfile
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ────────────────────────────────────────────────
#  LLM (lazy init)
# ────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
    )

# ────────────────────────────────────────────────
#  Prompt
# ────────────────────────────────────────────────

COVER_LETTER_PROMPT = PromptTemplate.from_template(
    """Write a professional, compelling cover letter (300-450 words) tailored
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
"""
)

# ────────────────────────────────────────────────
#  Streamlit UI
# ────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Cover Letter Generator",
    page_icon="✉️",
    layout="wide"
)

st.title("✉️ AI-Powered Cover Letter Generator")
st.markdown("Upload your resume (PDF) + paste the job description → get a tailored cover letter.")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found. Please set it in your .env file.")
    st.stop()

llm = get_llm()

# ─── Layout ────────────────────────────────────────────────────────────────

col1, col2 = st.columns([5, 5])

with col1:
    st.subheader("Job Description")
    job_desc = st.text_area(
        "Paste the full job description here…",
        height=380,
        placeholder="What You'll Bring:\n• 8+ years experience …",
        key="job_desc_input"
    )

with col2:
    st.subheader("Your Resume (PDF)")
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF only)",
        type=["pdf"],
        accept_multiple_files=False,
        help="Only PDF files are supported."
    )

    generate_clicked = st.button(
        "Generate Cover Letter",
        type="primary",
        disabled=not (uploaded_file and job_desc.strip())
    )

if generate_clicked:
    if not uploaded_file:
        st.warning("Please upload your resume PDF.")
    elif not job_desc.strip():
        st.warning("Please paste the job description.")
    else:
        with st.spinner("Extracting resume text…"):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                loader = PyPDFLoader(tmp_path)
                documents = loader.load()
                resume_text = "\n\n".join(doc.page_content for doc in documents)

                os.unlink(tmp_path)

            except Exception as e:
                st.error(f"Could not read PDF: {e}")
                st.stop()

        with st.spinner("Generating cover letter…"):
            try:
                chain = COVER_LETTER_PROMPT | llm

                response_container = st.empty()
                full_response = ""

                for chunk in chain.stream({
                    "job_description": job_desc,
                    "resume_text": resume_text
                }):
                    content = chunk.content if hasattr(chunk, "content") else str(chunk)
                    full_response += content
                    response_container.markdown(full_response + "▌")

                response_container.markdown(full_response)

                st.success("Cover letter generated!")

                st.download_button(
                    label="Download Cover Letter",
                    data=full_response,
                    file_name="Cover_Letter.md",
                    mime="text/markdown"
                )

            except Exception as e:
                st.error(f"Generation failed: {str(e)}")

st.markdown("---")
st.caption(
    "Powered by Groq (llama-3.3-70b-versatile) • Always review & personalize the output"
)
