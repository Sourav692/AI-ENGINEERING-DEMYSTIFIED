# Architecture

## System components

```text
FastAPI API
  -> EnterpriseAssistantWorkflow
      -> Planner
      -> PromptRegistry
      -> LocalRetriever
          -> Ingestion
          -> Chunking
          -> Offline lexical-vector scorer
          -> Permission filtering
          -> Reranking
      -> PII Redaction
      -> Grounding Guardrails
      -> Audit + Metrics
```

## Request lifecycle

1. User sends `POST /ask` with `user_id` and `question`.
2. The workflow creates a request ID.
3. The planner classifies intent.
4. The prompt registry loads the requested prompt version.
5. The retriever loads permitted chunks only.
6. The retriever scores and reranks chunks.
7. The answer generator creates a grounded answer with citation markers.
8. PII redaction is applied to the output.
9. Guardrails check citations, restricted terms, and unredacted PII.
10. Metrics and audit events are written.

## RAG pipeline

The local RAG pipeline includes ingestion, chunking, metadata extraction, deterministic local lexical-vector scoring, keyword fallback, reranking, and context assembly.

Production replacements:

- Use the optional sentence-transformer provider or replace it with a managed embedding model.
- Replace in-memory retrieval with Pinecone, Weaviate, pgvector, Elasticsearch, or Vertex AI Vector Search.
- Add tenant partitioning and row-level authorization.
- Add offline evaluation and online feedback loops.

## Agent workflow

The agent is intentionally controlled rather than autonomous. It follows a deterministic sequence:

```text
classify -> retrieve -> permission filter -> redact -> generate -> validate -> audit
```

This is appropriate for enterprise FDE work because customers usually value reliability, explainability, and policy control more than open-ended agent behavior.

## Permission model

Documents include `allowed_roles`. Retrieval filters by role before context is assembled. This is critical: restricted chunks should never reach the model context.

## Trade-offs

| Design choice | Benefit | Limitation |
|---|---|---|
| Local deterministic generator | Testable and free | Not a real LLM |
| Explicit role allowlists | Easy to audit | Less flexible than policy engines |
| Simple chunking | Easy to understand | Not robust for PDFs/HTML |
| In-memory retrieval | Easy local demo | Not scalable |
| CI eval tests | Catches regressions | Small dataset only |

## Production extensions

- Add OIDC authentication and identity-aware proxy.
- Add attribute-based access control.
- Add customer-level data partitions.
- Add real vector database and reranker.
- Add human approval for finance, legal, healthcare, and security responses.
- Add OpenTelemetry tracing and Prometheus metrics.
