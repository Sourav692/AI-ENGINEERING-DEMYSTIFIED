# Blueprint for an interview-prep tutorial

Two deliverables, one source of truth. The **markdown study guide** is written
first and is the canonical content; the **interactive artifact** renders that same
content as a drillable page. Never let them disagree — build the artifact from the
finished markdown, not in parallel with it.

Both files live in `tutorials/`, side by side, so git tracks the rendered page as well
as the guide. Never author the HTML in a scratchpad: publishing from a temp path leaves
the page unversioned, and once the session ends there is no local copy to diff or edit.

The header (see the fenced template below) is a **table**, not a blockquote — every
row is scannable at a glance. Multiple source paths are comma-separated in one
**Source** cell, never one path per line. An optional extra fact (series membership,
a weighted role, a web-sourcing note) goes in a single **Note** row; omit that row
entirely when there's nothing to say.

## Density rule — read this before writing a single line

Every section below defaults to **bullets, not paragraphs**. The failure mode this
guards against is a tutorial that restates the same point three times in slightly
different words — that pads length without adding anything a reader can use.

- **One short paragraph max per concept** (1-2 sentences: what it is, why it exists),
  then bullets for everything else. No second paragraph in the main flow — if there's
  more to say, it belongs in a Deep Dive (see below), not a longer intro.
- **One sentence per bullet.** If a bullet needs a comma-separated list of clauses to
  make its point, split it into two bullets or move it to a Deep Dive.
- **Never restate.** Say a thing once, in the place it belongs (concept vs. gotcha vs.
  interview answer), not again in different words two sections later.
- **Cut connective tissue.** No "it's worth noting that", "as we've seen", "in other
  words" — go straight to the content.
- **Target roughly half the length of a first, unconstrained draft.** If a section
  reads long, the fix is almost always cutting restatement and moving genuinely
  complex material into a Deep Dive — not writing more carefully-worded prose.

This rule governs every section in this blueprint — Core Concepts, Gotchas,
Tradeoffs, the question sections and the role tracks all follow it, not just the
concept write-ups.

## Deliverable 1 — the markdown study guide

Path: `tutorials/<slug>_INTERVIEW_TUTORIAL.md`, where `<slug>` is the input folder
name (or notebook stem for a single file), lowercased with underscores.

```
# <emoji> <Topic> — Interview Tutorial

| | |
|---|---|
| **Source** | `<path>`[, `<path 2>`, ...] |
| **Notebooks** | N |
| **Built** | <YYYY-MM-DD> |
| **Target roles** | Applied AI / AI Engineer · Agentic AI Engineer · Forward Deployed Engineer |
| **Note** _(optional)_ | anything that doesn't fit the rows above — series membership, a role weighted as primary focus, whether section 4 was web-sourced live, etc. Omit the row entirely when there's nothing to say. |

## What this covers            <- table: concept | source notebook | interview weight
## Coverage gaps               <- ONLY gaps specific to this topic (see SKILL.md); not the raw checklist

---
## 1. Core concepts            <- the SHARED CORE, every role needs this
### 1.x <Concept>
<1-2 sentence intro: what it is and why it exists — no more, see "Density rule">
   - **How it works**: the mechanism, one sentence
   - **Code**: `file.ipynb` -> the exact symbol demonstrated, with a short snippet
     inline (5-15 lines — see "Code snippets" below)
   - **Say this in an interview**: one spoken sentence

<details><summary>[optional] see "Deep Dive shape" below for when to add this</summary>
...
</details>

---
## 2. Gotchas                  <- see "Gotcha shape" below, 6-10 of them
---
## 3. Tradeoffs                <- see "Tradeoff shape" below, 5-8 of them
---
## 4. Top 10 interview questions: real-time agentic system design
                               <- web-sourced this run, each with a source link.
                                  3-4 sentence answers, not paragraphs.
---
## 5. Role tracks
### 5.1 Applied AI / AI Engineer
### 5.2 Agentic AI Engineer
### 5.3 Forward Deployed Engineer
   each: what they probe (1 bullet) · 6-8 questions, 1-2 sentence answers ·
   one take-home task described in 2-3 bullets, not a paragraph

---
## 6. Mock system design: <a real-time agentic scenario>
   - The prompt (as an interviewer would give it)
   - A scoring rubric (what a strong answer covers) — bullets, not prose
   - A worked strong answer — bullets hitting each rubric point, not an essay

---
## 7. Self-check
   - 15 rapid-fire Q -> A, one line each
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
6. **Deep Dives collapsed by default**, same as the markdown's `<details>` — a tap or
   click expands one, matching the source rather than flattening it into the card.
7. **Progress persistence.** `localStorage` is the floor. If the `artifact-capabilities`
   skill shows a durable store is available for this user, prefer it so progress
   survives a device change.

Deliberately excluded: timers, streaks and anything that gamifies speed. Interview
recall is about depth, and a countdown pushes toward memorized surface answers.

## Deep Dive shape

A Deep Dive is the pressure valve for the density rule above: it exists so the main
flow can stay short without ever dropping something genuinely hard. Most concepts get
none. Add one only when at least one of these is true:

- The concept has a **multi-step mechanism, formula, or algorithm** that a one-liner
  would misrepresent (e.g. exponential backoff with jitter, a checkpointing protocol,
  a scoring formula).
- The source notebooks show it **failing in a specific, instructive way** — a real
  error, a race condition, a silent no-op — worth walking through step by step.
- It's a **common, named interview failure mode**: something candidates routinely get
  wrong or hand-wave, where the detail is exactly what separates a strong answer.

If none of these apply, the concept's four bullets are the whole story — do not add a
Deep Dive just because a concept "feels important." Most concepts, including
important ones, don't need one.

Format — a collapsed HTML `<details>` block, placed immediately after the concept's
bullets:

```
<details>
<summary>🔍 Deep Dive: <specific angle, not just the concept name></summary>

<the extended explanation, formula, longer code, or failure walkthrough — still
bullets-first per the density rule, just longer than the four-bullet default>

</details>
```

- The `<summary>` names the *angle*, not just the concept — "Deep Dive: why jitter
  prevents thundering herd," not "Deep Dive: retries."
- Everything long that used to pad the main flow lives here instead: extended
  mechanism walkthroughs, a second/longer code example, edge cases. The four-bullet
  default never grows to accommodate this — it moves here or it's cut.
- Both deliverables use the same tag: it renders natively collapsed in the markdown
  study guide, and the artifact should render it the same way (collapsed, tap to
  expand) rather than flattening it into the main card.

## Gotcha shape

A gotcha is a thing that is true, surprising, and costly. Not a definition. Every
gotcha gets exactly these four lines, **one sentence each, no elaboration**:

```
**<One-line name>**
- **Symptom**: what the learner actually sees — the error text, the wrong number,
  the silent no-op. Quote real output verbatim where the notebooks show it.
- **Cause**: the mechanism underneath, in one sentence.
- **Fix**: the concrete change, with the API call or config that does it.
- **Interview angle**: how this shows up as a question, phrased the way it is asked.
```

Aim for 6-10 gotchas — fewer, sharper ones beat a long list of minor ones. Prefer
ones the source notebooks actually hit — a saved error output or a warning in a cell
is a gift, use it verbatim. If a cause genuinely needs more than one sentence to
explain (a multi-step failure chain), that is a Deep Dive candidate, not a longer
Cause line — link it: `**Cause**: <one sentence>. See the Deep Dive on <concept>.`

**Topic-specific, not implementation-generic.** A gotcha earns its place only if it
is a surprising behavior of *this tutorial's core concept* — something that would
still be a gotcha in a from-scratch reimplementation of the pattern being taught.
Cut anything that is really a fact about a different, generic component the
notebook happens to use: a text splitter's units, a chain type's context-window
limit, a store's persistence default, a broad `except` clause, an ID-generation
default, a notebook author's own placeholder-key check. Those are real facts, but
they belong to a different topic's tutorial (or nowhere) — including them here
dilutes the list and crowds out the gotchas that actually test understanding of
*this* concept. When in doubt, ask: "is this surprising because of how *the concept
this tutorial teaches* behaves, or because of some other library/notebook detail
that happened to be in the way?" Keep only the former. A shorter list of 2-4 sharp,
on-topic gotchas beats a longer list padded with generic ones — the 6-10 target
above is a ceiling, not a quota.

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

Aim for 5-8 tradeoffs — every table cell is a short phrase, not a sentence. Every
one must include the "one-liner" — that sentence is what actually gets said in the
room, and it is the only piece of full-sentence prose the tradeoff needs.

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

Markdown uses ` ```mermaid ` fences. The artifact uses `<pre class="mermaid">`.

**Rendering them in the artifact — learned the hard way.** Artifacts render mermaid
natively, but only for blocks present in the page's own markup. A block written into
the DOM by script — which is what any tab switcher or data-driven renderer does — is
missed entirely and displays as raw source text.

So: if every diagram is static in the file, rely on the native pass and load nothing.
If any diagram is injected by script, drive the library yourself:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/11.15.0/mermaid.min.js"></script>
<script>
const MERMAID = window.mermaid
  || (window.__esbuild_esm_mermaid_nm && window.__esbuild_esm_mermaid_nm.mermaid)
  || null;
if (MERMAID) MERMAID.initialize({startOnLoad: false, theme: "neutral"});

function drawDiagrams() {                       // call after every re-render
  if (!MERMAID) return;
  const nodes = [...document.querySelectorAll("pre.mermaid:not([data-processed])")];
  if (nodes.length) Promise.resolve(MERMAID.run({nodes})).catch(() => {});
}
</script>
```

Three details that matter. Pin an exact version and check it resolves before
publishing — the obvious guess `11.4.1` is a 404 on cdnjs. Resolve the global
defensively, because the cdnjs build may attach to an esbuild namespace rather than
`window.mermaid`. And give the diagram container an explicit dark `color`, so an
unrendered block is still readable if the script is ever blocked.

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

Every core concept gets a snippet in its main bullets — **all of them, including the
ones that already have a diagram**. A picture shows the shape; the code shows the API
names the learner has to say out loud. They do different jobs, so one never replaces
the other.

The concepts that most often get skipped are the ones where a diagram feels like
enough: a termination policy, a latency budget, a caching strategy. Those are exactly
the ones an interviewer asks you to write on a whiteboard, so they need code most.

- **5-15 lines in the main flow.** Long enough to be real, short enough to read at a
  glance. A longer or second example belongs in a Deep Dive, not a bigger main snippet.
- **Lift from the learner's own notebooks wherever possible**, and say which file it
  came from. That is what lets them say "I built this" truthfully.
- **Runnable in shape**: real imports, real API names, no `...` standing in for the
  part that matters.
- **Comment the non-obvious line only.** Do not narrate `import numpy as np`.
- **One pointer sentence, not a walkthrough.** Say what to look at in one sentence. A
  line-by-line narration of the snippet is exactly the restatement the density rule
  cuts — if the code needs that much explaining, that explanation is the Deep Dive.
- For a gap topic, the snippet shows what they would write, clearly labelled as
  not-yet-built.

## Answer quality bar

Every answer in the tutorial must survive a follow-up, in as few sentences as that
takes. Concretely:

- **Name the mechanism, not the vibe.** "Retries are exception-driven via
  `.with_retry()`, which re-runs the composite so the model resamples" beats
  "LangChain handles retries for you."
- **Give a number where a number exists.** Latency shape, cost order of magnitude,
  context window, token cost. Ranges are fine; vagueness is not.
- **State the failure mode.** A strong answer volunteers when the approach breaks.
- **Cite the learner's own notebook** when the concept is demonstrated there, so
  they can say "I've built this" rather than "I've read about this."
- **3-4 sentences, hard cap**, for every interview-question and role-track answer.
  Density over length: a correct answer in 3 sentences beats a correct answer in 8 —
  cut restatement before you cut substance.

## Grounding rule

The tutorial teaches what the source notebooks contain, plus explicitly-labelled
gap coverage. Run `scripts/extract_concepts.py` first and let its output decide the
section list. Two hard rules:

- **Never claim the source demonstrates something it does not.** The learner will
  be asked "walk me through how you built that" and must be able to.
- **Never silently skip an interview-critical gap.** Put it under "Coverage gaps",
  teach it from first principles, and mark it `(not in your notebooks — build this)`.
