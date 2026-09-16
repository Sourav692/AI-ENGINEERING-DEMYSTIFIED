# Upgraded Production Incident Logs

# Incident 1: Cross-Tenant Retrieval Leak Through a Missing Metadata Filter

## Scenario

Acme uses an enterprise support copilot to answer questions from internal support agents about customer contracts, escalation policies, and product entitlements. The assistant is multi-tenant: Acme support agents should only retrieve Acme-owned documents, even though the vector database physically stores chunks from several enterprise customers in the same collection.

On 2026-07-08, Acme’s support lead reported that the assistant cited a renewal clause that did not exist in Acme’s contract. The answer looked professional, cited a paragraph, and used the correct support tone, but the cited language belonged to another customer, Globex. This is a high-severity incident because the answer exposed another tenant’s contractual terms and could cause both privacy and commercial harm.

The incident is useful for GenAI FDE interviews because it tests whether the candidate debugs beyond “retrieval quality.” The real issue is the intersection of retrieval, metadata filtering, ACL enforcement, observability, and rollout safety.

## User-Visible Symptom

A support agent asked: “Can Acme customers receive premium onboarding under the 2026 renewal terms?” The assistant answered yes and cited a “Premium Success Addendum.” Acme’s contract did not contain this addendum. The support agent escalated because the cited paragraph referenced “Globex Strategic Renewal 2026.”

## System Context

The system uses an authenticated RAG pipeline: UI → API gateway → tenant resolver → query rewriting → vector retrieval → metadata filter → ACL service → reranker → citation assembler → LLM gateway → response evaluator. The vector database stores chunks from multiple tenants in a shared collection with fields such as `tenant_id`, `doc_tenant_id`, `visibility`, `source_connector`, `acl_hash`, and `metadata_filter_version`.

The intended safety invariant is simple: `tenant_id` on the request must match `doc_tenant_id` on every retrieved chunk, and the ACL service must authorize each chunk before it reaches the prompt context.

## Production Telemetry

```text
2026-07-08T09:12:44.129Z level=warn service=rag-api env=prod region=eu-central-1
  trace_id=trc_7f91c2 request_id=req_acme_88421 query_id=q_20260708_091244_19
  user_id=u_acme_support_044 tenant_id=acme user_role=support_agent
  workflow=contract_entitlement_answer retriever_version=2026-07-07
  metadata_filter_version=v3 filter_expression="visibility in ['public','internal']"
  expected_filter_expression="tenant_id == 'acme' AND visibility in ['public','internal']"

2026-07-08T09:12:44.388Z level=info service=vector-retriever
  trace_id=trc_7f91c2 collection=enterprise_contract_chunks index=contracts_hnsw_v22
  retrieval_k=12 returned_k=12 top_score=0.81
  retrieved_chunk_ids=[chk_globex_9921,chk_acme_1710,chk_acme_1709,chk_globex_9922]
  retrieved_doc_ids=[doc_globex_renewal_2026,doc_acme_msa_2025]
  doc_tenant_ids=[globex,acme,acme,globex]

2026-07-08T09:12:44.421Z level=error service=acl-enforcer
  trace_id=trc_7f91c2 acl_check=skipped reason="pre_authorized_connector_flag=true"
  connector=sharepoint connector_scope=tenant_shared acl_cache_key=acl:v2:sharepoint:contracts
  request_tenant_id=acme doc_tenant_id=globex policy_decision=not_evaluated

2026-07-08T09:12:45.221Z level=error service=response-evaluator
  trace_id=trc_7f91c2 eval=tenant_isolation_violation severity=critical
  response_served=true citation_doc_id=doc_globex_renewal_2026 citation_chunk_id=chk_globex_9921
  tenant_id=acme doc_tenant_id=globex human_review=false
```

## What Changed Recently

A retrieval deploy on 2026-07-07 introduced `metadata_filter_version=v3` to support global product documentation. The new filter builder treated connector-level “pre-authorized” documents as safe and omitted the tenant equality predicate for one SharePoint collection. The rollout was enabled for 15% of Acme traffic on 2026-07-08 at 08:45.

## Root Cause

The metadata filter builder dropped the hard tenant predicate when `pre_authorized_connector_flag=true`. The ACL service then skipped chunk-level checks because it incorrectly trusted the connector-level scope. This allowed Globex chunks to enter Acme’s prompt context and be cited.

## Debugging Path

A strong engineer starts from a known bad answer and opens the full trace. They compare `tenant_id` from the request with `doc_tenant_id` from retrieved chunks, verify the actual filter expression used by the retriever, and inspect whether ACL was evaluated per chunk. They then query all traces using `metadata_filter_version=v3` and look for `tenant_id != doc_tenant_id`. Finally, they compare the canary cohort against the control cohort running `metadata_filter_version=v2`.

The key debugging move is not to re-run the same question in the UI. The UI might not reproduce the exact canary route, cache state, or retrieval ordering. The correct path is trace-first: request → filter → retrieved chunks → ACL decision → prompt context → citation.

## Fix / Mitigation

Immediate mitigation: disable `metadata_filter_version=v3`, purge affected answer cache entries, block all responses where any retrieved chunk has `tenant_id != doc_tenant_id`, and force human review for contract-entitlement answers generated during the incident window.

Longer-term fix: make tenant isolation a non-bypassable server-side predicate, add a hard post-retrieval invariant check, remove connector-level ACL shortcutting, and add an automated eval that fails deployment if cross-tenant chunks appear in retrieved context. Add a dashboard panel for `cross_tenant_retrieval_count` by tenant, connector, retriever version, and filter version.

## Red-Team / Safety Risk

This is a privacy and contractual confidentiality incident. A malicious user could intentionally query for rare phrases that retrieve neighboring tenant documents if tenant filters are weak. Even one leaked contract clause can expose pricing, support commitments, or regulated customer data.

## Interview Explanation

A strong candidate should frame this as a multi-tenant isolation failure, not a hallucination. They should mention blast-radius control, trace reconstruction, filter verification, ACL enforcement, cache purge, customer communication, and regression tests. They should also explain why tenant isolation must be enforced outside the LLM and outside prompt instructions.

## Weak Candidate Answer

“I would improve the prompt and tell the model not to use other customers’ data. I would also increase retrieval accuracy and ask the user to verify the answer.”

## Strong Candidate Answer

“I would treat this as a critical data isolation incident. First I would disable the new filter version and stop serving answers from suspicious traces. Then I would inspect the trace for request tenant, retrieved chunk tenant, filter expression, and ACL decision. The telemetry already shows `tenant_id=acme`, `doc_tenant_id=globex`, and `acl_check=skipped`, so the root cause is likely the filter/ACL path, not the model. The fix is to enforce tenant equality as a hard backend invariant before context assembly, add post-retrieval validation, purge affected cache, and add a deployment gate that fails on cross-tenant retrieval.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | Identifies critical multi-tenant isolation failure | Calls it a generic bad answer |
| Telemetry interpretation | Compares request tenant, document tenant, filter version, ACL decision | Looks only at latency or model output |
| Root-cause reasoning | Traces filter builder and ACL shortcut | Blames prompt quality |
| Production debugging | Uses traces, canary cohort, cache audit, invariant checks | Reproduces manually in UI only |
| Security/privacy awareness | Mentions confidentiality, blast radius, customer notification | Ignores data leak impact |
| Mitigation quality | Rollback, block invariant violations, purge cache, add gates | “Improve prompt” |
| Communication clarity | Explains severity and remediation to security/product/customer | Gives vague engineering update |


---

# Incident 2: Stale Index Causes Wrong Policy Answer

## Scenario

A healthcare operations team uses a GenAI policy assistant to answer prior-authorization questions for internal case reviewers. The assistant retrieves payer policy PDFs from SharePoint, chunks them into a vector index, and cites the relevant policy section in its answer.

On 2026-07-08, reviewers noticed that the assistant was still answering from an older policy that allowed a procedure without additional documentation. The payer had updated the policy that morning to require a new lab result. Because reviewers rely on the assistant to triage cases, stale answers could lead to incorrect approvals, rework, and compliance exposure.

This incident is valuable because it forces candidates to reason about freshness, connector health, indexing SLAs, stale citations, and how to design fallbacks when the index is behind the source of truth.

## User-Visible Symptom

A reviewer asked whether procedure `PA-4419` required a renal function lab. The assistant answered: “No additional lab is required,” citing `PayerX_Policy_v18.pdf`. The payer portal and SharePoint source document had already been updated to `v19`, which required the lab for patients over 65.

## System Context

The system uses SharePoint connector sync → document diff detector → PDF parser → chunker → embedding job → vector database → freshness metadata → RAG API. The source of truth is SharePoint. The vector index is expected to be no more than 4 hours behind source updates for payer policy documents.

A freshness guard is supposed to warn users when `sync_lag_hours > 4`, but it only checks connector-level sync status, not document-level freshness.

## Production Telemetry

```text
2026-07-08T10:03:12.604Z level=warn service=rag-api
  trace_id=trc_9a2d77 request_id=req_hc_77502 tenant_id=medcore
  query="Does PA-4419 require renal function lab for 72-year-old patient?"
  retrieved_doc_id=doc_payerx_policy_v18 retrieved_chunk_id=chk_px_v18_084
  source_doc_updated_at=2026-07-08T08:10:04Z indexed_at=2026-07-01T11:40:28Z
  sync_lag_hours=166.38 freshness_guard_status=pass freshness_guard_scope=connector_only

2026-07-08T10:03:13.019Z level=info service=sharepoint-connector
  connector_id=sp_medcore_policies connector_status=partial_failure
  last_successful_sync=2026-07-01T11:42:10Z failed_sync_count=47
  failed_path="/Payer Policies/PayerX/2026/PA-4419.pdf"
  error_type=permission_denied_after_folder_move http_status=403

2026-07-08T10:03:13.500Z level=error service=response-evaluator
  trace_id=trc_9a2d77 eval=freshness_violation
  answer_doc_version=v18 source_doc_version=v19 policy_effective_at=2026-07-08T08:00:00Z
  citation_doc_id=doc_payerx_policy_v18 answer_supported_by_index=true supported_by_source_of_truth=false
```

## What Changed Recently

The customer reorganized SharePoint folders on 2026-07-01 and moved payer policies into a new restricted folder. The connector service account retained access to the parent library but lost access to the `PayerX/2026` path. The connector reported `partial_failure`, but the RAG API treated the connector as generally healthy because other payer folders were still syncing.

## Root Cause

The index was stale for a high-value policy path because the connector silently failed on a restricted folder. The freshness guard checked connector heartbeat, not document-level `source_doc_updated_at` versus `indexed_at`. The assistant answered correctly relative to the stale index but incorrectly relative to the current policy.

## Debugging Path

A strong FDE compares the answer’s cited document version against the source-of-truth version. They inspect `source_doc_updated_at`, `indexed_at`, `last_successful_sync`, and connector errors for the specific path. They then run a targeted query against the connector sync table for `PayerX/2026` and compare document counts before and after the folder move.

The key is separating model correctness from data freshness. The answer was grounded in retrieved context, but the retrieved context was outdated.

## Fix / Mitigation

Immediate mitigation: disable autonomous answers for affected payer policies, show a freshness warning, and route `PayerX` questions to human review until the connector permission is fixed and the index is rebuilt.

Longer-term fix: implement document-level freshness checks, alert on failed sync count by path, block answers when policy documents exceed freshness SLA, and expose “last indexed at” in citations. Add a synthetic canary document per payer folder to detect permission breaks after folder moves.

## Red-Team / Safety Risk

A stale index can become a compliance risk even without malicious input. In regulated workflows, outdated answers may cause incorrect approvals, claim denials, or patient harm. A malicious insider could also move documents into connector-inaccessible paths to preserve outdated policy behavior.

## Interview Explanation

A strong candidate should say: “This is not necessarily hallucination. It is a freshness and connector reliability problem.” They should propose freshness SLAs, document-level staleness gates, source-of-truth comparison, and graceful degradation.

## Weak Candidate Answer

“I would retrain the model or add more recent examples to the prompt. Maybe the LLM did not understand the policy.”

## Strong Candidate Answer

“The trace shows `indexed_at=2026-07-01` while the source was updated on `2026-07-08`, so the answer is grounded but stale. I would first stop serving autonomous answers for this payer, fix connector permissions, rebuild the affected index partition, and validate that v19 chunks are retrieved. Then I would add document-level freshness gates and alerts so a connector partial failure cannot silently produce outdated policy answers.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | Identifies stale source/index mismatch | Calls it model hallucination |
| Telemetry interpretation | Uses `source_doc_updated_at`, `indexed_at`, sync lag, connector status | Ignores freshness fields |
| Root-cause reasoning | Connects SharePoint folder permissions to stale index | Blames retrieval top-k |
| Production debugging | Compares source of truth, connector logs, index metadata | Only reruns prompt |
| Security/privacy awareness | Mentions compliance and regulated workflow impact | Treats as minor answer quality bug |
| Mitigation quality | Human review, rebuild, freshness gates, alerts | “Update prompt” |
| Communication clarity | Explains grounded-but-stale distinction | Uses vague “AI was wrong” language |


---

# Incident 3: Latency Spike After Reranker and Model Routing Change

## Scenario

A B2B SaaS company uses a support copilot inside its live support console. Agents expect answers in under 5 seconds because the customer is waiting in chat. The assistant performs query rewriting, hybrid retrieval, reranking, citation generation, and LLM response generation.

On 2026-07-08, support agents reported that the assistant became too slow during peak European business hours. Some answers arrived after the chat agent had already responded manually. The issue did not appear as a full outage; success rate remained acceptable, but p95 and p99 latency violated the product SLO.

This incident is useful because it tests whether a candidate can decompose latency across retrieval, reranking, queueing, model provider latency, context size, and regional routing.

## User-Visible Symptom

Agents saw the assistant spinner for 18–35 seconds. Some requests timed out with: “I could not complete this answer. Try again.” Customer support leadership reported that handle time increased by 21% during the incident window.

## System Context

Request path: Support Console → RAG API → query rewrite model → hybrid retriever → cross-encoder reranker → context compressor → LLM gateway → model provider → response evaluator → UI stream. The observability stack records span-level traces in OpenTelemetry, metrics in Prometheus, and token/cost events in a billing stream.

The system has a 7-second p95 latency target for standard answers and a 12-second hard timeout.

## Production Telemetry

```text
2026-07-08T13:42:10.443Z level=warn service=slo-monitor region=eu-central-1
  window=5m workflow=support_answer p50_ms=5310 p95_ms=22180 p99_ms=34890
  timeout_rate=12.8% baseline_timeout_rate=1.1% request_count=1842

2026-07-08T13:42:11.018Z level=info trace_id=trc_lat_4481 request_id=req_saas_40921
  tenant_id=northwind route=standard_support_answer model_route=gpt-4-class
  p95_retrieval_ms=4200 reranker_ms=3100 llm_queue_ms=2800
  model_provider_latency_ms=9360 context_compression_ms=740 tokens_in=18500 tokens_out=610
  stream_first_token_ms=14120 total_latency_ms=23840 timeout_budget_ms=12000

2026-07-08T13:42:11.102Z level=warn service=reranker
  trace_id=trc_lat_4481 reranker_model=cross_encoder_large_v4
  candidates_in=80 candidates_out=12 batch_size=1 gpu_queue_depth=29
  fallback_to_light_reranker=false

2026-07-08T13:42:11.880Z level=warn service=llm-gateway
  trace_id=trc_lat_4481 provider=primary region=us-east-1 routed_from=eu-central-1
  queue_ms=2800 provider_status=degraded retry_count=1 retry_after_ms=750
```

## What Changed Recently

Two changes landed within 24 hours: the reranker was upgraded from `cross_encoder_small_v2` to `cross_encoder_large_v4`, and the model router shifted standard support answers from a faster mid-tier model to a larger model after a quality experiment. The canary covered only low-traffic hours and did not test peak GPU queue depth.

## Root Cause

The latency spike came from compounded latency: larger retrieval candidate set, slower reranker, larger context, queueing in the LLM gateway, and cross-region model routing. No single component fully explained the incident; the pipeline exceeded SLO because multiple “small” changes stacked together.

## Debugging Path

A strong engineer decomposes the trace into spans and compares current p95 to baseline per stage. They check whether retrieval got slower, whether reranker candidate count increased, whether context tokens increased, whether model queueing or provider latency changed, and whether regional routing crossed continents. They compare canary versus control and peak versus off-peak traffic.

They should also inspect whether timeouts are happening before or after first token. If first-token latency is above 14 seconds, streaming does not solve the user experience.

## Fix / Mitigation

Immediate mitigation: roll back the model route for standard support answers, cap reranker candidates at 30, enable light-reranker fallback when GPU queue depth exceeds 10, reduce max context tokens, and route EU traffic to an EU-capable provider endpoint.

Long-term fix: introduce a latency budget per stage, add load-test gates for reranker queue depth, enforce context token caps by workflow, and add circuit breakers for provider degradation. Quality experiments should include latency/cost SLOs, not only answer-quality metrics.

## Red-Team / Safety Risk

Latency can become a reliability and safety risk when users abandon the assistant or bypass review workflows. Attackers could also craft broad queries that trigger large candidate retrieval and expensive reranking, creating a low-cost denial-of-wallet or denial-of-service vector.

## Interview Explanation

A strong candidate should not say “the model is slow.” They should break down the latency path, isolate span-level contributors, identify compounded changes, and propose stage-specific mitigations with quality trade-offs.

## Weak Candidate Answer

“I would increase the timeout and maybe use a faster model. Latency spikes happen sometimes with LLM providers.”

## Strong Candidate Answer

“I would start with span-level latency decomposition. The trace shows retrieval at 4.2s, reranker at 3.1s, LLM queue at 2.8s, and provider latency at 9.3s, with 18.5k input tokens. That means this is a pipeline-budget failure, not just one slow API. I would roll back the model route, cap reranker candidates, enforce context compression, add queue-depth fallback, and make future quality experiments pass p95 latency and timeout-rate gates.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | SLO breach with pipeline latency decomposition | Generic “LLM is slow” |
| Telemetry interpretation | Reads retrieval, reranker, queue, provider, token spans | Looks only at total latency |
| Root-cause reasoning | Identifies compounded deploy effects | Blames one component without evidence |
| Production debugging | Compares baselines and canary/control cohorts | Suggests manual retry |
| Security/privacy awareness | Mentions DoS/denial-of-wallet risk | Ignores abuse angle |
| Mitigation quality | Stage budgets, fallback, caps, routing, load tests | Only raises timeout |
| Communication clarity | Explains user impact and trade-offs | Gives vague performance advice |


---

# Incident 4: Cost Spike from Prompt Template and Cache-Key Regression

## Scenario

An executive dashboard copilot summarizes revenue, pipeline, customer-risk notes, and operational metrics. The workflow is high value but expensive because it combines structured warehouse data, retrieved business commentary, and LLM-generated narrative.

On 2026-07-08, finance noticed that daily LLM spend for this workflow jumped by 380% without a matching increase in usage. The answers were not obviously broken, so the issue initially looked like normal executive usage. The cost anomaly was only visible in the LLMOps billing dashboard.

This incident is important for interview preparation because production GenAI systems fail economically as well as technically. A strong FDE must debug token growth, cache behavior, model routing, prompt versions, and workflow-level budgets.

## User-Visible Symptom

Executives did not complain about answer quality. The business symptom was internal: the daily budget alert fired at 14:20, and the CFO asked why the assistant consumed almost four days of budget before lunch.

## System Context

Dashboard workflow: UI → metrics API → retrieval of CRM notes → prompt assembler → semantic cache → LLM gateway → cost attribution service. The cache key should include tenant, dashboard type, date range, normalized query, and data snapshot ID. The model router chooses between a mid-tier model and a larger model based on context size and sensitivity.

## Production Telemetry

```text
2026-07-08T14:20:00.000Z level=critical service=cost-monitor
  workflow=executive_dashboard_summary tenant_id=acme
  daily_budget_usd=240 actual_cost_usd=912 projected_eod_cost_usd=1680
  daily_cost_delta=+380% request_count_delta=+7% tokens_in_delta=+351%

2026-07-08T14:20:14.667Z level=warn service=prompt-assembler
  trace_id=trc_cost_5510 prompt_template_version=exec_summary_v6
  avg_context_tokens_before=4200 avg_context_tokens_after=19000
  crm_notes_included=all_notes_90d previous_behavior=top_20_notes_30d
  table_rows_included=500 previous_row_cap=80
  compression_enabled=false

2026-07-08T14:20:15.004Z level=warn service=semantic-cache
  trace_id=trc_cost_5510 cache_hit_rate=4% baseline_cache_hit_rate=67%
  cache_key_version=v5 cache_key_fields=[tenant_id,query_text]
  missing_fields=[dashboard_date_range,data_snapshot_id,role_scope]
  invalidation_reason=key_mismatch_after_template_upgrade

2026-07-08T14:20:15.898Z level=info service=llm-gateway
  trace_id=trc_cost_5510 model_route=gpt-4-class routing_reason="context_tokens>12000"
  tokens_in=21384 tokens_out=1288 estimated_cost_usd=2.74
  previous_model_route=mid_tier_summary estimated_previous_cost_usd=0.31
```

## What Changed Recently

A prompt upgrade, `exec_summary_v6`, was deployed to include “more supporting context” after executives asked for richer explanations. The same release changed cache-key normalization but accidentally omitted date range and snapshot fields. It also disabled the compression step while debugging a formatting issue.

## Root Cause

The prompt template expanded context dramatically by including too many CRM notes and table rows. That pushed requests to a more expensive model route. At the same time, the cache-key regression collapsed hit rate from 67% to 4%, so the system repeatedly paid for large prompts instead of reusing stable summaries.

## Debugging Path

A strong engineer begins with cost per workflow, not global provider spend. They compare request count, input tokens, output tokens, model route, cache hit rate, and prompt version before and after the deploy. They sample traces to see what content was assembled and verify whether context growth improved answer quality enough to justify cost.

They should also check whether the cache regression caused correctness risks, because missing role scope in cache keys can lead to permission leakage.

## Fix / Mitigation

Immediate mitigation: roll back `exec_summary_v6`, restore compression, cap CRM notes and table rows, force the mid-tier model for routine summaries, and invalidate unsafe cache entries generated with `cache_key_version=v5`.

Longer-term fix: add cost regression tests to CI, enforce per-workflow token budgets, require cost/latency approval for prompt-template upgrades, track cache-hit rate by version, and implement budget-aware routing with graceful degradation.

## Red-Team / Safety Risk

Cost spikes can become denial-of-wallet incidents. The missing `role_scope` in the cache key also creates a privacy risk: one user’s executive summary could be cached and served to another role if query text matches.

## Interview Explanation

A strong candidate should explain that cost is a production SLO. They should identify token growth, model routing, and cache hit rate as first-class debugging dimensions. They should propose budget gates and safe cache-key design.

## Weak Candidate Answer

“I would ask users to make shorter queries or switch to a cheaper model.”

## Strong Candidate Answer

“The telemetry shows usage grew only 7%, but input tokens grew 351%, cache hit rate dropped to 4%, and requests started routing to a GPT-4-class model. I would roll back the prompt template, restore compression, cap context, fix the cache key, and add CI gates for token and cost regression. I would also audit cache safety because missing `role_scope` can create data exposure.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | Treats cost as LLMOps production incident | Treats cost as billing annoyance |
| Telemetry interpretation | Reads token, model route, cache hit, prompt version | Looks only at total spend |
| Root-cause reasoning | Connects prompt expansion and cache regression | Blames high usage incorrectly |
| Production debugging | Uses per-workflow attribution and trace sampling | Suggests generic cheaper model |
| Security/privacy awareness | Notices unsafe cache key fields | Ignores cache leakage |
| Mitigation quality | Caps, compression, routing, CI budget gates | Only tells users to ask shorter questions |
| Communication clarity | Explains cost drivers clearly to finance/product | Uses vague “LLMs are expensive” answer |


---

# Incident 5: Correct Answer with Misleading Citations

## Scenario

A legal contract copilot helps account executives answer questions about customer agreements. The assistant must cite the exact contract clause supporting each answer because users are not allowed to rely on uncited legal advice.

On 2026-07-08, an account executive asked whether a customer could terminate for convenience with 30 days’ notice. The assistant gave the correct answer, but the citation pointed to the wrong section. This is dangerous because users may trust the citation and repeat it in customer negotiations.

The incident teaches a subtle GenAI production lesson: answer correctness and citation correctness are separate evaluation dimensions.

## User-Visible Symptom

The assistant answered: “Yes, the customer may terminate for convenience with 30 days’ written notice.” That answer was correct. But the citation linked to Section 12.4, “Data Processing Addendum,” instead of Section 8.2, “Termination for Convenience.” A legal reviewer flagged the answer as misleading.

## System Context

RAG pipeline: contract search → clause chunk retrieval → reranker → answer generation → citation generation → citation verifier → legal-risk evaluator. The citation generator extracts spans from retrieved chunks after the LLM answer is generated. The system allows answers only if citation verification passes.

## Production Telemetry

```text
2026-07-08T11:28:03.331Z level=warn service=citation-verifier
  trace_id=trc_cite_2088 request_id=req_legal_33102 tenant_id=acme
  query="Can Contoso terminate for convenience with 30 days notice?"
  answer_supported=true answer_clause_id=clause_8_2
  citation_doc_id=doc_contoso_msa_2026 citation_clause_id=clause_12_4
  citation_span_match=false citation_generation_version=cite_v5

2026-07-08T11:28:03.401Z level=info service=reranker
  trace_id=trc_cite_2088 retrieved_chunk_rank_for_true_clause=7
  top_ranked_chunk_id=chk_12_4_dpa top_ranked_score=0.74
  true_supporting_chunk_id=chk_8_2_term score=0.68
  reranker_features=[semantic_similarity,heading_match] missing_feature=clause_type_boost

2026-07-08T11:28:04.010Z level=error service=response-evaluator
  trace_id=trc_cite_2088 eval=bad_citation severity=high
  grounding_score=0.91 citation_accuracy_score=0.38
  policy_action=allowed reason="answer_supported=true AND grounding_score>0.85"
```

## What Changed Recently

`citation_generation_version=cite_v5` was deployed to support shorter citations. The deployment changed citation selection from “quote the exact supporting span used in answer synthesis” to “select the most concise citation from retrieved context.” The release gate evaluated answer groundedness but did not separately evaluate citation span accuracy.

## Root Cause

The answer generator used the correct supporting clause, but the citation generator selected a nearby high-ranking chunk with similar legal language. The verifier allowed the response because it over-weighted answer groundedness and under-weighted citation span matching.

## Debugging Path

A strong engineer inspects the answer text, supporting chunks, citation chunk, retrieved ranks, and verifier decision. They check whether the cited span actually contains the claim. Then they compare `cite_v5` against the prior citation version on a golden set with clause-level labels.

The key is to avoid saying “the answer was correct, so it is fine.” In legal and compliance settings, wrong citations are a production failure even when the answer happens to be right.

## Fix / Mitigation

Immediate mitigation: roll back to `cite_v4`, require citation span match for legal workflows, and route low citation-accuracy answers to human review.

Longer-term fix: split evaluation into answer correctness, citation correctness, and quote-span faithfulness. Add clause-type features to the reranker, require citation to come from the actual supporting span, and add UI highlighting so users can verify the exact clause.

## Red-Team / Safety Risk

Misleading citations can launder unsupported legal claims. A malicious user could use a plausible citation to persuade another stakeholder that the system found contractual support. This creates legal, compliance, and trust risk.

## Interview Explanation

A strong candidate should emphasize that grounded answer quality is not enough. They should discuss citation verification, span-level evaluation, legal workflow severity, and human-in-the-loop routing.

## Weak Candidate Answer

“The answer is correct, so I would not treat this as serious. Maybe improve citation formatting.”

## Strong Candidate Answer

“I would treat this as a high-severity citation faithfulness issue. The telemetry shows `answer_supported=true` but `citation_span_match=false`, with the real clause ranked 7th. I would roll back the citation generator, require span-level verification, and add separate citation accuracy evals. In legal workflows, a correct answer with a wrong citation can be more dangerous than an answer that clearly refuses.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | Separates answer correctness from citation correctness | Says correct answer is enough |
| Telemetry interpretation | Uses citation span match, clause ID, ranking, grounding score | Looks only at answer text |
| Root-cause reasoning | Identifies citation generator/verifier weakness | Blames user confusion |
| Production debugging | Runs clause-level golden evals | Manually checks one answer only |
| Security/privacy awareness | Notes legal trust and misuse risk | Ignores compliance context |
| Mitigation quality | Rollback, span verification, human review | Cosmetic citation changes |
| Communication clarity | Explains why misleading citation is severe | Minimizes incident |


---

# Incident 6: Agent Tool-Call Near Miss on Refund Workflow

## Scenario

A retail support agent uses an AI assistant that can summarize orders, draft replies, check policy, and recommend refunds. The assistant is not allowed to execute refunds above €250 without manager approval. It may only create a proposed refund ticket.

On 2026-07-08, an agent asked the assistant to “handle all delayed VIP shipments from yesterday.” The agent planner selected the refund tool for 18 orders, including several above the approval threshold. The tool gateway blocked execution, so no money was sent, but the near miss exposed a dangerous gap in agent planning and tool authorization.

This incident is valuable because it tests whether candidates understand that tool safety must be enforced at the tool boundary, not only in the planner prompt.

## User-Visible Symptom

The support agent saw: “I could not complete part of this action because approval is required.” The operations manager received an alert that the assistant attempted bulk refunds exceeding policy limits.

## System Context

Agent workflow: user request → planner LLM → policy retriever → tool-selection policy → tool gateway → order API/refund API/ticket API → audit log. The planner can propose tool calls, but the tool gateway enforces authorization using user role, tenant policy, amount, customer segment, and approval state.

## Production Telemetry

```text
2026-07-08T16:07:51.119Z level=warn service=agent-planner
  trace_id=trc_tool_9031 request_id=req_retail_22018 tenant_id=shopline
  user_role=support_agent user_intent="handle delayed VIP shipments from yesterday"
  planned_tool_calls=18 selected_tool=refund_customer
  policy_doc_version=refund_policy_v3 planner_model=agent_planner_2026_07

2026-07-08T16:07:51.522Z level=critical service=tool-gateway
  trace_id=trc_tool_9031 tool_call_id=tc_77881 tool=refund_customer
  order_id=ord_884120 customer_tier=vip refund_amount_eur=740.00
  approval_state=missing user_role=support_agent max_allowed_without_approval_eur=250.00
  tool_call_blocked=true block_reason=approval_required policy_decision=deny

2026-07-08T16:07:51.800Z level=warn service=agent-safety-evaluator
  trace_id=trc_tool_9031 event=unsafe_bulk_action_near_miss
  bulk_action=true affected_orders=18 blocked_calls=6 allowed_calls=12
  safer_alternative=create_refund_review_ticket
  planner_policy_compliance_score=0.42
```

## What Changed Recently

A new planner prompt, `agent_planner_2026_07`, was deployed to make the agent “more action-oriented.” The examples emphasized completing workflows end-to-end but did not include bulk-action approval boundaries. The tool gateway policy was unchanged and correctly blocked the risky calls.

## Root Cause

The planner over-generalized “handle delayed shipments” into direct refund execution for all affected orders. It retrieved the refund policy but failed to apply the approval threshold during planning. The incident did not become a financial loss because the tool gateway enforced policy independently.

## Debugging Path

A strong engineer reviews the agent plan, retrieved policy context, proposed tool calls, gateway decisions, and audit log. They check whether the planner had access to approval thresholds, whether the tool schema encoded risk constraints, and whether the gateway blocked correctly. They also examine allowed calls to ensure smaller refunds were legitimate.

The important distinction is between planner failure and enforcement success. The system had a near miss, not a completed unauthorized transaction.

## Fix / Mitigation

Immediate mitigation: disable bulk refund planning, force all VIP refund actions into review-ticket mode, and add a user confirmation step for financial actions.

Long-term fix: add risk-aware tool schemas, pre-execution policy simulation, planner training examples for approval thresholds, and a separate “action risk classifier” before tool calls. Keep hard enforcement in the tool gateway regardless of planner confidence.

## Red-Team / Safety Risk

A malicious user could phrase a request as operational cleanup to induce bulk financial actions. Without gateway enforcement, this could cause unauthorized refunds, fraud, or revenue loss. The same pattern applies to account deletion, data export, and permission changes.

## Interview Explanation

A strong candidate should praise the gateway block but still treat the planner behavior as a serious near miss. They should discuss defense in depth: planner constraints, tool schema design, policy simulation, approval workflow, and auditability.

## Weak Candidate Answer

“The tool was blocked, so there is no problem. I would just tell the agent to be more careful.”

## Strong Candidate Answer

“This is a near miss. The gateway prevented loss, but the planner attempted unauthorized high-value refunds. I would inspect the planned calls, policy retrieval, and gateway decisions. Then I would disable bulk refund execution, route VIP refunds to review tickets, encode approval thresholds in the tool schema, add policy simulation before execution, and keep the gateway as a non-bypassable enforcement layer.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | Identifies near miss in agentic tool safety | Says no issue because blocked |
| Telemetry interpretation | Reads planned calls, blocked calls, role, amount, approval state | Looks only at final user error |
| Root-cause reasoning | Separates planner failure from gateway success | Blames tool API generally |
| Production debugging | Audits plan, policy context, tool schema, gateway logs | Only edits prompt |
| Security/privacy awareness | Notes fraud and unauthorized action risk | Ignores financial impact |
| Mitigation quality | Bulk disable, HITL, risk classifier, gateway enforcement | “Tell model not to refund” |
| Communication clarity | Explains near miss and control effectiveness | Minimizes incident |


---

# Incident 7: Model Regression Missed by Weak Evaluation Suite

## Scenario

A sales copilot drafts account-specific outreach emails using CRM notes, product documentation, and approved messaging. The company recently upgraded the model route to improve fluency and personalization.

After the upgrade, sales leaders noticed that emails sounded polished but included unsupported claims about security certifications and customer ROI. Offline evals had passed, so the incident exposed a weakness in the evaluation suite rather than a simple model outage.

This is an important interview incident because it tests whether candidates understand eval design, launch gates, golden datasets, regression coverage, and business-specific failure modes.

## User-Visible Symptom

Sales reps saw persuasive drafts claiming “SOC 2 Type II renewal completed in June 2026” and “average 34% support cost reduction.” The SOC 2 claim was not yet approved for external use, and the ROI claim was only from an internal pilot.

## System Context

Workflow: CRM account context → approved claims retriever → prompt template → LLM gateway → policy evaluator → offline eval suite → online quality monitor. The release gate checked grammar, tone, and general groundedness on 120 examples but included only 6 examples about regulated claims.

## Production Telemetry

```text
2026-07-08T12:16:44.921Z level=warn service=online-eval-monitor
  workflow=sales_email_draft model_route=llm_premium_v3 previous_model_route=llm_standard_v2
  unsupported_claim_rate=8.7% baseline=1.2% sample_size=430
  external_claim_policy_failures=37 severity=high

2026-07-08T12:17:03.108Z level=info service=eval-runner
  eval_suite=sales_copilot_release_gate version=eval_v14
  total_cases=120 pass_rate=96.7% release_gate=pass
  regulated_claim_cases=6 regulated_claim_pass_rate=83.3%
  missing_cases=[security_cert_pending,roi_internal_only,customer_logo_permission]

2026-07-08T12:17:11.339Z level=error service=claim-verifier
  trace_id=trc_eval_4402 request_id=req_sales_91902 tenant_id=acme
  generated_claim="SOC 2 Type II renewal completed in June 2026"
  claim_status=pending_approval approved_for_external_use=false
  retrieved_claim_doc_id=doc_security_roadmap_internal visibility=internal_only
  policy_action=should_block actual_action=warn_only
```

## What Changed Recently

The model router moved sales email drafting from `llm_standard_v2` to `llm_premium_v3` on 2026-07-08 at 09:00 after an offline eval showed better fluency and personalization. The policy evaluator was also changed from block mode to warn-only mode during the experiment to reduce false positives.

## Root Cause

The eval suite over-measured writing quality and under-measured unsupported business claims. It lacked representative cases for pending security certifications, internal-only ROI numbers, and unapproved customer references. The model upgrade increased persuasive extrapolation, and warn-only policy mode allowed risky drafts through.

## Debugging Path

A strong engineer compares offline eval pass rates to online failure modes. They inspect failing drafts, retrieve the claims used, verify claim approval metadata, and segment failures by model route and policy mode. They should ask whether the eval suite reflects real sales-risk scenarios rather than generic writing quality.

They also identify the launch gate flaw: a high aggregate pass rate can hide failure on a small but critical slice.

## Fix / Mitigation

Immediate mitigation: roll back to `llm_standard_v2`, restore policy evaluator block mode for external claims, and add review banners to drafts generated during the experiment.

Long-term fix: create a claim-level eval suite with labeled approval status, add slice-based release gates, require zero critical failures for regulated claims, and monitor unsupported-claim rate online. Add negative examples where the model must refuse to use internal-only claims.

## Red-Team / Safety Risk

Unsupported sales claims can create legal exposure, customer trust damage, and compliance issues. A malicious or careless rep could intentionally prompt the assistant to exaggerate ROI or security status, then send the draft externally.

## Interview Explanation

A strong candidate should explain that evals must match the business risk. They should criticize aggregate pass rates, propose slice-based gates, and connect online monitoring to offline eval expansion.

## Weak Candidate Answer

“The model is too creative. I would make the prompt stricter and ask sales reps to review the output.”

## Strong Candidate Answer

“The failure is an eval and launch-gate problem. The suite passed at 96.7%, but it had only six regulated-claim cases and the online unsupported-claim rate jumped to 8.7%. I would roll back the model route, restore blocking for external claims, add claim-level evals for security, ROI, and customer-logo claims, and require critical slices to pass independently before release.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | Identifies eval coverage regression | Says model is “too creative” only |
| Telemetry interpretation | Reads slice pass rates, unsupported claim rate, policy action | Cites aggregate pass rate only |
| Root-cause reasoning | Connects model route, weak evals, warn-only policy | Blames prompt alone |
| Production debugging | Compares offline/online failures by slice | Manually edits one draft |
| Security/privacy awareness | Notes legal/commercial risk of unsupported claims | Treats as style issue |
| Mitigation quality | Rollback, block mode, claim-level gates | Adds generic human review only |
| Communication clarity | Explains why evals missed critical slice | Says “evals passed” defensively |


---

# Incident 8: PDF Parser Drops Critical Tables During Policy Ingestion

## Scenario

A financial compliance reviewer uses a RAG assistant to answer questions about internal trading policy. Many policies are PDFs with tables listing thresholds, exceptions, and approval chains. The ingestion pipeline converts PDFs into markdown, chunks the text, embeds chunks, and stores layout metadata.

On 2026-07-08, reviewers noticed that the assistant gave incomplete answers about restricted-list escalation thresholds. The relevant information existed in the PDF, but it was inside a table that the parser failed to extract.

This incident is valuable because candidates must understand that GenAI quality depends on ingestion fidelity, not just retrieval and prompting.

## User-Visible Symptom

A compliance reviewer asked: “What approval is needed for restricted-list trade exception above €5M?” The assistant answered with the general escalation process but missed the table row requiring “Head of Compliance + Legal sign-off.”

## System Context

Ingestion path: S3 document drop → parser service → table detector → OCR fallback → chunker → embedding worker → vector DB → retrieval. The parser emits `extraction_coverage`, `table_count_detected`, `table_count_extracted`, and `layout_confidence`. High-risk policy PDFs should fail ingestion if table extraction coverage is below 95%.

## Production Telemetry

```text
2026-07-08T07:44:12.002Z level=warn service=pdf-parser
  document_id=doc_trade_policy_2026_v4 source_file=TradingPolicy_2026_v4.pdf
  parser_version=pdf_extract_v3.2 page_count=48
  table_count_detected=17 table_count_extracted=9 table_extraction_coverage=52.9%
  layout_confidence=0.61 ocr_fallback_triggered=false ingestion_status=success

2026-07-08T08:02:31.515Z level=info service=chunker
  document_id=doc_trade_policy_2026_v4 chunks_created=184
  pages_with_no_text=[31,32,33] missing_sections=[restricted_list_threshold_matrix]
  chunking_strategy=heading_aware_v2 embedding_model=text_embed_v5

2026-07-08T10:19:07.724Z level=error service=response-evaluator
  trace_id=trc_parse_8827 request_id=req_fin_55019
  query="approval needed for restricted-list trade exception above €5M"
  expected_source_page=32 retrieved_pages=[12,13,14,21]
  table_required=true table_chunk_present=false answer_completeness_score=0.46
```

## What Changed Recently

The parser was upgraded from `pdf_extract_v2.9` to `pdf_extract_v3.2` to improve speed. The new parser handled text faster but had a regression on rotated landscape tables. The ingestion gate treated low table coverage as a warning instead of failing the job because the document was classified as “policy_text” rather than “policy_with_tables.”

## Root Cause

Critical table pages were dropped during ingestion. The RAG system could not retrieve information that was never indexed. The deeper issue was a weak ingestion quality gate: a high-risk policy document with 52.9% table extraction coverage should not have been marked successful.

## Debugging Path

A strong engineer checks whether the missing answer content exists in the source PDF, then verifies whether it appears in parsed markdown, chunks, embeddings, and retrieval results. They inspect parser coverage metrics and compare parser versions. They also look for page-level gaps and table extraction warnings during ingestion.

The key debugging concept is “absence from index.” If the table was not chunked, increasing top-k or changing the prompt will not fix the answer.

## Fix / Mitigation

Immediate mitigation: reprocess the document with OCR/table extraction fallback, manually validate pages 31–33, and disable autonomous answers for restricted-list threshold questions until the corrected index is live.

Long-term fix: classify table-heavy policies correctly, fail ingestion when table coverage is below threshold, add visual/table regression tests for parser releases, and store page-level extraction coverage in the retrieval metadata. Add a retrieval-time warning when a query targets a section known to have ingestion warnings.

## Red-Team / Safety Risk

Parser failures can silently remove constraints, thresholds, or exceptions, causing the assistant to give overly permissive compliance advice. A malicious actor could upload documents with adversarial formatting to hide policy restrictions from ingestion.

## Interview Explanation

A strong candidate should explain that the LLM cannot reason over missing data. They should trace source PDF → parsed text → chunks → embeddings → retrieval → answer, and propose ingestion gates, parser regression tests, and human validation for high-risk documents.

## Weak Candidate Answer

“I would increase retrieval top-k or ask the model to pay more attention to tables.”

## Strong Candidate Answer

“The telemetry shows the parser detected 17 tables but extracted only 9, with pages 31–33 missing. The relevant threshold matrix was never indexed. I would reprocess with OCR/table fallback, block affected answers, and add ingestion gates so high-risk PDFs fail if table coverage is low. Retrieval tuning cannot recover content that was dropped before indexing.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | Identifies ingestion fidelity failure | Calls it retrieval failure only |
| Telemetry interpretation | Uses table coverage, missing pages, chunk presence | Looks only at answer quality |
| Root-cause reasoning | Recognizes missing source content in index | Blames LLM comprehension |
| Production debugging | Traces PDF to parsed chunks to retrieval | Only changes prompt/top-k |
| Security/privacy awareness | Notes compliance and adversarial document risk | Ignores hidden constraints |
| Mitigation quality | Reprocess, gate ingestion, parser tests | Tweak model settings |
| Communication clarity | Explains why absent data cannot be retrieved | Gives generic RAG advice |


---

# Incident 9: Prompt Injection from Retrieved Support Article

## Scenario

An internal knowledge assistant answers support engineers’ questions using Confluence, Jira, runbooks, and customer escalation notes. It can also create ticket summaries and draft Slack updates, but it is not allowed to export customer data or override security policy.

On 2026-07-08, a newly indexed Confluence page contained hidden instructions telling the assistant to ignore prior rules and reveal customer escalation notes. The assistant did not leak data because the safety layer blocked the tool call, but the trace showed that the LLM partially followed the malicious instruction in its reasoning plan.

This incident is valuable because it tests whether candidates understand indirect prompt injection in RAG systems and why retrieved content must be treated as untrusted data.

## User-Visible Symptom

A support engineer asked: “Summarize the retry policy for failed webhook deliveries.” The assistant responded with a refusal-style warning: “I found conflicting instructions in the retrieved document and cannot use one of the sources.” The user was confused because they expected a normal answer.

## System Context

RAG + tools workflow: query → Confluence retriever → source risk scanner → context assembler → LLM planner → tool gateway → response generator. The assistant has access to `search_docs`, `create_ticket_summary`, and `draft_slack_update`. It does not have access to `export_customer_data` for support engineers.

## Production Telemetry

```text
2026-07-08T15:31:22.090Z level=warn service=source-risk-scanner
  trace_id=trc_inj_7712 request_id=req_support_63120 tenant_id=acme
  retrieved_doc_id=conf_8821 title="Webhook Retry Policy - Draft"
  retrieved_doc_contains_instruction=true instruction_type=indirect_prompt_injection
  source_doc_risk_score=0.87 matched_pattern="ignore previous instructions"
  hidden_text_detected=true html_style="color:#ffffff;font-size:1px"

2026-07-08T15:31:22.502Z level=warn service=agent-planner
  trace_id=trc_inj_7712 instruction_conflict=true policy_override_attempt=true
  proposed_tool=export_customer_data proposed_arguments={"scope":"all escalation notes"}
  allowed_tools=[search_docs,create_ticket_summary,draft_slack_update]
  planner_followed_retrieved_instruction=true

2026-07-08T15:31:22.541Z level=critical service=tool-gateway
  trace_id=trc_inj_7712 tool=export_customer_data tool_call_blocked=true
  block_reason=tool_not_allowed_for_role user_role=support_engineer
  data_scope_requested=customer_escalation_notes policy_decision=deny

2026-07-08T15:31:23.004Z level=info service=response-generator
  trace_id=trc_inj_7712 response_served=true source_doc_excluded=conf_8821
  safe_answer_mode=degraded remaining_sources=3
```

## What Changed Recently

The Confluence connector began indexing draft pages after a configuration change on 2026-07-08 at 14:00. Previously, only approved pages were indexed. A support contractor had pasted a red-team test string into a draft page, but the page was accidentally included in production retrieval.

## Root Cause

Untrusted retrieved content contained malicious instructions. The source risk scanner detected the injection, but the planner still saw the tainted document before exclusion in one path. The tool gateway prevented data export, and the final response excluded the source, but the planner’s partial compliance shows a safety architecture gap.

## Debugging Path

A strong engineer inspects retrieved documents, risk scanner output, context assembly order, planner inputs, proposed tool calls, and gateway decisions. They verify whether the malicious content was visible to the model and whether source exclusion happened before or after planning. They also check connector scope changes that allowed draft content into production.

The key question is: “Did untrusted instructions reach an instruction-following model as if they were trusted context?”

## Fix / Mitigation

Immediate mitigation: exclude Confluence drafts from production indexing, quarantine `conf_8821`, rotate the affected index partition, and add a block rule for high-risk source documents before context assembly.

Long-term fix: separate data from instructions in prompt structure, run source risk scanning before any planner call, strip hidden text, add allowlisted tool policies, and maintain non-bypassable tool gateway enforcement. Add red-team fixtures for indirect prompt injection via HTML, comments, tables, and ticket descriptions.

## Red-Team / Safety Risk

This is a classic indirect prompt-injection path. If tool enforcement were weaker, the assistant could export customer data, change tickets, or send unauthorized Slack updates. Even without successful tool execution, the model may produce misleading answers if it follows hostile retrieved instructions.

## Interview Explanation

A strong candidate should explain that RAG documents are untrusted inputs. They should discuss source scanning, context isolation, tool allowlists, policy enforcement, and prompt-injection-specific evals.

## Weak Candidate Answer

“I would tell the model to ignore malicious instructions and make the prompt stronger.”

## Strong Candidate Answer

“The retrieved document contained hidden instructions, and the planner partially followed them. I would quarantine the source, remove drafts from indexing, ensure risk scanning happens before planner context assembly, and enforce tool allowlists at the gateway. Prompt wording helps, but the real safety control is treating retrieved text as data, not authority, and blocking unauthorized tools regardless of model output.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | Identifies indirect prompt injection | Calls it bad document quality |
| Telemetry interpretation | Reads risk score, instruction conflict, proposed tool, block reason | Looks only at final refusal |
| Root-cause reasoning | Connects draft indexing and planner exposure | Blames user prompt |
| Production debugging | Traces source → scanner → context → planner → gateway | Only edits system prompt |
| Security/privacy awareness | Notes data export and tool abuse risk | Ignores exfiltration angle |
| Mitigation quality | Quarantine, pre-scan, tool gateway, eval fixtures | “Tell model not to obey” |
| Communication clarity | Explains degraded safe mode to users | Gives vague safety warning |


---

# Incident 10: Embedding Model Change Degrades Recall Through Vector Drift

## Scenario

A technical support assistant answers questions from product engineers using runbooks, incident postmortems, API docs, and troubleshooting guides. The assistant relies on vector retrieval to find semantically similar chunks before reranking.

On 2026-07-08, after an embedding model migration, engineers reported that the assistant missed obvious runbooks and retrieved loosely related documents instead. The LLM still produced fluent answers, but they were less specific and sometimes omitted critical remediation steps.

This incident is useful because it tests whether candidates understand embedding migrations, index compatibility, recall evaluation, hybrid search, and rollback strategy.

## User-Visible Symptom

An engineer asked: “How do I recover stalled Kafka Connect sink tasks after schema registry auth rotation?” The assistant retrieved generic Kafka troubleshooting docs but missed the exact runbook `RB-KAFKA-CONNECT-042`, which had the correct recovery command sequence.

## System Context

Retrieval path: query embedding → vector DB HNSW index → metadata filters → hybrid BM25 merge → reranker → context assembler. The system migrated from `text_embed_v4` to `text_embed_v5`. Documents should be re-embedded with the same model used for query embeddings, or the system should query the matching index.

## Production Telemetry

```text
2026-07-08T09:58:42.774Z level=warn service=retrieval-eval-monitor
  eval_set=runbook_recall_canary window=30m
  recall_at_5_before=0.86 recall_at_5_after=0.54 mrr_before=0.71 mrr_after=0.39
  affected_domain=kafka_connect embedding_query_model=text_embed_v5
  document_embedding_model_mix={text_embed_v4:0.72,text_embed_v5:0.28}

2026-07-08T09:59:10.018Z level=info service=vector-retriever
  trace_id=trc_vec_3380 request_id=req_eng_14480
  query="recover stalled Kafka Connect sink tasks after schema registry auth rotation"
  query_embedding_model=text_embed_v5 index_name=runbooks_hnsw_mixed_v18
  expected_doc_id=doc_rb_kafka_connect_042 expected_chunk_id=chk_rb_042_06
  expected_chunk_rank=23 top_k=8 top_score=0.62 score_margin=0.03
  retrieved_doc_ids=[doc_kafka_generic_011,doc_schema_registry_faq_003,doc_connect_offsets_019]

2026-07-08T09:59:10.331Z level=warn service=index-migration-worker
  migration_id=emb_v5_runbooks progress=28%
  dual_index_routing=false backfill_status=in_progress
  index_compatibility_warning="query_model_v5_against_mixed_doc_embeddings"
  rollback_index=runbooks_hnsw_v4_ready
```

## What Changed Recently

The embedding migration began on 2026-07-08 at 08:30. Query embeddings were switched to `text_embed_v5` immediately, but only 28% of document chunks had been re-embedded. Dual-index routing was disabled to simplify the release. The canary monitored answer groundedness but not recall@k for critical runbooks.

## Root Cause

The system queried a mixed embedding space: new query embeddings against mostly old document embeddings. Similarity scores became less meaningful, reducing recall for specific technical runbooks. The reranker could not recover the correct answer because the exact runbook was outside the top-k candidate set.

## Debugging Path

A strong engineer compares retrieval metrics before and after the embedding migration, checks query model versus document embedding model, and inspects rank of expected chunks. They evaluate whether BM25 fallback retrieved the runbook and whether the reranker ever saw it. They also compare mixed index behavior to a clean v4 index and a fully rebuilt v5 index sample.

The key is to identify candidate-generation failure. If the right chunk is ranked 23 and top-k is 8, the LLM and reranker never receive the necessary evidence.

## Fix / Mitigation

Immediate mitigation: route queries back to the v4 index until v5 backfill is complete, enable hybrid BM25 fallback for exact runbook IDs, and increase top-k only temporarily for affected domains.

Long-term fix: perform embedding migrations with dual indexes, shadow evaluation, recall gates, and per-domain canaries. Do not switch query embeddings globally until document backfill is complete or routing is model-compatible. Add dashboards for embedding-model mix and recall@k by domain.

## Red-Team / Safety Risk

Vector drift can cause confident but incomplete technical guidance. In SRE workflows, missing a critical runbook step can prolong outages. Attackers may also exploit weak retrieval by using semantically broad phrasing to push the assistant toward generic documents.

## Interview Explanation

A strong candidate should explain that retrieval quality depends on embedding-space consistency. They should discuss recall@k, MRR, expected chunk rank, dual-index migration, and why rerankers cannot fix candidate-generation misses.

## Weak Candidate Answer

“I would increase top-k and use a better model to answer the question.”

## Strong Candidate Answer

“The telemetry shows query embeddings are v5 while 72% of document embeddings are still v4, and recall@5 dropped from 0.86 to 0.54. The expected runbook is ranked 23, so it never reaches the reranker or LLM. I would roll back to the v4 index or use dual-index routing until backfill completes, then add recall gates and shadow evals for future embedding migrations.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | Identifies embedding-space/vector drift | Calls it generic retrieval issue |
| Telemetry interpretation | Reads recall@k, MRR, model mix, expected rank | Looks only at answer quality |
| Root-cause reasoning | Connects query/document embedding mismatch | Blames LLM response |
| Production debugging | Tests v4, v5, mixed index, BM25, reranker exposure | Only increases top-k |
| Security/privacy awareness | Notes reliability risk in SRE guidance | Ignores operational impact |
| Mitigation quality | Rollback, dual index, shadow evals, recall gates | “Use better embeddings” vaguely |
| Communication clarity | Explains candidate-generation failure clearly | Gives generic RAG answer |
