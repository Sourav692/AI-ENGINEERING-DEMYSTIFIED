---
id: T-009
title: Fix langchain.prompts imports (scanner blind spot)
type: migration
status: done
review: approved
review_rounds: 1
wave: 1
effort: S
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.2_Prompt_Templates.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.4_PromptTemplate_with_LangChain.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.6_Chain_Migration_Advanced.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.0_Basics_of_Chains.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.1_Chains_Basics_and_OutputParsers.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.2_Advanced_Chains.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/8.0_Summarization_Essentials.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/app.py]
rules: [IMP-prompts]
depends_on: []
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Fix langchain.prompts imports (scanner blind spot)** — `done` · review: ✓ approved · round 1

## Objective

No file imports from langchain.prompts; all use langchain_core.prompts.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.2_Prompt_Templates.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.4_PromptTemplate_with_LangChain.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.6_Chain_Migration_Advanced.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.0_Basics_of_Chains.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.1_Chains_Basics_and_OutputParsers.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.2_Advanced_Chains.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/8.0_Summarization_Essentials.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/app.py`

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

- 2026-09-05: Applied together with T-003, same pass. IMP-prompts went 12 -> 1; the single remainder is PipelinePromptTemplate, deliberately skipped and boarded as T-011 because the class was REMOVED from the ecosystem entirely (absent from langchain_core.prompts, langchain_classic, and all of site-packages) - that is a conceptual rewrite, not a repoint. Two dry-run bugs caught before applying: (1) the schema regex ate the space, producing 'importDocument'; (2) the script was about to rewrite the deliberate 0.x contrast cell in the 1.8 explainer - now skips cells tagged langchain-0x-contrast.

- 2026-09-05: review r1: APPROVED - all six gates. Reviewer resolved every destination symbol against the installed packages; content-routing of langchain.schema correct in ALL cases (Document -> langchain_core.documents in 3.4/3.5/3.6, message classes -> langchain_core.messages in 2.6/8.1); ZERO mis-routed lines. Structural comparison vs HEAD: cell counts identical across all 13, metadata/outputs/execution_counts untouched. Duplicate output_type collapse confirmed LOSSLESS (4.0: 4 keys->2, 8.0: 10->5, every pair had identical values - repaired invalid JSON). Explainer 1.8 confirmed untouched, contrast tags intact. Independently confirmed PipelinePromptTemplate absent from ALL of site-packages, justifying the T-011 deferral. 3 nits: 2 cosmetic serialization issues FIXED post-approval (three notebooks were reserialized at indent=1 when git had indent=2, turning 4 edits into ~15.7k changed lines; and json.dump emitted CRLF on all 13). Repaired: diff went 15831 -> 101 lines, all 28 notebooks still valid nbformat, scanner counts unchanged. Root-cause guidance added to notebook-folder-cleanup SKILL.md. 3rd nit is T-011's to handle (add a warning callout above cell 20).
