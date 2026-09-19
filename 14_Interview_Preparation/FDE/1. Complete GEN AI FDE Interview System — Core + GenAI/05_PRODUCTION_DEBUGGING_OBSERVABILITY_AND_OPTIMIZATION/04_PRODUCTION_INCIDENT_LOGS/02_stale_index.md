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
