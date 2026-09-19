# Caching, Streaming, CI/CD Rigor and Build vs Buy

> **Level** 🟠 Scale, Security, Operations · **Module** 06 · **Doc** 3 of 7 · **Time** ~30 min
> **Prerequisites:** Module 04 docs 5 and 7 (the response cache, the evaluation harness)
> **Source material:** `3. AI_Engineer_Interview_Preparation/Cross Cutting Preparation/03-cost-latency-cicd-rigor-and-build-vs-buy.md`

## Why this matters

Four topics that come up in every design round after the architecture is drawn, each with a specific trap: a cache that confidently serves a wrong answer; streaming that retracts an answer mid-flight; a quality gate that misses the regression you did not cause; and a build-vs-buy decision made on instinct rather than on the one question that decides it.

## 1 · Semantic caching

Module 04's response cache is **exact-match**: keyed on the question plus the compiled filter plus the exact context. Two questions that mean the same thing but are worded differently are two different keys, and the second recomputes everything.

**Semantic caching** embeds the incoming question, checks it against previously answered questions' embeddings, and treats a hit above a similarity threshold as a cache hit. It is a genuinely different problem, not a bigger cache:

- **A similarity threshold introduces a correctness risk exact-match never has.** "Refund policy for EU customers" and "refund policy for US customers" are close in meaning and expect different answers. A naive semantic cache serves a *wrong* answer confidently, not a *stale* one. Tune the threshold conservatively — and the safest version never matches across different permission scopes or tenants, however close the wording.
- **Invalidation is harder.** An exact-match cache clears cleanly when the content it answered from changes. A semantic cache has to decide when a stored answer's whole *neighbourhood* of similar questions is no longer trustworthy — after any relevant document changes, not only the one that produced the cached answer.

Exact-match is the safer starting point. Semantic caching is the next step when the hit rate justifies the risk, and it belongs in front of the expensive path (Module 02's travel-agent lesson: a cache after the fan-out saves nothing).

## 2 · Token streaming

Returning a complete answer in one shot is simplest. The next step: **stream tokens so perceived latency drops, even though total latency does not change.**

Be precise: streaming is a *perceived*-latency fix, not a *total*-latency fix. Generation takes exactly as long; what changes is when the user sees the *first* token versus the *last*. It matters most for interactive chat and much less for an asynchronous reply with minutes to spare. So streaming is a **channel-layer decision** — the retrieve-and-answer pipeline does not change; only whether the final step streams depends on which channel is asking.

**Why the refusal decision must happen before streaming starts.** If the system needs to decide "do I have enough to answer?" — Module 04's `grade` node — that decision must be made *before* the first token. A partially streamed answer that is then retracted is a worse experience than a clean up-front refusal. Streaming applies only to the final synthesis step, after "should I answer at all" is settled. That is one more reason `grade` sits where it does in the graph.

## 3 · Nightly regression runs — a different trigger

A quality gate that runs only when *you* change a prompt misses a real risk: **the model provider can silently change what a model version points to, with no change on your side.** Accuracy or safety drifts with zero commits to explain why.

The fix: run the same evaluation suite on a schedule, independent of any code change, comparing against the last known-good baseline. This is a scheduling change around infrastructure that already exists — Module 04's harness does not need rebuilding; it needs a *second trigger*. A schedule, not only a code-change hook, because the thing that can regress is not only your own work. The diff of `leak_count`, `refusal_accuracy` and `groundedness` against yesterday is also the simplest drift detector from the previous document.

## 4 · What A/B testing means for a RAG or agent system

In a normal product, A/B testing is "half the users see button A, half see B, count clicks". In a RAG or agent system the two versions are:

- two different **prompts** for the same step,
- two different **retrieval strategies** (Module 04's six, behind one interface, exist for exactly this),
- two different **models** doing the same job.

Real users or tenants are split, and the outcome is: did the answer resolve the question, did it need escalation, was it rated up or down, was it accurate against the golden set. Same mechanics as any A/B test — split, measure, compare — applied to "which prompt, retrieval or model answered better".

## 5 · Statistical rigor

LLM outputs are not perfectly consistent: the same question with the same prompt can produce two slightly different answers. So if you test two prompt versions on a handful of examples, "B scored a bit higher" may be noise — and the risk is bigger than for a click metric, because LLM answers vary more.

The fix is ordinary statistics: decide in advance how big an improvement would matter, make sure you test on *enough* examples to tell a real improvement of that size from noise, and do not declare a winner early. Easy to state, easy to skip in a hurry — which is why it is worth having rehearsed. It is also why Module 04's strategy table is explicitly *not* read as evidence that HyDE helps: 22 cases cannot distinguish 0.958 from 1.000.

## 6 · Unit-level testing for prompts

A full evaluation suite — grounded, safe, correct — is expensive and slow to run on every change. A cheaper layer sits in front: **does this prompt, in isolation, produce output that parses correctly** — right structure, every required field, nothing malformed — for a small set of known inputs.

This is the type check before the full test suite: fast, cheap, and it catches a class of failure (a broken template, a missing variable) that the expensive suite would also catch, far more slowly. It runs on every prompt change, before the real evaluation starts. A first gate, not a replacement.

The full ladder, cheapest first:

```
 prompt unit tests   →   golden-set eval (on change)   →   scheduled eval (nightly)   →   A/B in production
   parses? fields?         quality + zero-leak gate         provider drift                 real outcomes, with power
```

## 7 · Build vs buy — the one question

The principle: **buy the undifferentiated layers, build the customer-specific logic.**

| Layer | Default | Build only when |
|---|---|---|
| Identity / login | The customer's own identity provider | Never — always a solved problem someone else owns |
| Secrets storage | A managed vault | Almost never — "we built our own" security infrastructure is a red flag, not a differentiator |
| Search / vector index | A managed search product | Self-hosted only at very large scale, or when data cannot legally leave a specific environment |
| Monitoring | An existing, standards-compatible platform | A thin custom layer only for domain fields it does not yet support — on top, not instead |
| **The permission rules, the retrieval tuning, the prompt design, the actual business workflows for this customer** | — | **Always build.** This is the differentiated value — nothing off the shelf encodes what is specific to this customer's data, policy and process |

The line is not "build everything to prove capability" or "buy everything to move fast". It is whether a component encodes something specific to *this customer's business*. Identity, secrets and search infrastructure are vendor problems. Permission logic, retrieval tuning and workflow behaviour exist only because of who the customer is — that is where engineering time belongs. Module 08's Databricks variant is this table applied: most of Module 04's hand-written machinery becomes a platform primitive, and the permission policy stays yours.

## Interview lens

> *"Exact-match caching is the safer starting point — a similarity-threshold cache risks confidently serving a wrong answer for two questions that are close in wording but expect different answers, and it must never match across permission scopes. Streaming is a channel decision, not a pipeline decision, and it only applies after the 'can I answer at all' check has run — retracting a streamed answer is worse than refusing cleanly. And a quality gate that fires only on my changes misses the provider silently changing a model underneath me — that needs a scheduled run."*

## Checkpoint

- What correctness risk does semantic caching introduce that exact-match does not, and what is the safest constraint on it?
- Why must the refusal decision precede the first streamed token?
- What can regress with zero commits, and what is the fix?
- Give the four-rung testing ladder from cheapest to most expensive.
- State the one question that decides build vs buy, and apply it to a vector index and to a permission policy.

**Next →** [Prompt Injection, Egress and Tenancy](04_Prompt_Injection_Egress_Tenancy.md)
