# G10 — High-Volume Batch Pipeline: Deep Dive

> Read with the unchanged [source](G10_High_Volume_Batch_Pipeline.md). The [Main guide](G10_High_Volume_Batch_Pipeline_Main.md) is the interview path; the [Cheat Sheet](G10_High_Volume_Batch_Pipeline_Cheat_Sheet.md) is the quick recall card.

## 1. Contract before machinery

The question is recovery under a deadline. Get the output contract first: complete-only or partial publish; what to do with permanently bad records; acceptable fallback models; who approves changes. A queue cannot answer those product decisions. Store the policy with the job so an operator cannot improvise under pressure.

Job creation should be idempotent. Expose create, status, pause and replay-failures operations, guarded by authorization. Use ETags or equivalent conditional updates for operator actions. The job record pins snapshot ID, partition manifest, model/prompt/schema versions, deadline and publication rule. Preserve enough lineage to reproduce an individual result and the whole run.

## 2. Capacity arithmetic and cost

100 million / six hours is about 4,630 records/s. Fifteen percent capacity margin brings the target to about 5,320. At 10× volume, the same window needs about 53,200/s including margin. If one record averages 270 tokens, the base run is **27 billion tokens**; include retries, long-tail records and output variance in the estimate. The source's 5.15-billion-token total is an arithmetic error: 100 million × 270 = 27 billion. A provider's tokens/s quota may be the real ceiling even if CPU workers look idle.

Plan with measured distributions: p50/p95 record tokens, model latency, batch efficiency, provider throttling, sink throughput and hot partitions. ETA is remaining work divided by observed *effective* throughput, adjusted for the straggler tail. An average-rate graph alone hides deadline failure.

## 3. State and replay

The immutable snapshot prevents input drift during a long run. Partition IDs are deterministic and bounded; queue messages contain identifiers, while workers fetch scoped records. A lease expiration makes crashed work visible again. The result sink's unique key `(job_id, record_id, model_version)` turns reprocessing into an upsert rather than a duplicate. Commit output before checkpoint, checkpoint before queue ack. A crash at any point can replay work safely; it may still pay for another model call, so track replay cost.

Transient errors include throttling, network failure and temporary sink outage. Use backoff, jitter and capped retries. Validation failures or invalid source records should be quarantined with reason and lineage. Reconciliation compares manifest count, successful unique results and quarantined records. Publish only when those counts and the stored policy agree.

## 4. Security and operations

Keep input and output encrypted, isolate tenants, scope snapshots and credentials, and avoid full customer payloads in queue messages or logs. Record operator actions and model version changes. A per-tenant rate coordinator prevents one customer from starving others; global controls protect provider quota. Circuit breaking stops repeated failing calls while retaining durable pending work.

At 4 a.m. with 45% complete, calculate the throughput still required, then identify the limiting stage. Add workers only if provider and sink capacity permit. Splitting a straggler partition must preserve deterministic IDs. A fallback model changes output semantics, so it must be approved and versioned. If success is impossible, preserve the state, stop leasing and communicate the exact incomplete count. Partial output is a business rule, not an accident.

## 5. Variants and trade-offs

For bank documents, the pipeline expands to file validation, OCR/multimodal parsing, document classification and schema extraction, followed by confidence checks and human review. Lineage must point from output fields to source pages. Reprocessing by model version is necessary when a model improves or formats drift.

For nightly PDF summarization, deduplicate by content hash and process only changed documents; a cheaper batch model may handle routine summaries, with stronger-model audits. For an embedding-cost spike, incremental indexing and avoiding unchanged content are the first levers. None of these shortcuts should hide permanent failures or erase provenance.

## 6. Evidence to collect

Track throughput, tokens/s, provider throttles, lease retries, oldest queued partition, predicted completion time, unique committed records, quarantine reasons, sink p95, cost per million and replay spend. Begin rollout on a representative token distribution, then 1%, 10% and higher load. Inject worker crash after write, provider quota exhaustion, and sink outage. A successful demo is not enough; demonstrate restart and reconciliation under those failures.
