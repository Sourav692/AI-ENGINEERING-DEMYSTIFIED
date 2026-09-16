---
name: fde-tutorial-interview-format
description: Converts an FDE chapter tutorial (new or already-delivered) into a bullet-only, interview-cram-ready markdown format with sub-headings, a table of contents, mermaid diagrams for every process/flow, and interview-pointer callouts. Use for chapters in the OpenAI Interview Preparation project's FDE tutorial series.
---

# FDE Chapter Tutorial — Interview-Ready Format (v2)

This skill produces a bullet-dense, quickly scannable "cram" version of an FDE chapter tutorial, replacing the theory-heavy prose format used by the original `fde-chapter-tutorial` skill. It never overwrites the original tutorial file — it always produces a separate `_v2` file.

## Two entry modes

### A. Regenerating an already-delivered chapter
1. Read the full original tutorial file (e.g. `chapter-N-<slug>-tutorial.md`, wherever it currently lives — check the working directory and `/mnt/user-data/outputs/`). It is already complete and faithful to the source book chapter.
2. Do **not** re-read the Kindle/PDF source book — the existing tutorial is the source of truth and already contains the full, verified content.
3. Transform it into the v2 format below, preserving every fact, table, code block, and section, restructured per the rules.

### B. Drafting a new chapter for the first time
1. Follow Step 0 of the original `fde-chapter-tutorial` skill's source-gathering process exactly (full gapless read via Kindle/PDF/source, verifying no content is skipped).
2. Draft directly in the v2 format below — skip drafting a v1 prose version first.

## The v2 format, section by section

### 1. Table of Contents (new — at the very top)
- Immediately after the title and source attribution line, add a `## Table of Contents` section.
- A bullet list of every major section (`##`) and sub-heading (`###`) in the document, each as a markdown anchor link, e.g. `- [1. The Customer Problem and Discovery](#1-the-customer-problem-and-discovery)`.
- Nest sub-heading links one level under their parent section's bullet.
- This lets the reader jump straight to any concept during cram review.

### 2. Title and source line
- Keep as-is: `# Chapter N: <title>` plus a one-line source attribution underneath.

### 3. Major sections (unchanged — still the same 8 sections per chapter)
- Keep the 8 major `##` sections in source order (e.g. Customer Problem & Discovery, Clarifying Questions/Requirements/Constraints, Scale Estimates, Architecture & End-to-End Flow, Data Model/APIs/Working Code, Security/Reliability/Failure Handling, Delivery Plan/Observability/Business Impact, Interview Walkthrough/Trade-Offs/Practice).

### 4. Sub-headings inside each major section (new)
- Break every major section into `###` sub-headings, roughly one per 1-2 concepts (about every 150-250 words of the old prose).
- Sub-heading titles are short noun phrases naming the concept (e.g. "Stakeholder Map", "Non-Goals / Scope Fence", "Component Responsibility Table") — not full sentences.
- Each sub-heading contains, in this order:
  1. A tight bullet list capturing the concept — never flowing paragraphs. 1-2 sentences per bullet max; nest sub-bullets for supporting detail.
  2. Any table, code block, or mermaid diagram belonging to that concept, placed directly after the bullets that introduce it.
  3. Optionally, one interview-pointer callout (see below).

### 5. No "Key Points" preamble anymore
- The old "**Key Points**" bullet-list-before-prose pattern from the original skill is retired. Every bullet in a sub-section IS the key point now — there is no separate summary-then-detail split, since prose has been fully replaced by bullets.

### 6. Mermaid diagrams — mandatory for every process or flow
- Unlike the original skill (mermaid only for "genuine" flows, added conservatively), v2 adds a mermaid diagram for **any** process, sequence, decision fork, or multi-step flow described in that sub-section — even ones the original tutorial left as prose or a plain numbered list.
- This includes: architecture/component flows, request sequences, failure drills (detect → contain → recover → prevent), phased rollout timelines, decision trees (e.g. "what fails open vs. fails closed"), and named failure-mode walkthroughs.
- Use `flowchart` for structural/architectural/decision content, `sequenceDiagram` for request/interaction sequences with named participants, and `flowchart TD` with a highlighted branch for failure-path overlays.
- Skip mermaid only for genuinely flat, non-sequential content (a plain metrics list, a glossary, a static requirements list). If in doubt, add the diagram.
- Convert any ASCII-art diagrams from the source tutorial into mermaid using the same conversion approach as before.

### 7. Interview-pointer callouts
- Format: `> 🎯 **Interview Pointer:** <one or two sentences on what's most likely to be asked or most important to memorize from this sub-section>`.
- Place one after the bullets/table/diagram in a sub-section, only where there's a genuine interview-relevant angle (a common follow-up question, a trade-off the interviewer will probe, a number worth memorizing) — not mechanically on every sub-heading. Aim for roughly 6-10 across the whole document.
- Skip it on purely descriptive sub-sections (e.g. a plain data-model field listing) where there is nothing extra to flag.

### 8. Tables and code blocks
- Reproduce exactly as in the original tutorial — full detail, no trimming.
- Introduce each with a single bullet, not a paragraph, e.g. "- API contracts (4 endpoints, each with auth/idempotency/error codes):" followed immediately by the table.

### 9. Interview Walkthrough section (last major section)
- Keep all content: pacing plan, named trade-off pairs, follow-up Q&A, weak-answer repairs, scoring rubric, 90-second summary, practice exercises.
- Tighten any remaining prose into bullets.
- Break into sub-headings the same way as other sections (e.g. "Pacing Plan", "Named Trade-Off Pairs", "Common Follow-Ups", "Weak Answers and Repairs", "Scoring Rubric", "90-Second Summary", "Practice Set").
- Pacing plans (minute-by-minute or block-based) stay as bullet lists, not converted to a table — but do add a `flowchart LR` or `flowchart TD` diagram showing the pacing blocks as sequential stages with their time ranges as labels, since this is exactly the kind of "phased timeline" mermaid mandates.

### 10. Coverage Notes (closing section)
- Keep, but condensed: one line per rubric item instead of a full sentence. Format: `- **Item N (name):** Fully covered / Partial / Absent — <5-10 word reason>`.
- Keep grouped by the four phases (Problem Framing & Discovery / Estimation & Architecture / Trade-offs, Security & Reliability / Delivery, Governance & Communication) as before.
- If the source's Coverage Notes uses a "Fully covered (N items): ...; Partial (N items): ...; Absent (N items): ..." prose-list format instead of a numbered per-item format, map each named item into the correct numbered rubric item (1-20, using the standard rubric below) and restructure it into the per-item-per-phase bullet format. Do not lose any of the source's named gaps or their stated reasons.
- After the per-item breakdown, add a `### My Perspective on the Gaps` subsection: for every item marked Partial or Absent, write 3-6 sentences of your OWN supplementary point of view on how you would address that gap in a live interview for THIS specific chapter's scenario — grounded in the chapter's own architecture (reference actual components/sections from the chapter), not generic advice. Clearly label this as supplementary perspective, not sourced from the original chapter.

The standard 20-item / 4-phase FDE decomposition rubric (use this to map/number any gaps, and to sanity-check the source's coverage claims — do not re-run the review, just use it to label correctly):

**Phase 1 — Problem Framing & Discovery:** 1. Feature → business-outcome reframing, 2. Stakeholder/persona mapping, 3. Clarifying questions that change the architecture, 4. Requirements split (functional/nonfunctional) + prioritization, 5. Explicit non-goals/scope fence.
**Phase 2 — Estimation & Architecture:** 6. Back-of-envelope scale & capacity math, 7. Unit economics/cost-driver breakdown, 8. End-to-end architecture & data flow, 9. Data model & API contracts, 10. Build-vs-buy/vendor & model-selection trade-offs.
**Phase 3 — Trade-offs, Security & Reliability:** 11. Named trade-off pairs with balanced verdict, 12. Threat model/security controls, 13. Failure-mode & reliability drills, 14. Testing strategy.
**Phase 4 — Delivery, Governance & Communication:** 15. Layered evaluation metrics & observability, 16. Phased rollout/risk register/rollback gates, 17. Regulatory/governance depth, 18. Responsible-AI/risk framing beyond the obvious failure mode, 19. Change-management/adoption narrative, 20. Structured communication plan + self-scoring rubric.

## Formatting verification (run before delivery)

Adapt the grep checks used by the original skill:

```bash
F=<path-to-v2-file>
echo "== TOC present =="; grep -c "^## Table of Contents" "$F"
echo "== sections =="; grep -n "^## [0-9]" "$F"
echo "== sub-headings count =="; grep -c "^### " "$F"
echo "== mermaid count =="; grep -c '```mermaid' "$F"
echo "== interview pointer count =="; grep -c "^> 🎯 \*\*Interview Pointer:\*\*" "$F"
echo "== coverage notes count =="; grep -c "^## Coverage Notes" "$F"
echo "== stray Key Points check (should be 0) =="; grep -c "^\*\*Key Points\*\*" "$F"
echo "== total fence count (should be even) =="; grep -c '^```' "$F"
echo "== heading levels =="; grep -oE "^#{1,4} " "$F" | sort | uniq -c
echo "== line count =="; wc -l "$F"
```

- The stray Key Points check must return 0 — confirms the old preamble pattern was fully retired.
- Every `##` major section should have at least 2 `###` sub-headings.
- Spot-check that every mermaid fence has bullet/table context directly around it (no orphaned diagrams dropped with no lead-in).

## File naming and delivery

- Save as `<chapter-slug>-tutorial_v2.md` (underscore before `v2`) — **never** overwrite the original `-tutorial.md` file.
- If a `_v2` file already exists for that chapter, ask the user before overwriting it, or increment to `_v3`.
- Copy to `/mnt/user-data/outputs/` and deliver via `SendUserFile`.
- Chat summary: short header/bullet summary of which chapter, section/sub-heading count, mermaid diagram count, and any Coverage Notes gaps. Do not repaste the tutorial into chat.

## Regenerating the full existing set

When asked to regenerate all already-delivered chapters in a series:
- Process one chapter at a time, sourcing from its existing `-tutorial.md` (or condensed) file already on disk.
- Do not re-read the original source book for any of these — the existing tutorials are the verified source of truth.
- Deliver each `_v2` file as soon as it's completed rather than batching all of them into one delivery at the end.
- For chapters that are already delivered in bullet-only "condensed" form (rather than the older prose-plus-Key-Points format), skip the prose→bullet conversion step and apply only: the Table of Contents, any missing mandatory mermaid diagrams, interview-pointer callouts, and the Coverage Notes restructuring with "My Perspective on the Gaps".
