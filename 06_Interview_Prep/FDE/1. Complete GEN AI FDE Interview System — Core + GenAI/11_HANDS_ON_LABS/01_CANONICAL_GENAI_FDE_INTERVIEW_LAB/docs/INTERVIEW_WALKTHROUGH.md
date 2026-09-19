# Interview Walkthrough

## 2-minute explanation

"This repository is a compact enterprise GenAI assistant lab. It demonstrates how I would build a customer-facing FDE prototype that is not just a chatbot. It includes RAG, permission-aware retrieval, PII redaction, prompt versioning, evaluation tests, audit logs, observability, Docker setup, and CI gates. The key idea is that enterprise GenAI quality depends not only on model choice, but also on data permissions, retrieval quality, grounding, failure handling, and measurable evaluation."

## 5-minute architecture walkthrough

Walk through the request lifecycle:

1. User calls `/ask` with a role-backed `user_id`.
2. The workflow creates a request ID for traceability.
3. The planner classifies the question intent.
4. The prompt registry loads a versioned prompt.
5. The retriever searches only documents allowed for the user's role.
6. The reranker orders the best chunks.
7. The answer generator creates a grounded answer with citations.
8. PII redaction and grounding guardrails run.
9. The system emits metrics and an audit event.

Emphasize that permission filtering happens before context reaches the model.

## 10-minute deep dive

Discuss these areas:

### RAG quality

- Data ingestion quality matters more than demo UI polish.
- Chunking and metadata determine whether retrieval works.
- A vector database is not enough; permission filters and evaluation are required.

### Enterprise safety

- The model should never receive unauthorized context.
- Logs must not become a second data leak.
- PII redaction should run before customer-visible output.

### Evaluation

- Unit tests validate deterministic behavior.
- Eval tests validate GenAI-specific quality and safety.
- CI should block permission leakage and PII failures.

### Production path

- Replace local retriever with pgvector, Pinecone, Weaviate, Elasticsearch, or Vertex AI Vector Search.
- Replace local generator with an LLM provider.
- Add OIDC authentication and tenant isolation.
- Add OpenTelemetry, Prometheus, and model cost dashboards.
- Add human approval for high-risk workflows.

## Common interviewer questions

### Why not use a fully autonomous agent?

Because enterprise workflows need control, auditability, and predictable failure handling. I would start with a deterministic workflow and add agentic behavior only where tool use is bounded and measurable.

### Where would you enforce permissions?

Before retrieval results are assembled into context. Prompt-level instructions are not sufficient for authorization.

### How would you know the system works?

I would use golden datasets, retrieval metrics, groundedness checks, citation validation, PII tests, permission-leakage tests, human review, and online feedback metrics.

### How would you handle a customer data leak?

I would identify the request ID, inspect retrieved source IDs, confirm whether unauthorized context reached the model, disable affected index segments, notify security/legal, and add regression tests before re-enabling.

## Strong answer structure

Use this structure in interviews:

1. Clarify customer goal and risk.
2. Identify data sources and permissions.
3. Design retrieval and grounding path.
4. Define safety controls.
5. Define evaluation and observability.
6. Explain rollout and failure handling.
7. State trade-offs and production extensions.

## Trade-offs to mention

- Local mock components help interviews, but real systems need managed identity, vector stores, and observability.
- RAG improves grounding, but bad metadata can still produce wrong answers.
- Human review slows workflow but reduces risk in regulated domains.
- Larger context windows help recall but increase latency and cost.

## Production improvements

- Real vector DB
- Real LLM provider
- OIDC integration
- Tenant isolation
- ABAC policy engine
- OpenTelemetry traces
- Human review queue
- Prompt A/B testing
- Online evaluation dashboards
