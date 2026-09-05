---
id: T-013
title: Sweep personal absolute paths from notebook outputs
type: migration
status: done
review: approved
review_rounds: 2
wave: 5
effort: S
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/01_Getting_Started/1.0_LangChain_Introduction.ipynb]
rules: []
depends_on: []
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Sweep personal absolute paths from notebook outputs** — `done` · review: ✓ approved · round 2

## Objective

No committed notebook output contains a personal filesystem path. One survivor found in 1.0 during T-004 review r2; the 4.3 leak was already fixed. Worth a folder-wide grep, not just this file.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/01_Getting_Started/1.0_LangChain_Introduction.ipynb`

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

- 2026-09-05: Folder-wide sweep, not just the one file the review named. Found THREE leaks, not two: 1.0 cells 6 and 8 (as reported) plus 8.1 cell 15, which my earlier shell grep missed because its regex was mangled by escaping. All were in OUTPUTS (error tracebacks), none in source, so the fix is clearing outputs + execution_count - consistent with format rule 7 and with the T-004 r2 blocker fix. Script also reports any personal path found in SOURCE without touching it, since that would need a human decision; none found. Verified 0 personal paths remain anywhere in the folder.

- 2026-09-05: review r2: BLOCKER - 50 personal-path occurrences survived in 1.6 cells 3/7/12 and 3.2 cell 45, all in the '~/Documents/Codebases/2. AI ENGINEERING/LangChain_Demystified/.venv/...' form. My sweep matched /Users/, /home/ and C:\Users\ but NEVER '~/' - which is exactly how IPython renders a traceback under $HOME, i.e. the single most likely shape. Structurally the SAME too-narrow-verification defect as T-012 round 1, one task later. FIXED: broadened the detector to include ~/, %USERPROFILE% and $HOME forms while whitelisting benign ~/.cache paths; cleared outputs+execution_count on all four cells. RE-VERIFIED with a deliberately WIDER independent pattern plus a liveness assertion (confirms the regex still matches a known-benign hit, so a dead pattern cannot fake a clean result): 0 non-benign occurrences folder-wide.

- 2026-09-05: review r3: APPROVED. Reviewer re-swept all 28 notebooks with its own EIGHT-pattern detector (~/, $HOME, ${HOME}, %USERPROFILE%, $env:USERPROFILE, /Users/, /home/, C:\Users with any backslash count, JSON-escaped, OneDrive/Documents/Codebases, soura*, AI ENGINEERING/LangChain_Demystified) across source, cell metadata, outputs AND notebook metadata, with liveness assertions on every pattern. 3 raw hits, ALL benign: ~/.cache/huggingface/ in 1.3 c11 (generic) and 'Sourav' as demo data in 3.2 c20 (a first name in a dict, not a path). All six cleared cells confirmed outputs=[] execution_count=null. The too-narrow-verification defect did not recur.
