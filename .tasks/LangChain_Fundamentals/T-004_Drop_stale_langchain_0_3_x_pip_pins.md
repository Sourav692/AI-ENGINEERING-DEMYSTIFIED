---
id: T-004
title: Drop stale langchain 0.3.x pip pins
type: migration
status: done
review: approved
review_rounds: 2
wave: 1
effort: S
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/01_Getting_Started/1.2_Commercial_LLMs_with_LangChain.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.3_LLM_vs_ChatModel.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.4_PromptTemplate_with_LangChain.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.6_LangChain_LLM_Input_Output_Comprehensive.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.0_LCEL_Essentials.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.1_LCEL_Introduction.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.3_Branching_Routing_Merging_Chains.ipynb]
rules: [MSC-pip-pin, MSC-pip-install]
depends_on: []
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Drop stale langchain 0.3.x pip pins** — `done` · review: ✓ approved · round 2

## Objective

No notebook instructs a learner to install langchain 0.3.x.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/01_Getting_Started/1.2_Commercial_LLMs_with_LangChain.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.3_LLM_vs_ChatModel.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.4_PromptTemplate_with_LangChain.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.6_LangChain_LLM_Input_Output_Comprehensive.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.0_LCEL_Essentials.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.1_LCEL_Introduction.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/04_Chains/4.3_Branching_Routing_Merging_Chains.ipynb`

Findings this task closes: `MSC-pip-pin`, `MSC-pip-install`

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for `MSC-pip-pin`, `MSC-pip-install`
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified
- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: 13 commented langchain pins had their ==version stripped (package name and the notebook's own per-package explanation preserved). NON-LANGCHAIN pins deliberately left alone (openai, transformers, groq, huggingface_hub, google-generativeai) - those may be intentional and are outside this task's rule. SCOPE ESCALATION: 3.0 cell 0 and 4.3 cell 2 were not stale comments but LIVE uncommented '!pip install langchain==0.3.10/0.3.11' cells - running either would DOWNGRADE the venv and break the whole track. Both replaced with a commented install cell pointing at the repo's central 'uv pip install -r requirements.txt', per format rule 8. Rescan: MSC-pip-pin 0, MSC-pip-install 0.

- 2026-09-05: review r1: CHANGES_REQUESTED, 2 blockers + 4 nits. BLOCKERS (both fixed): the two replaced install cells kept their pre-edit pip OUTPUTS, so 3.0 and 4.3 still rendered a 'langchain==0.3.11' install log directly under a comment saying never to pin 0.3.x - an all-comment cell can emit no output, so the retained output was factually impossible. 4.3 also leaked an absolute macOS path from another machine. Cleared outputs + execution_count on both. NITS fixed: trailing newline in both replacement cells; 4.3's markdown heading reworded from 'Install OpenAI, and LangChain dependencies' to 'Environment: dependencies are installed centrally'; and the surviving non-langchain pins were stripped in the 5 already-edited notebooks after verifying openai==1.55.3 is ACTIVELY incompatible (langchain-openai 1.6.0 requires openai>=2.45.0,<4.0.0; repo pins openai==2.54.0) - same hazard class as the langchain pins. Pins in 1.1/1.3 left alone: T-004 never edited those files.

- 2026-09-05: review r2: APPROVED - all six gates, both blockers and all four round-1 nits verified landed. Reviewer confirmed: outputs=[] and execution_count=null on 3.0 c0 and 4.3 c2, the 0.3.11 log and macOS path both gone; zero occurrences of a pip-context '0.3.1' across all 28 notebooks; zero live uncommented pip lines anywhere; regex collateral checked line-by-line (every pin change is on a commented pip line); cell counts identical to HEAD in all 7 files; indent preserved per-file; no CRLF; static_check clean. 5 nits: 3 ACTED ON (T-012 opened for the 1.1/1.3 pins the reviewer called an arbitrary hazard boundary - its exact words: do not silently leave the track half-stripped; T-013 opened for the personal-path leak in the unedited 1.0; T-004 targets frontmatter populated with all 7 files). 1 FIXED (3.1 cell 11 now names the langchain-classic move, as a repoint disposition requires). 1 was the stale INDEX render, fixed by regenerating.
