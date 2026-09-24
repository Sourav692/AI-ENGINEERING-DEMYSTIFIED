# G16 — Real-Time Call Assistant: Cheat Sheet

[Main](/modules/15-fde-case-studies/agents-that-act/real-time-call-assistant#main) · [Deep Dive](/modules/15-fde-case-studies/agents-that-act/real-time-call-assistant#deep-dive) · [Unchanged source](/modules/15-fde-case-studies/agents-that-act/real-time-call-assistant#full-pack)

## Ask first

What must fit in 3 seconds? Can context be precomputed? Is streaming okay? Which facts must be current? What happens on timeout? Which languages, consent rules and CRM approvers?

## Three clocks

**Before:** permission-scoped account snapshot.  
**During:** consent → VAD/streaming ASR + diarization → redact → trigger → small prompt + snapshot → fast LLM → short streamed bullets; timeout means silence.  
**After:** queued larger LLM → cited summary/actions → confidence-scored CRM proposal → rep approval → idempotent write.

## Boundaries

- No consent: no recording, transcription or suggestion.
- Failed redaction: no transcript storage or model call.
- The model proposes CRM changes; the rep authorizes the write.
- Snapshot permissions mirror the rep; live facts use a timed allowlist.

## Numbers and evaluation

Source planning budget ≈ **2.0s** for first bullet, leaving ~1s under a 3s p95 target; measure the real stage tails. Evaluate summaries by action precision/recall, factual consistency, required-field coverage, CRM accuracy and edit distance, sliced by call type/language. Track live first-bullet p95, timeouts, accept rate and cost/call.

**60-second close:** “Precompute before, use a small streamed model during, and do careful reviewed enrichment after. Consent and redaction guard the data; human approval guards CRM writes.”
