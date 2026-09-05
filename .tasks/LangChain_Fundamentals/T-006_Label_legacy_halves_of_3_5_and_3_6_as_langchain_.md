---
id: T-006
title: Label legacy halves of 3.5 and 3.6 as langchain-classic
type: migration
status: in-review
review: pending
review_rounds: 0
wave: 4
effort: M
disposition: repoint
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.5_Chain_Migrations.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.6_Chain_Migration_Advanced.ipynb]
rules: [CHN-llmchain, CHN-retrieval]
depends_on: [T-002]
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [?] **Label legacy halves of 3.5 and 3.6 as langchain-classic** — `in-review` · review: ⏳ pending

## Objective

The before/after lessons still run, with the before side clearly marked legacy.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.5_Chain_Migrations.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.6_Chain_Migration_Advanced.ipynb`

Findings this task closes: `CHN-llmchain`, `CHN-retrieval`

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for `CHN-llmchain`, `CHN-retrieval`
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified
- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: 3.5: replaced the four bare section headings ('### Legacy Chains', '### LCEL', '### Legacy RAG', '### LCEL') with labelled versions explaining that LLMChain/RetrievalQA/hub are RETIRED and live in langchain-classic, that they are shown deliberately as the 'before' half, and that LCEL is not deprecated. 3.6: inserted two markdown cells (16 -> 18 cells) - one labelling the ConversationalRetrievalChain section as legacy, one marking where the LCEL rewrite begins; it previously had almost no narrative at all. SELF-CHECK CAUGHT ONE MORE: 3.5 cell 10 sits under the 'LCEL - the 1.x way' heading but imports 'from langchain_classic import hub'. A learner would read that as a contradiction. Cell 9 now explains it: the CHAIN is fully LCEL, only the prompt hub moved to classic, and inlining the prompt with ChatPromptTemplate drops the dependency (and the network call).
