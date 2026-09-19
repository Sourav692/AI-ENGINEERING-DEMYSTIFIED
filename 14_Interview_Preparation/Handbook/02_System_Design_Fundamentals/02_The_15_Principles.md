# The 15 Principles

> **Level** 🟢 Foundations · **Module** 02 · **Doc** 2 of 5 · **Time** ~25 min
> **Prerequisites:** [The 12-Part Framework](01_The_12_Part_Framework.md)
> **Source material:** `4. FDE_Related_Preparation/System_Design and Delivery/3. System Design Principles.md`

## Why this matters

The 12-part framework tells you *what to cover*. Principles tell you *how to decide* inside each part. Interviewers expect you to apply them naturally — not to recite them, but to reach for the right one at the right moment and let it justify a decision. Every principle below comes with an AI-system example, because the generic version ("keep it simple") is not what gets tested; the applied version ("start with single-agent RAG before multi-agent") is.

## The fifteen, at a glance

| # | Principle | Applied to an AI system |
|---|---|---|
| 1 | Simplicity (KISS) | Start with a single-agent RAG before introducing a multi-agent architecture |
| 2 | Separation of concerns | Ingestion, embedding, retrieval and generation as independent services |
| 3 | Loose coupling | The embedding service must not depend on the LLM service |
| 4 | High cohesion | All prompt templates and prompt management in one module |
| 5 | Scalability | Scale vector search independently from LLM inference |
| 6 | Reliability | Retry transient LLM failures; fall back to a secondary model |
| 7 | Fault tolerance | If reranking fails, return retrieved documents rather than failing the request |
| 8 | Availability | Inference endpoints across multiple regions |
| 9 | Performance | Cache embeddings and frequent answers |
| 10 | Security by design | Encrypt vector stores, authenticate APIs, redact before prompting |
| 11 | Observability | Track retrieval precision, tokens, latency, hallucination rate, model errors |
| 12 | Extensibility | An interface that swaps OpenAI for Gemini or Claude with minimal change |
| 13 | Cost optimisation | A small model for routing, a large one only for complex requests |
| 14 | Data consistency | Refresh embeddings when sources change; version the index |
| 15 | Maintainability | Modular services, clear APIs, automated tests, infrastructure as code |

## The fifteen, expanded

### 1 · Simplicity

Complexity should be earned by a real requirement, not added pre-emptively. A single-agent RAG pipeline is easier to reason about, test and debug than an orchestrator you do not yet need — and it gives you a clean baseline to point back to when someone asks why a component exists. Module 07 opens with exactly this principle: one agent by default.

### 2 · Separation of concerns

When ingestion, embedding, retrieval and generation live in separate services, each can be scaled, tested or redeployed without touching the others. It also isolates failure: an embedding-service outage does not have to take down response generation if the two were never coupled.

### 3 · Loose coupling

The embedding service should not need to know which LLM provider you call, and the LLM service should not care how embeddings were made. That independence is what lets you replace either side — swap embedding models, switch vendors — without a coordinated rewrite of both.

### 4 · High cohesion

Scattering prompt templates and prompt-management logic across services turns a single prompt change into a multi-file hunt. Keep everything that changes together — templates, versioning, injection logic — in one place to look and one place to test. Module 08 makes this concrete with prompt registries.

### 5 · Scalability

Vector search and LLM inference have different scaling profiles — one is I/O and index-size bound, the other compute bound. Bundle them into one scaling unit and you over-provision one to satisfy the other. Scale them independently and each grows, and costs, in proportion to its own load.

### 6 · Reliability

A production LLM call will occasionally time out or return a malformed response. Reliability is planning for that in advance — retries with backoff for transient failures, a secondary model to fail over to when the primary is down — rather than treating every failure as an incident. Module 03 builds this.

### 7 · Fault tolerance

Reliability's companion: a failure in one non-critical stage should not take down the whole request. If reranking fails, returning the raw retrieved documents — degraded but usable — beats failing outright. The RAG whiteboard script in Module 09 has a full table of *what degrades* rather than *what breaks*.

### 8 · Availability

Expressed in nines, bought with redundancy. Inference endpoints in multiple regions mean a single region's outage, maintenance window or capacity crunch does not take the service offline.

### 9 · Performance

Every embedding you recompute and every FAQ you re-answer from scratch is latency and cost you did not need to spend. Caching embeddings and frequent responses turns the expensive path into the exception — usually the single biggest lever on both metrics at once. Module 06 covers semantic caching and its correctness risk.

### 10 · Security by design

Retrofitting security into an AI pipeline after launch means auditing every place a document or prompt has already touched. Building it in from the start — encrypted vector stores, authenticated APIs, PII redaction before anything reaches a prompt — means sensitive data never has a window of exposure. Module 04's entire access-control design is this principle.

### 11 · Observability

An LLM system fails in ways a traditional service does not — a technically successful call that hallucinates, or retrieval that quietly returns the wrong documents. Tracking retrieval precision, token usage, latency, hallucination rate and model errors turns "the answers feel worse lately" into a specific, fixable regression.

### 12 · Extensibility

This quarter's best model is rarely next quarter's. An interface that swaps providers with a config change rather than a rewrite keeps you from being locked into a decision made under different constraints. Module 01's brain contract is a small instance of this.

### 13 · Cost optimisation

Not every request needs your most expensive model. Routing simple lookups to a small, cheap model and reserving the large one for genuinely complex requests can cut inference spend by an order of magnitude with little quality loss on the easy cases.

### 14 · Data consistency

An embedding that no longer matches its source document is a subtle, silent failure — the system confidently retrieves and answers from stale content. Refreshing embeddings on source change and versioning the vector index keeps retrieval grounded in current truth. Module 04's freshness tracking and Module 06's ACL-vs-content sync separation are applications.

### 15 · Maintainability

The system you ship is rarely the system you are still running a year later. Modular services, clear APIs, automated tests and infrastructure as code make the next change safe instead of risky.

## A mnemonic: SCALED PRINCIPLES

Fifteen items is a lot to hold mid-conversation. **SCALED** compresses the six core design goals into six letters, and reminds you that the remaining five are not a seventh category — they are a lens applied to every one of the six.

```
              S — Simplicity
              |
D — Durability &                C — Cohesion &
    Data Consistency                 Coupling
        \                          /
         \      SCALED PRINCIPLES /
         /                        \
        /                          \
E — Extensibility            A — Availability
              \                /
               \              /
                L — Latency (Performance)

   outer ring (applies to every spoke):
   Security · Observability · Reliability · Cost · Maintainability
```

## How this sounds in a design conversation

A strong candidate does not list principles; they narrate decisions, and the principle is implicit in the reasoning. For *"design an AI-powered customer support chatbot"*:

| Principle | What it sounds like |
|---|---|
| Simplicity | "I'll start with a single-agent RAG architecture because it meets the current requirements." |
| Scalability | "The retrieval service and the inference layer will scale independently." |
| Reliability | "If the primary LLM is unavailable, requests fail over to a backup model." |
| Performance | "I'll cache frequent responses and reuse embeddings to reduce latency." |
| Security | "Sensitive customer data is masked before it enters any prompt." |
| Observability | "I'll monitor latency, retrieval quality, token usage and hallucination rate." |
| Cost | "Simple queries use a smaller model; complex ones route to a more capable one." |

## Eight lenses, in order

When evaluating any design, work these in order. The order is what makes the answer sound structured rather than improvised:

1. **Requirements** — what problem are we solving?
2. **Architecture** — how are the components organised?
3. **Scalability** — can it handle growth?
4. **Reliability** — what happens when components fail?
5. **Performance** — does it meet latency and throughput goals?
6. **Security** — how is data protected?
7. **Observability** — how will we detect and diagnose issues?
8. **Cost & evolution** — is it economical today, and can it evolve tomorrow?

## Interview lens

The principles are most useful as *tie-breakers you can name*. When two designs both work, "I chose this one because it keeps the embedding service decoupled from the model provider, which we will want when we switch vendors" is a decision with a reason. "I chose this one" is a guess.

## Checkpoint

- For any five principles, give the AI-specific example without looking.
- What do the six SCALED spokes stand for, and why are the outer five not a seventh spoke?
- Take the customer-support chatbot prompt and narrate three decisions, each carrying a principle implicitly.
- Which principle argues *against* multi-agent architectures as a starting point, and why?

**Next →** [Monolith vs Microservices](03_Monolith_vs_Microservices.md)
