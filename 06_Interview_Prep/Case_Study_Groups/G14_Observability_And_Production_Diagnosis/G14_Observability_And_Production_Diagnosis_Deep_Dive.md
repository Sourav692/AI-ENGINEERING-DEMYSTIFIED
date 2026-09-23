# G14 — Observability and Production Diagnosis: Deep Dive

> Read with the unchanged [source](G14_Observability_And_Production_Diagnosis.md). The [Main guide](G14_Observability_And_Production_Diagnosis_Main.md) is the interview path; the [Cheat Sheet](G14_Observability_And_Production_Diagnosis_Cheat_Sheet.md) is the recall card.

## 1. Collection policy is the first capacity decision

Use a fixed schema: correlation ID, tenant, span name, timing, model and prompt-template versions, retrieval references, tool outcome, error class and user-visible outcome. Exclude full prompts, raw documents, secrets and arbitrary labels by default. A narrow break-glass path can capture deeper evidence only with approval, strict access, a short timer and an audit record. If raw content is never collected, it cannot be leaked through the trace store.

The supplementary example is 500 requests/s × six spans ≈ 3,000 raw spans/s. Keep every error and latency outlier, approximately 2–5% of traffic, plus a 5% head sample of normal traffic. At roughly 200 bytes per redacted span for 30 days, storage is of order hundreds of GB. Exact volume depends on actual span size, overlap between sampling classes and traffic shape. Classifier CPU and redaction correctness can become the bottleneck even when storage is affordable.

## 2. Boundaries and data mechanics

Request handling never waits for telemetry export. A bounded asynchronous buffer emits spans; export failure reduces visibility and alerts but does not stall the user. Correlation and tenant scope must be serialized across queue boundaries or traces become orphan spans. Trace ingestion is idempotent so retries do not double-count. Classify and hash before storage. A salted HMAC-SHA256 fingerprint can correlate repeated queries while resisting easy dictionary reversal; a missing salt is an error, not a reason to fall back to an unsalted hash. Reject or collapse unknown high-cardinality attributes.

Debug traces and access audit have separate paths. The trace store is sampled and short-lived. The audit store records who viewed which trace, when and why, and has stricter durability. Global dashboards aggregate across tenants; support views are tenant-scoped by role. Check the access gateway itself for leakage and audit every break-glass use.

## 3. Sampling and missing-evidence drill

Head sampling is cheap but cannot know a request's final outcome. Tail-biased retention costs more buffering but preserves slow and failed traces. Combine normal low-rate sampling with error-class overrides, always-on exemplars and temporary tenant/route incident escalation. Monitor trace coverage against complaints and request errors. If a bad trace is lost, raise sampling for the affected slice, reconstruct from adjacent gateway/dependency evidence and record uncertainty. A missing trace must never be interpreted as proof of health.

## 4. Root-cause method and incident evidence

For latency, distinguish first-token, per-token and total time. Split client/network, auth, middleware, retrieval, prompt assembly, model prefill, decode, tool calls, post-processing and stream delivery. Queue wait versus service time matters at peak. Long input prompts increase prefill and time to first token; output length increases decode time. A rising p99 with flatter p50 often suggests queueing. A synchronous evaluator or logger accidentally placed on the hot path can erase the value of streaming.

Incident #87 shows a compounded budget failure: eu-central-1 p95 22,180ms and p99 34,890ms; timeout rate 12.8% versus 1.1%. Retrieval p95 was 4,200ms, large reranker 3,100ms with 80 candidates and GPU queue depth 29, LLM gateway queue 2,800ms, provider 9,360ms through cross-region routing, and input context 18,500 tokens. The canary ran off-peak. Immediate fixes were route rollback, 30-candidate cap, light reranker when depth >10, context cap and regional endpoint; permanent fixes were per-stage budgets and peak load gates.

For quality, compare retrieval evidence and output. Use recall@k/precision@k or ranking metrics for retrieval; citation correctness/context sufficiency for assembly; faithfulness, relevance and abstention for generation; task success for the application. Fine-tuning addresses behavior, not missing knowledge, stale indexing or unauthorized retrieval.

Incident #88 shows cost attribution: daily budget $240, actual $912 by 14:20, projected $1,680; traffic +7%, input tokens +351%. `exec_summary_v6` expanded context from 4,200 to 19,000 tokens, disabled compression and crossed a premium-route threshold. Cache hit rate fell to 4% from 67%. The changed key omitted date range, snapshot ID and role scope. Fix both spend and permissions: restore the key, invalidate unsafe entries, cap context and route routine work to the appropriate model.

## 5. Failure matrix and operational use

Missing auth and out-of-tenant support lookups fail closed. Telemetry export degrades with a bounded buffer; an audit sink failure blocks an audited action or requires a human. Retrieval may retry once then return a clearly reduced answer. Model limits may queue briefly or return a retry instruction. Breakers stop repeated downstream timeouts. A buffer overflow enters restricted quarantine with an incident marker. Raw-prompt export is a privacy incident: contain sink access, rotate exposed credentials if necessary, delete/redact by contract and fix the exporter guardrail.

Build dashboards top-down: user outcome, probable cause, support mechanics. Alert on sustained SLO breaches, empty retrieval spikes, fallback growth, critical tool failures and wrong-answer feedback by tenant. Roll out SLO agreement, one end-to-end path, support workflow, then quality/cost signals. Go/no-go depends on trace coverage and overhead. Keep trace schemas compatible during migration and a quick rollback switch available.

## 6. Cost and latency pivot pattern

Measure by tenant, workflow, model and prompt version. Route simple tasks to smaller models and segregate batch/eval spend. Bound output, context, top-k, retries, agent steps and budgets. Cache only with tenant, permission scope and version in the key. For peak 429s, separate provider from gateway limits and shed non-interactive work. For abandoned streams, cancel generation and tools. For a sudden cache miss, inspect normalization, prompt prefix bytes, TTL and version before adding capacity.
