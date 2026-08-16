---
name: ai-roadmap-organizer
description: Organizes this specific "AI ENGINEERING" folder (D:\3. Github Folders\AI ENGINEERING) into a 13-phase AI Engineering end-to-end roadmap where each phase owns exactly one topic (Theory & Foundations, LangChain Fundamentals & Prompting, LangGraph Fundamentals, Retrieval & RAG, AI Agent Fundamentals, Agent SDKs First-Party, Advanced Agentic Systems, Advanced RAG, Agent Protocols, Alternative Agent Frameworks, Claude Code & AI Coding Tools, Production & Observability, Projects) — never split the same topic across two phases, and never let a framework's content become a second home for a topic that already has a phase. ALWAYS invoke this skill whenever the user says "organize the folder(s)", "organize this repo", "clean up this folder", "sort the new files", "where should this go", mentions adding a new framework/protocol/topic/phase to the roadmap, or has just dropped new files/folders into this project and wants them integrated into the structure — even without the word "organize" (e.g. "I added some CrewAI notebooks, sort them in" or "I'm starting a fine-tuning track, set it up"). Do not use this skill on other repos or unrelated folders.
---

# AI Engineering Roadmap Organizer

This folder is a hand-curated learning path toward end-to-end AI engineering, organized into 13 numbered **phases**, each owning **exactly one topic**. This is the single most important rule and it was hard-won: earlier structures let the same topic (RAG, agents, memory, observability) live in 2–3 different phases at once, and the user's own words were "the structure seems little confusing... with duplicate RAG, and other module entries." Read `references/roadmap-map.md`'s History section before touching anything — it explains exactly how that happened and what fixed it, so you don't reintroduce it.

Inside a phase, one or more **tracks** (subfolders) hold the specific framework implementations that belong to that phase's topic — e.g. Phase 4 ("Retrieval & RAG") has `RAG_with_LangGraph/` and `RAG_with_LangChain/` side by side, not split across two different phases. `NOTEBOOK_INDEX.md` is the source of truth for what exists and where; `references/roadmap-map.md` is this skill's living memory of the phase/track shape and the reasoning behind non-obvious placements.

**Never treat the current phase list as fixed** — new phases and tracks are the expected way this grows. But **before adding anything, check whether its topic already has a phase.** If it does, the new content is a track (or addition to a track) *inside* that phase — never a new top-level folder for "the same topic, but this framework's version."

## Mental model

- **One topic, one phase.** Before placing anything, ask "what topic is this, fundamentally?" (not "what framework is it in?"), then check `roadmap-map.md` for which phase already owns that topic. RAG content always goes to Phase 4 (foundational) or Phase 8 (advanced/agentic) depending on prerequisite, never anywhere else. Agent-building content always goes to Phase 5. Memory always goes to Phase 7. There is no such thing as "LangGraph's RAG phase" as a concept — LangGraph's RAG *implementation* is a track inside the RAG *phase*.
- **Sequencing matters, not just topic.** A phase's number should reflect what it depends on, not just its subject. This repo deliberately splits "RAG" into two phases (4 and 8) because agentic/self-correcting RAG depends on already knowing agents (Phase 5) — putting it in the same early phase as foundational RAG would put applied content before its prerequisite. When placing new content, ask what it depends on, and don't assume same-keyword content belongs together if the prerequisites differ.
- **Tracks vary in shape.** A framework track (like `LangChain_Fundamentals/`) might have its own internal numbered progression; a narrower topic (like `Memory_and_State/LangChain/`) might just be one folder of notebooks; a protocol track (like `MCP/`) might be `01_Foundations/02_Building_Servers/03_Building_Clients/04_Applications` instead of a learning arc. Check a track's existing `README.md`/contents before assuming its shape.
- **Most new frameworks are NOT new phases.** A first-party SDK goes in Phase 6's existing subfolders. A framework you'd pick up after the core path goes in Phase 10, "Alternative Agent Frameworks," as a new track. A protocol goes in Phase 9. Only propose a genuinely new phase when it's a new topic none of the 13 phases own — that should be rare at this point.

## Process

### 1. Diff disk state against `NOTEBOOK_INDEX.md`

Read `NOTEBOOK_INDEX.md` fully — it's the ground truth of what's already placed. Then list the actual folder tree (skip `.git`, `.venv`, `node_modules`, `__pycache__`, `.databricks`). Anything on disk not accounted for in the index is a candidate for organizing.

Also flag (but don't move) clearly *supporting* material — source PDFs feeding a notebook, a self-contained sub-module's own `README.md`/`requirements.txt`, config files. These stay put.

### 2. Classify each new item — topic first, then framework, then prerequisite

For each new item:
1. Identify its topic (RAG? agents? memory? observability? a specific framework's fundamentals?).
2. Look up which phase in `references/roadmap-map.md` owns that topic. If one exists, the item is a track (or goes inside an existing track) there — full stop, don't create anything new at the top level.
3. If the topic doesn't have a phase yet, check whether it's foundational or has a prerequisite that changes where it should sit (the Phase 4 vs Phase 8 RAG split is the reference example — copy that reasoning, don't just default to "put it near the similar-sounding existing phase").
4. Only if genuinely novel, propose a new phase — explain what topic it owns and why no existing phase covers it.

**A new source repo being merged in is the highest-risk moment for reintroducing duplication** — a repo is usually a whole course spanning multiple topics (its own "fundamentals," "RAG," "agents," "production" sections), and dumping it into one phase wholesale is the exact mistake that caused the last cleanup. Split it by topic across the phases that already own each topic instead, the same way `LangChain_Demystified`'s 12 modules got distributed across 6 different phases.

For naming/numbering within a track, match whatever convention that track already uses.

### 3. Check for a safety net before touching anything

Check whether `.git` exists and is a real repo (`git status`) before moving or renaming anything. If a repo exists, run `git status`, and prefer `git mv` over a plain filesystem move so history is preserved — though on Windows, a directory that's open in an editor or has a running dev-server process can throw "Permission denied"/"Device or resource busy" even for `git mv`. If that happens: individual file moves out of the "busy" directory usually still work even when renaming the directory itself doesn't — drain its contents one level at a time into the new location, then `rmdir` the emptied shell. **`Deep_Agents_and_Harness_Engineering/` (and its `app/` subfolder specifically) has hit this 3 times across different restructurings** — expect it, don't be surprised, just drain and move on.

### 4. Propose the plan, then wait for confirmation

Never move files or create phase/track folders speculatively — this repo has 130+ real notebooks/builds now. Present a concrete plan grouped by target phase/track: current path → proposed destination, and for any brand-new phase, why it's a genuinely new topic rather than belonging to one of the 13 existing ones. Only execute after the user confirms — they may accept some items and redirect others; apply per-item.

### 5. Execute, then update the index AND the roadmap map

- Update `NOTEBOOK_INDEX.md` — add rows/sections reflecting the new placement so it keeps matching actual disk state.
- **Update `references/roadmap-map.md`** — the skill's own memory of the roadmap's shape and reasoning. If a new phase or track was created, add an entry. If a "planned, no content yet" track just got its first real content, update its status. Keep this in sync every time the structure changes, same as the index.
- If a brand-new phase was created, it probably wants its own `README.md` — draft one if asked, don't assume.
- Note that `README.md`'s tables can lag `NOTEBOOK_INDEX.md` — ask if the user wants those reconciled too; don't rewrite `README.md` unprompted unless asked.
- Don't commit the changes yourself. Summarize what moved and let the user decide when to commit.

## What this skill is not for

- Don't reorganize `archive/` — intentionally frozen, retired material.
- Don't touch root scaffolding (`pyproject.toml`, `requirements.txt`, `uv.lock`, `databricks.yml`, `helpers/`, `LICENSE`) unless the user is specifically asking about dependency/package structure, not roadmap content. Note `pyproject.toml`'s `[tool.ruff] extend-exclude` hardcodes 3 JS frontend paths — add a 4th if another JS app shows up.
- Don't silently merge or delete a merged-in repo's own reusable tooling (e.g. its own `.claude/skills/`) — stage it at `.claude/skills-candidates/` for the user's separate review, same as was done for `format-notebook` and `virtual-env-setup`.
- Don't edit notebook/file *content* — only placement and the index/map docs.
