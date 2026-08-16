# Resume Genie

Phase 13 project at `13_Projects/Resume_Genie/`. Streamlit + LangGraph career suite (cover letter, JD match, resume checker, coach). Distinct from CrewAI job-application tailoring and from the AutoGen interview coach.

> An AI-powered career suite that turns your resume PDF into actionable insights — instant scoring, tailored cover letters, ATS optimization, and interactive career coaching. Now with an **agentic chat interface** that auto-detects your intent and chains tools together.

<!-- image: width=800 -->
![Resume Genie — An AI-Powered Career Suite](assets/image.png)

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45+-FF4B4B?logo=streamlit&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-Llama--3.3--70B-7C3AED)
![Groq](https://img.shields.io/badge/Provider-Groq-F55036)
![LangGraph](https://img.shields.io/badge/Agent-LangGraph-1C3C3C?logo=langchain&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E)

---

## Features

| Tool | What it does |
| --- | --- |
| **Cover Letter Generator** | Upload resume + paste JD → tailored 300–450 word cover letter with streaming output and markdown download |
| **Resume-JD Matcher** | Score your resume against a job description — keyword analysis, ATS compatibility, readability, skill gaps, and improvement suggestions |
| **Resume Checker** | Standalone resume evaluation (no JD needed) — scores clarity, format, ATS-friendliness, skills inventory, and next career steps |
| **Career Coach Chat** | Interactive chatbot grounded in your resume — career guidance, interview prep, job search strategy with full conversation history |
| **Agentic Mode** | Chat naturally and the agent auto-routes to the right tool(s). Say *"give me a full analysis"* and it chains Checker → Scorer → Cover Letter in one go |

## Architecture

```
                    STREAMLIT CHAT UI (agent/app.py)
  ┌──────────────────────────────────────────────────────┐
  │  SIDEBAR              │  CHAT INTERFACE              │
  │  [Upload Resume PDF]  │  user: "Full analysis for    │
  │  [Paste JD]           │         this job"            │
  │  [View resume text]   │  agent: Running checker...   │
  │  [Clear chat]         │         Running scorer...    │
  │                       │         Writing cover letter  │
  └───────────────────────┴──────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  LangGraph Agent   │
                    │                    │
                    │  router ─(LLM)──┐  │
                    │     │           │  │
                    │  ┌──┴──┬────┬───┘  │
                    │  ▼     ▼    ▼      │
                    │  CL   RS   RC  CC  │
                    │  │     │    │      │
                    │  └──┬──┴────┘      │
                    │     ▼              │
                    │  responder → END   │
                    └────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │     ChatGroq       │
                    │  Llama 3.3 70B     │
                    └────────────────────┘

  CL = Cover Letter   RS = Resume Scorer
  RC = Resume Checker  CC = Career Coach
```

**How routing works:**
- *"Check my resume"* → Router → Resume Checker → Response
- *"Score against this JD"* → Router → Resume Scorer → Response
- *"Full analysis"* → Router → Checker → Scorer → Cover Letter → Combined Response
- *"Help me prep for interviews"* → Router → Career Coach → Response

## Quick Start

### Prerequisites

- Python 3.12+
- A free [Groq API key](https://console.groq.com/)

### Setup

```bash
# Clone
git clone https://github.com/Sourav692/Resume-Genie.git
cd Resume-Genie

# Virtual environment (using uv — recommended)
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"
```

<details>
<summary>Alternative: using pip</summary>

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
</details>

### Configure

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your-groq-api-key-here
```

### Run

```bash
# Agentic chat interface (recommended)
streamlit run agent/app.py

# Classic dashboard (manual tool selection)
streamlit run scripts/main_dashboard.py
```

Opens at `http://localhost:8501`.

<details>
<summary>Run individual tools standalone</summary>

```bash
streamlit run scripts/cover_letter_generator.py
streamlit run scripts/resume_scorer.py
streamlit run scripts/resume_checker.py
streamlit run scripts/ai_career_coach.py
```
</details>

## Usage

### Agentic Mode (agent/app.py)

1. **Upload** your resume PDF in the sidebar
2. **Paste** a job description (optional — needed for scoring and cover letters)
3. **Chat** naturally:

| Try saying | What happens |
| --- | --- |
| *"Evaluate my resume"* | Runs Resume Checker |
| *"Score my resume against this JD"* | Runs Resume Scorer |
| *"Write me a cover letter"* | Generates a Cover Letter |
| *"Give me a full analysis"* | Chains all 3 tools together |
| *"How should I prepare for interviews?"* | Career Coach conversation |
| *"What salary should I expect?"* | Career Coach conversation |

The agent maintains conversation memory — follow-up questions reference earlier context.

## Project Structure

```
Resume-Genie/
├── agent/                               # Agentic orchestration layer
│   ├── app.py                           # Streamlit chat UI (main entrypoint)
│   ├── graph.py                         # LangGraph StateGraph definition
│   ├── state.py                         # AgentState TypedDict
│   ├── tools.py                         # Tool functions wrapping prompts
│   ├── prompts.py                       # All prompt templates + router prompt
│   └── pdf_utils.py                     # Shared PDF extraction
├── scripts/                             # Standalone Streamlit tools
│   ├── main_dashboard.py                # Unified dashboard (manual tool selection)
│   ├── cover_letter_generator.py        # Standalone cover letter generator
│   ├── resume_scorer.py                 # Standalone resume-JD matcher
│   ├── resume_checker.py               # Standalone resume evaluator
│   └── ai_career_coach.py              # Standalone career coach chatbot
├── notebooks/                           # Jupyter notebook prototypes
│   ├── AI_Career_Coach.ipynb
│   ├── Cover_Letter_Generator.ipynb
│   ├── Resume_Scorer.ipynb
│   └── Resume_Checker.ipynb
├── assets/                              # Images and diagrams
│   ├── image.png                        # Project banner
│   ├── logo.png                         # App sidebar logo
│   └── architecture.excalidraw          # Editable architecture diagram
├── content/
│   └── Resume.pdf                       # Sample resume for testing
├── docs/                                # Documentation
│   ├── tools.md                         # Detailed tool reference
│   └── Deployment.txt                   # Server deployment notes
├── .env                                 # API keys (git-ignored)
├── pyproject.toml                       # Project metadata and dependencies
├── requirements.txt                     # Pip dependencies
└── uv.lock                             # Lockfile for reproducible installs
```

## Tech Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | Streamlit |
| **LLM** | Llama 3.3 70B Versatile |
| **Inference** | Groq (ultra-low latency) |
| **Agent Framework** | LangGraph (stateful graph with conditional routing) |
| **Orchestration** | LangChain (`langchain_groq`, `langchain_core`, `langchain_community`) |
| **PDF Parsing** | PyPDFLoader via `langchain_community` |
| **Config** | python-dotenv |

## Deployment (EC2 / Remote Server)

```bash
# System setup (Ubuntu/Debian)
sudo apt update && sudo apt install python3-pip python3-venv -y

# Project setup
git clone https://github.com/Sourav692/Resume-Genie.git
cd Resume-Genie
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run in background (survives SSH disconnect)
nohup python3 -m streamlit run agent/app.py &

# Monitor logs
tail -f nohup.out
```

## License

MIT
