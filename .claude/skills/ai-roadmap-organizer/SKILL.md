---
name: ai-roadmap-organizer
description: Organizes this specific "AI ENGINEERING" folder (D:\3. Github Folders\AI ENGINEERING) into a growing, multi-framework AI Engineering end-to-end roadmap — today it's LangGraph only, but it's expected to expand with top-level sections for LangChain, CrewAI, AutoGen, MCP, ADK, OpenAI SDK, Google SDK, A2A, fine-tuning, evaluation/observability, capstone projects, and whatever else gets added later. ALWAYS invoke this skill whenever the user says "organize the folder(s)", "organize this repo", "clean up this folder", "sort the new files", "where should this go", mentions adding a new framework/section/folder to the roadmap, or has just dropped new files/folders into this project and wants them integrated into the structure — even without the word "organize" (e.g. "I added some CrewAI notebooks, sort them in" or "I'm starting a fine-tuning section, set it up"). Do not use this skill on other repos or unrelated folders.
---

# AI Engineering Roadmap Organizer

This folder is a hand-curated learning path toward end-to-end AI engineering. Today it holds one framework's worth of content (`01_Foundations` through `07_Deep_Agents`, covering LangGraph). That is the **current state**, not the final shape — the user is going to add whole new top-level sections over time (other agent frameworks, protocols like MCP/A2A, SDKs, and cross-cutting competencies like fine-tuning, evaluation, and observability, plus integration projects). `NOTEBOOK_INDEX.md` is the source of truth for what exists and where.

**Never treat the existing chapter list as fixed.** Your job is to keep whatever structure currently exists internally coherent while making room for new sections as they show up — not to force everything into today's 7 chapters. When something doesn't fit any existing top-level section, creating a new one is the *expected*, normal outcome, not an edge case.

## Mental model

The roadmap has two kinds of top-level sections, both numbered sequentially in the order they were added (`01_`, `02_`, ... continuing from whatever the current highest number is — never hardcode a specific count):

1. **Framework/SDK/protocol sections** — one per major technology (LangGraph today; LangChain, CrewAI, AutoGen, MCP, ADK, OpenAI Agents SDK, Google's SDK, A2A, etc. as they arrive). Each is largely self-contained and, going by the LangGraph precedent, tends to internally progress from fundamentals toward production use (foundations → core capabilities → applied patterns like RAG/agents → design patterns → production). That progression is a useful template, not a mandatory shape — a protocol like MCP or A2A may not need a "RAG" stage at all. Use judgment per section; ask the user if the right internal shape isn't obvious.
2. **Cross-cutting sections** — competencies that apply across every framework rather than belonging to one: fine-tuning, evaluation & observability, and similar. These also get their own top-level numbered folder rather than being nested inside a framework section, since they cut across all of them.

A **Projects** area (capstone/integration work spanning multiple frameworks) is also expected — treat it the same way: a top-level section, numbered like the rest unless the user prefers it unnumbered/parallel (ask when it first comes up).

## Process

### 1. Diff disk state against `NOTEBOOK_INDEX.md`

Read `NOTEBOOK_INDEX.md` fully — it's the ground truth of what's already placed. Then list the actual folder tree (skip `.git`, `.venv`, `node_modules`, `__pycache__`, `.databricks`). Anything on disk not accounted for in the index is a candidate for organizing: new notebooks, new top-level folders (a whole new framework dropped in), new scripts at root, new subfolders inside an existing section.

Also flag (but don't move) clearly *supporting* material — source PDFs feeding a notebook, a self-contained sub-module's own `README.md`/`requirements.txt`, config files. These stay put.

### 2. Classify each new item

Read `references/roadmap-map.md` — it's the living record of every top-level section that currently exists or has been discussed, with a short description of what each covers. Treat it as a lookup, not a ceiling:

- If the new item matches a framework/topic already in `roadmap-map.md` with an existing folder → place it inside that section, following that section's established internal convention (numbered flat files, or numbered subfolders per sub-topic — check what's already there).
- If it matches a framework/topic listed in `roadmap-map.md` as "anticipated but not yet created" (the user has already named it as coming, e.g. CrewAI, MCP, fine-tuning) → this is the first content for that section. Propose creating it as the next top-level number in sequence.
- If it's something not mentioned anywhere yet → it's a genuinely new section. Propose one, explain why it's distinct from existing sections, and pick a name that matches the technology/competency's own name (e.g. `MCP` not `Model_Protocol_Stuff`).
- Never wedge a new framework's content into an existing framework's folder just because the concepts rhyme (e.g. a CrewAI agent-patterns notebook does NOT go in `05_Agentic_Design_Patterns/`, which is LangGraph-specific — it gets its own `CrewAI/` section, internally organized however makes sense for CrewAI, possibly with its own agent-patterns subfolder).

For naming/numbering within a section, match whatever convention that section already uses (check a couple of existing files/folders in it before proposing a name) — don't impose LangGraph's specific convention on a different framework's section unless the user wants consistency across sections.

### 3. Check for a safety net before touching anything

This folder has no `.git` by default. Before moving or renaming a single file, check whether `.git` exists. If not, tell the user and offer to run `git init` plus a baseline commit of the current state first, so the reorganization becomes a revertible diff instead of an unrecoverable file shuffle. Wait for their go-ahead before doing this — don't silently init or commit.

If a repo already exists, run `git status` first, and prefer `git mv` over a plain filesystem move so history is preserved.

### 4. Propose the plan, then wait for confirmation

Never move files or create section folders speculatively. Present a concrete plan grouped by target section: current path → proposed destination (exact filename if renaming to match convention), and for any brand-new top-level section, its proposed number/name and why it doesn't fit an existing one. Only execute after the user confirms — they may accept some items and redirect others; apply per-item.

### 5. Execute, then update the index AND the roadmap map

This step is what keeps the skill dynamic instead of going stale as the roadmap grows:

- Update `NOTEBOOK_INDEX.md` — add rows/sections reflecting the new placement so it keeps matching actual disk state.
- **Update `references/roadmap-map.md`** — this is the skill's own memory of the roadmap's shape. If a new top-level section was created, add an entry for it (name, number, one-line scope, internal convention) so the *next* time content for that framework shows up, it's recognized immediately instead of re-litigated. If an "anticipated but not yet created" entry just got its first real folder, update its status. This file should always reflect the actual current structure — edit it every time the structure changes, the same way you'd update the index.
- If a brand-new section was created, mention it probably wants its own `README.md` matching the pattern other sections use — draft one if asked, don't assume.
- Note that `README.md`'s top-level tables are known to lag `NOTEBOOK_INDEX.md` — ask if the user wants those reconciled too; don't rewrite `README.md` unprompted.
- Don't commit the changes yourself. Summarize what moved and let the user decide when to commit.

## What this skill is not for

- Don't reorganize `archive/` — intentionally frozen, retired material.
- Don't touch root scaffolding (`pyproject.toml`, `requirements.txt`, `uv.lock`, `databricks.yml`, `helpers/`, `LICENSE`) unless the user is specifically asking about dependency/package structure, not roadmap content. Note that as new frameworks arrive, some may need their own dependency scoping (a separate `requirements.txt`/`pyproject.toml` inside their section, similar to how `02_Core_Capabilities/01_Memory/memory/` is self-contained) — flag this as a question rather than deciding unilaterally.
- Don't edit notebook/file *content* — only placement and the index/map docs.
