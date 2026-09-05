---
id: T-019
title: Format 2.2_Prompt_Templates to Format_Python_Notebook
type: migration
status: done
review: approved
review_rounds: 1
wave: 5
effort: M
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.2_Prompt_Templates.ipynb]
rules: []
depends_on: []
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Format 2.2_Prompt_Templates to Format_Python_Notebook** — `done` · review: ✓ approved · round 1

## Objective

md_to_notebook --check reports 8 pre-existing violations in 2.2: cell 0 has no leading emoji on its H1 and no Learning Objectives or Prerequisites; cells 7, 9, 12, 25 lack the 3-line banner; the last cell is code rather than a markdown summary. All predate T-011 and sit in cells it did not touch. Same shape as T-016 did for 3.5/3.6.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.2_Prompt_Templates.ipynb`

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

- 2026-09-05: APPLIED T-018 + T-019 in one pass (both touch cells 23-25). T-018: .save() and load_prompt() replaced with dumps/loads from langchain_core.load. Both deprecation strings quoted VERBATIM from warnings I triggered, not from memory. Two honest caveats the rewrite states rather than hides: dumps is JSON-ONLY, so the old lesson's YAML half has no 1.x equivalent (dumpd gives a dict you can write yourself); and loads is itself marked BETA and emits a pending-deprecation warning unless you pass allowed_objects. I pass allowed_objects=[PromptTemplate] and teach it as what it is - a security boundary, since deserializing reconstructs arbitrary objects from file contents. Verified by execution: round trip preserves both rendering and input_variables, and ZERO non-beta warnings are emitted. T-019: 8 format violations -> 0. H1 got an emoji, Prerequisites added, banners on cells 7/9/12 normalised to the documented NAME: description form (they used parenthesised lowercase or a dash), cell 25 given a banner, and the KEY TAKEAWAYS comment block promoted into a real markdown summary cell with Next Steps (26 -> 27 cells). CHECKER BUG FOUND AND FIXED: two of the eight reported violations were MY CHECKER being wrong, not the notebook. It did a literal substring test for '## Learning Objectives', so '## 🎯 Learning Objectives' failed - even though format rule 2 asks for one emoji per heading. md_to_notebook.py now matches an optional emoji on the fixed headings (Learning Objectives, Prerequisites, Summary, Next Steps). Regression-checked: 1.8, 8.2, 3.5 and 3.6 all still pass. Without that fix I would have 'corrected' a notebook that was already right. SURFACED, NOT ABSORBED: prompt.json/prompt.yaml are committed notebook artifacts absent from .gitignore, and prompt.yaml is now orphaned since no cell writes YAML. Boarded as T-020 because removing tracked files is destructive.

- 2026-09-05: review r2: APPROVED, all six gates. All four round-1 fixes verified landed: cell 22 no longer advertises YAML and its pointer resolves to cell 23's note; the beta warning is now IN THE NOTEBOOK and character-exact; EMOJI_PREFIX behaves as claimed (accepts bare and emoji forms, rejects 'Optional Learning Objectives' and 'Draft Summary'); joke_prompt renamed with prompt confirmed NOT rebound by cells 23-25. Reviewer swept every markdown heading in every non-archive notebook for a leading non-ASCII char outside the range: zero hits, so no existing heading is silently rejected. It also flagged the range's known blind spot for future reference - emoji below U+2100 ((c), (r), keycaps) would be rejected on a fixed heading; none are used here. 3 nits, ALL FIXED. The important one is mine from T-011: cell 19's ```python snippet had my escaped newlines collapse into REAL newlines, so the string literal was split across three physical lines and the blockquote prefix was lost - a learner copying it got SyntaxError: unterminated string literal. Rebuilt with chr(92) so the JSON carries a literal backslash-n; verified by extracting the block and ast.parse-ing it. Second: cell 10's comment claimed 'last 200 chars' while slicing [1:300] (pre-existing, now [:300] with a matching comment). Third: my EMOJI_PREFIX used an INCLUSIVE 0x2100 lower bound while _has_emoji uses exclusive '> 0x2100', so U+2100 satisfied one and not the other - tightened to 0x2101. All five notebooks still pass.
