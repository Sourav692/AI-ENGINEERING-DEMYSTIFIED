---
id: T-003
title: Fix moved core imports (schema, text_splitter, llms, parsers)
type: migration
status: done
review: approved
review_rounds: 1
wave: 1
effort: S
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.1_LCEL_Introduction.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.2_Runnables.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.4_LCEL_and_Runnables.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.6_LangChain_LLM_Input_Output_Comprehensive.ipynb]
rules: [IMP-schema, IMP-textsplitter, IMP-llms, IMP-parsers]
depends_on: []
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Fix moved core imports (schema, text_splitter, llms, parsers)** — `done` · review: ✓ approved · round 1

## Objective

No import resolves through a path that 1.x removed.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.1_LCEL_Introduction.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.2_Runnables.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.4_LCEL_and_Runnables.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.6_LangChain_LLM_Input_Output_Comprehensive.ipynb`

Findings this task closes: `IMP-schema`, `IMP-textsplitter`, `IMP-llms`, `IMP-parsers`

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for `IMP-schema`, `IMP-textsplitter`, `IMP-llms`, `IMP-parsers`
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified
- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: Applied with T-009 in a single editing pass (they touched overlapping cells - e.g. 4.0 cell 3 has langchain.llms and langchain.prompts on adjacent lines - so splitting them would have meant editing the same cells twice). 27 lines changed across 13 files. Scope note: the ORIGINAL target list named 4 files; the true span was 14, because the first scan predated the IMP-prompts rule and because the scanner dedupes identical lines so it under-reported repeats (4.0 had 4 hits, not 2). All destinations verified in .venv BEFORE editing. Rescan: IMP-schema/textsplitter/llms/parsers all ZERO.

- 2026-09-05: review r1: APPROVED - all six gates. Reviewer resolved every destination symbol against the installed packages; content-routing of langchain.schema correct in ALL cases (Document -> langchain_core.documents in 3.4/3.5/3.6, message classes -> langchain_core.messages in 2.6/8.1); ZERO mis-routed lines. Structural comparison vs HEAD: cell counts identical across all 13, metadata/outputs/execution_counts untouched. Duplicate output_type collapse confirmed LOSSLESS (4.0: 4 keys->2, 8.0: 10->5, every pair had identical values - repaired invalid JSON). Explainer 1.8 confirmed untouched, contrast tags intact. Independently confirmed PipelinePromptTemplate absent from ALL of site-packages, justifying the T-011 deferral. 3 nits: 2 cosmetic serialization issues FIXED post-approval (three notebooks were reserialized at indent=1 when git had indent=2, turning 4 edits into ~15.7k changed lines; and json.dump emitted CRLF on all 13). Repaired: diff went 15831 -> 101 lines, all 28 notebooks still valid nbformat, scanner counts unchanged. Root-cause guidance added to notebook-folder-cleanup SKILL.md. 3rd nit is T-011's to handle (add a warning callout above cell 20).
