# RAG Voice AI Agent - Project Report

---

## 1. Project Title
**AI-Powered Real-Time Voice Assistant with RAG (Retrieval Augmented Generation)**

---

## 2. Duration
**40–50 hours total** (Full implementation from setup to deployment)
- Setup & Configuration: 4–5 hours
- Backend Development: 12–15 hours
- Frontend Development: 8–10 hours
- RAG Implementation: 10–12 hours
- AWS Deployment & Testing: 6–8 hours

---

## 3. Introduction
This project builds an intelligent voice assistant that enables call center agents and industrial operators to access technical documentation through natural conversation. Using Retrieval Augmented Generation (RAG), the system retrieves relevant information from uploaded manuals and documents, then delivers accurate, citation-backed answers in under 2 seconds via voice. The solution combines real-time speech processing, vector databases, and Large Language Models to eliminate manual document searching and reduce customer wait times by 45-50%.

---

## 4. Aim
Build a production-ready, real-time voice AI assistant that:
- Enables natural voice conversations with <2 second response latency
- Automatically retrieves relevant information from equipment documentation using semantic search
- Provides accurate, fact-based responses grounded in actual manuals (no hallucinations)
- Supports multiple equipment with isolated knowledge bases (multi-tenancy)
- Deploys on AWS with scalable, enterprise-grade infrastructure

---

## 5. Dataset Used
**Name**: Equipment Documentation Knowledge Base (PDFs, DOCX, TXT)

**Format**: 
- Input: PDF/DOCX/TXT documents (technical manuals, SOPs, troubleshooting guides)
- Processed: JSON documents stored in MongoDB with vector embeddings
- Structure: Document chunks with 768-dimensional embeddings, metadata (equipment_id, file_name, chunk_index)

**Description**: 
Technical documentation for industrial equipment (e.g., hydraulic pumps, compressors, control systems). Each document is chunked into 1000-character segments with 250-character overlap, then converted to vector embeddings for semantic search.

**Sample Size**: 3-10 documents per equipment, resulting in 50-150 searchable chunks per knowledge base.

---

## 6. Tools & Technologies

### Backend
- **Python 3.10+**: Core programming language
- **FastAPI**: Web framework for REST APIs and WebSocket handling
- **Pipecat**: Voice pipeline orchestration framework
- **MongoDB Atlas**: Vector database with semantic search
- **Motor**: Async MongoDB driver

### AI Services
- **Deepgram Nova-2**: Real-time Speech-to-Text
- **Groq (Llama 3 70B)**: LLM for natural language understanding and function calling
- **ElevenLabs Turbo v2.5**: Text-to-Speech with low latency
- **Google Gemini**: Text embedding generation (768 dimensions)
- **LangChain**: Text splitting and document processing

### Frontend
- **React 18 + TypeScript**: UI framework
- **Vite**: Build tool
- **TailwindCSS**: Styling
- **@pipecat-ai/client-react**: Voice client SDK

### Infrastructure & DevOps
- **AWS ECS Fargate**: Container orchestration
- **AWS ALB**: Application Load Balancer (HTTP/WebSocket)
- **AWS ECR**: Docker image registry
- **AWS Secrets Manager**: Secure credential storage
- **AWS CloudWatch**: Logging and monitoring
- **Docker**: Containerization
- **GitHub Actions**: CI/CD pipeline
- **CloudFormation**: Infrastructure as Code

---

## 7. Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    User (Agent/Operator)                     │
│                           │                                   │
│                           ▼                                   │
│                  ┌─────────────────┐                         │
│                  │  React Frontend │                         │
│                  │  (WebSocket)    │                         │
│                  └─────────────────┘                         │
└──────────────────────────┬───────────────────────────────────┘
                           │ Voice Stream (WebSocket)
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                       AWS Cloud                              │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────┐      │
│  │ Load Balancer│──►│ ECS Fargate  │──►│  Secrets    │      │
│  │    (ALB)     │   │  (Backend)   │   │  Manager    │      │
│  └─────────────┘   └──────────────┘   └─────────────┘      │
└──────────────────────────┬───────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   ┌───────────┐    ┌──────────┐    ┌─────────────┐
   │ Deepgram  │    │ MongoDB  │    │    Groq     │
   │   (STT)   │    │  Atlas   │    │    (LLM)    │
   └───────────┘    │ (Vector  │    └─────────────┘
                    │  Search) │
   ┌───────────┐    └──────────┘    ┌─────────────┐
   │ElevenLabs │                     │   Google    │
   │   (TTS)   │                     │  (Embed)    │
   └───────────┘                     └─────────────┘
```

**Voice Processing Pipeline:**
```
User Voice → VAD (Silero) → STT (Deepgram) → LLM (Groq) 
                                                  ↓
                                    [Function Call: Search KB]
                                                  ↓
                                   RAG Service (Vector Search)
                                                  ↓
                                MongoDB Atlas (Top 5 Chunks)
                                                  ↓
                          LLM Response (with context)
                                                  ↓
                               TTS (ElevenLabs) → Audio Output
```

---

## 8. Key Steps / Modules

### Module 1: Document Upload & Processing
- Upload PDF/DOCX documents via REST API
- Extract text using PyMuPDF and python-docx
- Validate document quality and format

### Module 2: Text Chunking & Embedding Generation
- Split documents into 1000-char chunks with 250-char overlap
- Generate 768-dimensional embeddings using Google Gemini
- Store chunks with metadata in MongoDB

### Module 3: Vector Search Index Configuration
- Create MongoDB Atlas Vector Search index
- Configure cosine similarity search on embedding field
- Set up equipment-based filtering for multi-tenancy

### Module 4: Real-Time Voice Pipeline (Pipecat)
- Implement WebSocket transport for bidirectional audio streaming
- Integrate Deepgram for Speech-to-Text with Voice Activity Detection
- Connect ElevenLabs for Text-to-Speech synthesis

### Module 5: RAG Service Implementation
- Embed user query using Google Gemini
- Execute vector similarity search in MongoDB
- Return top-K relevant chunks with similarity scores

### Module 6: LLM Integration with Function Calling
- Configure Groq LLM (Llama 3 70B) with system prompt
- Register `search_knowledge_base` function tool
- Implement function call handling and context injection

### Module 7: Frontend Development
- Build React interface with equipment selector
- Implement WebSocket connection with Pipecat client
- Display real-time transcriptions and chat history

### Module 8: AWS Infrastructure Setup
- Create CloudFormation template (VPC, ALB, ECS, ECR)
- Configure ECS task definitions with environment variables
- Set up Secrets Manager for API key storage

### Module 9: CI/CD Pipeline
- Create GitHub Actions workflow for automated builds
- Implement Docker image build and push to ECR
- Configure automatic ECS service deployment on git push


---

## 9. Learning Outcomes

After completing this project, you will be able to:

**AI & Machine Learning:**
- ✅ Implement Retrieval Augmented Generation (RAG) for grounded AI responses
- ✅ Work with vector embeddings and semantic similarity search
- ✅ Understand prompt engineering for conversational AI

**Real-Time Systems:**
- ✅ Build WebSocket-based bidirectional communication systems
- ✅ Implement Voice Activity Detection (VAD) for natural conversations
- ✅ Integrate Speech-to-Text and Text-to-Speech APIs
- ✅ Optimize for ultra-low latency (<2 second) response times

**Backend Development:**
- ✅ Build production-grade FastAPI applications with async/await
- ✅ Work with MongoDB and vector databases
- ✅ Implement multi-tenant data isolation architecture
- ✅ Handle WebSocket connections at scale


**Cloud & DevOps:**
- ✅ Deploy containerized applications on AWS ECS Fargate
- ✅ Configure Application Load Balancers for HTTP/WebSocket traffic
- ✅ Implement Infrastructure as Code with CloudFormation
- ✅ Build CI/CD pipelines with GitHub Actions
- ✅ Manage secrets securely with AWS Secrets Manager
- ✅ Set up monitoring and logging with CloudWatch

**Software Architecture:**
- ✅ Design event-driven pipeline architectures
- ✅ Implement microservices with Docker containers
- ✅ Build scalable, production-ready systems
- ✅ Apply separation of concerns and modular design patterns

**Industry Skills:**
- ✅ Work with technical documentation and knowledge management
- ✅ Apply AI to solve real-world business problems
- ✅ Deploy and maintain production AI applications

