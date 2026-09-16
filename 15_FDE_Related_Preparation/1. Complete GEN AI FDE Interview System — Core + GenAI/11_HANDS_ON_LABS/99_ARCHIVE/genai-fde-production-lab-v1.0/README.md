# Upgraded Working Production Lab - Permission-Aware RAG + Tool Approval

This is a small runnable lab for GenAI FDE interview practice. It demonstrates:

- tenant-aware document retrieval
- role-based permission filtering
- grounded answer generation with citations
- red-team detection for prompt injection
- tool-call approval gating
- audit logging
- evaluation tests

## Quickstart

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
uvicorn genai_fde_lab.api:app --reload
```

## API examples

```bash
curl -X POST http://127.0.0.1:8000/ask -H 'Content-Type: application/json' -d '{"tenant":"acme","role":"support","question":"What is the refund policy?"}'
```

## Interview use

Use this lab to explain how production GenAI systems need more than a model call: auth context, retrieval, policy filtering, evals, red-team tests, human approval, and observability.
