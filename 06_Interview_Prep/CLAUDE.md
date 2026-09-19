<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 14 — Interview Preparation

**Owns:** interview preparation. Created 2026-09-19 by collapsing four top-level phases plus `tutorials/` into one phase with five tracks.

| Track | Was | Content |
|---|---|---|
| `Handbook/` | `14_AI_Engineering_Handbook/` | 12-chapter written handbook |
| `FDE/` | `15_FDE_Related_Preparation/` | ⚠ Purchased GenAI FDE interview system, system-design scenarios, behavioural/leadership, STAR stories |
| `AI_Engineer/` | `16_AI_Engineer_Interview_Preparation/` | Cross-cutting prep + delivery framework |
| `OpenAI_Applied/` | `17_OpenAI_Applied_Engineer_Preparation/` | Coverage/gap analysis + sample questions |
| `Study_Guides/` | `tutorials/` | Per-phase interview study guides, Cost & Latency cram sheets + drill deck, chunking/retrieval notes |

## ⚠ Licensing — read before touching `FDE/`

This track contains **third-party commercial material**. `.gitignore` lines ~160–162 ignore everything under `FDE/Complete GEN AI FDE Interview System — Core + GenAI/` **except** `.md` files.

**Those patterns are path-anchored.** If this folder ever moves, repoint them in the same commit — when they broke during the 2026-09-19 restructure, 107 purchased vendor PDFs silently became committable. Verify after any move:

```bash
git status --porcelain | grep -c '^??'   # expect 0
git ls-files '06_Interview_Prep/FDE' | grep -c '\.md$'   # expect 122
```

`site/scripts/sync-content.mjs` also reads `SOURCE_ROOT = '06_Interview_Prep/FDE'` — the public site builds from this track.

## Conventions here

- **`Handbook/` is kept whole deliberately.** Its chapters re-cover RAG, agents, multi-agent and AgentOps, so it looks like duplication of Phases 4/5/7/12 — but it is prose, not notebooks, and splitting a book across five phases destroys it. Same precedent as `Comprehensive_RAG_Techniques/`.
- Skills that target this phase: `fde-case-study-worksheet-v3`, `fde-tutorial-interview-format`, `interview-book-tutorial-builder`, `notebook-interview-tutorial`.

## Open issue

- `Handbook/11_Telling_The_Story/stories/` and `FDE/Star_Stories/` hold 9 byte-identical STAR story files; the same set also exists in `Agent_Evaluation_Demystified/Star_Stories/`. Unresolved.
