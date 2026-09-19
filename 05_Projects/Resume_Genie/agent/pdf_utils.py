import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader


def extract_resume_text(uploaded_file) -> str:
    """Extract text from an uploaded PDF file.

    Args:
        uploaded_file: A Streamlit UploadedFile object.

    Returns:
        Concatenated text from all pages of the PDF.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    try:
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        return "\n\n".join(doc.page_content for doc in docs)
    finally:
        os.unlink(tmp_path)
