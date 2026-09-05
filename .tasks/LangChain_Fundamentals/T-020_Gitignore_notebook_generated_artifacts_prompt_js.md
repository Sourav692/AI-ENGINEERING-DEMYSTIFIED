---
id: T-020
title: Gitignore notebook-generated artifacts (prompt.json / prompt.yaml)
type: migration
status: todo
review: pending
review_rounds: 0
wave: 5
effort: S
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/prompt.json, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/prompt.yaml, .gitignore]
rules: []
depends_on: []
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [ ] **Gitignore notebook-generated artifacts (prompt.json / prompt.yaml)** — `todo` · review: ⏳ pending

## Objective

prompt.json and prompt.yaml are notebook-generated artifacts COMMITTED to the repo (in dad1931) and absent from .gitignore, so anyone running 2.2 gets spurious diffs. Two parts: add a .gitignore rule, and decide whether to git rm the two tracked files. prompt.yaml is now ORPHANED - after T-018 no cell writes YAML, because dumps is JSON-only. Deleting tracked files is destructive so it needs a human yes; the .gitignore line alone does not untrack them.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/prompt.json`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/prompt.yaml`
- `.gitignore`

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
