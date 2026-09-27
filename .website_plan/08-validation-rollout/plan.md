# Plan 08: Validation and rollout

## Outcome

Ship the redesign in reversible slices with measurable quality gates and no regression to content parsing or saved user work.

## Approach

- Implement on an isolated branch and keep each workstream reviewable.
- Capture baseline screenshots and performance numbers before code changes.
- Use a route/page-type matrix rather than checking only the homepage.
- Preserve storage keys and run migration tests against sample saved data.
- Validate locally, create a Vercel preview, and compare before approving production.
- Do not deploy or merge as part of this planning phase.

## Required page types

- Homepage
- Guide
- Last-Day Prep hub and standalone HTML content
- Live module page
- Worksheet in empty, partial, and mastered state
- Grouped case-study reading page with all document tabs
- Search dialog with results and no results
- Not-found, loading, error, and blocked-storage states

## Acceptance criteria

- All repository checks pass.
- Visual-regression review passes at mobile, tablet, laptop, and wide desktop.
- Existing saved answers/status/scores restore correctly.
- Search, tabs, hash deep links, export, print, reset, and theme switching pass.
- Production deployment requires explicit approval after preview review.

