---
id: T-011
title: Rewrite PipelinePromptTemplate section (class removed from ecosystem)
type: migration
status: todo
review: pending
review_rounds: 0
wave: 4
effort: M
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.2_Prompt_Templates.ipynb]
rules: [IMP-prompts]
depends_on: []
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [ ] **Rewrite PipelinePromptTemplate section (class removed from ecosystem)** — `todo` · review: ⏳ pending

## Objective

Cell 20 teaches composable prompts without PipelinePromptTemplate, which no longer exists in langchain_core, langchain_classic, or anywhere in site-packages. Needs a conceptual replacement (PromptTemplate composition / ChatPromptTemplate assembly), not an import repoint.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.2_Prompt_Templates.ipynb`

Findings this task closes: `IMP-prompts`

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for `IMP-prompts`
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified
- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_
