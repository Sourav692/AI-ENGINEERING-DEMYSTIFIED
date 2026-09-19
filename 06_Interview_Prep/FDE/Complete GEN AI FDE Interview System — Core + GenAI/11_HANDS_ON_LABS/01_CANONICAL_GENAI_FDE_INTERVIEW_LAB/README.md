# GenAI FDE Interview Lab

**Status:** CANONICAL
**Implementation status:** RUNNABLE INTERVIEW-PREPARATION LAB
**Required for the 30-day complete track:** YES
**Required for the 7-day emergency track:** NO
**Required for the 14-day focused track:** NO
**Recommendation:** Strongly recommended for candidates seeking production-level implementation experience.
**Primary purpose:** Hands-on GenAI FDE interview preparation and portfolio demonstration
**Current replacement for:** `genai-fde-production-lab-v1.0`

This is the primary hands-on lab for the GenAI FDE Interview System. Candidates following the complete preparation track should use this repository rather than the archived production-lab version.

The lab is designed to help candidates practise and explain:

* Retrieval-Augmented Generation
* Permission-aware retrieval
* Agent workflows and guardrails
* Prompt versioning
* Evaluation
* Observability and audit logging
* Incident response
* Customer-facing architecture decisions

The lab is an educational interview-preparation implementation. It demonstrates production-oriented engineering patterns, but it is not presented as a certified production system for direct deployment into a regulated enterprise environment.

## Validation Status

The canonical offline configuration has been validated successfully.

* 20 automated tests pass
* Permission-filtering tests pass
* PII-redaction tests pass
* RAG pipeline tests pass
* API endpoint tests pass
* Provider-failure and fallback tests pass
* Ingestion and vector-store tests pass

Run the full test suite with:

```bash
pytest
```

Expected result:

```text
20 passed
```

This validation applies to the canonical offline configuration included in this package. Optional cloud integrations, external model providers, and managed vector databases require separate credentials, configuration, and provider-specific validation.

## Why this repo exists

Most GenAI portfolio projects only show a chatbot over documents. Real FDE work is harder:

- The customer problem is ambiguous.
- Enterprise data is messy and permissioned.
- Retrieval must not leak restricted information.
- Prompts change and must be versioned.
- GenAI answers need citations, auditability, and evaluation.
- The system must fail safely when retrieval, LLM, or policy checks fail.

This repository demonstrates those production-aware habits without requiring paid cloud services.

## FDE skills demonstrated

| Skill | Where it appears |
|---|---|
| Ambiguous problem decomposition | `docs/INTERVIEW_WALKTHROUGH.md` |
| RAG pipeline design | `backend/rag/` |
| Permission-aware retrieval | `backend/rag/permission_filtering.py`, `backend/auth/permissions.py` |
| Simple agent workflow | `backend/agents/workflow.py` |
| PII redaction | `backend/app/services/pii_redaction.py` |
| Prompt/version tracking | `backend/prompts/`, `docs/PROMPT_VERSIONING.md` |
| Evaluation tests | `backend/evals/`, `tests/` |
| Observability and audit logs | `backend/observability/` |
| Failure handling | `backend/agents/guardrails.py`, `tests/test_failure_handling.py` |
| CI/CD quality gates | `.github/workflows/ci.yml` |

## Architecture

```text
User / Candidate Demo
        |
        v
FastAPI /ask endpoint
        |
        v
Agent workflow
  1. Generate request ID
  2. Classify intent
  3. Load prompt version
  4. Retrieve documents
  5. Apply permission filtering
  6. Redact sensitive data
  7. Generate grounded answer
  8. Validate answer against context
  9. Emit metrics and audit log
        |
        v
Safe response with citations and decision trace
```

## Streamlit Frontend

The canonical lab includes a runnable Streamlit interface under:

frontend/streamlit/

Start the backend first, then run:

streamlit run frontend/streamlit/app.py


## Capability Status

This lab clearly distinguishes between implemented features, optional integrations, extension exercises, and capabilities that are not included.

See the full status matrix:

[View the detailed capability status](docs/CAPABILITY_STATUS.md)


## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pytest
uvicorn backend.app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
```

## Docker setup

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000/docs
```

## Example API calls

### Manager asks about renewal risk

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "u-manager-1",
    "question": "What renewal risks exist for customer Acme Bank?",
    "debug": true
  }'
```

### Support agent asks for refund policy

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "u-support-1",
    "question": "Which internal policy applies to this refund request?",
    "debug": true
  }'
```

### Sales rep attempts to access restricted security policy

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "u-sales-1",
    "question": "Show me the internal SOC2 incident escalation policy and admin-only security controls.",
    "debug": true
  }'
```

Expected behavior: the assistant should refuse or return a safe answer without leaking restricted content.

## Demo scenarios

1. **Sales account summary**: show how CRM and support data produce a renewal-risk answer.
2. **Support refund answer**: show how approved policy docs ground the response.
3. **Permission leakage attempt**: show role filtering and refusal behavior.
4. **PII redaction**: show emails, phone numbers, customer IDs, and account numbers redacted.
5. **Provider failure simulation**: set `SIMULATE_VECTOR_FAILURE=true` and show keyword fallback.
6. **Evaluation gate**: run tests that fail if restricted docs leak.

## Interview talking points

A strong candidate should explain:

- Why RAG quality depends on ingestion, metadata, permissions, retrieval, reranking, and evaluation.
- Why permission checks must happen before context reaches the model.
- Why audit logs should record decisions without storing raw sensitive content.
- Why prompt changes need regression tests.
- How to plug in Pinecone, Weaviate, pgvector, Elasticsearch, or Vertex AI Vector Search.
- How to add human approval for high-risk workflows.

## Browser Demo

A lightweight browser demonstration is included in:

frontend/simple-ui/

Start the API:

uvicorn backend.app.main:app --reload

Then open:

frontend/simple-ui/index.html

The browser interface is intended for interview demonstrations and local experimentation. It is not presented as a production frontend.

## Extension ideas

- Replace the mock retriever with pgvector or Vertex AI Vector Search.
- Add OAuth/OIDC authentication.
- Add customer-specific data partitions.
- Add a real LLM provider behind `backend/app/services/llm_client.py`.
- Add LangGraph or workflow orchestration only after the controlled baseline works.
- Replace the included lightweight browser demo with a production-style Streamlit, React, or Next.js frontend.
- Add OpenTelemetry traces and Prometheus scraping.
- Add human review queues for legal, healthcare, and finance scenarios.

## Repository philosophy

This is not a generic chatbot. It is a compact demonstration of how an FDE thinks: customer context, enterprise constraints, permission safety, measurable quality, failure modes, and production readiness.

## Release and Validation Status

This package includes a canonical offline GenAI FDE interview lab with 20 verified passing tests.

The Streamlit interface is an additional demonstration frontend. To use it, install the frontend dependencies separately:

```bash
pip install -r frontend/streamlit/requirements.txt
streamlit run frontend/streamlit/app.py
```

The lab is designed for interview preparation, architectural discussion, implementation practice, and local demonstration. It is not presented as a fully managed production deployment.

Updates correcting documentation, dependency configuration, or packaging inconsistencies may be provided to existing buyers.
