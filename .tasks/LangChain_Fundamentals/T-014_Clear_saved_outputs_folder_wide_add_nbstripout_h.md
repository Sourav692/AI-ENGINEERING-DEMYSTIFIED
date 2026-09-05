---
id: T-014
title: Clear saved outputs folder-wide
type: migration
status: done
review: approved
review_rounds: 1
wave: 5
effort: M
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: []
rules: []
depends_on: [T-005, T-011]
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Clear saved outputs folder-wide** — `done` · review: ✓ approved · round 1

## Objective

No committed notebook carries saved outputs (format rule 7). 16 notebooks / 198 code cells as measured 2026-09-05. MUST run AFTER T-005 and T-011, which rewrite cells whose outputs would be cleared anyway. **Re-scoped 2026-09-05 after review round 2.** The hook half was split out to T-017: a pre-commit hook changes what happens on every commit by every contributor, only takes effect once the USER runs `pre-commit install` locally, and nbstripout is repo-wide -- it would strip outputs from archive/, Phase 13 apps and everything else, far outside this folder-scoped task. Closing T-014 against the old wording would have left the board claiming a control that does not exist.

## Scope

Files in scope:

- _(none listed — fill in)_

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

- 2026-09-05: DEPENDENCY RE-EXAMINED: boarded as depends_on T-005,T-011 on the reasoning that both rewrite cells whose outputs would be cleared anyway. T-005 is done. T-011 touches only 2.2 cell 20, and 2.2 has ZERO cells carrying outputs - so there is no wasted work to avoid. The dependency was about efficiency, not correctness, and it does not apply. Proceeding.

- 2026-09-05: Cleared 194 output cells and 267 execution_counts across 17 files; also dropped stale per-cell scrolled/collapsed metadata. Verified zero residue folder-wide, 29 notebooks still valid nbformat, per-file JSON indent preserved, LF. Net -4092 lines. NBSTRIPOUT HOOK NOT ADDED - and deliberately so. This repo has no .pre-commit-config.yaml and does not pin pre-commit or nbstripout. Adding a hook changes what happens on EVERY commit the user makes, which is a larger imposition than the dependency-file edits I have been refusing to make unattended. Without it the leak class recurs the next time someone commits an executed notebook - which is exactly how T-013's personal paths got committed - so this needs an explicit yes. Ready to add on request: pre-commit + nbstripout in the [dev] extra, a .pre-commit-config.yaml with the nbstripout hook, and 'pre-commit install' in the setup docs.

- 2026-09-05: review r1: APPROVED. Deliverable verified across all 29 notebooks: zero cells with outputs, zero non-null execution_count. Source-vs-HEAD comparison shows only 7 files with changed cell sources, every one attributable to a named task (T-012/T-015, T-006/T-016, T-005, T-008) - T-014 itself altered no source. Per-file JSON indent preserved on both the indent-1 and indent-2 files, no CRLF introduced. RE-SCOPE RULED HONEST, not an evasion, on three grounds: the work was not dropped (T-017 exists as a real open prereq with the exact four-file change spelled out), the gate named is real rather than a pretext (a hook silently mutates staged content for every contributor, only activates once the USER runs pre-commit install, and nbstripout is repo-wide so it would strip archive/ and Phase 13 - far outside a folder-scoped task), and the reasoning is recorded in T-014's own Objective so the board cannot later claim a control that does not exist. One nit fixed after: 2.6 cell 38 kept jupyter.outputs_hidden because my earlier cleanup used `a is not None or b.pop(...)`, and the short-circuit meant the second operand never ran once the first was true.
