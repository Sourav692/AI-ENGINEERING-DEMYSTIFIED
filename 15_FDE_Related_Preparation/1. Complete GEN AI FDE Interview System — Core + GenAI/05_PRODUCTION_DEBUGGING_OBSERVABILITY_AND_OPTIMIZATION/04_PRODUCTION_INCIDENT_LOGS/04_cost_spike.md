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
