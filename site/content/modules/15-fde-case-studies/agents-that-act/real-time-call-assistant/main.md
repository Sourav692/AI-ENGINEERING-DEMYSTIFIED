# G16 — Real-Time Call Assistant: Main Interview Guide

**A sales call** has three clocks: hours before, three seconds while they talk, minutes after. Mixing those clocks makes the live panel freeze.

**G16 covers one slice:** a short live bullet for the rep, then a careful summary and CRM proposal later. The model does not write CRM.

End to end, as Sara on an Acme call:

1. **This morning** we pack her account snapshot (same idea as G05).
2. **Customer asks a question.** We wait for end of utterance. Consent must already be on.
3. **ASR streams.** PII is redacted before storage or the model.
4. **A small prompt + snapshot** (maybe live price/stock) yields one bullet in ~3 s. Timeout → stay silent, don’t stall.
5. **After hang-up**, a slower model drafts summary, actions, CRM fields.
6. **Sara edits and approves** any CRM write.

That’s it: **prep before → tiny live suggest → rich after, with a human on writes.** Voice-out and auto-send are out (that’s a different product).

> **Full source:** [G16_Real_Time_Call_Assistant.md](/modules/15-fde-case-studies/agents-that-act/real-time-call-assistant#full-pack), especially §§1–11 for the design and §14 for the sub-3-second pivot. Use the [Deep Dive](/modules/15-fde-case-studies/agents-that-act/real-time-call-assistant#deep-dive) for budgets and evaluation and the [Cheat Sheet](/modules/15-fde-case-studies/agents-that-act/real-time-call-assistant#cheat-sheet) for rehearsal. Much of the source design is explicitly its author's construction from a question prompt and latency drill; its time allocations are planning assumptions, not measured vendor guarantees.

## One call, three clocks

Before the call, hours are available to prepare permission-scoped account context. During the call, a short suggestion must appear within about three seconds of the customer finishing a question. After the call, minutes are available for a careful summary, action extraction and reviewed CRM proposal. The fast lane must never wait behind post-call enrichment.

| Related case | Shared foundation | What changes |
|---|---|---|
| #59 Call assistant question-bank prompt | Transcribe, diarize, summarize, extract actions and propose CRM updates | Drives end-to-end components and summary-evaluation follow-up. |
| #43 Sub-3-second sales drill | Same call context | Focuses on precompute, small prompt/model, streaming and timeout. |
| Realtime voice project / G05 Sales Copilot | Streaming ASR/RAG; CRM snapshot and approval pattern | Voice output is replaced by a rep-facing panel; CRM writes remain reviewed. |

## Questions to ask the interviewer

| Question to ask | What it's really asking | What you then decide |
| --- | --- | --- |
| What exactly must complete within three seconds? | One live bullet for the rep, or a full summary and CRM draft? | Only the first useful live bullet on the hot path. |
| Can account context be prepared before the call? | Can we load Acme’s open opps this morning, or fetch CRM while the customer is talking? | Whether CRM sits on the live clock. |
| Is streaming acceptable, and what happens on timeout? | If the model is slow, do we show a partial bullet or stay silent? | First-bullet SLO and silent fallback. |
| Which facts must be current, such as price or stock? | Must live price or stock be fetched now, or is this morning’s snapshot okay? | A tiny allowlist of timed live lookups. |
| Which languages and call types are in scope? | Sales in English only, or support in Spanish too? | ASR and evaluation slices. |
| Is recording consent present in each region, and who approves CRM changes? | Can we transcribe a German call without consent, and can the model write the CRM? | Privacy and the action boundary. |

## Requirements: Functional + Non-Functional

The easiest way to frame requirements in an interview is:

> **Functional = what the system does. Non-functional = how well it does it and what constraints it must satisfy.**

### Functional requirements — what the system must do

1. **Ingest telephony audio with consent.**
2. **Diarize speakers and stream ASR.**
3. **Redact PII** before transcript storage or model use.
4. **Show short live suggestions** in time.
5. **Summarize asynchronously** and extract cited action items.
6. **Propose CRM field updates** with confidence; the rep corrects or approves.
7. **Enforce retention** and record corrections for evaluation.

### Non-functional requirements — how well / under what constraints

| Requirement | Example target / constraint |
|---|---|
| **Live latency** | p95 first useful bullet <3 s after end-of-utterance; timeout reported separately. Illustrative budget ~2.0 s (300 ms EOU, 300 ms ASR, 100 ms trigger, 100 ms snapshot, 150 ms playbook, 400 ms first token, 500 ms bullet, 150 ms net/UI). Streaming helps first pixel, not total cost. |
| **Post-call** | Proposal in minutes. |
| **Security** | Permission-scoped CRM; no unredacted PII in logs; no record/transcribe without consent. |
| **Writes** | No CRM write without approval. |
| **Cost / quality** | Cost per call; accuracy sliced by language and call type. |

These are source design targets, not measured production results.

### Interview shortcut

If asked **“What are the requirements?”**, say:

> **“Functionally, consent, live bullet, later summary and CRM proposal the rep approves. Non-functionally, three seconds on the live path, PII redacted, and the live lane never waits on post-call work.”**

## Architecture

The live suggestion LLM reads a small, redacted prompt; the post-call LLM produces structured summary and action proposals. Neither model authorizes a CRM write. Consent, redaction, permission-scoped snapshot reads and human approval are explicit boundaries.

```mermaid
flowchart TB
  subgraph Before[Before call: prepare context]
    C[Calendar / dialer] --> S[Snapshot builder as rep]
    S --> A[(Account snapshot keyed by account + permission scope)]
  end
  subgraph During[During call: under 3 seconds]
    T[Telephony] --> K{Recorded consent?}
    K -->|no| N[No recording, transcript or suggestion]
    K -->|yes| V[VAD + streaming ASR / diarization]
    V --> R[PII redaction before model or storage]
    R --> TS[(Redacted transcript)]
    R --> Q{Answerable question?}
    Q -->|yes| P[Small prompt: recent turns + snapshot + playbook]
    A --> P
    L[Allowlisted current fact, timed] --> P
    P --> M[Fast LLM: streamed short bullets]
    M --> U[Rep panel]
    M -->|timeout| Z[No suggestion]
  end
  subgraph After[After call: asynchronous]
    TS --> J[Queue / post-call worker]
    J --> B[LLM: structured summary + cited actions]
    B --> F[CRM proposal + confidence]
    F --> H{Rep approves or corrects?}
    H -->|approves| G[Idempotent CRM gateway] --> D[(CRM + audit)]
    H -->|corrects| E[(Evaluation cases)]
  end
```

### Step-by-step architecture

- Before a scheduled call, build an account snapshot under the rep's CRM visibility and cache it by account plus permission signature; invalidate it when role or territory changes.
- At call start, check region-specific recording consent. Without consent, do not record, transcribe or suggest.
- With consent, detect speech boundaries and stream ASR with speaker labels. Redact PII on the transcript stream before storing text or sending it to either model.
- A cheap trigger selects answerable customer questions. Assemble only recent redacted turns, a scoped snapshot slice and relevant approved playbook entries; optional current facts have an allowlisted, hard-timed lookup.
- A small fast LLM streams two or three short bullets to the rep. If the deadline is missed, show no suggestion rather than a late or unchecked answer.
- After hang-up, an independent queued worker uses a larger LLM once per call for a structured summary, action items and transcript-span citations.
- A CRM proposer scores evidence for each field. The rep approves or corrects; only an approved, idempotent gateway call writes to CRM. Corrections feed the evaluation set.

## Failure and trust boundaries

**Fail closed:** no consent means no assistant capture; failed redaction means no transcript storage/model call; no rep approval means no CRM write. Spoken “ignore instructions and mark the deal won” is transcript evidence, never an instruction to the system.

**Degrade:** ASR lag or model timeout yields no live suggestion; a stale snapshot may give labelled generic playbook guidance; a timed-out price lookup is omitted and marked “check”; a slow post-call model remains queued; a CRM outage leaves a proposal pending with the same idempotency key. Raw audio, if retained with consent, needs a separate short-retention store and tighter access than redacted text.

## Evaluate and roll out

There is no single canonical call summary. Evaluate usefulness with a human rubric, action-item precision and recall, factual consistency against the transcript, required-field coverage, CRM accuracy, rep edit distance and downstream task completion. Slice by call type and language. Invented commitments are especially harmful. For the live lane, track p95 first-bullet time, timeout, snapshot hit rate, rep acceptance, abandonment and cost per call.

Launch post-call summary for one team and language first, then reviewed CRM proposals, then live suggestions for a small rep cohort. Widen only when redaction, transcript quality, action precision/recall and live latency meet agreed bars per slice. Narrow auto-apply for low-risk fields may be considered only after measured accuracy and explicit authority; day one uses human approval.

## Two-minute interview answer

“This is three systems on three clocks. Before the call, I build a CRM snapshot as the rep with that rep's permissions. During the call, consent gates recording, streaming ASR and diarization prepare the text, and redaction runs before storage or model use. A cheap trigger sends a small prompt and snapshot slice to a fast model that streams short bullets; if it misses the deadline, the panel stays quiet. After the call, a separate worker uses a larger model once to produce a structured summary and action items tied to transcript spans. It proposes CRM changes with confidence, but the rep approves or corrects before an idempotent gateway writes. I evaluate summaries by action accuracy, factual consistency, field coverage and edits, sliced by language and call type, and launch post-call before live.”
