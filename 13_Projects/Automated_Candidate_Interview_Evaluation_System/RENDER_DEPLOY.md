# Deploying AI Interview Coach to Render Cloud

## Prerequisites

- A [Render](https://render.com) account
- A [Groq API key](https://console.groq.com)
- This project pushed to a GitHub/GitLab repo

## Deployment Files

The following files have already been added to this project for Render deployment:

| File | Purpose |
|------|---------|
| `render.yaml` | Render Blueprint — defines service config (runtime, build/start commands, env vars) |
| `.python-version` | Pins Python to 3.12.3 |
| `.env.example` | Documents required environment variables |

## Environment Variables

| Key | Description | Required |
|-----|-------------|----------|
| `GROQ_API_KEY` | API key from [Groq Console](https://console.groq.com) | Yes |

## Deploy — Option A: One-Click Blueprint

1. Go to [dashboard.render.com/select-repo?type=blueprint](https://dashboard.render.com/select-repo?type=blueprint)
2. Select your GitHub repo (e.g., `Sourav692/AgenticAI_Projects_Demystified`)
3. Render auto-detects `render.yaml` and pre-fills all settings
4. When prompted, paste your `GROQ_API_KEY`
5. Click **Apply** — deployment starts automatically

## Deploy — Option B: Manual Web Service

1. Go to [dashboard.render.com](https://dashboard.render.com) → **New** → **Web Service**
2. Connect your GitHub repo
3. Configure the service:

| Setting | Value |
|---------|-------|
| **Name** | `ai-interview-coach` |
| **Region** | Oregon (or closest to your users) |
| **Root Directory** | `Full Stack Projects/Automated Candidate Interview & Evaluation System` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Starter ($7/mo) or Free (with limitations) |

4. Go to the **Environment** tab and add `GROQ_API_KEY`
5. Click **Create Web Service**

## After Deployment

Your app will be live at a URL like:

```
https://ai-interview-coach.onrender.com
```

### Verify It Works

1. Visit your Render URL in a browser
2. Enter a job role (e.g., "AI Engineer") and click **Start Interview**
3. The WebSocket connection auto-upgrades to `wss://` — no code changes needed

### Check Logs

If something goes wrong, check the **Logs** tab in the Render dashboard for errors.

## Important Notes

### WebSocket Support

Render natively supports WebSocket connections over `wss://`. The frontend (`static/script.js`) auto-detects the protocol, so it works out of the box on Render.

### Free Tier Caveats

- Service spins down after **15 minutes** of inactivity (~30s cold start)
- WebSocket connections may drop on spin-down
- For reliable interviews, use the **Starter** plan ($7/mo)

### Architecture

```
Browser (HTML/JS)  ←— wss:// —→  Render Web Service (FastAPI + Uvicorn)
                                        │
                                        ├── Interviewer Agent (Groq LLM)
                                        ├── Candidate Agent (User via WebSocket)
                                        └── Evaluator Agent (Groq LLM)
```
