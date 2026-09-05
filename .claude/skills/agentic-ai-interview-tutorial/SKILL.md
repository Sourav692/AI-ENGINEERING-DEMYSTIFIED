---
name: agentic-ai-interview-tutorial
description: >-
  Turns a folder of notebooks (or individual notebooks) in this AI ENGINEERING repo
  into an interview-prep tutorial for Generative AI and Agentic AI roles — a markdown
  study guide plus a published interactive HTML artifact with click-to-reveal question
  cards, role filtering and self-scoring. Grounds every concept in what the source
  notebooks actually demonstrate, adds gotchas (symptom/cause/fix) and tradeoff tables,
  runs a LIVE web search each time for the current top 10 real-time agentic system
  design interview questions, and splits practice into a shared core plus tracks for
  Applied AI / AI Engineer, Agentic AI Engineer, and Forward Deployed Engineer. Use
  when the user says "make an interview tutorial", "prep me for interviews from these
  notebooks", "turn this folder into interview prep", "create a study guide for
  agentic AI interviews", "help me get interview ready for AI engineer / agentic AI /
  FDE roles", or points at notebooks and asks what they would be asked about them.
  One tutorial per input folder — not one per notebook.
---

# Interview-Prep Tutorial Builder

Input: a folder of notebooks, or one or more individual notebook paths.
Output: **two files in the repo, plus a published page** —

1. `tutorials/<slug>_INTERVIEW_TUTORIAL.md` — the canonical study guide
2. `tutorials/<slug>_INTERVIEW_TUTORIAL.html` — the artifact's source, versioned in git
3. A **published interactive artifact** rendered from that HTML

The user studies from the artifact and greps the markdown. Both must say the same
thing, so write the markdown first and build the HTML from it.

**Write the HTML into `tutorials/`, never into a scratchpad.** Publishing from a temp
directory leaves the page unversioned and unmaintainable once the session ends: the
markdown lives in git, the rendered page does not, and the two drift with no diff to
show it. Passing the repo path to the Artifact tool fixes that at no cost.

**Read `references/tutorial-blueprint.md` before drafting.** It owns the output
structure, the required gotcha and tradeoff shapes, and the answer quality bar.
**Read `references/role-competency-map.md` before writing section 5.** It owns what
each of the three roles is actually probed on.

## The rule that matters most

**Teach what the notebooks contain.** The learner will be asked "walk me through
how you built that," and every claim in this tutorial is a claim they will have to
defend. So:

- Never assert the source demonstrates something it does not.
- Never silently skip an interview-critical topic the source misses. Put it under
  **Coverage gaps**, teach it from first principles, and label it
  `(not in your notebooks — build this)`.

`scripts/extract_concepts.py` decides which is which. Run it first, every time.

## Pipeline

### 1. Resolve the input and inventory it

```bash
python .claude/skills/agentic-ai-interview-tutorial/scripts/extract_concepts.py <path> [<path> ...]
```

Accepts folders (crawled recursively) and individual `.ipynb` paths, mixed. It is
read-only and never executes a notebook. Add `--json` to consume it programmatically,
`--quiet` to drop per-notebook outlines.

It reports, per notebook: title, heading outline, third-party imports, library-looking
symbols called, and cell counts. Aggregated: frameworks in use, **topics demonstrated
with the evidence for each**, and **interview-critical topics absent from the source**.

That last list is the Coverage gaps section. Do not editorialize it away.

If the run finds no notebooks, stop and say so rather than inventing a curriculum.

### 2. Read the source before writing about it

The inventory gives you symbols and headings, not understanding. Open the notebooks
that anchor each topic and read the actual cells. Two things to harvest that only
reading gives you:

- **Saved outputs and warnings.** A real error string or a deprecation warning in a
  cell is the best possible gotcha. Quote it verbatim.
- **Commented-out or broken code.** Often a real trap the author already hit.

### 3. Live web search for the top 10 questions

Required every run — the user asked for current questions, not a frozen bank. Run
several searches and synthesize; do not lift one listicle.

Suggested queries, adapted to the source's actual stack:

- `agentic AI system design interview questions <current year>`
- `LLM agent system design interview real-time production`
- `AI engineer interview questions RAG evaluation production`
- `forward deployed engineer interview questions AI`
- `multi-agent system design interview questions`

Then:

- Prefer engineering blogs, first-party docs and interview write-ups over content farms.
- **Cite a source link per question.** A question with no source did not come from the web.
- **Bias hard toward real-time and production concerns** — latency budgets, streaming,
  concurrency, partial failure, termination, cost ceilings, observability. That is what
  "real-time agentic system design" means and it is the section the user asked for by name.
- Write a strong answer for each, to the blueprint's quality bar. A question list
  without answers is not a tutorial.

**If the web is unreachable**: say so in the run report and in the tutorial header,
write the section from your own knowledge, and mark it
`(offline fallback — not web-sourced this run)`. Never present unsourced questions
as web-sourced.

### 4. Write the markdown study guide

Follow `references/tutorial-blueprint.md` exactly. Write to
`tutorials/<slug>_INTERVIEW_TUTORIAL.md`, creating `tutorials/` at the repo root if
needed. `<slug>` is the input folder name lowercased with underscores; for a single
notebook, its filename stem.

Section 1 is the shared core. Sections 2 and 3 are the gotchas and tradeoffs, in the
blueprint's mandated shapes — a gotcha without a symptom is a definition, and a
tradeoff without a "pick when" is noise. Section 5 is the three role tracks, driven
by `references/role-competency-map.md`.

### 5. Build and publish the interactive artifact

**Load the `artifact-design` skill before writing the page.** If you want progress to
survive across devices, load `artifact-capabilities` first and check what this user
actually has; otherwise `localStorage` is the floor.

Write the page to `tutorials/<slug>_INTERVIEW_TUTORIAL.html` and publish **that path**,
so the source is versioned next to the markdown.

Build it from the finished markdown. The blueprint lists the required interactions in
priority order — click-to-reveal question cards first, then role filtering, then
self-scoring. Answers must never render visible on load; recall attempt before reveal
is the whole point. Render the same mermaid diagrams and code snippets.

**Diagrams injected by script need the library loaded explicitly.** The native
Artifact pass only sees `<pre class="mermaid">` blocks that are in the page markup;
anything a renderer writes into the DOM later displays as raw source. The blueprint
has the exact snippet, the pinned version to use, and the two traps in it.

Give it a favicon and a distinctive title, and hand the user the URL.

> **Regenerating an existing tutorial**: the Artifact tool ties a URL to a file path.
> Republishing the same path in the same session keeps the URL. From a *later* session,
> pass the existing artifact `url` explicitly, or you will create a second artifact and
> orphan the user's self-scores.

### 6. Report

State plainly: how many notebooks were read, which topics were grounded in the source,
which were gap-filled, whether the web search succeeded, and both output locations.

## Scope rules

- **One tutorial per invocation.** A folder of 12 notebooks produces one tutorial, not
  12. Concepts shared across notebooks get taught once, well.
- **Never modify the source notebooks.** This skill reads them. If a notebook is broken,
  note it as a gotcha and tell the user; do not fix it here.
- **Regenerating overwrites.** If the target tutorial already exists, read it first and
  tell the user what will change before overwriting. Their self-scores live in the
  artifact, not the markdown, so republishing to the same artifact URL preserves them.

## Quality gate before you hand it over

Check each of these against the draft, and fix rather than report:

1. Every section-1 concept cites a real notebook, or is marked as a gap.
2. Every core concept has a code snippet, lifted from the learner's notebooks where
   one exists and labelled with the file it came from.
3. There are 5-8 mermaid diagrams, each showing a flow, a decision or a comparison —
   and every node label is quoted, `A["like this"]`, so none render blank.
4. Every gotcha has all four lines: symptom, cause, fix, interview angle.
5. Every tradeoff table has a populated "Pick when" column and a spoken one-liner.
6. All 10 system-design questions carry a source link, or the whole section is marked
   as the offline fallback.
7. Every role track has questions no other track has. If the three tracks are
   interchangeable, they are not tracks.
8. No answer stops at what a thing is without saying when it breaks.
9. Every acronym and term of art is expanded on first use. Read the first paragraph
   of each section as a beginner would: if it opens with jargon, rewrite it.
10. The artifact hides answers until clicked, renders the same diagrams and snippets,
    and its content matches the markdown.
