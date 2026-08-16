#This python code will create an interactive Chatbot to talk to documents.
from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
import streamlit as st
import os
import sys
import tempfile
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain,RetrievalQA
from langchain.chat_models import ChatOpenAI
from streamlit_option_menu import option_menu
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

#Let's integrate langsmith
from dotenv import load_dotenv, find_dotenv
import streamlit.components.v1 as components
#******* Evaludate with RAGAS *****
from datasets import Dataset
from ragas import evaluate

#load langsmith API key
load_dotenv(find_dotenv())
os.environ["OPENAI_API_KEY"]=str(os.getenv("OPENAI_API_KEY"))



#Initialize the Client

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
            
            source_docs = st.file_uploader(label ="Upload a document", type=['pdf'], accept_multiple_files=True)
            if not source_docs:
                st.warning('Please upload a document')
            else:
                RAG(source_docs)
    
    

            
def RAG(docs):
    #load the document
    for source_docs in docs:
        with tempfile.NamedTemporaryFile(delete=False,dir=TMP_DIR.as_posix(),suffix='.pdf') as temp_file:
            temp_file.write(source_docs.read())

    
    loader = DirectoryLoader(TMP_DIR.as_posix(), glob='**/*.pdf', show_progress=True)
    documents = loader.load()

    #Split the document
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    text = text_splitter.split_documents(documents)

    #Vector and embeddings
    DB_FAISS_PATH = 'vectorestore/faiss'
    #embedding = OpenAIEmbeddings()
    embedding = HuggingFaceEmbeddings(model_name ='sentence-transformers/all-MiniLM-L6-v2',
                                         model_kwargs={'device':'cpu'})

    db = FAISS.from_documents(text,embedding)
    db.save_local(DB_FAISS_PATH)
    retriever = db.as_retriever(search_kwargs={'k':20}),

    #Build a conversational chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm,
        retriever,
        return_source_documents=True
    ) 
 
    chat_history = []
    #Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages =[]
    
    
    #React to user input
    if prompt := st.chat_input("Ask question to document assistant"):
        #Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        #Add user message to chat history
        st.session_state.messages.append({"role":"user","context":prompt})

        response = f"Echo: {prompt}"
        #Display assistant response in chat message container
        response = qa_chain({'question':prompt,'chat_history':chat_history})

        with st.chat_message("assistant"):
            st.markdown(response['answer'])
            st.markdown(response['source_documents'])

        st.session_state.messages.append({'role':"assistant", "content":response})
        chat_history.append({prompt,response['answer']})
   


streamlit_ui()