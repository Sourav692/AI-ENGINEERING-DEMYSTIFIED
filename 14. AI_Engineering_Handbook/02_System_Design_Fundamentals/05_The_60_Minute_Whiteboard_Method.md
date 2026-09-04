# The 60-Minute Whiteboard Method

> **Level** 🟢 Foundations · **Module** 02 · **Doc** 5 of 5 · **Time** ~30 min
> **Prerequisites:** [The First Ten Minutes](../00_Orientation/03_The_First_Ten_Minutes.md), [The 12-Part Framework](01_The_12_Part_Framework.md)
> **Source material:** synthesised from the shared structure of the four whiteboard scripts — `Enterprise RAG Platform/INTERVIEW_SCRIPT.md`, `INTERVIEW_SCRIPT_DATABRICKS.md`, `Enterprise Agentic Workflow Automation Platform/INTERVIEW_SCRIPT.md`, `Delivery Framework from Scoping to Delivery/INTERVIEW_SCRIPT.md`

## Why this matters

The 12-part framework is complete but it is not *timed*. A 60-minute design round punishes completeness without prioritisation: candidates who cover all twelve parts evenly spend eight minutes on the one thing that mattered and run out of time before the failure modes. The four full whiteboard scripts in Module 09 — for enterprise RAG, RAG on Databricks, an agent platform and a delivery framework — were all written to the same six-step method. This document extracts that method so you can apply it to a prompt you have never seen.

## The six steps and the clock

Write this in the corner of the board before you say anything else:

| Minutes | Step | What it produces |
|---|---|---|
| 0–8 | **1 · Clarify and scope** | The questions that change the design; explicit scope and assumptions; a concrete anchor case |
| 8–12 | **2 · Entities and the happy path** | The nouns; one request narrated end to end *in words* |
| 12–20 | **3 · Architecture** | Two flows drawn (offline and online), every arrow labelled |
| 20–40 | **4 · Deep dive** | The hardest part, announced as such, with the strongest single insight |
| 40–55 | **5 · Cross-cutting, failure, scale** | Multi-tenancy, security, observability, evaluation, what degrades, what breaks first at 10× — raised *unprompted* |
| 55–60 | **6 · Close deliberately** | Three-sentence summary; top three trade-offs and what would change your mind; the forward-deployed close |

The asymmetry is the point. Twenty minutes on the deep dive; four on entities. If you find yourself at minute 25 still drawing boxes, you have spent the deep dive on the architecture.

## Step 1 — Clarify and scope (0–8)

**Do not draw anything yet.** Ask the questions from [The First Ten Minutes](../00_Orientation/03_The_First_Ten_Minutes.md), out loud, and write the answers where they stay visible. Then do three things the scripts all do:

**Say the one sentence that frames the round.** Each script opens with a single sentence, delivered in the first two minutes, that names the real difficulty and sets up every later decision. For enterprise RAG:

> *"Anyone can build multi-source RAG. The thing that makes this hard is that a Tier-1 agent, a Tier-3 engineer and an account manager must get different correct answers to the same question — so access control isn't a feature I add at the end, it decides the shape of the retrieval path."*

For the agent platform, the sentence is about trust rather than mechanics. For the delivery framework, it is that two weeks is only possible if the work existed before the customer showed up. Find the sentence for *your* prompt before you touch the board. If you cannot, you have not yet understood the prompt.

**Scope explicitly and say your assumptions.** *"I'm designing for read-only Q&A over six sources with attribute-based access, multi-tenant, sub-3-second latency. I'm explicitly descoping write actions and streaming ingestion — happy to return to those."* Interviewers score this as scope control, not ignorance.

**Anchor on a concrete case.** Every script names a fictional customer, a small set of sources, and *one question* that drives the whole design — and draws a table early showing how the answer differs by persona. That table becomes the requirement everything else is justified against.

## Step 2 — Entities and the happy path (8–12)

Write the nouns before the boxes:

```
Tenant · Principal · Group · Document · Chunk · ACL · Query · Run · Trace · Citation
```

Then narrate one request end to end **in words, before drawing**:

> *"A Tier-3 engineer asks about the March incident. We resolve their identity from the IdP. We compile that into a filter. We search only the slice they're allowed to see. We re-check the policy on what came back. We rerank to the best six. We check it's sufficient. We generate with citations. We verify every citation. Then we answer."*

The narration exposes every component you are about to draw, and lets the interviewer redirect you before you have spent ten minutes on the wrong box.

## Step 3 — Architecture (12–20)

Draw two flows — typically an offline one (ingestion, or a pipeline's setup phase) and an online one (per request). **Label every arrow.** Then say the one or two sentences per flow that show judgement. For the RAG scripts that is *"the connector's real job is translating each source's permission model into ours"* and *"authorize is first, enforce runs before the model sees anything — I encode that ordering in the graph's edges, not in a code convention someone can forget."*

Eight minutes is enough for two flows if you do not decorate them. Save the detail for the deep dive.

## Step 4 — Deep dive (20–40)

**Announce where the risk is.** This reads as senior judgement:

> *"The hardest parts of this system are access control and retrieval quality. I want to spend my time there — the vector database choice is close to irrelevant by comparison."*

Then spend the time there. Each script has a primary deep dive (the thing the sentence in Step 1 promised) and a secondary one, roughly 12 and 8 minutes. Inside the primary deep dive, the scripts share a shape:

1. **Name the alternatives, then choose.** Three access-control patterns; three ways to handle channel diversity; gates as checklist vs gates as authority.
2. **Deliver the strongest single insight and mark it.** The scripts literally star it: the two-layer filter/post-check, determinism over free text, gates that block rather than remind. One idea, stated crisply enough that the interviewer writes it down.
3. **Prove you built it with one specific bridge.** *"Chroma can't store a list, so group membership becomes one boolean column per group and an `$or` reproduces list-overlap."* Details like this are unfakeable.
4. **State the interaction between the primary and secondary deep dives.** *"Reranking runs after ACL enforcement, so a restricted user's top-5 is the best of their pool."*

## Step 5 — Cross-cutting, failure, scale (40–55)

**Raise all of this unprompted.** Being asked costs you the signal. Five sub-sections, two to three minutes each:

- **Multi-tenancy** — where tenant ID travels, where it is enforced (data layer, never assembled per query in application code), noisy-neighbour limits.
- **Security** — AuthN via the customer's IdP; retrieved content and tool output as untrusted input; least-privilege credentials in a secrets manager; PII as an obligation; full audit trail.
- **Observability** — every run a replayable record; *"three audiences, one artefact: the engineer, the auditor, finance."*
- **Evaluation** — the metric families, and the one gate that is not a metric. *"A retrieval regression is a bug I fix next sprint. A leak is an incident. So the security suite blocks the release outright."* If you have a war story about an evaluation bug, this is where it lands.
- **Failure modes** — as a table of *what degrades*, not what breaks. One row said slowly: *fail closed on authorisation.*
- **Scale** — what breaks first at 10×, named specifically, with the production answer.

## Step 6 — Close deliberately (55–60)

Three moves, in order:

**Summarise in three sentences.** Not a recap of the diagram — the design's *thesis*.

**Your top three trade-offs — and what would change your mind.** As a table: decision, what you chose, what evidence would make you revisit it. This is the single strongest signal of engineering maturity available in five minutes.

**The forward-deployed close.** Every script ends the same way, and it is the line that distinguishes an FDE answer from an architect's answer:

> *"If I were deploying this at a customer, week one is not this whole diagram. It's: connect one source, get the permission translation provably right for three personas, build the golden set with their SMEs, and stand up the leak test. That proves the risky part before anyone argues about embeddings. Everything else is incremental."*

## Three artefacts to prepare in advance

The scripts each carry three appendices worth building for any design you might be asked about:

**A cheat sheet of the lines that carry the round.** Eight to ten sentences, each one a complete idea. *"The filter makes retrieval cheap; the post-check makes it correct."* *"Fail closed on authorisation; degrade on everything else."* You will not read them aloud, but having them means you never lose the thread.

**Questions to ask them.** Four or five, specific to the company: how do they handle X today; where do they draw the platform/custom line; what do the first two weeks of an engagement look like; how do they evaluate quality once the customer owns it.

**The one artefact you could show on a laptop.** A visibility matrix. A negative-control demo. A gate-failure run. Something that takes two seconds and proves the risky part is real.

## Interview lens

The method's underlying claim: a design round is won in Step 1 (the framing sentence and the scope) and Step 4 (the marked insight and the unfakeable detail), and *lost* in Step 5 (by waiting to be asked) and Step 6 (by summarising the diagram instead of the thesis). Practise the four steps that carry weight and let the middle two be brisk.

## Checkpoint

- Write the six steps and their minute ranges from memory.
- For a prompt you know well, write the one sentence that frames the round.
- What are the four moves inside a primary deep dive?
- Why must Step 5 be raised unprompted?
- Deliver the forward-deployed close for a system of your own.

**Next →** [Module 03 · Robust Agents](../03_Robust_Agents/README.md)
