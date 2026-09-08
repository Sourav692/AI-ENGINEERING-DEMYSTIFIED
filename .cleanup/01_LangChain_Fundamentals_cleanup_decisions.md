---
plan: 01_LangChain_Fundamentals_cleanup_plan.md
slug: 01_LangChain_Fundamentals
decided: 2026-09-07
round: 1
scope: per-id
---

# Decisions — `01_LangChain_Fundamentals`

Approved removing NB-014 only; every other ID in the plan is unruled and stays untouched per
the plan's own "no decision = safe side" default.

## Round 1 — 2026-09-07

| ID | Decision | Note |
| --- | --- | --- |
| DUP-001 | approve | User: "remove NB-014 for Langchain_fundamentals" — approves the plan's consolidate→retire for NB-014 (`2.6_LangChain_LLM_Input_Output_Comprehensive.ipynb`): port the `HuggingFacePipeline` local-inference walkthrough and the raw `InferenceClient` streaming example into NB-011 (`2.3_LLM_vs_ChatModel.ipynb`), then retire NB-014 |

## Round 2 — 2026-09-07

User: "Proceed with FMT" — approves the formatting pass, minus items blocked on an
unanswered open question or requiring notebook execution.

| ID | Decision | Note |
| --- | --- | --- |
| FMT-001 | approve | |
| FMT-002 | approve | |
| FMT-003 | approve | |
| FMT-004 | approve | |
| FMT-005 | approve | |
| FMT-006 | approve | |
| FMT-007 | approve | |
| FMT-008 | reject | Moot — notebook already retired per DUP-001 |
| FMT-009 | approve | |
| FMT-010 | approve | |
| FMT-011 | defer | Blocked on Q-002 (unanswered) — legacy-API labelling convention |
| FMT-012 | defer | Blocked on Q-002 (unanswered) |
| FMT-013 | approve (partial) | Title/Summary cell only — the legacy-label half stays deferred with Q-002 |
| FMT-014 | approve (partial) | Same split as FMT-013 |
| FMT-015 | approve (partial) | Same split as FMT-013 |
| FMT-016 | approve | |
| FMT-017 | approve | |
| FMT-018 | defer | Requires actually re-running the notebook top to bottom (API calls/kernel execution) — out of scope for a static formatting pass; user should re-run manually |

## Round 3 — 2026-09-07

| ID | Decision | Note |
| --- | --- | --- |
| Q-001 | defer | User confirmed the framing is accurate (restated it back verbatim, including that it's `ai-roadmap-organizer`'s call) but did not choose replace/merge/sit-alongside. The actual placement decision is still open — belongs to `ai-roadmap-organizer`, not this cleanup. Not resolved; carries forward. |

## Round 4 — 2026-09-07

| ID | Decision | Note |
| --- | --- | --- |
| Q-001 | answered (moot) | User: "Ok for Q001 replace this folder with the older folder", clarified to: keep `01_LangChain_Fundamentals`, retire the older track. On handoff to `ai-roadmap-organizer`, discovered the premise was stale: `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/` no longer exists on disk. The repo's top-level phase structure was renumbered 0-16 (00_Theory_and_Foundations, 01_LangChain_Fundamentals, `02. Prompt_and_Context_Engineering`, ... 16_AI_Engineer_Interview_Preparation) in commit `30ddca0` — `01_LangChain_Fundamentals` is already the current Phase 1 folder. User confirmed this renumbering is the intended, final structure. No move/retirement needed; question resolved by the fact that it was already done. `CLAUDE.md`/`NOTEBOOK_INDEX.md` are now stale relative to disk and need a separate refresh (not part of this cleanup). |

## Round 5 — 2026-09-07

| ID | Decision | Note |
| --- | --- | --- |
| Q-003 | answered | User: "Ok so rename the folder to Legacy_Chains and keep 4.0 to 4.2 and move the 4.3 to LCEL folder and rename and number that appropriately" — `04_Chains/` renamed to `04_Legacy_Chains/` (keeps `4.0`-`4.2`); `4.3_Branching_Routing_Merging_Chains.ipynb` moved to `03_LCEL/3.7_Branching_Routing_Merging_Chains.ipynb`. Executed via `git mv`; cross-references fixed in `1.8_Package_Split_and_Imports_LangChain_v1.ipynb`, `3.4_LCEL_and_Runnables.ipynb`, `4.2_Advanced_Chains.ipynb`. |

## Round 6 — 2026-09-07

| ID | Decision | Note |
| --- | --- | --- |
| MIG-001 | reject | User: "handle the mig items" — investigated before applying. The cited `create_stuff_documents_chain` import does not exist anywhere in the target notebook; nothing to migrate. Marked invalid in the plan, no edit made. |
| MIG-002 | reject | Same investigation. Every `config["configurable"]["thread_id"]` occurrence is the checkpointer's own correct, current usage — not app-level context needing `context=`/`Runtime[ContextSchema]`. Marked invalid in the plan, no edit made. |

## Round 7 — 2026-09-07

| ID | Decision | Note |
| --- | --- | --- |
| FMT-018 | approve | User: "Proceed with 018 by running the notebook" — re-executed `7.5_Middleware.ipynb` top to bottom via `jupyter nbconvert --execute`. Monotonic execution counts, zero errors. Applied. |

## Round 8 — 2026-09-07

| ID | Decision | Note |
| --- | --- | --- |
| Q-002 | answered | User chose "Plain markdown note" over stretching the existing `langchain-0x-contrast` tag or introducing a new tag, after being shown that the existing tag's semantics (broken/raises-exception, contrast-only) don't match this content (which runs fine via `langchain_classic`, just on a retired API). |
| FMT-011 | approve | Applied per Q-002's answer — note added to `3.5_Chain_Migrations.ipynb` |
| FMT-012 | approve | Applied per Q-002's answer — note added to `3.6_Chain_Migration_Advanced.ipynb` |

Also applied the same note to `4.0`, `4.1`, `4.2` (`03_Legacy_Chains/`) per Q-002, though
those weren't separately-numbered FMT rows (their title/summary formatting was FMT-013/014/015,
already applied in round 7's FMT pass).

## Additional instructions

None.
