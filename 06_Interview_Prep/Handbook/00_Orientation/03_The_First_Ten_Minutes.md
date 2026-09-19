# The First Ten Minutes

> **Level** 🟢 Foundations · **Module** 00 · **Doc** 3 of 3 · **Time** ~20 min
> **Prerequisites:** none
> **Source material:** `3. AI_Engineer_Interview_Preparation/Cross Cutting Preparation/00-first-ten-minutes.html`

## Why this matters

Interviewers are not testing whether you can design a system. They are testing whether you would waste three months building the wrong one. The same is true of a customer's first scoping call. In both settings the failure mode is identical: someone reaches for the pen, draws the architecture they already had in their head, and discovers on day forty that the customer is multi-tenant, or the data changes hourly, or the system is allowed to *act* and nobody discussed what a wrong action costs.

**Ask before you architect.** This document gives you five areas to question, two or three questions in each, and the reason each area changes the design. It applies unchanged whether the problem is a RAG platform, an agent platform, or a delivery process — which is why it sits in Orientation rather than in any one technical module.

## The five areas

### 1 · Who is the customer, really

- Is this for one enterprise customer, or a platform serving many tenants?
- What decision or workflow does the answer actually feed into?
- Who are the end users — internal employees, external customers, or both? Technical or not?

**Why it matters.** One answer here decides your entire isolation model — and, for an agent platform, the entire authoring surface — before you have made a single architecture choice. "One customer" and "many tenants" are not two sizes of the same system; they are two systems. "Non-technical users configure it" is not a UI detail; it is the reason Module 05 exists.

### 2 · Data and system reality

- What shape is the underlying data, or the systems being integrated with, today?
- Is it static, or does it change — and how fast?
- Who owns data and access quality, and can we get it before day one?

**Why it matters.** Most demos assume clean, structured input. Real deployments never are. A corpus that changes hourly needs incremental sync and freshness tracking; a corpus whose permissions nobody owns cannot be made access-aware no matter how good the retrieval is. The third question is the one people forget, and it is the one that stalls engagements.

### 3 · Access control and blast radius

- Does every user or tenant have uniform access, or does visibility vary by group, role or region?
- Is the system read-only, or can it take real actions — and which costs more, a wrong action or an over-cautious refusal?

**Why it matters.** This decides how much of the design has to be permission-aware and guardrailed, and how much can stay simple. Per-user visibility reshapes the retrieval path (Module 04). The ability to act introduces every containment mechanism in Module 05. And the wrong-action-vs-refusal question sets the tone for the whole guardrail policy: a refund bot and a research assistant should not have the same default.

### 4 · Scale and SLAs

- Roughly how many tenants, users, items, and what volume of requests?
- What latency is acceptable — and is that p50, or p95/p99?

**Why it matters.** Ten of something and ten million are different systems, not different sizes of one. Module 06 shows what breaks first at twenty million documents; none of it matters if the customer has two thousand. The percentile question matters because an LLM pipeline's tail latency is dominated by the slowest of several sequential model calls — a p50 target and a p99 target lead to different architectures.

### 5 · Definition of done

- How will we know if this is working — is quality or accuracy even measured today?
- Is there a fallback if it is wrong or down — does it escalate to a human?

**Why it matters.** Offering to own evaluation is the strongest FDE signal in the room. It says you intend to be judged on outcome, not on shipping. It also surfaces, early, whether a golden set exists or has to be built with the customer's experts — which is a week of the two-week plan in Module 10.

## How to use the questions

Do not fire all twelve. Ask three or four, then **visibly let the answers change the design, out loud**:

> "Okay — if it's multi-tenant with per-user visibility, that changes how I'd structure this. Let me start from the access model rather than from the index."

The adaptation is the signal, not the question count. An interviewer who watches you ask a question and then draw exactly what you would have drawn anyway has learned that you ask questions as a ritual. An interviewer who watches an answer move a box on the whiteboard has learned that you listen.

A workable rhythm for a 60-minute round, which Module 02 expands into a full method:

```
 0–8 min    clarify and scope        ← this document
 8–12 min   entities and happy path
12–20 min   architecture
20–40 min   deep dive on the hardest part
40–55 min   cross-cutting, failure, scale
55–60 min   close deliberately
```

## Interview lens

The five areas map directly onto sections of the design you will draw later:

| Area | Decides |
|---|---|
| Customer | tenancy model, authoring surface, isolation level |
| Data reality | ingestion design, freshness, connector strategy |
| Access and blast radius | retrieval path shape, guardrail policy, approval gates |
| Scale and SLAs | index architecture, caching, what breaks first |
| Definition of done | evaluation plan, golden set, escalation path |

If you find yourself twenty minutes in with a question in one of these rows unanswered, stop and ask it. Late is better than assumed.

## Checkpoint

- Without looking: name the five areas and give one question for each.
- For each area, name the architectural decision it settles.
- Why is "visibly adapting" a stronger signal than asking more questions?
- Which question in the list is most often forgotten, and what does forgetting it cost?

**Next →** [Module 01 · LLM Systems Foundations](../01_LLM_Systems_Foundations/README.md)
