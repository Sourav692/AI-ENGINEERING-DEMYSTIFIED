# Caching, streaming, CI/CD rigor, and build vs. buy

Cross-cutting topics for any AI platform system design round. None of this needs a codebase — it's
architecture to describe on a whiteboard.

---

## 1. Semantic caching

A simple cache keyed on the exact question (plus whatever filters apply) is **exact-match**: two
questions that mean the same thing but are worded differently are two different cache keys, and the
second one recomputes everything from scratch even though the first one already answered it.

The next step is **semantic caching**: embed the incoming question, check it against previously
answered questions' embeddings, and treat a hit above a similarity threshold as a cache hit — serving
the prior answer instead of recomputing.

**Why this is a genuinely different problem, not just a bigger cache:**
- **A similarity threshold introduces a correctness risk exact-match never has.** Two questions can be
  close in meaning but expect different answers ("refund policy for EU customers" vs. "refund policy
  for US customers") — a naive similarity cache risks serving a *wrong* answer confidently, not just a
  *stale* one. The threshold has to be tuned conservatively, and the safest version never matches
  across different permission scopes or tenants, even if the wording is close.
- **Invalidation is harder.** An exact-match cache clears cleanly when the underlying content it
  answered from changes. A semantic cache has to decide when a stored answer's whole *neighborhood* of
  similar questions is no longer trustworthy — for example, after any relevant document changes, not
  only the one that produced the original cached answer.

## 2. Token streaming

Returning a complete answer in one shot is the simplest design. The next step, named explicitly in
most system design guides: **stream tokens to the user so perceived latency drops, even though total
latency doesn't change.**

**The point worth being precise about:** streaming is a *perceived*-latency fix, not a *total*-latency
fix — generation still takes exactly as long. What changes is when the user sees the *first* token
versus the *last* one. This matters most for interactive chat (where sub-second first response is the
whole point) and matters much less for an async reply that has minutes to spare. Streaming is
therefore a **channel-layer decision** — the underlying retrieve-and-answer pipeline doesn't change;
only whether the final step streams token-by-token depends on which channel is asking.

**Why a refusal decision has to happen before streaming starts, not during it:** if a system needs to
decide "do I even have enough information to answer" before generating, that decision has to be made
*before* the first token streams — a partially-streamed answer that then gets retracted mid-flight is a
worse experience than a clean up-front refusal. Streaming only ever applies to the final answer step,
after the "should I answer at all" decision is already settled.

## 3. Nightly regression runs — a different trigger than your own changes

A quality gate that only runs when *you* change a prompt misses a real risk: **the model provider can
silently change what a model version points to, without any change on your side at all.** Your
accuracy or safety metrics can quietly drift with zero commits to explain why.

**The fix:** run the same evaluation suite on a schedule (nightly), independent of any code change,
comparing against the last known-good baseline. This is a scheduling change around infrastructure that
already exists for any project with a real eval suite — worth naming precisely as that: the eval
suite itself doesn't need to be rebuilt, it needs a second trigger — a schedule, not only a
code-change hook — because the thing that can regress isn't only your own work.

## 4. What A/B testing actually means for a RAG/agent system

In a normal product, A/B testing usually means "show half the users button A, half button B, see
which one gets clicked more." In a RAG or agent system, the two "versions" being compared aren't
buttons — they're things like:

- **Two different prompts** for the same step (e.g. two ways of asking the model to answer with
  citations).
- **Two different retrieval strategies** (e.g. plain search vs. search-plus-reranking).
- **Two different models** doing the same job (e.g. a cheaper model vs. a more expensive one for the
  final answer).

Real users (or real tenants) get split between the two versions, and instead of "which one got
clicked," you compare things like: did the answer actually resolve the question, did it need to be
escalated to a human, did the user thumbs-up or thumbs-down it, was it accurate against the test set.
The mechanics are the same as any A/B test — split traffic, measure an outcome, compare — just applied
to "which prompt/retrieval/model answered better" instead of "which button got more clicks."

## 5. Statistical rigor in A/B testing

LLM outputs aren't perfectly consistent — ask the same question with the exact same prompt twice, and
you can get two slightly different answers. Because of that, if you only test two prompt versions on a
handful of examples, "version B scored a bit higher" might just be random noise, not a real
improvement — and this risk is bigger for LLMs than for a typical product metric, because LLM answers
naturally vary more than something like a click.

**The simple fix:** before running the test, decide how big an improvement would actually matter to
you. Then make sure you're testing on *enough* examples to reliably tell a real improvement of that
size apart from random noise — this is just ordinary statistics, nothing LLM-specific. And don't
declare a winner early, before you've reached that number of examples. It's an easy rule to state and
an easy one to skip when you're in a hurry — which is exactly why it's worth having a rehearsed answer
ready instead of winging it in the room.

## 6. Unit-level testing for prompts

A full evaluation suite (does the answer sound right, is it grounded, is it safe) is expensive and
slow to run on every single change. A cheaper, faster layer sits in front of it: **does this prompt, in
isolation, even produce output that parses correctly** — the right structure, every required field
present, nothing malformed — for a small set of known test inputs.

This is the equivalent of a type check running before the full test suite: fast, cheap, and it catches
a whole class of failure (a broken template, a missing variable) that the expensive full evaluation
would also eventually catch, just far more slowly. It runs on every prompt change, before the real
evaluation suite even starts — a cheap first gate, not a replacement for the real one.

## 7. Build vs. buy — a decision worth arguing explicitly

The general principle: **buy the undifferentiated layers, build the customer-specific logic.**
Applied across a typical AI platform stack:

| Layer | Default | Build only when |
| --- | --- | --- |
| Identity / login | Use the customer's own identity provider | Never — this is always a solved problem someone else already owns |
| Secrets storage | A managed vault product | Almost never — security infrastructure is a place where "we built our own" is a red flag, not a differentiator |
| Search / vector index | A managed search product | Self-hosted only at very large scale, or when data can't legally leave a specific environment |
| Monitoring | An existing, standards-compatible monitoring platform | A thin custom layer only for the domain-specific fields the platform doesn't yet support — layered on top, not instead of |
| **The permission rules, the retrieval tuning, the prompt design, the actual business workflows for this customer** | — | **Always build.** This is the differentiated value — nothing off the shelf can encode what's specific to this customer's data, policy, and process |

**The one-line version:** the line isn't "build everything to prove capability" or "buy everything to
move fast" — it's whether a component encodes something specific to this customer's business. Identity,
secrets, and search infrastructure are solved problems available from a vendor. The permission logic,
the retrieval tuning, and the actual workflow behavior are the parts that only exist because of who
the customer is — that's where engineering time belongs.

---

## What to say if asked directly

*"Exact-match caching is the safer starting point over semantic caching, since a similarity-threshold
cache risks confidently serving a wrong answer for two questions that are close in wording but expect
different answers. Streaming is a channel decision, not a core pipeline decision — and it only ever
applies after a 'do I have enough information to answer at all' check has already run, never before,
since retracting a partially-streamed answer is worse than a clean up-front refusal. And on
regression: a quality gate that only fires on my own changes misses the case where the model provider
silently changes something underneath a model version — that needs a scheduled run, independent of
any change I make."*
