---
name: agentic-ai-tutorial-builder
description: >-
  Generate short, diagram-heavy, jargon-free tutorials from "Cracking Agentic AI
  System Design Interviews" (sole source text, via project_knowledge_search),
  for OpenAI Applied AI interview prep. Produces a matched Markdown + HTML pair
  per chapter, part, or single concept that condenses every book concept into
  plain-language explanations with one diagram each, flagging points most
  relevant for an Agent-Evals-heavy OpenAI panel. Trigger on "make/build a
  tutorial" for a chapter/part/concept from this book, chapter/part number
  references, "turn chapter N into a tutorial," "cheat sheet"/"study guide" for
  this book, or any request to condense a book concept into digestible form
  with diagrams — even without saying "skill." Use instead of improvising
  structure when the request touches this book's content.
---

# Agentic AI Interview Book — Tutorial Generator

Turns any unit of *Cracking Agentic AI System Design Interviews* — a chapter, a
whole Part, or one named concept — into a matched Markdown + HTML tutorial pair.
The goal is the opposite of the book itself: where the book is a full reference,
the tutorial is the fast, digestible version a person reads instead of the
chapter, not in addition to it. Every concept the book covers must show up, but
each one gets only as much space as it needs to be understood — never more.

## When to use this skill

Trigger on any of:
- "Make a tutorial for Chapter N" / "Turn Chapter N into a tutorial"
- "Do Part N" / "Cover [named concept]" (e.g. "do the evaluation pyramid")
- "Cheat sheet / study guide / crash course for [chapter/part/concept]"
- Any request referencing this book's chapters, parts, or named concepts, even
  without saying "skill"

Ask the user only one thing if it isn't already clear: **which unit** (chapter
number, part number, or named concept). Don't ask about format — always produce
both Markdown and HTML. Don't ask about depth — follow the density rules below
by default, and only add a deep dive where the rules say to.

## Source material

One book, one source of truth, accessed via `project_knowledge_search` (and
`/mnt/project/Cracking_Agentic_AI_System_Design_Interviews.pdf` directly for
figures/tables that need exact numbers). Never invent a concept, term, number,
pattern name, or case study that isn't in the book. If a detail doesn't surface
after two differently-worded searches, mark it `[verify against source]` rather
than guessing.

## Chapter / Part map (authoritative)

| Part | Chapters | Focus |
|---|---|---|
| I — Foundations and Architecture | 1–4 | Agent definition, six-component architecture, control loop, design method, reasoning models/test-time compute, frameworks (LangGraph, Temporal) |
| II — Core Agent Capabilities | 5–8 | Tool use/ACI, orchestration & context engineering, memory & retrieval, learning surfaces |
| III — Multi-Agent Systems and Protocols | 9–11 | Coordination topologies, handoffs, MCP/A2A protocols, agent UX |
| IV — Production Engineering | 12–15 | Evaluation pyramid, observability, cost/FinOps, improvement loops |
| V — Safety, Security, and Governance | 16–18 | Threat taxonomy/lethal trifecta, responsible AI, human-agent governance |
| VI — Frontier Capabilities | 19–22 | Computer use, edge/on-device agents, code generation, agentic RAG |
| VII — System Design Deep Dives | 23–25 | 30 design patterns, scale/resilience, production case studies |
| VIII — Interview Preparation | 26–29 | Interview roadmap, technical Q&A, system design script, behavioural questions |
| IX — Capstone | 30–32 | AgentOps Studio end-to-end build |
| X — Bonus Mock Interviews | 33 | 12 topic mock-interview transcripts |

Each of Parts I, II, III, IV, V, VII, VIII also has an **Interview Drill**
section (5 questions each: 4 scenario/technical + 1 real-world case study, e.g.
Knight Capital, Zillow Offers, Replit database deletion). When tutorializing a
Part, always include its Interview Drill as a distinct final module — these are
themselves interview-prep gold and must not be dropped.

## Workflow

### Step 1 — Research

1. Run `project_knowledge_search` for every named concept in the target
   unit — pull each concept's core mechanism, any numbers/formulas, and any
   named real-world example (Knight Capital, Moffatt v. Air Canada, Replit,
   Cursor, Zillow Offers, DoNotPay/FTC, Slack AI, etc.) mentioned for it.
2. Cross-check the target chapters/parts against **Appendix A: Chapter Summary
   Table** and the book's own Contents/ToC so no named concept, pattern, or
   sub-topic is silently skipped. A chapter with "40 concept answers" or "30
   patterns" must actually list all of them (condensed), not a sample.
3. Note every number, formula, or named metric (e.g. the readiness formula in
   Ch. 26, the six reliability patterns table in Ch. 23) — these are exactly
   what a concise tutorial must keep, because they're the parts prose alone
   can't replace.
4. Only start writing after research confirms full coverage of the unit.

### Step 2 — Read the format reference

Read `references/tutorial-format.md` in this skill before writing anything. It
defines the fixed module structure, the diagram rule, the OpenAI-interview
callout convention, the deep-dive trigger rule, and the full HTML design
system/boilerplate to reuse across every tutorial in the set.

### Step 3 — Write the two output files

- Markdown filename: `chXX_kebab_case_title.md` (single chapter) or
  `partX_kebab_case_title.md` (whole part) or `concept_kebab_case_title.md`
  (single named concept).
- HTML filename: same stem, `.html`.
- Save both to `/mnt/user-data/outputs/`.
- Every concept module gets exactly one diagram (Mermaid in Markdown; the same
  diagram, or an interactive SVG/HTML version where it adds real value, in
  HTML) — see the format reference for which diagram type fits which content
  shape.
- Verify HTML tag balance before presenting (`grep -c` on `<div` vs `</div>`).
- Cross-check the finished draft against Step 1's concept list — nothing
  silently dropped, nothing padded.

### Step 4 — Present

Call `present_files` with both paths together. No long postamble.

## Voice — approachable, example-driven, low jargon

Borrow the strengths of good applied-ML crash-course writing (the instructor
walking through code out loud), not textbook or corporate-memo voice:

- **Ground every module in one small concrete scenario**, not abstract prose.
  Reuse a single running example across a chapter where possible (e.g. one
  support-ticket agent, one research agent) so concepts stack instead of each
  needing its own new mental model. If the book already has a running example
  or named case study for a concept, use that one first; only invent a small
  illustrative scenario when the book doesn't supply one, and if invented,
  say so isn't from the book (e.g. "picture a ticket bot that...").
- **Plain, conversational sentences.** "Here's the problem," "Notice that,"
  "This is the part that breaks" — talk to the reader, don't describe at them.
  Short sentences over long compound ones.
- **Define jargon the moment it's used, in the same breath**, not before or
  after it in a separate sentence — e.g. "a façade tool (one tool with an
  `operation` enum standing in for several similar ones)" rather than a
  standalone glossary-style definition ahead of the term.
- **No filler restatement.** Never repeat a point in slightly different words
  to sound thorough — one clear pass beats two similar ones (this is the
  single most common flaw in crash-course-style writing; avoid it deliberately).
- Code/config snippets get a one-line "what this line does" note inline, the
  same rhythm as walking through code live — not a wall of code followed by a
  wall of separate explanation.

This voice guidance governs *how* every module is written; the density rule
below still governs *how much* gets written.

## Core density rule — read this before writing a single line

This is the opposite failure mode from a normal study guide: the risk isn't
missing content, it's over-explaining it. For every concept:

- **1 short paragraph or tight bullet list** stating what it is and why it
  exists (the problem it solves) — 3-6 sentences, plain words, no unexplained
  jargon. If the book itself defines a term precisely, keep that definition;
  don't paraphrase it into vagueness.
- **1 diagram** — never zero, never more than one per concept.
- **Skip mechanically** any book content that is scaffolding rather than
  substance: repeated framing sentences, "as we'll see," cross-chapter
  callbacks, and rhetorical setup. Compress worked examples/case studies to
  their punchline and the one lesson they teach, unless the case study *is*
  the concept (e.g. Knight Capital in a drill).
- **Never stretch.** If a concept is genuinely one sentence (e.g. a definition
  in a glossary-style list), give it one sentence and move on. Don't manufacture
  three paragraphs to make it feel substantial.

### The deep-dive exception

Add a collapsible **Deep Dive** (HTML: `<details>`; Markdown: a clearly
labeled `> **🔍 Deep Dive**` blockquote placed after the concise version, never
replacing it) only when at least one of these is true:
- The concept has a formula, algorithm, or multi-step mechanism a one-liner
  would misrepresent (e.g. the readiness/expected-return formula, the seven-step
  design method, the tool gateway's five typed result states).
- The book itself treats it as a load-bearing concept referenced repeatedly in
  later chapters (e.g. the lethal trifecta, the bounded control loop, the
  evaluation pyramid).
- Getting it wrong in an interview is a common, named failure mode the book
  calls out (e.g. mistaking prompt-level compliance for a security boundary).

Otherwise, no deep dive. Most concepts don't get one — that's the point.

## OpenAI interview callouts — the special-mention layer

Because the user's target panel is known to weight **Agent Evals and
Evaluation Harnesses** heavily, and the interview is collaborative/discussion-
based system-architecture and judgment, apply this priority lens to every
module (this is Claude's editorial judgment, layered on top of the book's
content — never invented as if the book said it):

- Add a **🎯 OpenAI Interview Pointer** callout to any module that is:
  1. Directly about evaluation, evals harnesses, LLM-as-judge, trajectory
     assertions, calibration, or regression suites in CI (Ch. 12 material
     especially, but flag it wherever it recurs — Ch. 8's skill promotion
     gate, Ch. 15's regression-from-incidents, Ch. 27's forty concept answers).
  2. About agent architecture fundamentals a discussion-based loop would probe
     first (the six-component architecture, the bounded control loop, the
     seven-step design method, orchestration topologies).
  3. A named production failure/case study — these are exactly the "say a
     specific detail, not a framework name" moments the book itself says
     separate strong candidates (Ch. 26).
  4. A concept the book explicitly flags as a common rejection reason or
     interviewer probe (silence while thinking, naming frameworks instead of
     mechanisms, no owned failure story, etc.)
- Keep each pointer to 1-2 sentences: *why* it's likely to come up and *what a
  strong answer names* (a mechanism, a number, a trade-off) — never a generic
  "this is important."
- Don't force a pointer onto every module. A module with nothing distinctively
  OpenAI-relevant gets none — false emphasis dilutes the real ones.

## Fidelity rules

- Every concept named in the book's own chapter contents/summary table for the
  target unit must appear as its own module — cross-check before presenting.
- Preserve the book's concrete numbers, named patterns, and named case studies
  exactly; never genericize a specific detail into vague prose.
- Never invent a case study, number, or pattern name not in the book.
- OpenAI Interview Pointers are Claude's additions, clearly labeled as such via
  their callout style — never blended into body text as if the book said them.
