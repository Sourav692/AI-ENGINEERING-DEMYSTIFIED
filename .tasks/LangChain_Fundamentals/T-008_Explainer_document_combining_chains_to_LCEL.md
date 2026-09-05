---
id: T-008
title: Explainer: document-combining chains to LCEL
type: explainer
status: done
review: approved
review_rounds: 2
wave: 5
effort: M
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: []
rules: [CHN-loaders]
depends_on: [T-005]
output: 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/8.2_Doc_Chains_to_LCEL_LangChain_v1.ipynb
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Explainer: document-combining chains to LCEL** — `done` · review: ✓ approved · round 2

## Objective

A learner can replace stuff/map_reduce/refine loaders with LCEL or a map-reduce graph.

## Scope

Files in scope:

- _(none listed — fill in)_

Findings this task closes: `CHN-loaders`

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for `CHN-loaders`
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified
- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: Drafted in markdown, converted with md_to_notebook (23 cells: 6 code, 17 markdown; format check clean on first write). Wired into NOTEBOOK_INDEX.md (2 nb -> 3 nb) and the track README. VERIFIED BEFORE DRAFTING, not from memory: load_summarize_chain resolves in langchain_classic.chains.summarize; Document/StrOutputParser/ChatPromptTemplate/ChatOpenAI all resolve; Runnable.batch and .with_retry exist. CENTRAL TEACHING POINT was discovered by experiment rather than assumed - I constructed the legacy chain in a fresh process with -W always and captured ZERO deprecation warnings, even though load_summarize_chain returns a StuffDocumentsChain carrying @deprecated(since=0.2.13, removal=2.0.0). The loader hides the deprecation entirely; the only warning a learner ever sees is about .run(), and it arrives at call time. That silence is why the API persists, and the notebook makes it the subject of its own runnable audit cell rather than a claim. Also uses the verbatim Chain.run warning text captured earlier in this session. Contrast cell tagged langchain-0x-contrast so the scanner and future bulk-edit passes skip it. Own checks: static_check clean, AST name-resolution pass shows zero forward references.

- 2026-09-05: review r1: CHANGES_REQUESTED, 1 blocker + 3 nits, all fixed. BLOCKER: my contrast callout said the legacy snippet 'Runs on LangChain 1.x only if langchain-classic is installed' - false, and it contradicted the notebook's OWN cells 6 and 20, which correctly say the import raises. Verified: langchain.chains.summarize raises ModuleNotFoundError with classic 1.0.8 installed. Replaced with the blueprint's mandated wording. NITS: stray f-string with no placeholder (F541) that also hardcoded the very fact the cell claims to audit - now reads type(chain).__deprecated__ off the class so the cell proves itself; emoji outside the documented set; and prerequisites citing langchain>=1.2.7 when pyproject's actual floors are 1.4.0 / core 1.6.1 / classic 1.0.8. REVIEWER DISCREPANCY WORTH NOTING: it reported __deprecated__ returns a string containing '0.2.13' and the removal version; on this venv it returns only 'Use langchain.agents.create_agent instead.' I used it accurately rather than as quoted, and moved the version facts into markdown prose where they are narrative rather than a fake audit result. Everything else passed - the reviewer independently reproduced the zero-warnings claim for all three chain_type values.

- 2026-09-05: review r2: APPROVED - all six gates, both round-1 nits closed. The reviewer independently verified StuffDocumentsChain.__deprecated__ returns ONLY 'Use langchain.agents.create_agent instead.' - confirming my reading and overturning round 1's, which had claimed it contains the version numbers. The version facts now live in markdown prose attributed to the source decorator, not fabricated into the audit print. It also reproduced the zero-warnings result for all three chain_type values, and flagged a fact worth not generalising: `since` is NOT uniform - stuff is 0.2.13 while map_reduce and refine are 0.3.1. This notebook only builds stuff, so it is accurate as written. LINE ENDINGS: 8.2 shipped CRLF, which was a bug in md_to_notebook.py itself (platform-default newline), so EVERY explainer it generates carried it - 1.8 had 351. Fixed the generator with newline='' and re-serialized both; 1.8 verified byte-identical apart from line endings. All 29 notebooks in the folder are now LF.
