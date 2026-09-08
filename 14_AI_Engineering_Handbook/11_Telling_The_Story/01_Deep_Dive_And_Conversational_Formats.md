# Deep-Dive and Conversational Formats

> **Level** 🔴 Telling the Story · **Module** 11 · **Doc** 1 of 2 · **Time** ~35 min, then practice
> **Prerequisites:** Module 10 doc 2 (the six-stage delivery story); a project of your own
> **Source material:** synthesised from the nine narratives in `4. FDE_Related_Preparation/Star_Stories/` — their shared structure, timing budgets, coaching notes and appendices

## Why this matters

You have built something. Now a director with fifteen minutes, or a hiring manager with an open agenda, asks you to talk about it. The same substance has to land in three very different shapes: a **timed deep-dive** you move through top to bottom; an **open-ended conversation** where they steer; and a **technical implementation flow** for when the audience wants the architecture evolution and the reasoning behind every tool choice. The narratives in `stories/` were each written in one of these formats for a specific engagement. This document extracts the formats so you can apply them to your own work.

One meta-rule governs all three: **every technical term gets translated in the same breath it is introduced**, not three sentences later. *"A two-layer access control system — think a fast ID check at the door, then a second, more careful check right before you're handed anything sensitive"* is one sentence, not two ideas.

## Format 1 — The 15–20 minute deep-dive

A speakable script with embedded coaching notes. You read it aloud a few times, then work from segment headers and bold cues rather than memorising — memorised scripts sound memorised. Roughly fifteen minutes of talking with room to be interrupted; the last three to five minutes are Q&A, not more script.

### The timing budget

| Segment | Time | What it does |
|---|---|---|
| **1 · The hook** | 0:30 | One sentence, zero jargon, that the listener remembers if they remember nothing else. Say it, then *pause* |
| **2 · STAR narrative** | 3:30–4:00 | Situation (plain English) → Task (what you personally owned, and your bar for "done") → Action in **two passes** → Result (business framing first, numbers second) |
| **3 · Technical development** | 2:30–3:30 | The "if they want more" branch. Business framing for each sub-point, then depth only as far as the conversation wants |
| **4 · Governance and security** | 3:00–3:30 | **Weight this heaviest for a senior or enterprise audience.** Where "I built a cool system" becomes "I understand what enterprise trust requires" |
| **5 · Deployment and platform reality** | 1:30–2:00 | What you learned about the platform that generalises — and the bridge to the listener's world, said out loud |
| **6 · Honest limitations** | 0:45 | Before they ask. Offered honesty reads as confidence; extracted honesty reads as getting caught |
| **7 · Close → the role** | 0:45 | Why this project, for this role, in one breath |
| Q&A buffer | 5:00 | |

For an FDE audience, the AIA narratives add an eighth segment between the hook and STAR: **requirements gathering and scoping** — the discovery conversations *before* a line of code — because that is the part of the job the FDE interviewer is actually hiring for.

### The two-pass Action

The Action beat is delivered twice. **Pass 1** is the analogy pass — no architecture terms. *"Permission-checking happens before the AI ever sees a document — built into the shape of the pipeline so it's structurally impossible to skip. Think of a venue with two checkpoints…"* **Pass 2** is the technical layer — *"in system terms, that's attribute-based access control enforced in two layers…"* — delivered **only if you sense engagement**: a nod, a question, leaning in. If the room says "got it, what's the result", skip to Result. The two passes let one script serve a business-heavy and a technical-heavy listener without rewriting.

### The trust story

The strongest segment in every deep-dive is not the architecture. It is **the mistakes your own testing caught** — told as evidence that the testing works. *"I want to tell you about three mistakes, because how you respond to your own testing catching you is more informative than a system that never had a wrinkle."* Then the false alarm, the shadowed rule, the flaky gate (Module 04 doc 7), each with what changed. This beat invites follow-up questions, which is the conversation doing your work for you.

### The two appendices

Every deep-dive carries two appendices you prepare but do not read:

**Anticipated follow-ups — a crib sheet.** A table: *if asked X → lead with (business) → then, if pushed (technical)*. Five to eight rows. *"Why two layers instead of one good filter?"* → *"Because permissions change after the index is built"* → *"Pre-filter on index-time attributes; post-check on live attributes; staleness becomes a logged event, not a leak."*

**Delivery notes.** Pause after the hook. Watch for the "go deeper" signal before launching Pass 2 or segment 3. Never apologise for the limitations segment — state it like a fact you are proud to know. If time runs short, compress technical development and Pass 2 first; the business framing and the governance segment are what a senior listener remembers and must never be rushed.

## Format 2 — The open-ended conversational guide

Not a script — a **toolkit**. Self-contained "story beats" of 30–60 seconds each that you deploy in whatever order the conversation goes, plus bridges for moving between business and technical framing, and a "go deeper" menu organised by topic rather than by time. Read it once to internalise the beats; never try to force the conversation into a fixed order.

### The cold open

If asked *"tell me about something you built"* with zero other context, one sentence — then **stop talking**:

> *"I built an enterprise AI search system where the hardest part wasn't finding the right answer — it was that the same question needed a different correct answer depending on who was asking, and I wanted to prove that boundary never breaks, not just hope it doesn't."*

Wait. Their next question tells you which beat to go to.

### The beats

Five to six, each standing alone, each with a bridge to the next level of depth:

| Beat | Purpose | The bridge |
|---|---|---|
| **A · The business problem** | Relatability — the scenario a non-engineer recognises | *"That's an access-control problem before it's an AI problem — so that's where I spent most of my design effort"* |
| **B · The core technical idea, business-first** | The one mechanism, as an analogy | *"In system terms, that's a pre-filter compiled into the vector search, and a live re-check right before generation"* |
| **C · The trust story** | The bugs your testing caught | Naturally invites *"how did you catch that?"* |
| **D · The platform-reality insight** | What you learned that generalises beyond the platform | The bridge to the listener's stack — *only if the moment allows; do not force it* |
| **E · Honest limitations** | Deployed proactively | *"What it does prove, independent of scale, is…"* |

### Bridges — for when you feel yourself about to drop a term

- *"…which, in plain terms, means…"*
- *"…think of it like [analogy] — technically that's called [term], but the idea is…"*
- *"I can go as deep as you'd like on the how — where should I take this?"* — handing the depth-dial to them, confidently.
- *"The business reason I did that is X; the engineering reason is Y."* — the same decision in both framings.

### The "go deeper" menu

A topic map, not a timeline. *If they ask about architecture* → the pipeline, the policy, the physical isolation. *If they ask why you chose the retrieval approach* → the benchmark and its honest result. *If they ask about testing philosophy* → security decided by hard rules never by the model; the release gate; the docs-match-code check. *If they ask about deployment* → the portability lesson. *If they ask what you would do differently* → the two or three things you would pull forward. Each entry is three bullets you can expand.

### Reading the room

| Signal | Means | Do |
|---|---|---|
| Nodding, "mm-hm", quiet | Tracking; keep moving | Continue at current depth; do not over-explain |
| "How exactly does that work?" | Green light | Move from plain English into the technical layer |
| Redirecting to a different angle | They want a different lens | Drop what you are doing and follow — it is a conversation, not a script to protect |
| Silence after a technical sentence | Too deep too fast | Re-anchor immediately: *"the short version is…"* |
| Checking the time | Close | Go straight to a closing line |

### Closing lines

Prepare one per likely ending thread — security/trust, platform/deployment, limitations/what's next — plus a generic fallback: *"Happy to go deeper on any piece of this — whichever's most useful to you."*

## Format 3 — The technical implementation flow

For a technical audience that wants the *evolution*, not the pitch. The structure the AIA and Bajaj flows share:

1. **The story in brief** — the business problem in a paragraph; what you led; the time box.
2. **Architecture evolution in stages** — a diagram of each stage and the pivot between them. *Why three stages, not one design up front?* Because the first design failed in real testing, and the second pivot happened for a different reason than the first. That shows iterative judgement, not a plan that worked first time.
3. **Why each pivot happened** — the specific failure (context bloat, tool confusion), and why the fix was architectural rather than a better model.
4. **Why each tool, specifically** — evaluated against what, and the concrete reasons it won. A table of *requirement → why this fit*.
5. **The components and the trade-off each embodies** — for every specialist or service, one row: role, tools, and the trade-off it represents.
6. **The constraint that shaped the build** — the regional beta, the legacy API, the compliance rule — and what you traded to work around it.
7. **Full stack** — a table.
8. **Results, stated honestly, and what you would verify next** — *"a correlational signal, not a controlled experiment — worth saying exactly that if pressed."*

Module 07 doc 5 is one of these flows, rewritten as a case study; read them side by side to see how the same material serves a narrative and a lesson.

## Choosing the format

| Situation | Format |
|---|---|
| A fixed slot, a senior audience, a mixed business/technical panel | Deep-dive |
| An open agenda, one-on-one, "tell me about something you built" | Conversational guide |
| A technical peer or hiring manager who wants the architecture story | Implementation flow |
| Behavioural framing — "tell me about a time" | STAR inside any of the above; the deep-dive's segment 2 *is* a STAR |

## Building your own

For each project you might be asked about:

1. Write the **cold-open sentence**. If you cannot write it, you have not yet found what was hard about the project.
2. Write the **five beats**, each 30–60 seconds spoken, each with a bridge.
3. Write the **trust story** — the three things your own testing or review caught. If there are none, your testing was not strong enough to be a story.
4. Write the **honest limitation** you will offer before being asked.
5. Write the **follow-up crib sheet** — five rows, business lead then technical depth.
6. Assemble the deep-dive from the beats with the timing budget; assemble the implementation flow from the pivots.
7. Rehearse aloud with a timer. Then close the script and deliver from the headers.

## Checkpoint

- State the meta-rule and give an example of a term translated in the same breath.
- Give the deep-dive timing budget and say which segment is weighted heaviest for a senior audience and why.
- What are the two passes of the Action beat and what decides whether you deliver the second?
- Why is the trust story the strongest beat?
- Write the cold-open sentence for a project of your own.

**Next →** [Proof vs Cheat-Sheet — the Honesty Discipline](02_Proof_vs_Cheat_Sheet_Honesty.md)
