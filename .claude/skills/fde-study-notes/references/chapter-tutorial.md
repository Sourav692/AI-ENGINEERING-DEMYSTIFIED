# FDE Chapter Tutorial Builder

Turns one chapter of source material (a book read in Kindle/PDF/web, a pasted transcript, an existing summary) into a polished, interview-ready tutorial markdown file — then grades its own draft against a fixed decomposition-round rubric and revises it, up to three review passes, before delivering the final version.

Use this whenever the user asks to "make a tutorial," "turn this chapter into notes," "create an FDE-style writeup," or asks for a chapter summary that should double as interview prep.

## Step 0 — Get the full source content

Do not summarize from a title page or a partial read. If the source is:
- **A Kindle/web reader tab:** page through it screen by screen (click into the text area, then use the `Right` arrow key, or the page-turn buttons) and capture every section until the chapter/heading boundary is reached — the next chapter's title is the stop signal. Do not rely on `get_page_text` alone on reader apps that render text as canvas/images; verify with a screenshot first.
- **A PDF or long doc:** read it fully, not just the first pages.
- **Pasted text:** use it directly.

Hold the raw material (notes, screenshots, quotes) until Step 1 — do not start formatting yet.

## Step 1 — Draft the tutorial (v0)

Write a single markdown file with this structure:

1. **Title** — `# Chapter N: <exact chapter title>`, with a one-line source attribution underneath.
2. **One section per major topic/heading in the source**, in source order. For each section:
   - Start with a **"Key Points"** bullet list (4–8 bullets) — the pointers a reader should walk away with even if they read nothing else in that section.
   - Then cover the concept **in detail**, following the source's own depth: prose explanations, tables (requirement tables, comparison tables, failure-mode tables — reproduce them as markdown tables), numbered sequences, and code blocks, exactly as thorough as the source material. Do not compress detailed content into a vague paraphrase — a reader should not need to go back to the source.
   - Preserve concrete illustrative numbers, formulas, sample answers, and interview phrasing from the source (as guidance/example text, not verbatim copyrighted prose beyond short quoted lines).
3. **Closing section** — an interview-application section if the source has one (pacing plan, trade-offs, common weak answers, self-scoring rubric), reproduced in full.

Keep headers/bullets/tables — never collapse a structured source table into a paragraph.

## Step 2 — Add mermaid diagrams where a picture earns its place

Add a mermaid diagram **only** where the concept is inherently a flow, hierarchy, sequence, or decision branch that prose alone makes hard to follow — not decoratively. Typical candidates in this kind of content:

- **End-to-end architecture / component flow** → `flowchart` or `graph` showing systems of record → ingestion path → query path → response, with the trust boundary noted.
- **Request sequence (auth → retrieve → rerank → generate → cite)** → `sequenceDiagram`.
- **A named failure drill (detect → contain → recover)** → small `flowchart` with the failure branch highlighted.
- **A decision/trade-off fork (e.g., query-time vs. precomputed ACLs)** → `flowchart` with the two branches and their consequences.
- **A phased rollout timeline** → `flowchart LR` or a simple stage list — only if the source frames it as sequential stages with gates.

Skip a diagram if the section is a definition, a metric list, or a rubric — bullets serve those better. Use GitHub-flavored mermaid fences:

\`\`\`mermaid
flowchart LR
  A[...] --> B[...]
\`\`\`

## Step 3 — Self-review against the decomposition rubric (max 3 passes)

After drafting (and after every revision), score the current draft against this fixed rubric — the same one used for the standalone coverage-audit artifact. Group into four phases; mark each item **Covered / Partial / Absent** with a one-line reason tied to a specific section of the draft:

**Phase 1 — Problem Framing & Discovery**
1. Feature → business-outcome reframing
2. Stakeholder / persona mapping
3. Clarifying questions that would change the architecture
4. Requirements split (functional/non-functional) + prioritization
5. Explicit non-goals / scope fence

**Phase 2 — Estimation & Architecture**
6. Back-of-envelope scale & capacity math
7. Unit economics / cost-driver breakdown
8. End-to-end architecture & data flow
9. Data model & API contracts (if the source has them)
10. Build-vs-buy / vendor & model-selection trade-offs (if the source addresses them)

**Phase 3 — Trade-offs, Security & Reliability**
11. Named trade-off pairs with a balanced verdict
12. Threat model / security controls
13. Failure-mode & reliability drills (not just a component list)
14. Testing strategy (contract tests, failure injection, or equivalent)

**Phase 4 — Delivery, Governance & Communication**
15. Layered evaluation metrics & observability
16. Phased rollout, risk register, rollback gates
17. Regulatory / governance depth (if relevant to the topic)
18. Responsible-AI or equivalent risk framing beyond the obvious failure mode
19. Change-management / adoption narrative
20. Structured communication plan + self-scoring rubric for the interview

**Rules for the review loop:**
- Run this scoring pass, then immediately revise the markdown to close every gap that the *source chapter itself* actually supports — pull the missing content from the source material gathered in Step 0, never invent facts the source doesn't contain.
- If a rubric item genuinely has no basis in the source (e.g., the chapter never discusses regulatory compliance), leave it **Absent** and say so plainly — do not fabricate content to force a checkmark.
- Repeat the score → revise cycle **at most 3 times total**. Stop earlier if a pass finds no more closeable gaps.
- After the last pass (whether it's pass 1, 2, or 3), append a short **"Coverage Notes"** section at the end of the tutorial listing what stayed Partial/Absent and why (mirrors the transparency of the standalone audit) — this is the only place review meta-commentary appears; the rest of the tutorial should read as clean instructional content, not a review log.

## Step 4 — Final formatting check

Before delivering, verify:
- Every major section leads with a Key Points bullet list before its detailed prose.
- Tables, code blocks, and formulas from the source are preserved, not summarized away.
- Mermaid diagrams render valid syntax (balanced brackets, no stray quotes) and are placed right after the prose they illustrate, not bunched at the end.
- The Coverage Notes section is present and honest about gaps.
- File is well-formed markdown with consistent heading levels (`#`, `##`, `###`).

## Step 5 — Deliver

Save the file as `<chapter-slug>-tutorial.md`, copy it to the outputs directory, and deliver it with `SendUserFile`. In the chat reply (per the user's standing formatting preference), give a short header/bullet summary of: which chapter, how many review passes ran, and what ended up in Coverage Notes — do not repaste the whole tutorial into the chat.

If the user separately wants the same rubric as a standalone visual audit artifact (like the earlier coverage-audit page), that is a different deliverable — load `artifact-design` and build it only if asked.
