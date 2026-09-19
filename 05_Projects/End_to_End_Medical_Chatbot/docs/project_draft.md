# Project Draft: Medical Chatbot 

## 1. Project Overview
This project involves building a **Medical Chatbot** capable of answering medical-related queries by leveraging **Retrieval-Augmented Generation (RAG)**. The system uses a knowledge base created from medical PDF documents, stores them as vector embeddings in **Pinecone**, and retrieves relevant information to generate accurate responses using **GPT-4o** via **LangChain**. The application is served using **Flask** and is designed for deployment on **AWS** using **Docker** and **GitHub Actions**.

## 2. Key Features
- **RAG-based Question Answering**: Retrieves relevant context from a medical knowledge base to minimize hallucinations and provide accurate info.
- **PDF Knowledge Base Integration**: Automatically loads and processes PDF documents from the `data/` directory.
- **Efficient Vector Search**: Uses **Pinecone** for fast and scalable similarity search of embeddings.
- **State-of-the-art LLM**: Integrates **GPT-4o** for high-quality natural language generation.
- **Web Interface**: Simple and intuitive chat interface built with **HTML/CSS/JS** and served via **Flask**.
- **CI/CD Pipeline**: Automated deployment pipeline using **GitHub Actions** to **AWS EC2** with **Docker**.

## 3. System Architecture

### 3.1 Data Preparation (`store_index.py`)
1.  **Loading**: PDF files are loaded from the `data/` directory using `PyPDFLoader` and `DirectoryLoader`.
2.  **Splitting**: Text is split into chunks of 500 characters with a 20-character overlap using `RecursiveCharacterTextSplitter`.
3.  **Embedding**: Text chunks are converted into 384-dimensional vectors using the `sentence-transformers/all-MiniLM-L6-v2` model from **HuggingFace**.
4.  **Indexing**: These vectors are upserted into a **Pinecone** index (`medical-chatbot`).

### 3.2 Application Logic (`app.py`)
1.  **Initialization**: The Flask app initializes the Pinecone vector store and the OpenAI Chat model (`gpt-4o`).
2.  **Retrieval**: When a user asks a question, the system searches the Pinecone index for the top 3 most similar text chunks.
3.  **Generation**:
    - A `system_prompt` defines the bot's persona ("Medical assistant") and rules (concise answers, max 3 sentences).
    - The retrieved context and user query are passed to the LLM.
    - The LLM generates a response based *only* on the provided context.
4.  **Interface**:
    - `/`: Renders the chat UI (`chat.html`).
    - `/get`: Handles the chat POST requests and returns the bot's response.

### 3.3 Folder Structure
```
├── app.py                 # Main Flask application
├── store_index.py         # Script to ingest data and populate Pinecone
├── src/
│   ├── helper.py          # Utilities for loading PDFs, splitting text, downloading embeddings
│   ├── prompt.py          # System prompt definition
├── templates/
│   └── chat.html          # Chat interface template
├── static/                # Static assets (CSS/JS)
├── data/                  # Directory for storing medical PDF documents
├── Dockerfile             # Docker configuration for containerization
├── .github/workflows/     # CI/CD configuration files
└── requirements.txt       # Python dependencies
```

## 4. Technology Stack
- **Language**: Python 3.10
- **Framework**: Flask
- **Orchestration**: LangChain
- **LLM**: GPT-4o (OpenAI)
- **Vector Database**: Pinecone
- **Embeddings**: HuggingFace (`all-MiniLM-L6-v2`)
- **Deployment**: AWS (EC2, ECR), Docker, GitHub Actions

## 5. Setup and Usage

### Prerequisites
- AWS Account (for deployment)
- OpenAI API Key
- Pinecone API Key

### Local Installation
1.  **Clone the repository.**
2.  **Create a Conda environment:**
    ```bash
    conda create -n medibot python=3.10 -y
    conda activate medibot
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Environment Variables:**
    Create a `.env` file:
    ```ini
    PINECONE_API_KEY="your_api_key"
    OPENAI_API_KEY="your_api_key"
    ```
5.  **Index Data:**
    ```bash
    python store_index.py
    ```
6.  **Run Application:**
    ```bash
    python app.py
    ```

## 6. Deployment (AWS)
The project includes a CI/CD pipeline configured to:
1.  Build a Docker image.
2.  Push the image to AWS ECR.
3.  Deploy the image to an AWS EC2 instance (configured as a self-hosted runner).
