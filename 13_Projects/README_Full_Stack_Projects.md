# Full Stack Agentic AI Projects

End-to-end full-stack agentic AI applications with real-time voice interaction, RAG pipelines, and cloud deployments.

## Projects

### 1. Pipecat Quickstart

A voice AI bot built with [Pipecat](https://docs.pipecat.ai/) that supports real-time WebRTC conversation.

| Component | Technology |
|-----------|-----------|
| Speech-to-Text | Deepgram |
| LLM | OpenAI |
| Text-to-Speech | Cartesia |
| Transport | Daily (WebRTC) |

**Quick Start:**

```bash
cd pipecat_quickstart
uv run bot.py
# Open http://localhost:7860
```

**Deployment:** Pipecat Cloud via `pcc-deploy.toml` and Docker.

**Dependencies:** `pipecat-ai[webrtc,daily,silero,deepgram,openai,cartesia,runner]`, `pipecat-ai-cli`, `groq`

---

### 2. Realtime Voice AI Agent with RAG

A production-grade voice AI agent combining Retrieval-Augmented Generation with a real-time voice pipeline. Users can upload documents and have natural voice conversations about their content.

#### Architecture

```
┌─────────────────────────────────────────────────┐
│                  Frontend (React)                │
│         Pipecat Client + TailwindCSS             │
└────────────────────┬────────────────────────────┘
                     │ WebRTC
┌────────────────────▼────────────────────────────┐
│                Backend (FastAPI)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Pipecat  │  │   RAG    │  │  Embeddings  │  │
│  │ Pipeline │  │ Service  │  │   Service    │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│       │              │              │            │
│   Deepgram       LangChain      MongoDB         │
│   Groq LLM       pypdf                          │
│   ElevenLabs     python-docx                    │
└─────────────────────────────────────────────────┘
```

#### Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, TypeScript, Vite, TailwindCSS, `@pipecat-ai/client-react` |
| **Backend** | FastAPI, Pipecat, LangChain, Motor (async MongoDB) |
| **Voice Pipeline** | Deepgram (STT), Groq (LLM), ElevenLabs (TTS) |
| **Document Processing** | pypdf, python-docx |
| **Infrastructure** | AWS ECS Fargate, CloudFormation, Docker Compose |

#### Backend Structure

| Module | Purpose |
|--------|---------|
| `app/bot.py` | Pipecat voice pipeline with RAG integration |
| `app/config.py` | Application settings |
| `app/database.py` | MongoDB connection management |
| `app/models/` | Data models — `equipment.py`, `document.py`, `rag.py` |
| `app/routers/` | API routes — `stream.py`, `equipment.py` |
| `app/services/` | Business logic — `rag.py`, `embeddings.py`, `text_extraction.py` |

#### Deployment

- **Local:** `docker-compose up`
- **Production:** AWS ECS Fargate with CloudFormation (`infrastructure/cloudformation.yaml`)
- **CI/CD:** GitHub Actions (`.github/workflows/deploy.yml`)

See [`Codes/rag_voice_ai_agent-deployment_live/DEPLOYMENT.md`](Realtime%20Voice%20Ai%20agent%20with%20RAG/Codes/rag_voice_ai_agent-deployment_live/DEPLOYMENT.md) for full deployment instructions.

---

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (for Pipecat Quickstart)
- Node.js 18+ (for RAG Voice Agent frontend)
- API keys: Deepgram, OpenAI/Groq, Cartesia/ElevenLabs
- MongoDB (for RAG Voice Agent)
- Docker (for local development)

## Resources

- [Pipecat Documentation](https://docs.pipecat.ai/)
- [Deepgram](https://deepgram.com/)
- [Cartesia](https://cartesia.ai/)
- [Project Report](Realtime%20Voice%20Ai%20agent%20with%20RAG/Docs/PROJECT_REPORT.md)
