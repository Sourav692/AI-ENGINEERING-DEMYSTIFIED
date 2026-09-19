import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

# Set up the Streamlit app
st.title("Resume-Based Career Coach Chatbot")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found. Please set it in your .env file.")
    st.stop()

chat = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
)

# Initialize session state for chat history and resume context
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "resume_context" not in st.session_state:
    st.session_state.resume_context = None

# File uploader for resume PDF
uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")

if uploaded_file:
    # Save uploaded file to temp path for loading
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name

    # Load the PDF
    loader = PyPDFLoader(temp_path)
    documents = loader.load()
    context = "\n\n".join(doc.page_content for doc in documents)
    st.session_state.resume_context = context

    # Clean up temp file
    os.unlink(temp_path)

    st.success("Resume uploaded and processed!")

# If no resume context, show a message and stop
if not st.session_state.resume_context:
    st.info("Please upload a resume to start the chatbot.")
    st.stop()

# Create system message with resume context
system_message = SystemMessage(
    content=f"""
    You are a professional career coach and resume mentor.

    You help with:
    - Career Guidance
    - Resume Improvements
    - Interview Preparation
    - Job Search Strategy
    - Skill Gap Analysis

    Candidate Resume:
    {st.session_state.resume_context}
    """
)

# Split the screen into two columns: left for resume, right for chat
left_col, right_col = st.columns(2)

# Left column: Display resume text
with left_col:
    st.subheader("Your Resume")
    with st.expander("View Resume Content", expanded=True):
        st.text_area("Resume Text", st.session_state.resume_context, height=600, disabled=True)

# Right column: Chatbot interface
with right_col:
    st.subheader("Chat with Career Coach")

    # Display chat history
    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)

    # User input
    user_input = st.chat_input("Ask a question about your career or resume...")

    if user_input:
        # Append user message
        st.session_state.chat_history.append(HumanMessage(content=user_input))

        # Prepare messages
        messages = [system_message] + st.session_state.chat_history

        # Stream the response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            response_text = ""
            for chunk in chat.stream(messages):
                response_text += chunk.content
                response_placeholder.markdown(response_text + "▌")

            # Finalize without cursor
            response_placeholder.markdown(response_text)

        # Append AI message to history
        st.session_state.chat_history.append(AIMessage(content=response_text))

        # Rerun to update the UI
        st.rerun()
