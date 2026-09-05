---
id: T-002
title: Repoint legacy chain imports to langchain-classic
type: migration
status: done
review: approved
review_rounds: 1
wave: 1
effort: M
disposition: repoint
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.0_Basics_of_Chains.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.1_Chains_Basics_and_OutputParsers.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.2_Advanced_Chains.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.3_Branching_Routing_Merging_Chains.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.5_Chain_Migrations.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.6_Chain_Migration_Advanced.ipynb]
rules: [IMP-chains, IMP-hub]
depends_on: [T-001]
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Repoint legacy chain imports to langchain-classic** — `done` · review: ✓ approved · round 1

## Objective

The six repoint notebooks import and run on 1.x without changing what they teach.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.0_Basics_of_Chains.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.1_Chains_Basics_and_OutputParsers.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.2_Advanced_Chains.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.3_Branching_Routing_Merging_Chains.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.5_Chain_Migrations.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.6_Chain_Migration_Advanced.ipynb`

Findings this task closes: `IMP-chains`, `IMP-hub`

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for `IMP-chains`, `IMP-hub`
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified
- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: Applied 16 import rewrites across 6 notebooks (11 cells). All 12 target symbols verified present in langchain_classic 1.0.8 BEFORE editing (chains.LLMChain/SimpleSequentialChain/RetrievalQA/ConversationalRetrievalChain/OpenAIModerationChain, chains.llm, chains.sequential, chains.router.MultiPromptChain, chains.router.llm_router.LLMRouterChain+RouterOutputParser, chains.router.multi_prompt_prompt.MULTI_PROMPT_ROUTER_TEMPLATE, hub). Re-scan confirms ZERO IMP-chains/IMP-hub left in the six target files. METHOD DEVIATION: used a scripted json round-trip rather than 11 NotebookEdit calls - cells carry no ids, and the change is a provable prefix swap on import lines only. Verified cell counts unchanged per file and diff limited to import lines. SIDE EFFECT: the round-trip collapsed duplicate 'output_type' keys that existed in some saved outputs (invalid JSON, last-wins); benign but outside task scope.

- 2026-09-05: review r1: APPROVED. All 12 symbols verified in langchain_classic 1.0.8 by reading .venv source + import probe. Zero IMP-chains/IMP-hub in the six target files. Collateral damage check: cell counts identical (12/11/13/58/11/16), cell-type sequences identical, top-level metadata byte-identical, all six pass nbformat.validate; diff is exactly 16 insertions/18 deletions, the 2-line surplus being precisely the two disclosed duplicate output_type keys in 4.0 (identical values, so nothing rendered changes - the JSON is now strictly better-formed). Narrative consistency: grepped all markdown + non-import code for the old paths, zero hits. NON-OBVIOUS FINDING recorded in the rewrite map: 'from langchain_classic import hub' works via CPython's IMPORT_FROM submodule fallback, NOT via export - langchain_classic.__init__ has a __getattr__ that raises AttributeError for 'hub'. So attribute access after a bare 'import langchain_classic' fails. The rewritten lines use the working form. 2 nits, both explicit deferrals (T-003 sibling imports, T-006 legacy labelling) - no action.
