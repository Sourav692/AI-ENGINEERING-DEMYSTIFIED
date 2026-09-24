# G06 — Natural Language over Governed Data: Deep Dive

The [Main guide](/modules/15-fde-case-studies/knowledge-retrieval/nl-over-governed-data#main) is the spoken design. This is the technical backup to the unchanged [source study](/modules/15-fde-case-studies/knowledge-retrieval/nl-over-governed-data#full-pack), especially §§3–14.

## 1. Authority, state, and versions

The warehouse catalog owns physical schema. Metric owners own business definitions in `Metric(id, name, definition, dimensions, owner, version)`. The identity provider and policy store own permission decisions. Caches hold versioned, expiring schema and metric snippets but own neither. `QueryRun(id, actor, sql_hash, policy_decision, bytes_scanned, result_ref)` is append-only and stamps metric, schema, policy, prompt, and model versions so a changed number can be reconstructed. Question interpretation, candidate SQL, AST, validation, and execution trace are request state.

The executive variant adds `KPIValue`, dashboard refresh time, and a cited `Insight`; the retail variant adds forecast, actual sales, and driver-signal records. Forecast drivers from promotions, weather, inventory, or events are computed from data and then narrated. The assistant cannot infer a causal claim from correlation. Feedback and analyst corrections feed evaluation only after review.

## 2. Query routing and ambiguity

| Question | Route | Reason |
|---|---|
| “Revenue last week” | Versioned metric view and structured query | A financial definition and grain must be selected. |
| “How many high-priority tickets?” | Structured count/filter | Semantic search does not count a complete set. |
| “Status of ticket #4821?” | Exact ID lookup | Approximate retrieval is unnecessary. |
| “Pattern in billing tickets this quarter?” | Structured filter, then summarize scoped prose | Filters establish the set; the LLM summarizes its content. |

If a word maps to multiple metrics, present the supported definitions, ask, refuse, or escalate according to the agreed policy. Use a default only when a context-specific canonical definition has been approved. The AIA supervisor’s **<60%** clarification threshold is an example from that engagement, not a universal value. Catalog staleness is also a gate: refresh, narrow the supported question set, or ask; do not silently generate against an unknown schema.

## 3. SQL as an untrusted proposal

The LLM proposes SQL from a narrow, authorized metric and schema context. A dialect-aware parser builds an AST and policy checks the statement type, physical tables, columns, functions, joins, aggregate semantics, limits, date filters, and cross-join/fan-out risk. Regex cannot reliably detect nested queries, aliases, CTEs, comments, or obfuscation. A hidden-column request must fail even if the SQL is syntactically valid.

Authorization has several independent controls: least-privileged read-only credentials, warehouse-native row and column policies, entitlements rechecked at execution, filtered schema metadata, and redacted result/log handling. The model cannot rewrite access predicates. A cost estimator checks bytes, time, and row limits before admission; a live timeout cancels overruns. Auto-run only on a high-confidence, approved, low-cost pattern; otherwise show a draft or request privileged review. Do not retry policy denial with a stronger model.

## 4. Failure drills and evidence

| Drill | Detect and contain | Prevent |
|---|---|---|
| “Active customers” mapped to login activity instead of paid activity | Compare chosen metric and SQL with governed metadata; block sharing, mark run, retain prompt hash, SQL, policy and asset versions. | Tighten aliases and add a semantic golden case. |
| Schema drift | Validate plans against catalog versions before the warehouse call; stop affected template and refresh. | Version-stamped cache and regression replay on schema change. |
| Join fan-out | Compare cardinality and row counts with expected grain; refuse unrequested expansion. | Reviewed join paths, heuristics, and golden cases. |
| Excessive scan | Estimate before running; use bounded date window or pre-aggregation, otherwise stop and ask. | Per-metric scan budgets and trend alerting. |
| Prose summary disagrees with table | Reject prose and return table, SQL, lineage; notify review queue. | Numeric cross-check against structured result. |

Authorization failure closes the request. A brief warehouse outage can queue or degrade if freshness permits. A summary outage can return the table. A business-definition conflict goes to the metric owner or analyst. Treat a suspicious row count or scan volume as a correctness and reliability problem, not merely a billing issue.

## 5. Evaluation and delivery mechanics

Golden cases pair natural-language question, approved SQL, and expected result shape, including paraphrases, grain and date traps, unauthorized columns, large scans, and ambiguity. Execution accuracy asks whether the SQL runs and matches the expected result; **semantic correctness** asks whether it answers the governed business question and is the release gate. Analysts judge subtle wrong answers in shadow mode. Zero escaped policy violations is a separate gate. The source uses a trust target of **4.2/5 or 80% positive** as an example; falling trust matters even if usage rises. Compare bytes scanned per answer with the seven-day baseline and investigate **>20%** drift.

The rollout is ten owned metrics, then golden replay, then analyst shadowing, then executive release, then domain expansion. Metric owners approve definitions and cases; application owners run orchestration and generation; data owners manage warehouse and policy mappings; security reviews access and audit; support receives escalations. Rollback on semantic mismatch, policy leakage, scan-cost jump, or sustained trust decline.

## 6. AIA: when a supervisor is justified

The [source §13](/modules/15-fde-case-studies/knowledge-retrieval/nl-over-governed-data#full-pack) tells an engagement story, not the default architecture for every NL-to-SQL product. At AIA, a 2–10-business-day BI question queue and roughly four-week dashboard delivery led to a governed self-service assistant. A monolithic agent with **20+ tools** and full history failed through context bloat and tool confusion. The shipped supervisor used a fixed **eight-node LangGraph** flow: classify → clarify below 60% → resolve endorsed assets from a **16-asset Context Index** → route → compose. It routed to a managed Genie text-to-SQL specialist, a narrower generated-SQL/RAG worker, deterministic analysis for Z-scores and trends, and a Lakeview visualization worker.

Governance used **seven metric views** rather than raw fact tables, Delta-backed conversation state with **30-day retention**, versioned base-plus-overlay prompts with a five-minute cache, MLflow traces per node, and an AI Gateway for rate limits and PII filtering. As domains grew, the supervisor’s tool list approached the same bloat; an orchestrator delegated to customer, channels, policy, and claims domain agents, each with a small toolset, while a memory manager owned categorized long-term memory. The managed supervisor was not generally available in the customer’s Azure region, so the team built on available primitives. The source reports time-to-insight falling from days to minutes and about **35% year-to-date platform-consumption growth** after rollout; that growth is correlational, not a controlled attribution. The source’s “if rebuilt” lesson is to measure resolution-time and accuracy from day one.

## 7. Cost and scale follow-ups

Measure SQL retries, context tokens, bytes scanned, first-try success, p95, and cost per answer before changing models. Shrink context to metric definitions and a few permitted tables; use reviewed operations or managed SQL for common paths; dry-run cost; cache versioned metric metadata and recurring questions; cap scans and date windows. A stronger model retry loop cannot repair a missing business definition. Background catalog crawling and evaluation replay use partitioned, rate-limited queues; query-time authorization and policy never move off the hot path.
