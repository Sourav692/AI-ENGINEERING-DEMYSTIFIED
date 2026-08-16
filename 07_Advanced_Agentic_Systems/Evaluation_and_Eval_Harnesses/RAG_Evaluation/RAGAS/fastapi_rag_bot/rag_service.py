import os
import tempfile
from pathlib import Path
from typing import List

from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

TMP_DIR = Path(__file__).resolve().parent.joinpath("data", "tmp")
TMP_DIR.mkdir(parents=True, exist_ok=True)
DB_FAISS_PATH = "vectorestore/faiss"

llm = ChatOpenAI(model="gpt-4.1-nano", api_key=os.environ["OPENAI_API_KEY"])
chat_history = []

async def process_documents(files: List):
    file_paths = []
    for file in files:
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=TMP_DIR.as_posix(), suffix=".pdf")
        temp_file.write(await file.read())
        temp_file.close()
        file_paths.append(temp_file.name)

    loader = DirectoryLoader(TMP_DIR.as_posix(), glob="**/*.pdf", show_progress=True)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    split_text = text_splitter.split_documents(documents)

    embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                      model_kwargs={'device': 'cpu'})

    db = FAISS.from_documents(split_text, embedding)
    db.save_local(DB_FAISS_PATH)
    return file_paths

def ask_question(prompt: str):
    embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                      model_kwargs={'device': 'cpu'})
    db = FAISS.load_local(DB_FAISS_PATH, embedding, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={'k': 20})

    qa_chain = ConversationalRetrievalChain.from_llm(llm, retriever, return_source_documents=True)

    response = qa_chain({'question': prompt, 'chat_history': chat_history})
    chat_history.append((prompt, response['answer']))

    retrieved_docs = [doc.page_content for doc in response['source_documents']]

    return response['answer'], [doc.metadata.get("source", "N/A") for doc in response['source_documents']],retrieved_docs