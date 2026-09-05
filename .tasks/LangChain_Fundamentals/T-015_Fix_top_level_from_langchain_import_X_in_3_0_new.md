---
id: T-015
title: Fix top-level 'from langchain import X' in 3.0 (new scanner rule)
type: migration
status: done
review: approved
review_rounds: 1
wave: 1
effort: S
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.0_LCEL_Essentials.ipynb]
rules: [IMP-toplevel]
depends_on: []
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Fix top-level 'from langchain import X' in 3.0 (new scanner rule)** — `done` · review: ✓ approved · round 1

## Objective

3.0 cell 3 does 'from langchain import PromptTemplate', which raises ImportError on 1.x (langchain/__init__.py exports essentially nothing). Repoint to langchain_core.prompts. Found only after adding the IMP-toplevel rule during T-005 prep - 3.0 had been reported clean apart from pip pins through four prior scans.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.0_LCEL_Essentials.ipynb`

Findings this task closes: `IMP-toplevel`

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for `IMP-toplevel`
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified
- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: 3.0 cell 3: 'from langchain import PromptTemplate' -> langchain_core.prompts. One line. Verified IMP-toplevel now 0 folder-wide.

- 2026-09-05: review r1: APPROVED as part of the T-005+T-015 review. One-liner confirmed correct and complete; IMP-toplevel now 0 folder-wide.
