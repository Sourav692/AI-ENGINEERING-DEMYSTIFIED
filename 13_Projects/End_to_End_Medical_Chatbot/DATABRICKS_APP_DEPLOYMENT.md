# Deploying the Medical Chatbot to Databricks Apps with GitHub Actions

> **Reference**: [How to Deploy Databricks Apps with GitHub Actions CI/CD Pipelines](https://medium.com/@rasmus-haapaniemi/how-to-deploy-databricks-apps-with-github-actions-ci-cd-pipelines-98af7cb49c6c)

Databricks Apps lets you host web applications (Flask, Gradio, Streamlit, etc.) directly inside your
Databricks workspace — no EC2, no Docker registry, no self-hosted runner required. This guide adapts
the Medical Chatbot (`app.py`) to run as a Databricks App deployed via GitHub Actions.

---

## Architecture Overview

```
Push to main
     │
     ▼
GitHub Actions (CI/CD)
     │  1. Install Databricks CLI
     │  2. Upload source files to Databricks Volume
     │  3. databricks apps deploy
     │
     ▼
Databricks App (Flask on port 8080)
     │
     ├── Pinecone  (vector search)
     └── Groq      (LLM inference)
```

---

## Prerequisites

| Requirement | Details |
|---|---|
| Databricks workspace | Any cloud (AWS / Azure / GCP) with Apps enabled |
| Databricks personal access token | Settings → Developer → Access Tokens |
| Pinecone index populated | Run `store_index.py` once beforehand |
| `GROQ_API_KEY` and `PINECONE_API_KEY` | Stored as Databricks App secrets **and** GitHub secrets |

---

## Step 1: Add `app.yaml` (Databricks App manifest)

Create this file in the project root. Databricks Apps reads it to know how to start your app.

```yaml
# app.yaml
command: ["python", "app.py"]

env:
  - name: PINECONE_API_KEY
    valueFrom: secret
  - name: GROQ_API_KEY
    valueFrom: secret
```

---

## Step 2: Adjust `app.py` for Databricks Apps

Databricks Apps expects the app to bind to the port provided by the `APP_PORT` environment variable.
Change the last block of [app.py](app.py):

```python
if __name__ == '__main__':
    port = int(os.environ.get("APP_PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
```

---

## Step 3: Add GitHub Secrets

Go to **GitHub Repo → Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|---|---|
| `DATABRICKS_HOST` | `https://<your-workspace>.azuredatabricks.net` |
| `DATABRICKS_TOKEN` | Personal access token from Step 0 |
| `DATABRICKS_APP_NAME` | `medical-chatbot` (or any unique name) |
| `DATABRICKS_VOLUME_PATH` | `/Volumes/<catalog>/<schema>/<volume>/medical-chatbot` |

---

## Step 4: Store App Secrets in Databricks

Databricks Apps has its own secret store, separate from GitHub secrets. Set them once via the CLI:

```bash
databricks secrets create-scope medical-chatbot-scope

databricks secrets put-secret medical-chatbot-scope PINECONE_API_KEY \
  --string-value "pcsk_..."

databricks secrets put-secret medical-chatbot-scope GROQ_API_KEY \
  --string-value "gsk_..."
```

Then reference the scope in `app.yaml` (update the `valueFrom` fields to use
`secret: medical-chatbot-scope/PINECONE_API_KEY` per your workspace SDK version).

---

## Step 5: GitHub Actions Workflow

Create [.github/workflows/databricks-app.yaml](.github/workflows/databricks-app.yaml):

```yaml
name: Deploy Medical Chatbot to Databricks Apps

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Databricks CLI
        run: pip install databricks-cli

      - name: Configure Databricks CLI
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: |
          databricks configure --token <<EOF
          $DATABRICKS_HOST
          $DATABRICKS_TOKEN
          EOF

      - name: Upload source files to Databricks Volume
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
          VOLUME_PATH: ${{ secrets.DATABRICKS_VOLUME_PATH }}
        run: |
          # Upload everything except data/, research/, and .venv/
          databricks fs cp --recursive \
            --exclude "data/" --exclude "research/" --exclude ".venv/" \
            . dbfs:$VOLUME_PATH

      - name: Deploy Databricks App
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
          APP_NAME: ${{ secrets.DATABRICKS_APP_NAME }}
          VOLUME_PATH: ${{ secrets.DATABRICKS_VOLUME_PATH }}
        run: |
          databricks apps deploy $APP_NAME \
            --source-code-path $VOLUME_PATH

      - name: Print App URL
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
          APP_NAME: ${{ secrets.DATABRICKS_APP_NAME }}
        run: |
          databricks apps get $APP_NAME --output json | \
            python3 -c "import sys,json; d=json.load(sys.stdin); print('App URL:', d.get('url','(see workspace)'))"
```

---

## Step 6: First-Time App Creation

Before the workflow can `deploy`, the app must exist in Databricks. Create it once:

```bash
databricks apps create medical-chatbot \
  --description "RAG-based Medical Question Answering Chatbot"
```

Subsequent `apps deploy` calls update the running app in-place.

---

## Step 7: Deploy

```bash
git add app.yaml app.py .github/workflows/databricks-app.yaml
git commit -m "Add Databricks Apps deployment"
git push origin main
```

Monitor the run at **GitHub Repo → Actions**. Once green, the app URL is printed in the
"Print App URL" step. It will look like:

```
https://<workspace-id>.databricksapps.com/
```

---

## Key Differences vs. EC2 Deployment

| | EC2 + ECR (existing) | Databricks Apps (this guide) |
|---|---|---|
| Container build | `docker build` + ECR push | Not needed |
| Runtime | Self-hosted EC2 runner | Databricks-managed compute |
| Secrets | `docker run -e` flags | Databricks secret scope |
| Scaling | Manual | Managed by Databricks |
| Networking | Public IP + Security Group | Workspace-authenticated URL |
| Cost | EC2 instance always-on | Pay per request (serverless) |

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `App not found` on deploy | Run `databricks apps create medical-chatbot` first |
| `401 Unauthorized` | Check `DATABRICKS_TOKEN` secret hasn't expired |
| App starts but crashes | Check logs: `databricks apps logs medical-chatbot` |
| Secrets not found at runtime | Verify secret scope name matches `app.yaml` `valueFrom` |
| `APP_PORT` binding error | Ensure `app.py` reads `APP_PORT` env var (Step 2) |

---

*Reference: [How to Deploy Databricks Apps with GitHub Actions CI/CD Pipelines](https://medium.com/@rasmus-haapaniemi/how-to-deploy-databricks-apps-with-github-actions-ci-cd-pipelines-98af7cb49c6c)*
