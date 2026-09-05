---
id: T-012
title: Strip stale non-langchain pip pins in 1.1 and 1.3
type: migration
status: done
review: approved
review_rounds: 3
wave: 1
effort: S
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/01_Getting_Started/1.1_Commercial_LLMs_Natively.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/01_Getting_Started/1.3_Open_Source_LLMs_HF_Transformers.ipynb]
rules: [MSC-pip-pin]
depends_on: []
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Strip stale non-langchain pip pins in 1.1 and 1.3** — `done` · review: ✓ approved · round 3

## Objective

No notebook in the track pins a package version that conflicts with the repo environment. Raised by T-004 review r2: openai==1.57.0 in 1.1 is the SAME hazard as the openai==1.55.3 stripped from 2.4 (langchain-openai 1.6.0 needs openai>=2.45.0; repo pins 2.54.0). T-004 stopped at files it had already edited - defensible as diff hygiene, arbitrary as a hazard boundary.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/01_Getting_Started/1.1_Commercial_LLMs_Natively.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/01_Getting_Started/1.3_Open_Source_LLMs_HF_Transformers.ipynb`

Findings this task closes: `MSC-pip-pin`

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for `MSC-pip-pin`
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified
- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: 5 version pins stripped from commented pip lines: 1.1 cell 1 (openai==1.57.0, google-generativeai==0.8.3), 1.3 cell 2 (transformers==4.47.0, accelerate==1.1.0, groq==0.13.0). Package names and each notebook's own per-package explanations preserved. Verified 0 pinned lines remain in both files. This closes the half-stripped-track inconsistency the T-004 r2 reviewer flagged.

- 2026-09-05: review r1: CHANGES_REQUESTED, 1 blocker. A stale '# pip install -qq torch==2.7.1' survived in 1.3 cell 3 - one cell after the cell I edited, in my OWN target file. Repo pins torch==2.14.0. Root cause is worse than the miss: my regex required '!pip install' and that line is '# pip install' with no bang, AND I verified using THE SAME narrow pattern I fixed with, so the log claim 'Verified 0 pinned lines remain in both files' was vacuously true. FIXED: torch==2.7.1 -> torch==2.14.0, keeping the pin because the cell's teaching point is literally 'Option 1: Install specific version (for reproducibility)' - so matching the repo's pin preserves the lesson and removes the hazard. RE-VERIFIED with an INDEPENDENT enumeration (any 'pip install' form, any package): exactly 1 pinned line remains folder-wide and it is torch==2.14.0, which matches requirements.txt.

- 2026-09-05: review r2: blocker fixed and the keep-the-pin judgement was confirmed correct by the reviewer (stripping would have deleted the 'Option 1: specific version for reproducibility' lesson and made it indistinguishable from Option 2). Independent enumeration of all 34 pip-install lines in the folder found exactly one pinned line: torch==2.14.0, matching requirements.txt:111. NIT fixed: 1.3 cells 3 and 4 used '# pip install' with no bang - the very shape that hid the round-1 blocker, and independently broken since uncommenting produced a SyntaxError. Both now '# !pip install'.

- 2026-09-05: review r3: APPROVED. Independent enumeration of all 35 pip-install lines folder-wide: exactly one pinned, torch==2.14.0 in 1.3 c3, matching requirements.txt:111. The '# pip' -> '# !pip' nit landed on both cells. No collateral damage: nbformat versions unchanged per file (4.0/4.5/4.2), zero CRLF bytes, per-file indent preserved, static_check clean.
