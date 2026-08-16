import streamlit as st
import requests

st.set_page_config(page_title="RAG Document Assistant")

st.title("📄 RAG Document Assistant")

backend_url = "http://localhost:8000"  # Change this if hosted remotely

# Upload documents
st.header("Step 1: Upload Documents")
uploaded_files = st.file_uploader("Upload one or more PDF files", type=["pdf"], accept_multiple_files=True)

if st.button("Upload to RAG Backend"):
    if uploaded_files:
        files = [("files", (file.name, file.read(), "application/pdf")) for file in uploaded_files]
        with st.spinner("Uploading and processing..."):
            response = requests.post(f"{backend_url}/upload", files=files)
        if response.status_code == 200:
            st.success("Documents uploaded and processed successfully!")
        else:
            st.error(f"Upload failed: {response.json().get('error')}")
    else:
        st.warning("Please upload at least one PDF file.")

# Ask questions
st.header("Step 2: Ask Questions")
user_question = st.text_input("Ask a question based on the uploaded documents")

if st.button("Get Answer"):
    if user_question.strip():
        with st.spinner("Getting answer..."):
            response = requests.post(f"{backend_url}/ask", data={"prompt": user_question})
        if response.status_code == 200:
            data = response.json()
            st.markdown("### ✅ Answer")
            st.write(data["answer"])
            st.markdown("### 📚 Sources")
            for source in data["sources"]:
                st.write(f"- {source}")
            st.markdown("### 🧠 Retrieved Contexts")
            for i, chunk in enumerate(data["retrieved_docs"], 1):
                st.markdown(f"**Context {i}:**")
                st.write(chunk)
        else:
            st.error(f"Failed to get answer: {response.json().get('error')}")
    else:
        st.warning("Please enter a question.")