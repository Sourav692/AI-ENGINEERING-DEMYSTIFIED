# Blueprint for an interview-prep tutorial

Two deliverables, one source of truth. The **markdown study guide** is written
first and is the canonical content; the **interactive artifact** renders that same
content as a drillable page. Never let them disagree — build the artifact from the
finished markdown, not in parallel with it.

Both files live in `tutorials/`, side by side, so git tracks the rendered page as well
as the guide. Never author the HTML in a scratchpad: publishing from a temp path leaves
the page unversioned, and once the session ends there is no local copy to diff or edit.

## Deliverable 1 — the markdown study guide

Path: `tutorials/<slug>_INTERVIEW_TUTORIAL.md`, where `<slug>` is the input folder
name (or notebook stem for a single file), lowercased with underscores.

```
# <emoji> <Topic> — Interview Tutorial

> Built from N notebook(s) in `<path>` on <YYYY-MM-DD>.
> Target roles: Applied AI / AI Engineer · Agentic AI Engineer · Forward Deployed Engineer

## What this covers            <- table: concept | source notebook | interview weight
## Coverage gaps               <- interview-critical topics the source does NOT teach

---
## 1. Core concepts            <- the SHARED CORE, every role needs this
### 1.x <Concept>
   - **What it is** (3-4 sentences, no hand-waving)
   - **How it works** (the mechanism, not the marketing)
   - **In your notebooks**: `file.ipynb` -> the exact symbol demonstrated
   - **Say this in an interview**: a 2-3 sentence spoken answer

---
## 2. Gotchas                  <- see "Gotcha shape" below
---
## 3. Tradeoffs                <- see "Tradeoff shape" below
---
## 4. Top 10 interview questions: real-time agentic system design
                               <- web-sourced this run, each with a source link
---
## 5. Role tracks
### 5.1 Applied AI / AI Engineer
### 5.2 Agentic AI Engineer
### 5.3 Forward Deployed Engineer
   each: what they probe · 8-12 questions with answers · one take-home style task

---
## 6. Mock system design: <a real-time agentic scenario>
   - The prompt (as an interviewer would give it)
   - A scoring rubric (what a strong answer covers)
   - A worked strong answer

---
## 7. Self-check
   - 15 rapid-fire Q -> A
   - "Explain to a skeptical staff engineer" prompts
```

## Deliverable 2 — the interactive artifact

Path: `tutorials/<slug>_INTERVIEW_TUTORIAL.html` — the same `<slug>`, beside the
markdown. Publish that path so the URL is tied to a file git tracks.

Same content, rendered for drilling rather than reading. Load the
`artifact-design` skill before writing it; load `artifact-capabilities` if you
want progress to persist across sessions.

Required interactions, in priority order:

1. **Question cards with click-to-reveal answers.** Never show the answer first —
   the learner must attempt recall. This is the single most valuable interaction.
2. **Role filter.** Toggle Applied AI / Agentic / FDE / All, filtering every
   question on the page.
3. **Self-scoring.** Per question: Got it / Shaky / Missed. Show a running tally
   and let the learner re-drill only Shaky and Missed.
4. **Gotcha flip-cards.** Symptom on the front, cause and fix on the back.
5. **Tradeoff tables.** Sortable or at minimum scannable, with the "pick X when"
   column always visible.
6. **Progress persistence.** `localStorage` is the floor. If the `artifact-capabilities`
   skill shows a durable store is available for this user, prefer it so progress
   survives a device change.

Deliberately excluded: timers, streaks and anything that gamifies speed. Interview
recall is about depth, and a countdown pushes toward memorized surface answers.

## Gotcha shape

A gotcha is a thing that is true, surprising, and costly. Not a definition. Every
gotcha gets exactly these four lines:

```
**<One-line name>**
- **Symptom**: what the learner actually sees — the error text, the wrong number,
  the silent no-op. Quote real output where the notebooks show it.
- **Cause**: the mechanism underneath. One or two sentences.
- **Fix**: the concrete change, with the API call or config that does it.
- **Interview angle**: how this shows up as a question, phrased the way it is asked.
```

Aim for 8-15 gotchas. Prefer ones the source notebooks actually hit — a saved
error output or a warning in a cell is a gift, use it verbatim.

## Tradeoff shape

A tradeoff needs a decision, at least two live options, and a rule for choosing.
"It depends" without the rule is worthless in an interview.

```
### <Decision being made>
| Option | Costs you | Buys you | Pick when |
|---|---|---|---|
| A | ... | ... | ... |
| B | ... | ... | ... |

**The one-liner**: <the sentence a candidate says out loud to settle it>
```

Aim for 6-10 tradeoffs. Every one must include the "one-liner" — that sentence is
what actually gets said in the room.

## Plain language

The reader may be new to this. Assume they are smart and know Python, and assume
nothing else. Concretely:

- **Explain the thing before you name it.** "A number that says how close two pieces
  of text are in meaning — that's cosine similarity." Not the reverse.
- **Expand every acronym and term of art on first use**, in the same sentence.
  RAG, MRR, recall@k, p95, ACL, BM25, MMR. Once expanded, use it freely.
- **Short sentences.** One idea each. If a sentence has two commas and a semicolon,
  it is two sentences.
- **No throat-clearing.** Cut "it is worth noting that", "importantly", "essentially".
- **Analogies are allowed and encouraged**, but each one must be followed
  immediately by the literal mechanism. An analogy that replaces the explanation is
  worse than no analogy.

The interview answers themselves stay precise — a hiring manager wants the
mechanism. Simple wording, not simple content.

## Diagrams

A diagram earns its place when it shows a **flow, a decision, or a comparison** that
prose makes the reader hold in their head. Aim for 5-8 across the tutorial. Do not
draw a picture of a list.

Markdown uses ` ```mermaid ` fences. The artifact uses `<pre class="mermaid">` —
Artifacts render mermaid natively, so never load a library for it.

The diagrams that consistently earn their place:

| Diagram | Why it works |
|---|---|
| The pipeline, end to end | Gives the reader one mental model to hang everything on |
| A debugging decision tree | Turns "diagnose it" into steps they can follow under pressure |
| A loop with its exits | The only clear way to show termination guards |
| A time or cost budget | Makes latency and spend concrete instead of hand-waved |
| Two architectures side by side | Comparison is what a tradeoff section is for |

**Mermaid syntax rules that prevent silent breakage:**

- **Always quote node labels**: `A["Retrieve top k"]`, never `A[Retrieve top k]`.
  Unquoted brackets, parentheses, commas and colons break the parse or render blank.
- Keep labels under about 40 characters; put detail in the prose, not the box.
- Prefer `flowchart TD` or `LR`. Use `sequenceDiagram` only for real time-ordered
  message passing.
- No styling directives, no click handlers, no HTML inside labels.

## Code snippets

Every core concept gets a snippet. It is the difference between a reader who can
describe the idea and one who can build it.

- **5-15 lines.** Long enough to be real, short enough to read at a glance.
- **Lift from the learner's own notebooks wherever possible**, and say which file it
  came from. That is what lets them say "I built this" truthfully.
- **Runnable in shape**: real imports, real API names, no `...` standing in for the
  part that matters.
- **Comment the non-obvious line only.** Do not narrate `import numpy as np`.
- Pair each snippet with one or two sentences saying what to look at in it. A
  snippet dropped in without a pointer is decoration.
- For a gap topic, the snippet shows what they would write, clearly labelled as
  not-yet-built.

## Answer quality bar

Every answer in the tutorial must survive a follow-up. Concretely:

- **Name the mechanism, not the vibe.** "Retries are exception-driven via
  `.with_retry()`, which re-runs the composite so the model resamples" beats
  "LangChain handles retries for you."
- **Give a number where a number exists.** Latency shape, cost order of magnitude,
  context window, token cost. Ranges are fine; vagueness is not.
- **State the failure mode.** A strong answer volunteers when the approach breaks.
- **Cite the learner's own notebook** when the concept is demonstrated there, so
  they can say "I've built this" rather than "I've read about this."

## Grounding rule

The tutorial teaches what the source notebooks contain, plus explicitly-labelled
gap coverage. Run `scripts/extract_concepts.py` first and let its output decide the
section list. Two hard rules:

- **Never claim the source demonstrates something it does not.** The learner will
  be asked "walk me through how you built that" and must be able to.
- **Never silently skip an interview-critical gap.** Put it under "Coverage gaps",
  teach it from first principles, and mark it `(not in your notebooks — build this)`.
