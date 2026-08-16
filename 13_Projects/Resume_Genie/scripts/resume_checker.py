import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ───────────────────────────────────────────────
#  Config
# ───────────────────────────────────────────────
st.set_page_config(page_title="Resume Checker", layout="wide")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found. Please set it in your .env file.")
    st.stop()

# ───────────────────────────────────────────────
#  LLM
# ───────────────────────────────────────────────
@st.cache_resource(show_spinner="Initializing model...")
def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
    )

llm = get_llm()

# ───────────────────────────────────────────────
#  Prompt
# ───────────────────────────────────────────────
EVAL_PROMPT = """
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
"""

prompt_template = PromptTemplate(
    input_variables=["context"],
    template=EVAL_PROMPT
)

# ───────────────────────────────────────────────
#  UI
# ───────────────────────────────────────────────
st.title("📄 Resume Checker")
st.markdown("Upload your resume (PDF) → get a detailed score & improvement suggestions")

col1, col2 = st.columns([3, 2])

with col1:
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF only)",
        type=["pdf"],
        accept_multiple_files=False,
        help="Only PDF files are supported at the moment"
    )

    evaluate_button = st.button("Evaluate Resume", type="primary", disabled=not uploaded_file)

if evaluate_button and uploaded_file:
    with st.spinner("Reading PDF → Evaluating resume..."):
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

            # Load PDF
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()
            context = "\n\n".join(doc.page_content for doc in documents)

            # Clean up
            os.unlink(tmp_path)

            if not context.strip():
                st.error("No readable text was extracted from the PDF.")
                st.stop()

            # Prepare and stream
            formatted_prompt = prompt_template.format(context=context)

            st.subheader("Evaluation Result")

            response_container = st.empty()
            full_response = ""

            for chunk in llm.stream(formatted_prompt):
                content = chunk.content if hasattr(chunk, "content") else str(chunk)
                full_response += content
                response_container.markdown(full_response + "▌")

            response_container.markdown(full_response)

        except Exception as e:
            st.error("An error occurred during processing.")
            st.exception(e)

# Footer
st.markdown("---")
st.caption("Powered by Groq (llama-3.3-70b-versatile)")
