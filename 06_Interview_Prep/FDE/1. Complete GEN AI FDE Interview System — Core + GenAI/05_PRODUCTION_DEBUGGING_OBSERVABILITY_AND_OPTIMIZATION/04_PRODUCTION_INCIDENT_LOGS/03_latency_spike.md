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
