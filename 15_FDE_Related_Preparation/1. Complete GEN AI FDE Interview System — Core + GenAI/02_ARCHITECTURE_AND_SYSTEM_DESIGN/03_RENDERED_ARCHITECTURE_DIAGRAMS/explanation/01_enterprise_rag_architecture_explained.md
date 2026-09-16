# 01. Enterprise RAG Architecture
## What the diagram shows

This diagram shows an enterprise Retrieval-Augmented Generation system from user request to grounded answer. The main path is: user enters a question in the web app, the API gateway authenticates the request, tenant context is attached, the query router decides how to handle the request, policy filtering is applied, relevant knowledge is retrieved, the LLM gateway produces an answer, and observability captures traces, latency, cost, retrieval metrics, and safety events.

The important interview point is that this is not “just RAG.” It is an enterprise workflow where authorization, tenant isolation, policy filtering, citation quality, and production monitoring matter as much as the vector search itself.

## How to explain it in an interview

A strong spoken explanation could be:

> I would separate the system into a control plane and a data plane. The control plane handles authentication, tenant context, routing, policy decisions, rate limits, and auditability. The data plane handles retrieval, ranking, LLM generation, citation validation, and response construction. Every request carries a tenant ID, user role, permission claims, trace ID, and policy context. The retriever only sees documents allowed for that user, and the final answer must include citations from approved chunks. Observability captures retrieval quality, latency, token cost, safety violations, and answer feedback so we can improve the system after launch.

## Key trade-offs

- **Latency vs answer quality:** More retrieval, re-ranking, and citation validation improve quality but increase response time.
- **Cost vs reliability:** Larger models may give better reasoning but higher per-request cost. Smaller models may need stricter prompt design and validation.
- **Recall vs permission safety:** Broad retrieval may find more relevant chunks, but permission filtering must happen before any chunk reaches the LLM.
- **User experience vs guardrails:** Strict refusal and citation rules reduce hallucination risk but can frustrate users when documents are incomplete.
- **Single pipeline vs routed workflows:** A simple RAG chain is easier to build; query routing allows specialized paths for FAQs, policy questions, analytics, and support tickets.

## Failure modes

- Retriever returns stale, irrelevant, or low-authority documents.
- Query router sends the request to the wrong workflow.
- Policy filter is applied after retrieval but before generation incorrectly, leaking restricted context into prompts.
- The LLM produces an answer that is plausible but unsupported by retrieved chunks.
- Citations point to documents that do not actually support the claim.
- Tenant context is missing or incorrectly attached.
- Observability logs prompt content without masking sensitive data.
- Vector DB index drift causes newly updated documents to be missing.

## Security concerns

- Enforce tenant isolation at API gateway, retriever, metadata filter, and audit layers.
- Never rely only on prompt instructions for access control.
- Store permission metadata with every chunk.
- Redact sensitive fields in logs and traces.
- Protect the LLM gateway from prompt injection and unsafe tool calls.
- Validate citations before showing final answers.
- Record audit events for sensitive queries, refusal decisions, and administrative access.

## What a weak candidate misses

A weak candidate usually says: “Use embeddings, store documents in a vector DB, retrieve top-k chunks, send them to the LLM, and return the answer.”

That answer misses tenant isolation, policy filtering, citations, evals, observability, freshness, latency budget, failure handling, and rollout strategy.

## What a strong candidate says

A strong candidate says the architecture must be permission-aware, observable, and evaluable. They explain where authorization happens, how metadata filters are enforced, how retrieved chunks are validated, how hallucination is measured, how canary rollout works, and how production incidents would be debugged using traces.

## Visual improvement suggestion

Convert the horizontal chain into a layered architecture diagram:

- **Client Layer:** User, Web App
- **Control Plane:** API Gateway, Auth, Tenant Context, Query Router, Policy Filter
- **Retrieval/Data Plane:** Retriever, Vector DB, Metadata Store, Document Store
- **LLM Plane:** LLM Gateway, Answer Composer, Citation Validator
- **Observability Plane:** Traces, Retrieval Metrics, Latency, Cost, Safety Events
- **Evaluation Loop:** Offline Eval, Canary Monitoring, Feedback, Rollback
