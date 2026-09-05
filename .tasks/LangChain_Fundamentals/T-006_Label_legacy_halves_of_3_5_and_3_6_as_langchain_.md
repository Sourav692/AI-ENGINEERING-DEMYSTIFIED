---
id: T-006
title: Label legacy halves of 3.5 and 3.6 as langchain-classic
type: migration
status: blocked
review: changes-requested
review_rounds: 2
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
- [!] **Label legacy halves of 3.5 and 3.6 as langchain-classic** — `blocked` · review: ✗ changes requested · round 2

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

- 2026-09-05: review r2: 2 BLOCKERS, both fixed. (1) My hub explanation was WRONG in the direction I asked the reviewer to check. I said hub.pull 'still goes through langchain-classic', implying it is the supported 1.x route. Verified myself against .venv: langchain_classic/hub.py decorates BOTH pull and push with @deprecated(since=1.0.6, removal=2.0.0, 'Use the LangSmith SDK instead') and each body is a 2-line delegation to langsmith.Client.pull_prompt/push_prompt. langsmith==0.12.1 is already pinned. Cell 9 now says plainly that the hub.pull line is NOT the 1.x way, gives Client().pull_prompt() as the native path, keeps inlining as the offline option, and surfaces hub.pull's own docstring warning that hub manifests are untrusted executable config. Cell 6 amended from 'moved with it' to 'reduced to a deprecated shim'. (2) 3.6's 'LCEL rewrite begins here' marker sat at index 8, three cells AFTER the rewrite actually starts - cells 5-7 build rephrase_chain in pure LCEL, so they were stranded under the Legacy heading and the marker's own text was falsified by the code above it. Moved to index 5, immediately after the legacy cell; 18 cells preserved. NITS fixed: legacy labels now name BOTH deprecations (retired class AND chain(...) vs chain.invoke(...)); 3.5 cell 5 reuses the bound llm instead of constructing a second inline ChatOpenAI. Formatting nit boarded as T-016.

- 2026-09-05: review r3: blockers 1+3 confirmed fixed; blocker 2's FIX introduced a NEW error. I replaced a wrong hub claim with another wrong one: Client().pull_prompt('rlm/rag-prompt') raises ValueError on the pinned langsmith 0.12.1 - _validate_public_prompt_pull (client.py:464) rejects any owner != '-' unless dangerously_pull_public_prompt=True. Verified myself. WORSE than the reviewer stated: langchain_classic/hub.py:117 delegates WITHOUT that flag, so the LEGACY cell 8 fails too, not just the LCEL cell 10 - both halves of the RAG lesson were unrunnable, falsifying T-006's core objective. FIXED by inlining the rag-prompt in cells 8 and 10 (three lines, no network, no trust decision), demoting hub.pull and the LangSmith SDK route to documented comments in cell 9 with the correct dangerously_pull_public_prompt=True, and rewriting cell 6 to say hub.pull RAISES rather than merely warns. Nits fixed: 3.5 c7 duplicate llm binding dropped; 3.6 c7/c10 ChatOpenAI(temperature=0) given model='gpt-4o-mini' (was silently falling back to the legacy gpt-3.5-turbo default). SELF-CAUGHT after applying: my cell 8 rewrite had switched to .invoke(), contradicting cell 6's promise of TWO deprecation warnings - restored the legacy qa_chain(...) call style so the 'before' half actually demonstrates the before behaviour. T-006 HAS NOW HIT THE 3-ROUND REVIEW CAP.

- 2026-09-05: DEFERRED BY USER at the 3-round review cap. State on disk: all round-1/2/3 fixes ARE applied to 3.5 and 3.6 (legacy labels naming both deprecations, marker repositioned to index 5, hub.pull inlined in cells 8 and 10 so both halves run, cell 9 documenting the three prompt options, duplicate llm bindings removed, 3.6 ChatOpenAI given an explicit model). Those edits were verified against .venv source, but they carry NO review approval - the last self-assessment on this task was wrong twice in a row, so treat the labelling text as unverified. Deliberately NOT closed as done and NOT force-closed: the review gate is doing its job. To resume: run notebook-review round 4 on 3.5/3.6, or accept and close with --force (which stamps the bypass in this log).
