---
id: T-005
title: Rewrite summarization off load_summarize_chain
type: migration
status: in-progress
review: pending
review_rounds: 0
wave: 4
effort: L
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/8.0_Summarization_Essentials.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/8.1_Text_Summarization.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/app.py]
rules: [CHN-loaders, CHN-llmchain]
depends_on: [T-002]
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [~] **Rewrite summarization off load_summarize_chain** — `in-progress` · review: ⏳ pending

## Objective

Summarization taught with LCEL and an explicit map-reduce, not legacy chain loaders.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/8.0_Summarization_Essentials.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/8.1_Text_Summarization.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/app.py`

Findings this task closes: `CHN-loaders`, `CHN-llmchain`

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for `CHN-loaders`, `CHN-llmchain`
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified
- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: From T-013 review r1 (nit): clearing 8.1 cell 15's outputs removed the only place in the notebook showing the verbatim LangChainDeprecationWarning text for LLMChain and Chain.run - exactly the string a learner would paste into a search box. When this task rewrites that cell to 'prompt | llm', quote BOTH deprecation strings verbatim in the accompanying markdown so the searchable text survives the output clear. Also in scope for this task: 8.1 cell 9 'response = llm(chat_message)' raises TypeError on 1.x (BaseChatModel.__call__ removed) - use llm.invoke(...).
