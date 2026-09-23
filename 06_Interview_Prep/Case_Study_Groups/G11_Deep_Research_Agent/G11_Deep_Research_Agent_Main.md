# G11 — Deep Research Agent: Main Interview Guide

**Research process** is: a question, hunt on the web and in *your* files, a cited brief. Failed hunt should look incomplete, not confident-fake.

**G11 covers one slice:** bounded, read-only research with citations. It cannot send email or buy anything.

End to end, as “Who is Acme’s CEO, with sources?”

1. **You authenticate.** Budgets and rate limits lock in. First signal in seconds.
2. **A planner splits work:** public web vs your Drive. Web never inherits Drive tokens.
3. **Subagents search.** Wikipedia timeout is “couldn’t check,” not “not found.”
4. **Findings go to a ledger.** A grader asks: enough coverage, or one more hop?
5. **A synthesizer writes only from that ledger.** Every fact needs a citation.
6. **A verifier and sanitizer** strip bad links/HTML. Gaps stay visible.

That’s it: **plan → search in isolation → cite or show the hole → stop.** External actions stay out.

> **Source:** [G11_Deep_Research_Agent.md](G11_Deep_Research_Agent.md). Use the [Deep Dive](G11_Deep_Research_Agent_Deep_Dive.md) for state and security mechanics and the [Cheat Sheet](G11_Deep_Research_Agent_Cheat_Sheet.md) for rehearsal.

## The case in one sentence

Build a read-only research agent for public web and a user's private documents: about 100,000 daily users and 40,000 research runs/day, p95 under 90 seconds, first signal under 3 seconds, 3–12 steps/run, cited claims, and about $0.20/run. A failed branch yields an explicitly incomplete answer, not fabricated certainty.

## Questions to ask the interviewer

| Question to ask | What it's really asking | What you then decide |
| --- | --- | --- |
| What is an acceptable citation, and must every factual claim have one? | If we say “Acme’s CEO is Jane,” must we show the URL and span, or is a vibe okay? | Evidence schema and verifier. |
| Which sources are public and which are user-scoped? | Can the web agent see my Drive, or only public pages? | Tool identities and isolation. |
| What happens when a source is unavailable or search finds nothing? | If Wikipedia timed out, do we say “not found” or “we couldn’t check”? | `EMPTY` vs `UNAVAILABLE`, and when a partial answer is allowed. |
| What makes a research run complete? | After 12 hops we still lack a number — keep going, or stop and show the gap? | Coverage rubric, hop cap, and no-progress stop. |
| May answers contain external links, images or rendered HTML? | Can the answer include a tracking pixel or a `javascript:` link from a random page? | Egress sanitization. |
| Is $0.20 a hard cap or target, and at what traffic peak? | At noon, if a run would cost $0.50, do we stop mid-research? | Model routing and search budgets. |

## Requirements and sizing

**Functional:** authenticate and rate-limit; plan a bounded research task; search the web and user documents with separate privileges; merge typed evidence; check coverage and replan if useful; synthesize with citations; verify claims and sanitize rendered output; stream status and return explicit gaps.

**Non-functional:** p95 run latency <90s, first progress <3s, roughly $0.20/run, strict cross-user isolation, bounded tool calls and retries, auditable citations, safe handling of untrusted web content. The agent is read-only and cannot take external actions.

40,000 runs/day averages about 28/minute. A rough 3× peak is about 100/minute; at 70 seconds of active time that implies roughly 120 in flight, or around 170 slots at 70% utilization. These are planning estimates, not a precise queueing guarantee. A naive seven-step plan can send around 30,000 input tokens, so context isolation and routing are primary cost levers.

## Architecture

The planner and synthesizer use a reasoning-tier LLM; narrower web/document agents can use smaller models. The supervisor is bounded by deterministic hop, budget and no-progress rules. Web agents never inherit private-document access.

```mermaid
flowchart LR
  U[User + auth / rate limit] --> P[LLM planner: bounded dependency plan]
  P --> W[Parallel web subagents: public tools only]
  P --> D[User-scoped document subagent]
  W --> T[Typed findings boundary]
  D --> T
  T --> L[User-scoped evidence ledger: append / dedupe]
  L --> G[Coverage + agreement grader]
  G -->|thin, budget remains| P
  G --> Y[Reasoning LLM synthesizer with citations]
  Y --> V[Claim and citation verifier]
  V --> E[Egress sanitizer: links / images / markup]
  E --> O[Streamed answer + explicit coverage gaps]
```

### Step-by-step architecture

1. Authenticate the user, apply run budgets and rate limits, and emit a first progress signal quickly.
2. A reasoning LLM makes a small dependency-aware plan; deterministic controls cap hops, elapsed time, calls and spend.
3. Independent web subagents search public sources in parallel while a separate document subagent retrieves only documents that this user may read.
4. Each branch returns typed findings and citations, not instructions. A reducer appends and deduplicates evidence in a user-scoped ledger.
5. A coverage grader compares findings with the plan. It may request a capped replan; repeated delegation without new evidence stops.
6. A synthesizer writes claims grounded in the ledger; a verifier checks claim-citation support and marks unavailable or uncovered areas.
7. An egress sanitizer removes image/markup fetches and disallowed links before streaming a cited answer or clearly labelled partial result.

## Key choices and failure modes

**Isolation is the hard boundary.** Web pages and retrieved content are untrusted. The web agent gets no private-document credentials. Prompt text cannot enforce this. The final rendered answer is also an egress path, so strip Markdown images and fetch-inducing markup. Never share private-answer caches across users.

**Parallel merge must be correct.** If branches write a single `summary` field, last-write-wins can silently drop findings. Store a list of typed evidence with an append/concatenate reducer, provenance and dedupe. Sum budget consumption across branches.

**Termination matters.** Use a hard hop cap (the source gives eight as an example), per-run money/tool limits and no-progress detection. Distinguish no evidence found from a failed source. On a cap or outage, provide a partial answer with the missing section named.

**Cost and latency:** isolate subagent contexts; use smaller models for narrow extraction and a stronger model for planning/synthesis; cap rounds; deduplicate searches; cache public facts and user-scoped private work separately; measure cost by branch, hop and synthesis tokens. Parallelism helps only when tasks are independent and provider limits permit it.

## Evaluation, rollout and variants

Score outcome and trajectory: citation support, unsupported-claim rate, coverage, cross-user leak rate, p95 latency, first signal, cost/run, hop count and tool routing. Test poisoned web pages, missing documents, conflicting sources, empty search and unavailable tools. Audit not only final answers but the evidence ledger and link sanitizer.

The related AWS research platform uses API limits, Bedrock guardrails, Redis/RDS memory, a search–summarize–write–critic loop and observability, but its source notes lack of per-user ACL and deterministic release gating; those defaults cannot be imported unchanged into this enterprise case. The supervisor-worker variant justifies multiple agents for parallelism, distinct permissions or context isolation. If decomposition is predictable, a deterministic workflow is simpler.

## Two-minute interview answer

“I would clarify citation quality, private-document permissions and the partial-answer contract first. The planner builds a bounded research plan, then public-web workers and a separate user-scoped document worker gather typed findings in parallel. Their evidence is appended into a user-scoped ledger; a coverage check can trigger a limited replan. A stronger LLM synthesizes the answer, and a claim verifier plus egress sanitizer ensures citations support the claims and rendered output cannot leak private content through images or links. I enforce hop, time and spend caps, return explicit gaps on failure, and measure both answer quality and the path the agents took.”
