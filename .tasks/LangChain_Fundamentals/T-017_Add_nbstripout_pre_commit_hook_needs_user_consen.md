---
id: T-017
title: Add nbstripout pre-commit hook (needs user consent)
type: prereq
status: done
review: n/a
review_rounds: 0
wave: 5
effort: S
disposition: n/a
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: []
rules: []
depends_on: []
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Add nbstripout pre-commit hook (needs user consent)** — `done`

## Objective

Prevent executed-notebook outputs from being committed again. T-014 cleared 194 output cells once, but nothing stops the next jupyter session plus git add from re-committing them -- which is exactly how the personal filesystem paths in T-013 reached the repo. BLOCKED ON USER CONSENT, deliberately: this changes every contributor's commit flow, silently mutates staged content, needs the user to run `pre-commit install` themselves, and nbstripout is repo-wide so its blast radius covers archive/ and Phase 13, far beyond this folder. Ready to apply on an explicit yes: add pre-commit + nbstripout to the [dev] extra in pyproject.toml, mirror into requirements.txt and regenerate requirements.lock.txt, create .pre-commit-config.yaml with the nbstripout hook, and document `pre-commit install` in the setup steps.

## Scope

Files in scope:

- _(none listed — fill in)_

Findings this task closes: _n/a_

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for _n/a_
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] No notebook executed by this task; no saved outputs committed

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: USER CONSENT GIVEN 2026-09-05: 'yes add it repo-wide'. Proceeding with the repo-wide scope (archive/ and Phase 13 included), which was the explicitly offered option.

- 2026-09-05: APPLIED with explicit user consent ('yes add it repo-wide'). Four files: pyproject.toml [dev] gained pre-commit>=4.6.2 + nbstripout>=0.9.1; requirements.txt mirrors the exact pins; requirements.lock.txt regenerated with the documented command (548 -> 556 entries, 172 -> 173 direct pins); .pre-commit-config.yaml created. CLAUDE.md's Environment Setup now documents `pre-commit install` as a required per-clone step, with the reason, and its extras table and pin/lock counts were refreshed. VERIFIED BY TEST, NOT ASSUMED: ran nbstripout against a real copy of 8.2 seeded with fake outputs. Outputs emptied, execution_count nulled, cell count preserved, notebook kernelspec kept - and critically cell metadata TAGS SURVIVE, which the whole pipeline depends on: the explainers mark 0.x contrast cells with raises-exception and langchain-0x-contrast, and both the scanner and the bulk-edit scripts key off those tags. Had the hook stripped them, every future scan would have re-flagged the contrast cells as debt. CONFIG CORRECTION: my first draft passed --keep-count=false. --keep-count is a store_true FLAG, so that was invalid; and since stripping the count is the default, the whole args block was unnecessary. Config now uses defaults only. `pre-commit validate-config` passes and a real hook run against two notebooks passes. SCOPE DISCIPLINE: three additional hooks I considered (check-json, mixed-line-ending, end-of-file-fixer) are left COMMENTED OUT in the config. Each guards a failure this repo actually hit this session, but consent was for the nbstripout hook, not for three more. STILL NEEDS THE USER: `pre-commit install` must be run in the clone. Nothing is active until then - an agent cannot do it on your behalf.
