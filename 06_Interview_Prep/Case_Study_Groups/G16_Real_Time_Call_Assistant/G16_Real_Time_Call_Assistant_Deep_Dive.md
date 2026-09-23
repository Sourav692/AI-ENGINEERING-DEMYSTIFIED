# G16 — Real-Time Call Assistant: Deep Dive

> Read with the unchanged [source](G16_Real_Time_Call_Assistant.md). The [Main guide](G16_Real_Time_Call_Assistant_Main.md) is the interview path; the [Cheat Sheet](G16_Real_Time_Call_Assistant_Cheat_Sheet.md) is the recall card. The source marks much of the architecture and the 2-second stage budget as its own construction; validate those assumptions with production measurements.

## 1. Three lanes and the budget

Before call: calendar or dialer triggers a CRM snapshot under the rep's identity, containing accessible account history, open cases and approved playbook context. Key cache by account and permission signature; invalidate on role or territory changes. Inbound calls require rapid caller-to-account matching and a minimal snapshot during the greeting. Keep frequently changing facts, such as price, stock and open case status, out of stale snapshots.

During call: end-of-utterance is the clock start. The illustrative budget is VAD 300ms, final ASR tail 300ms, trigger 100ms, snapshot 100ms, playbook 150ms, first model token 400ms, first bullet 500ms and network/UI 150ms, roughly 2.0 seconds plus about one second of headroom. These figures are planning allocations. Measure p95 end-to-end and each stage under real accents, networks and model load. A live fact lookup must be allowlisted, read-only, parallel and timed; if it misses, omit that fact. Avoid sequential CRM calls and large prompts. Streaming changes perceived latency, not total work.

After call: an independent queue isolates summary/extraction from the hot path. A larger LLM reads the redacted transcript once and returns a fixed schema: summary, action items with owner/due date and cited transcript span, commitments, objections and proposed CRM fields. Retries must preserve idempotency; slow post-call work must never queue in front of the next call's suggestions.

## 2. Privacy, consent and permissions

Audio may contain voices, payment data and other PII. No recorded consent means no recording, transcript or suggestion. ASR with diarization uses separate speaker channels when available, and model-based diarization only when needed. A speaker swap changes who made a promise, so diarization is a correctness control. Redact the transcript stream before storage and before either LLM call, using typed placeholders. If consented raw audio is retained, use a separate short-retention store and tighter access. Enforce regional retention through scheduled deletion and alert on deletion failure.

The snapshot must mirror the rep's CRM field visibility. A useful suggestion containing another territory's deal value is still a leak. The transcript is untrusted content and cannot instruct a CRM write. The model only proposes; policy and the rep authorize. An approved write uses a gateway idempotency key so a double click or retry does not update twice. Log corrections for review without exposing raw PII in telemetry.

## 3. Evaluation without one correct summary

Reference-text overlap is a poor metric for open-ended summaries. Score by purpose: human usefulness rubric, action-item precision/recall, factual consistency to the transcript, required field coverage, CRM update accuracy, rep edit distance and downstream completion. Every action item should point to its supporting transcript span. Invented actions are particularly costly because they create false promises. Slice the golden set by call type and language; do not let strong English sales scores hide poor accented support transcription. Rep corrections create high-value cases after review and redaction.

For live suggestions, use first-bullet p95, total latency, timeout, precompute hit rate, rep accept rate, abandonment and cost per call. Trigger only on useful questions, cap bullet length, keep connections warm and cancel generation if the rep has already answered. A late suggestion may be worse than silence.

## 4. Failure matrix and rollout

Consent, redaction and CRM approval fail closed. ASR or fast-model failure yields no live help; a missing snapshot allows labelled generic playbook guidance; a timed-out live lookup says “check” rather than inventing a price. Post-call provider failure queues/retries, CRM failure leaves proposals pending, and retention deletion failure alerts. Separate these by stage so a post-call incident cannot consume live capacity.

Rollout: one team/language gets consented transcription, redaction and post-call summary first; next add action extraction and review-only CRM proposals; then five reps or another small cohort get live suggestions; finally expand call types and languages based on each slice's metrics. Narrow auto-apply is a later, evidence-based exception. The week-by-week dates in the source are a proposed plan, not a production outcome.
