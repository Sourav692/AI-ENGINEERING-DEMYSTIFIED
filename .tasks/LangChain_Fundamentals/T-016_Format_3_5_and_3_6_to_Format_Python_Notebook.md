---
id: T-016
title: Format 3.5 and 3.6 to Format_Python_Notebook
type: migration
status: done
review: approved
review_rounds: 2
wave: 5
effort: M
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.5_Chain_Migrations.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.6_Chain_Migration_Advanced.ipynb]
rules: []
depends_on: []
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Format 3.5 and 3.6 to Format_Python_Notebook** — `done` · review: ✓ approved · round 2

## Objective

Both are raw imported Udemy course notebooks: cell 0 is a bare 'Link: https://udemy.com/...' with no title, no Learning Objectives, no Prerequisites; no code cell has a banner; no summary or Next Steps. md_to_notebook --check reports 10 and 18 findings. All predates T-006, whose acceptance criteria say nothing about formatting - boarded separately so a labelling task does not become unbounded.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.5_Chain_Migrations.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.6_Chain_Migration_Advanced.ipynb`

Findings this task closes: _n/a_

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for _n/a_
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified
- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: Both notebooks now pass md_to_notebook --check (were 10 and 18 violations). 3.5: title cell replaced the bare Udemy link with H1 + 4 objectives + prerequisites (link kept as a source note), 6 code cells given 3-line UPPER_CASE banners, summary + Next Steps appended (11 -> 12 cells). 3.6: same treatment, 14 banners, 18 -> 19 cells. CRITICAL CONSTRAINT HONOURED: T-006's legacy labels (3.5 cells 2/6/9, 3.6 cells 3/5) are deliberate content from a DEFERRED task; the script asserted they were untouched after every write and all five passed. No code cell was rewritten - this task only added structural scaffolding.

- 2026-09-05: review r1: 4 blockers - 3 fully closed, 1 half-closed, now fixed. The survivor: 3.5 cell 7 is banner-labelled SETUP and builds embeddings, a Chroma store and a retriever, but ended silently. Round 1 had pointed at cell 7 for the MODEL print; I correctly relocated that to cell 5 (T-006 had removed cell 7's duplicate llm binding, so cell 5 is the only place llm is created - the reviewer confirmed that call was right) but then dropped the other half of the finding instead of answering it. Cell 7 now ends with a vector-store confirmation print, and its now-unused ChatOpenAI import - orphaned by that same T-006 edit - is removed. Also fixed: 3.6 cell 1 import order (dotenv above LangChain, rule 4). T-006's labels re-verified intact by re-deriving their positions rather than trusting indices, since two markdown insertions shifted 3.6; the insertions landed at 9 and 12, both after label index 5, so nothing moved or split. Left alone deliberately: the ---on-### separator inconsistency between 3.5 and 3.6, because normalising it would mean editing T-006's frozen cells.

- 2026-09-05: review r2: 1 blocker, fixed. The blocker was TEXT I ADDED IN ROUND 1: 3.6 cell 1 carried 'Provider alternatives -- swap the active line, the rest of the notebook is unchanged'. That is false. Verified myself: cells 7, 11 and 16 each construct their own ChatOpenAI inline (they need temperature=0 for deterministic rephrase/retrieval), so only cell 4 consumes the bound llm. A learner following that comment would get a silently provider-mixed notebook still requiring OPENAI_API_KEY. Took the reviewer's option (a) - amend the comment to state the truth and name the three cells - rather than option (b), binding a second client, which would change code semantics and step outside this task's scaffolding-only charter. Also dropped 3.6 cell 7's ChatOpenAI re-import (cell 1 already imports it); re-ran a name-resolution pass afterwards, zero forward references. SEPARATOR NIT RULED: leaving it is correct and must not block - rule 2 requires --- only ahead of major ## sections, both notebooks do that on their Summary, and 3.6's extra --- on ### cells is optional garnish. Normalising would mean editing T-006's frozen cells for zero compliance gain. ATTRIBUTION CORRECTION: the reviewer credited T-016 with changing 3.5 cell 5 to 'prompt | llm | StrOutputParser()'. That was T-006 round 3 (its duplicate-binding nit fix), not this task - recorded so the boundary stays accurate.
