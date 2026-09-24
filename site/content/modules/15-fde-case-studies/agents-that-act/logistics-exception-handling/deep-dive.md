# G17 — Logistics Exception Handling: Deep Dive

> Read with the unchanged [source](/modules/15-fde-case-studies/agents-that-act/logistics-exception-handling#full-pack). The [Main guide](/modules/15-fde-case-studies/agents-that-act/logistics-exception-handling#main) gives the interview flow; the [Cheat Sheet](/modules/15-fde-case-studies/agents-that-act/logistics-exception-handling#cheat-sheet) is the recall card.

## 1. Event rate, exception rate and feed freshness

The approximately 200 webhook events/s at peak are not 200 agent decisions/s. A peak sustained for 24 hours would be 17.3M events, an upper bound. The approximately 150 agents each handle 30–50 cases daily, or 4,500–7,500 cases in the simple sizing estimate. Put cheap detection before the model so inference spend follows disruptions. The 40 concurrent agents at shift handoff size review UX and queue SLA, not stream ingestion. Batch-only carriers report every 2–6 hours; no polling trick removes that upstream delay.

Webhook ingest validates payload and deduplicates carrier retries. File ingest parses CSV/EDI and diffs the latest shipment state, emitting only changes. Both use the same regional event schema. Include source timestamp, ingest timestamp and detection timestamp to expose freshness. A regional queue absorbs weather bursts; monitor oldest-event age and detection recall rather than only queue depth.

## 2. Gate, identity and execution

Detection supplies the exception type. The model/agent supplies a proposed action, confidence and reasons but does not have carrier-write credentials. The gate checks customs/regulatory first; then only a non-customs shipment below $500 with calibrated high confidence can enter auto-execution. Missing type, value, confidence or policy version means human review. Keep the policy version with the decision and test forced-high-confidence customs examples on every release.

Each carrier action needs an idempotency key tied to the specific shipment and resolution version. A timed-out rebook could have succeeded, so blind retry risks a second booking. Carrier APIs without idempotent semantics may remain human-only. Limit retries and use a circuit breaker to send work to review when a carrier is unhealthy. Audit both automated and human decisions, including original draft, agent edit/reject and action result. If the audit store is unavailable, do not perform an unaudited action.

## 3. Residency and stakeholder surface

One versioned control plane distributes prompts, model routes, policy definitions and UI logic, but US, EU and APAC data planes hold their own event stores, model inputs and audit logs. EU data never leaves EU. Application sessions must enforce region access too; isolated storage alone does not prevent a cross-region query. Cross-region reporting can use approved aggregate metrics rather than raw shipment records.

In the #66 rerouting variant, SAP is authoritative shipment state and a possible write target; weather is a predictive signal stamped with freshness; 500 warehouse managers are distributed approvers. Regional system differences belong in adapters. A walking skeleton should take one SAP extract and one weather feed to one regional manager, even with a mocked agent, before broad integration work. If weather disappears, scan-driven detection still works and the draft states the missing signal.

## 4. Evaluation and rollout

Replay historical shipments with labels for detection recall and false alarms per exception type. Calibrate confidence, then inspect approve-unedited, approve-edited and reject rates. Join outcome to delivery against revised ETA days later. Test executor crash/replay for duplicate booking and every region-to-region access denial. Compare rerouted shipments with matched holdouts because one shipment cannot reveal the alternative route's outcome.

First run offline with no carrier writes, then shadow live traffic while humans act, then enable low-value, high-confidence known-route missed scans for one carrier and region. Release gates: customs auto-resolve count zero on adversarial cases, detection recall not worse, residency tests passing and audit complete. Monitor cost/resolved exception, model calls/exception, time-to-draft by feed, queue age and reversal rate. A quality gain in draft fluency does not compensate for a customs gate failure.
