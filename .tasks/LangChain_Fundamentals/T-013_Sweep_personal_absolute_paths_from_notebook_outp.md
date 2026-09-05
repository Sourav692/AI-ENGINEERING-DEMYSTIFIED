---
id: T-013
title: Sweep personal absolute paths from notebook outputs
type: migration
status: in-review
review: pending
review_rounds: 0
wave: 5
effort: S
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/01_Getting_Started/1.0_LangChain_Introduction.ipynb]
rules: []
depends_on: []
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [?] **Sweep personal absolute paths from notebook outputs** — `in-review` · review: ⏳ pending

## Objective

No committed notebook output contains a personal filesystem path. One survivor found in 1.0 during T-004 review r2; the 4.3 leak was already fixed. Worth a folder-wide grep, not just this file.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/01_Getting_Started/1.0_LangChain_Introduction.ipynb`

Findings this task closes: _n/a_

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for _n/a_
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified
- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: Folder-wide sweep, not just the one file the review named. Found THREE leaks, not two: 1.0 cells 6 and 8 (as reported) plus 8.1 cell 15, which my earlier shell grep missed because its regex was mangled by escaping. All were in OUTPUTS (error tracebacks), none in source, so the fix is clearing outputs + execution_count - consistent with format rule 7 and with the T-004 r2 blocker fix. Script also reports any personal path found in SOURCE without touching it, since that would need a human decision; none found. Verified 0 personal paths remain anywhere in the folder.
