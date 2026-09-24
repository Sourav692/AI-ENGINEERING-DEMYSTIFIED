# G14 — Observability and Production Diagnosis: Cheat Sheet

[Main](/modules/15-fde-case-studies/delivery-evaluation-operations/observability-and-production-diagnosis#main) · [Deep Dive](/modules/15-fde-case-studies/delivery-evaluation-operations/observability-and-production-diagnosis#deep-dive) · [Unchanged source](/modules/15-fde-case-studies/delivery-evaluation-operations/observability-and-production-diagnosis#full-pack)

## Ask first

What is slow? What is wrong? Which tenants? What content is forbidden to collect? Who may diagnose? What overhead and retention are acceptable?

## Whiteboard path

`Request: auth/tenant → retrieval → LLM → tools → response`  
`Spans: async collector → classify/redact/HMAC → error-and-slow biased sampling → bounded store → global aggregate + tenant-scoped support views`  
Access audit is separate. Telemetry export never blocks the user.

## Four rules

- No full prompts, raw documents, secrets or unbounded labels by default.
- Redact before storage; missing salt is an error.
- Keep rare failures with error overrides, exemplars and incident sampling.
- Missing auth, cross-tenant lookup and required audit evidence fail closed.

## Numbers and incidents

Illustrative: 500 requests/s × six spans ≈ 3,000 raw spans/s; retain errors/slow traces plus about 5% of normal traffic. #87: p95 22.18s from stacked retrieval, reranker, queue and provider delays. #88: traffic +7%, input tokens +351%, cache 67% → 4%; missing `role_scope` also risks leakage.

## Diagnosis

Start at user outcome, then stage spans. Empty/stale retrieval → upstream. Good evidence contradicted by answer → model/prompt. One tenant → configuration, access or integration. First-token versus total time separates prompt/prefill from long decode.

**60-second close:** “Correlate every request, collect structured evidence without raw content, retain anomalies preferentially, and let support trace a complaint to a cause within its tenant. Prove both privacy and low overhead before widening rollout.”
