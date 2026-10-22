---
name: fde-study-notes
description: "Turn FDE / Applied-AI interview source material into study notes, in three modes: (1) build a full tutorial markdown from a book chapter or source doc, self-reviewed up to 3 times against a 20-item decomposition-round rubric, with mermaid diagrams; (2) convert a chapter tutorial (new or already delivered) into the bullet-only, interview-cram `_v2` format with a TOC, a mermaid diagram for every flow (pacing plans included), Interview Pointer callouts, the 20-item rubric mapping and a My Perspective on the Gaps section; (3) summarize an FDE Interview Handbook (fdehandbook.com) page open in Chrome into a crammable bullet list with quiz answers. Use when the user asks to make a tutorial or notes from a chapter, create an FDE-style writeup, convert a tutorial to interview/cram format or v2, or summarize / bullet-point / make crammable an fdehandbook.com page."
---

# FDE study notes

Three modes over one pipeline: source chapter, then full tutorial, then cram version. Separately, handbook pages become chat summaries.
Pick the mode, then read and follow its reference file in full.

| The user wants to... | Mode | Read | Output |
|---|---|---|---|
| Turn a book chapter or source doc into a full tutorial | Chapter tutorial | `references/chapter-tutorial.md` | `<chapter-slug>-tutorial.md` |
| Turn a tutorial into the bullet-only interview-cram format, or draft a new chapter straight in that format | Interview format | `references/interview-format.md` | `<chapter-slug>-tutorial_v2.md` |
| Summarize the fdehandbook.com page open in Chrome | Handbook summary | `references/handbook-summary.md` | bullets in chat, no file |

Routing rules:
- "Make a tutorial" with no format named: use Chapter tutorial.
- "Cram", "interview-ready", "v2", or "bullet-only" for a chapter: use Interview format. For a new chapter, its mode B reuses Step 0 of `references/chapter-tutorial.md` for source gathering.
- Any fdehandbook.com page: use Handbook summary, even if the user says "tutorial".

Shared across the chapter modes:
- Read the whole source chapter, never a title page or partial read.
- Never invent facts the source lacks. Mark rubric gaps Absent in Coverage Notes.
- Never overwrite an existing `-tutorial.md` or `_v2.md` file.
