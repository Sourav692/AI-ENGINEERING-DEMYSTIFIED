---
id: T-007
title: Explainer: the package split and where imports moved
type: explainer
status: done
review: approved
review_rounds: 3
wave: 5
effort: M
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: []
rules: [IMP-chains, IMP-schema, IMP-textsplitter, IMP-llms, IMP-parsers, IMP-hub]
depends_on: []
output: 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/01_Getting_Started/1.8_Package_Split_and_Imports_LangChain_v1.ipynb
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Explainer: the package split and where imports moved** — `done` · review: ✓ approved · round 3

## Objective

A learner can resolve any moved-import error in this track unaided.

## Scope

Files in scope:

- _(none listed — fill in)_

Findings this task closes: `IMP-chains`, `IMP-schema`, `IMP-textsplitter`, `IMP-llms`, `IMP-parsers`, `IMP-hub`

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for `IMP-chains`, `IMP-schema`, `IMP-textsplitter`, `IMP-llms`, `IMP-parsers`, `IMP-hub`
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified
- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: review r1: CHANGES_REQUESTED — 3 blockers. (1) cell 11 fused 3 sections with literal <!-- split --> markers: root cause was a BUG in md_to_notebook.py, where a closing plain fence was re-read as an opening fence, leaving the parser stuck in fence mode and swallowing every later split/---. Script fixed (in_plain_fence toggle); 12 -> 14 cells. (2) format rule 5: added commented provider alternatives under init_chat_model. (3) NOTEBOOK_INDEX.md:64 updated 8 nb -> 9 nb. Nit: Next Steps now marks 8.2 as upcoming (T-008 output).

- 2026-09-05: bookkeeping: the original --status in-progress call never executed (it was chained after a bash heredoc that failed to parse). Task was worked despite showing todo; corrected here.

- 2026-09-05: review r2: APPROVED - all six gates pass (syntax, api_correctness, pedagogy, format_compliance, task_fidelity, placement). Reviewer verified symbol-by-symbol against .venv: init_chat_model signature accepts temperature via **kwargs; langchain.messages.HumanMessage IS langchain_core's (so the 'is' claim is literally true); all 7 MOVED paths genuinely raise ModuleNotFoundError on installed langchain 1.4.0; no runnable cell imports the uninstalled langchain_classic/langchain_text_splitters. 3 nits raised; 2 applied post-approval using the reviewer's own prescribed fixes (audit-loop emoji 0x1F916->warning; README.md topic line), 1 declined (init_chat_model vs direct ChatOpenAI - reviewer judged it correct since init_chat_model IS the subject of Part 5).

- 2026-09-05: REOPENED after T-001: installing langchain-classic made a previously unverifiable claim checkable, and it was wrong. langchain_classic.memory DOES export ConversationBufferMemory/SummaryMemory/BufferWindowMemory etc. The notebook said memory was 'the exception - no new home', and exercise 2 was built on that false premise. Corrected: audit dict, mapping table row, summary key point, Part 1 Key Concepts, and exercise 2 (now asks the learner to argue both sides). Also corrected the same claim in the audit skill's rewrite map and the IMP-memory scanner rule text. Going to review round 3.

- 2026-09-05: review r3: APPROVED - all six gates. Reviewer re-verified every langchain_classic/langchain_text_splitters claim now that both are installed: chains/.retrievers/.indexes are real populated packages, 'from langchain_classic import hub' resolves (hub.py, push deprecated since 1.0.6), text-splitters exports RecursiveCharacterTextSplitter, and NO row is wrong in the opposite direction. Also confirmed installing langchain-classic does NOT resurrect the old langchain.* paths (no langchain/* files in its RECORD, no .pth hook), so the audit cell's output is unchanged. 2 nits: (1) APPLIED - narrative said 'every one raises ModuleNotFoundError' but 'from langchain import hub' actually raises ImportError (verified independently); reworded and added it as a 4th entry in Part 7 since objective 3 is 'reading the error'. (2) DECLINED - adding live langchain_classic imports to the audit cell; the reviewer itself landed on 'still correct not to', since the cell is a proof of absence and importing LLMChain would model what Part 1 warns against.
