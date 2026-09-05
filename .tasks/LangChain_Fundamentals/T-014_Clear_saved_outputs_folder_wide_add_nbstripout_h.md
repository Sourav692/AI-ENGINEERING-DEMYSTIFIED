---
id: T-014
title: Clear saved outputs folder-wide + add nbstripout hook
type: migration
status: todo
review: pending
review_rounds: 0
wave: 5
effort: M
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: []
rules: []
depends_on: [T-005, T-011]
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [ ] **Clear saved outputs folder-wide + add nbstripout hook** — `todo` · review: ⏳ pending

## Objective

No committed notebook carries saved outputs (format rule 7). 16 notebooks / 198 code cells as measured 2026-09-05. MUST run AFTER T-005 and T-011, which rewrite cells whose outputs would be cleared anyway. Pair with an nbstripout pre-commit hook - a one-time clear leaves the leak class free to recur, which is how the personal-path leaks in T-013 got committed in the first place.

## Scope

Files in scope:

- _(none listed — fill in)_

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
