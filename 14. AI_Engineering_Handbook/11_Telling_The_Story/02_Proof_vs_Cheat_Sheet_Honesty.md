# Proof vs Cheat-Sheet — the Honesty Discipline

> **Level** 🔴 Telling the Story · **Module** 11 · **Doc** 2 of 2 · **Time** ~25 min
> **Prerequisites:** the three coverage maps — Module 04 doc 10, Module 05 doc 7, Module 10 doc 7; Module 04 doc 7 ("read these numbers honestly")
> **Source material:** synthesised from the three coverage maps, the three project READMEs' "Verified results" and "What this deliberately does not do" sections, and the "Honest limitations" segments of the narratives

## Why this matters

Everything in this handbook that was built was also *audited against what it claims*. Each project carries a coverage map (✅ built and runnable · 🟡 partial · ❌ not built), a "read these numbers honestly" section, and a "what this deliberately does not do" list. That is not modesty. It is the single most valuable habit an engineer can bring to a design conversation or a customer engagement, and it is what makes everything else you say believable. This document names the discipline and shows how to practise it.

## The distinction

For every claim a design makes, there are two legitimate positions:

| | *"I built this — let me show you"* | *"I know how this is done"* |
|---|---|---|
| Evidence | A running demo, a test that fails if it is wrong, a number from a real execution | Architecture knowledge, a reference design, a vendor's documentation |
| Legitimacy | Full | Full — most of any real system is knowledge, not code you personally wrote |
| The failure | — | **Presenting the second as the first** |

Confusing them is the failure. A candidate who says "my system handles 10 million chunks" when the corpus is 22 documents has not lied about the architecture — the design might well scale. They have lied about the *evidence*, and an experienced listener will find out with one question, after which nothing else they say is trusted.

## The three habits

### 1 · Keep a coverage map

Before any conversation about a system, write down every claim the design makes and mark each: built and runnable, partial, or not built. For every ❌ or 🟡, write two more things — **what it would take to close** (code, and roughly how much; data only; or infeasible locally) and, where closing is infeasible, **what to say instead**, worded ready to speak.

The three maps in this handbook are the template. Notice what the "what to say" column does: it turns a gap from an embarrassment into a *prepared* answer that demonstrates you understand the production version even though you could not build it on a laptop. *"The lock and idempotency mechanisms are correct in shape but wrong in storage — a real deployment needs a distributed lock and a durable key store; the mechanism doesn't change, only where it's persisted."* That sentence is stronger than a claim to have built it.

### 2 · Read your own numbers honestly

Every project's results section has a paragraph that begins *"read these numbers honestly"*:

> *"The corpus is 22 documents. Retrieval is easy at that size, so every strategy scores near-perfectly and the differences are noise. Do not read this table as proof that HyDE or multi-query earn their keep. The value is that the harness exists and gates the release. The number that matters here is the zero-leak column."*

> *"This is one engagement, run once. `time_to_first_value_days = 1` and `eval_score = 0.83` are demo-scripted values, not measurements. The point being proven is that the pipeline enforces its own gates, not that these numbers are typical."*

> *"~35% growth in platform consumption following rollout — a correlational signal, not a controlled experiment, and worth saying exactly that if pressed."*

The pattern: state the number, state what it does *not* prove, state what it *does* prove. Do this before anyone asks. Module 06 doc 3's statistical rigour is the technical basis; this is the communication habit built on it.

### 3 · Name what it deliberately does not do

Each project ends with a list headed *"named because an architect should know where the demo ends"*: BM25 rebuilt per request; identity is a JSON file; no real authoring surface; the eval harness referenced not run; rollback an attestation not a mechanism. Each item says what the production answer is. An architect who can name where their own system ends is an architect whose claims about where it *works* can be trusted.

## Why it works in the room

**Offered honesty reads as confidence; extracted honesty reads as getting caught.** The narratives in `stories/` all deploy the limitation *before* it is asked for, and the delivery notes say: never apologise for it — state it like a fact you are proud to know.

Three things happen when you do this:

1. **Every other claim gains weight.** If you volunteered the 22-document caveat, the listener believes the zero-leak gate without checking.
2. **The follow-up questions get better.** Instead of probing for the edge, they ask what you would do at scale — which is the conversation you wanted.
3. **You demonstrate the job.** An FDE's work is telling a customer exactly where a guarantee holds and where it has to be verified on their stack. *"I'd rather tell you exactly where the edges of what I've proven are than let you find them later"* is the closing line of one narrative, and it is the job description.

## The war stories are the proof

The bugs each project caught are not confessions — they are the evidence that the testing works. The false security alarm, the shadowed rule, the flaky gate; the unscoped reset, the stale content hash, the schema migration; the spend cap checking $0.00, the idempotent replay that still accumulated cost; the accelerator `kind` colliding with the event `kind`. Each is told with what changed and what the lesson was. *"How you respond to your own testing catching you is more informative than a system that never had a wrinkle."* A project with no war stories has either not been tested hard enough or is not being described honestly.

## Applying it to your own work

For any project you will talk about:

1. **Write the coverage map.** Every claim; ✅ 🟡 ❌; to-close; what-to-say.
2. **Write the "read these numbers honestly" paragraph.** For every number you might cite: what it does not prove, what it does.
3. **Write the "does not do" list.** With the production answer for each.
4. **Collect the war stories.** What broke, how you found it, what changed, the lesson in one sentence.
5. **Put the limitation in the script before the close**, and rehearse saying it without apology.

Then, in the room, the sentence that carries it:

> *"Here's what I can show you running, here's what I know how to do but couldn't demonstrate at this scale, and here's where the demo ends — and I'd rather tell you that than have you find it."*

## Checkpoint

- State the distinction and the failure in one sentence each.
- For a project of your own, write three ✅ rows and two ❌ rows with "what to say".
- Write the "read these numbers honestly" paragraph for one number you usually cite.
- Name one war story from each of the three platform projects and its lesson.
- Why does offered honesty strengthen every other claim?

**Next →** [Appendices](../99_Appendices/README.md)
