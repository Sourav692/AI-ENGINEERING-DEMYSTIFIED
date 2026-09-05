---
id: T-010
title: Assign orphaned IMP-chains hits in 3.1_LCEL_Introduction
type: migration
status: done
review: approved
review_rounds: 2
wave: 1
effort: S
disposition: repoint
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.1_LCEL_Introduction.ipynb]
rules: [IMP-chains]
depends_on: []
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Assign orphaned IMP-chains hits in 3.1_LCEL_Introduction** — `done` · review: ✓ approved · round 2

## Objective

create_sql_query_chain import repointed; this hit belonged to no task on the original board.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.1_LCEL_Introduction.ipynb`

Findings this task closes: `IMP-chains`

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for `IMP-chains`
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified
- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: 3.1_LCEL_Introduction cell 12: 'from langchain.chains import create_sql_query_chain' -> langchain_classic. Verified present at langchain_classic.chains.create_sql_query_chain AND langchain_classic.chains.sql_database.query.create_sql_query_chain before editing. This hit belonged to no task on the original board - it surfaced only because T-002's completeness check listed leftover IMP-chains by file.

- 2026-09-05: review r1: frontmatter said disposition=rewrite but the work is a repoint (and the Objective says so). Corrected to repoint.

- 2026-09-05: review r2: APPROVED - all six gates, both blockers and all four round-1 nits verified landed. Reviewer confirmed: outputs=[] and execution_count=null on 3.0 c0 and 4.3 c2, the 0.3.11 log and macOS path both gone; zero occurrences of a pip-context '0.3.1' across all 28 notebooks; zero live uncommented pip lines anywhere; regex collateral checked line-by-line (every pin change is on a commented pip line); cell counts identical to HEAD in all 7 files; indent preserved per-file; no CRLF; static_check clean. 5 nits: 3 ACTED ON (T-012 opened for the 1.1/1.3 pins the reviewer called an arbitrary hazard boundary - its exact words: do not silently leave the track half-stripped; T-013 opened for the personal-path leak in the unedited 1.0; T-004 targets frontmatter populated with all 7 files). 1 FIXED (3.1 cell 11 now names the langchain-classic move, as a repoint disposition requires). 1 was the stale INDEX render, fixed by regenerating.
