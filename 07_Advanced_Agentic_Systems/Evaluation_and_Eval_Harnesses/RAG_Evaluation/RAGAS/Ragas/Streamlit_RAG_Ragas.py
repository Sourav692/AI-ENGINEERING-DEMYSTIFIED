#This python code will create an interactive Chatbot to talk to documents.
# Set environment variable before importing torch to force CPU usage
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''

from langchain.embeddings import HuggingFaceEmbeddings
import streamlit as st
import sys
import tempfile
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from streamlit_option_menu import option_menu
from dotenv import load_dotenv, find_dotenv
#******* Evaludate with RAGAS *****
from datasets import Dataset
from ragas import evaluate


# Load openai api key from .env file
load_dotenv(find_dotenv())
os.environ["OPENAI_API_KEY"]=str(os.getenv("OPENAI_API_KEY"))

#Create temporary folder location for document storage
TMP_DIR = Path(__file__).resolve().parent.parent.joinpath('data','tmp')
llm = ChatOpenAI(model='gpt-4.1-nano', api_key=os.environ["OPENAI_API_KEY"])

header = st.container()

def streamlit_ui():

    with st.sidebar:
        choice = option_menu('Navigation',["Home",'RAG_Evaluation_Ragas'])

    if choice == 'Home':
        st.title("Evaluation of LLM")

    elif choice == 'RAG_Evaluation_Ragas':
        with header:
            st.title('Evaluate RAG with RAGAs framework')  
            st.write("""This is a simple RAG process where user will upload a document then the document
                     will go through RecursiveCharacterSplitter and embedd in FAISS DB.
                     Next we will evaludate the RAG app with RAGAs framework""")
            
            source_docs = st.file_uploader(label ="Upload a document", type=['docx'], accept_multiple_files=True)
            if not source_docs:
                st.warning('Please upload a document')
            else:
                RAG(source_docs)
    
def RAG(docs):
    #load the document
    for source_docs in docs:
        with tempfile.NamedTemporaryFile(delete=False,dir=TMP_DIR.as_posix(),suffix='.docx') as temp_file:
            temp_file.write(source_docs.read())

    
    loader = DirectoryLoader(TMP_DIR.as_posix(), glob='**/*.docx', show_progress=True)
    documents = loader.load()

    #Split the document
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    text = text_splitter.split_documents(documents)

    #Vector and embeddings
    DB_FAISS_PATH = 'vectorestore/faiss'
    #embedding = OpenAIEmbeddings()
    # Initialize embeddings with CPU device (CUDA_VISIBLE_DEVICES is set at top to force CPU)
    try:
        embedding = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2',
            model_kwargs={'device': 'cpu'}
        )
    except Exception as e:
        # Fallback: try without device specification if device parameter causes issues
        st.warning(f"Error with device specification: {e}. Trying without device parameter...")
        embedding = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2'
        )

    db = FAISS.from_documents(text,embedding)
    db.save_local(DB_FAISS_PATH)
    retriever = db.as_retriever(search_kwargs={'k':20})
        
    # Setup RAG pipeline
   

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm,    
        retriever,
        return_source_documents=True
    ) 

    # Changes related to RAGAs
    questions = ["How many years of experience Soumen has?", 
                "Which are the different organization Soumen has worked?",
                "Which are the framework skills Soumen has?",
                ]
    ground_truths = [["Soumen has total 18 years plus experience in software industry"],
                    ["Soumen has worked in Praxis softek solution, Lexmark International India, Cognizant Technologies, Infosys and IBM"],
                    ["Soumen has framework skills like Cucumber, Appium, Rest Assured, Selenium and Playwright"]]
    answers = []
    contexts = []

    chat_history=[]
    # Inference
    for query in questions:
        response = qa_chain({"question":query, "chat_history":chat_history})
        answers.append(response['answer'])
        contexts.append([docs.page_content for docs in retriever.get_relevant_documents(query)])

    # To dict
    data = {
        "question": questions,
        "answer": answers,
        "ground_truths": ground_truths,
        "contexts": contexts,
    }

    # Convert dict to dataset
    dataset = Dataset.from_dict(data)

    from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    )

    result = evaluate(
        dataset = dataset, 
        metrics=[
            faithfulness,
            answer_relevancy,
        ],
    )

    df = result.to_pandas()
    
    st.dataframe(df)

streamlit_ui()


