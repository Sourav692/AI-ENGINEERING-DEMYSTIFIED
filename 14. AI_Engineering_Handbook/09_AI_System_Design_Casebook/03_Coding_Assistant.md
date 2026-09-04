# Case 3 — AI-Powered Coding Assistant

> **Level** 🔴 Design Mastery · **Module** 09 · **Doc** 3 of 6 · **Time** ~30 min
> **Prerequisites:** Module 01 doc 2, Module 02, Module 06 doc 3
> **Source material:** `4. FDE_Related_Preparation/System_Design and Delivery/7. AI Powered Coding Assistant Design.md`

## The prompt

Design an AI-powered coding assistant like GitHub Copilot: real-time completion, code explanation, unit-test generation, bug fixing, refactoring, developer Q&A — integrated into the IDE. Explain how **context engineering, semantic retrieval, model routing, semantic caching and output validation** combine to keep suggestions fast, accurate and safe.

## Step 1 — Define the problem space

The combination of *"must feel instant"* and *"must understand my entire repository"* is what makes this a context-engineering problem as much as a distributed-systems one.

| Question | Answer | What it decides |
|---|---|---|
| Cloud or local? | Both exist | Where inference happens; the privacy story |
| Real-time as the user types? | Yes | The latency budget is set before anything else — **< 300 ms** |
| Which IDEs and languages? | VS Code, IntelliJ, Visual Studio; mainstream languages | A thin, IDE-agnostic extension talking to a shared backend |
| Whole repository or current file? | The whole repo, within reason | Context engineering is the hard problem |
| Private models and on-prem for enterprise? | Yes | Security and deployment shaped from day one |

**Functional:** completion (single and multi-line); explain; generate tests, docs, commit messages; refactor; fix errors; answer questions; search the codebase; multi-language; workspace-aware. **Non-functional:** < 300 ms autocomplete; accuracy; low hallucination; availability; enterprise security; millions of developers; personalisation; cost.

## Step 2 — High-level architecture: cache first, retrieve on a miss, route by task

```
IDE Extension
│
Authentication Service
│
API Gateway / Load Balancer
┌──────────────┴──────────────┐
Context Collection      User Preferences
└──────────────┬──────────────┘         Conversation Memory
               │  ◄──────────────────────────────┘
        Context Builder
               │
        Semantic Cache
        ┌──────┴──────┐
    Cache Hit      Cache Miss
        │              │
        │        Embedding Service
        │              │
        │        Vector Database
        │              │
        │        Relevant Code Retrieval
        └──────┬────────┘
          Prompt Builder
               │
          Model Router
        ┌──────┴──────┐
Small Fast Model   Large Reasoning Model
        └──────┬──────┘
        Output Validation
               │
          IDE Suggestions
```

The semantic cache is the load-bearing latency optimisation: the common case — a completion the assistant has effectively seen before — skips embedding, retrieval, and often the large model entirely.

## Step 3 — The request flow, keystroke to accepted suggestion

1. **User types** — `def calculate_total(items):`; the extension detects the cursor position.
2. **Context collection** — current function, file, open tabs, imports, repo structure, cursor location, language, recent edits, compiler errors — *selecting only what is relevant*, never the whole repository.
3. **Semantic code search** — similar functions, existing helpers, internal APIs, conventions — preventing duplicate implementations and encouraging reuse.
4. **Prompt construction** — system instructions, the request, current code, retrieved snippets, language/framework, conventions, relevant docs.
5. **Model routing** — by task complexity, balancing latency, quality, cost.
6. **Generate.**
7. **Output validation** — parse the code, check syntax, validate formatting, apply security filters, **detect hallucinated APIs**, remove unsafe patterns. Invalid or low-confidence output is regenerated or suppressed.
8. **Return** — streamed inline. Accept, partial-accept, reject, or request alternatives — feedback for personalisation.

## Step 4 — Context engineering and model routing

Not every task needs the largest model, and not every context signal is worth its token cost. The routing decision and the context-collection decision are the same kind of trade: spend latency and money only where it buys accuracy.

| Task | Model |
|---|---|
| Next-word completion | Small, low-latency |
| Multi-line completion | Medium |
| Code explanation | Larger reasoning |
| Bug fixing | Larger reasoning |
| Refactoring | Larger reasoning |
| Architecture questions | Most capable |

**Context engineering is a funnel, not a filter that runs once:**

```
Full Repository & Workspace (potentially millions of tokens)
                    │  ✕ unrelated files
Relevant Signals (current file, imports, open tabs, cursor, recent edits)
                    │  ✕ distant history
Compressed & Ranked Context (semantic search + prioritisation)
                    │
Final Prompt (fits the model's context window)
```

The concepts interviewers want to hear, named: **context engineering** (include only what materially improves the response); **semantic search** (*"calculate tax"* retrieves `compute_gst()`); **prompt management** (templates per task — completion, tests, bug fix, refactor, docs, explain — versioned for safe experimentation and rollback; Module 08 doc 1); **model routing**; **semantic cache** (boilerplate, standard algorithms, popular API usage); **context window management** (retrieve only relevant files, chunk intelligently, compress history, prioritise nearby code).

## Step 5 — Scaling to millions of developers under 300 ms

1. **Stateless API servers** behind load balancers.
2. **Distributed vector databases** sharded across regions and repositories.
3. **GPU inference clusters** autoscaling to absorb bursty keystroke demand.
4. **Streaming responses** — perceived latency drops even when total does not (Module 06 doc 3).
5. **Multi-region deployment** — inference close to developers; static assets on a CDN.
6. **Rate limiting and batching.**

**The latency budget, decomposed:** ~10 ms cache check → ~40 ms context assembly → ~200 ms model inference (streamed) → ~50 ms validation. The cache check and context assembly stay cheap; most of the budget goes to streamed inference; validation runs in the remaining margin. Being able to *decompose* a latency target like this is what turns "< 300 ms" from a requirement into a design.

## Security — source code is the most sensitive asset in the pipeline

Never train foundation models on private enterprise code without explicit consent. Encrypt in transit and at rest. Enforce repository-level access control and **respect organisational permissions during retrieval** — Module 04's problem, over code. Mask secrets and credentials before sending context. Support private deployment for regulated industries. Audit logs.

## Trade-offs

| Decision | Pros | Cons |
|---|---|---|
| Small model | Fast, inexpensive | Lower reasoning quality |
| Large model | Better suggestions | Latency and cost |
| Full repository context | Richer understanding | Token usage |
| Retrieved context only | Cheaper, faster | May miss relevant information |
| Cloud inference | Easy to scale | Privacy |
| Local inference | Privacy | Limited by local hardware |

## Follow-ups to have ready

**How do you avoid leaking customer code?** Isolate by tenant; never use private repos for training without permission; retrieve only what the user is authorised to access; mask sensitive information before prompts; offer private or on-prem deployment; strict access control and audit.

**How do you get below 300 ms?** A lightweight model for inline completion; stream tokens; persistent connections from the IDE; cache embeddings and frequent completions; semantic indexing in the background; inference close to users; limit retrieved context; speculative decoding where supported.

**How do you personalise?** Learn coding style; prioritise project-specific APIs; incorporate accepted vs rejected suggestions; respect repository standards and lint rules; tailor prompts to developer and team preferences while keeping raw source protected; refine retrieval on feedback.

## Summary

A retrieval-augmented, context-engineered system — not one call to a big model. Gather and prioritise context instead of sending repositories; use semantic retrieval; route across models to balance latency, cost and quality; manage the context window for large codebases. Scale from stateless servers, distributed vector DBs, autoscaling GPU inference, streaming and multi-region. Security from tenant isolation, repository-level access control, secret masking, and private deployment for regulated industries — shaping the architecture from the first clarifying question.

## Checkpoint

- Why is the semantic cache placed where it is, and what does a hit skip?
- Draw the context-engineering funnel and name what each stage removes.
- Decompose the 300 ms budget.
- What does output validation check, and why is "detect hallucinated APIs" on the list?
- How does Module 04's access-control problem reappear in this design?

**Next →** [Case 4 — Recruiting Platform](04_Recruiting_Platform.md)
