# G10 — High-Volume Batch Pipeline: Cheat Sheet

[Main](/modules/15-fde-case-studies/platforms-and-scale/high-volume-batch-pipeline#main) · [Deep Dive](/modules/15-fde-case-studies/platforms-and-scale/high-volume-batch-pipeline#deep-dive) · [Unchanged source](/modules/15-fde-case-studies/platforms-and-scale/high-volume-batch-pipeline#full-pack)

## Open with the contract

“Is 6 a.m. a hard deadline, and can we publish partial results?” Ask about token distribution, provider quotas, permanent errors, fallback approval and replay/version requirements.

## Whiteboard path

`Job API → immutable snapshot + partition manifest → durable leases → workers → rate coordinator → classifier model/LLM → typed validation → idempotent sink → checkpoint + ack → reconcile + publish`

The model classifies or extracts; deterministic orchestration owns the workflow. Checkpoint **after** sink success.

## Numbers

100M / 6h ≈ **4,630 records/s**; +15% ≈ **5,320/s**. At 270 tokens/record, ≈ **27B tokens/run** before retries (the source's 5.15B figure is an arithmetic error). At 10×, ≈ **53,200/s** with margin. Confirm against measured token and latency distributions.

## Failure answer

At 4 a.m. and 45% complete: forecast remaining capacity; inspect quota, hot shards, compute and sink; increase concurrency only with headroom; use approved fallback or explicitly labelled partial output only if policy allows. Preserve checkpoints and page the owner if impossible.

## Five anchors

- Immutable snapshot and pinned model/prompt/schema make replay meaningful.
- Unique `(job_id, record_id, model_version)` gives one logical result under retries.
- Transient failures retry; permanent failures quarantine with lineage.
- Watch ETA, oldest partition, throttles, cost/million and reconciliation counts.
- For document variants, add OCR, typed extraction, human review and versioned reprocessing.

**60-second close:** “I design for safe replay and deadline recovery. The immutable manifest feeds leased workers behind shared rate limits; outputs are validated and upserted before checkpointing. A live ETA and a pre-agreed publish policy determine the response when the window is at risk.”
