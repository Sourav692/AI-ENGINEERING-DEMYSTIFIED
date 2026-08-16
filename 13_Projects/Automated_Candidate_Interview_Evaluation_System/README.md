# AI Interview Coach

Phase 13 project at `13_Projects/Automated_Candidate_Interview_Evaluation_System/` (same app as GitHub `AI-Interview-Coach`).

An AI-powered mock interview system that conducts realistic job interviews, collects your answers in real time, and delivers instant feedback from a virtual career coach — all in the browser.

Three specialised agents collaborate via [AutoGen AgentChat](https://microsoft.github.io/autogen/stable/):

| Agent | Role |
|-------|------|
| **Interviewer** | Asks 3 targeted questions (technical, problem-solving, culture) |
| **Candidate** | You — answers are typed live through the web UI |
| **Evaluator** | Career coach that critiques each answer and summarises performance |

## Architecture

```
Browser (HTML/CSS/JS)  ←— wss:// —→  FastAPI + Uvicorn
                                          │
                                          ├── Interviewer Agent (Groq LLM)
                                          ├── Candidate Agent  (User via WebSocket)
                                          └── Evaluator Agent  (Groq LLM)
```

The backend streams agent messages over a WebSocket. The frontend locks the input field until it's the candidate's turn, creating a natural conversational flow.

## Quick Start

```bash
git clone https://github.com/Sourav692/AgenticAI_Projects_Demystified.git
cd "Automated Candidate Interview & Evaluation System"

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # then paste your Groq key
uvicorn app:app --reload
```

Open [http://localhost:8000](http://localhost:8000), enter a job role, and start interviewing.

## Prerequisites

- Python 3.12+
- A [Groq API key](https://console.groq.com) (free tier works)

## Installation

### 1. Clone and enter the project

```bash
git clone https://github.com/Sourav692/AgenticAI_Projects_Demystified.git
cd "Automated Candidate Interview & Evaluation System"
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set your Groq API key:

```
GROQ_API_KEY=gsk_your_key_here
```

### 5. Run the application

```bash
uvicorn app:app --reload
```

The app is now live at [http://localhost:8000](http://localhost:8000).

## Usage

### Web Application

1. Open the app in your browser
2. Enter any job role (e.g. *AI Engineer*, *Product Manager*, *Data Scientist*)
3. Click **Start Interview**
4. Answer each question in the chat — the Evaluator gives feedback after every response
5. After 3 questions the interview ends with a performance summary

### Notebook (Interactive)

The notebook `agent_test.ipynb` runs the same interview loop in a Jupyter environment with terminal-based input — useful for experimentation and learning how the agents work.

```bash
jupyter notebook agent_test.ipynb
```

### CLI Script

`agent_test.py` provides a minimal command-line version using OpenAI directly:

```bash
python agent_test.py
```

## Project Structure

```
.
├── app.py                 # FastAPI server — WebSocket interview endpoint
├── agent_test.ipynb       # Jupyter notebook walkthrough
├── agent_test.py          # CLI version of the interview
├── templates/
│   └── index.html         # Chat UI template
├── static/
│   ├── style.css          # Styling
│   └── script.js          # WebSocket client logic
├── requirements.txt       # Python dependencies
├── render.yaml            # Render deployment blueprint
├── RENDER_DEPLOY.md       # Step-by-step Render deployment guide
├── .env.example           # Required environment variables
└── LICENSE                # Apache 2.0
```

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `autogen-agentchat` | Multi-agent orchestration (RoundRobinGroupChat) |
| `autogen-ext[openai]` | OpenAI-compatible model client for Groq |
| `fastapi` | Async web framework with WebSocket support |
| `uvicorn` | ASGI server |
| `python-dotenv` | Environment variable management |

## Deployment

The project includes a ready-to-use [Render](https://render.com) deployment configuration. See [RENDER_DEPLOY.md](RENDER_DEPLOY.md) for one-click and manual deployment options.

**Quick deploy**: push to GitHub, connect the repo on Render, and add your `GROQ_API_KEY` — the `render.yaml` blueprint handles everything else.

## Configuration

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `GROQ_API_KEY` | Groq API key for LLM inference | *(required)* |

The model defaults to `llama-3.3-70b-versatile` via Groq. To switch models, update the `model` field in `app.py`.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push to the branch and open a Pull Request

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.
