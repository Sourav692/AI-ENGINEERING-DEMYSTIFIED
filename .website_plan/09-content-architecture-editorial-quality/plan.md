# Plan 09: Content architecture and editorial quality

## Outcome

Make every page clear about its purpose, audience, prerequisites, expected outcome, source basis, and next step. Preserve the depth of the existing corpus while removing ambiguity between practice, tutorial, case-study, revision, and personal behavioral content.

## Content contract

Each independently reachable page should answer five questions near the top:

1. Who is this for?
2. What should the learner already know?
3. What will they be able to do afterward?
4. How should they use this page, and how long should it take?
5. Where should they go next or deeper?

Content sets may share references and metadata, but dependencies must be explicit and linked.

## Structural direction

- Treat Practice, Tutorials, Case Studies, Revision, and Behavioral Preparation as distinct modes.
- Add a coverage map between the 15-module roadmap, 18-module revision sequence, and 33 case studies.
- Keep the four-layer case-study model where it adds progressive depth.
- Select one canonical tutorial version for each standalone case.
- Treat behavioral pages as personalization tools with privacy and completeness rules.
- Attach provenance, assumptions, and review dates to claims that can age.

## Primary files and sources

- `site/content/manifest.json`
- Generated Markdown under `site/content/modules/`
- Canonical sources under `06_Interview_Prep/FDE/` and `06_Interview_Prep/Case_Study_Groups/`
- Last-Day sources under `06_Interview_Prep/Last_Day_Prep/`
- `site/src/app/guide/page.tsx`
- Content parsers and sync scripts under `site/scripts/` and `site/src/lib/`

## Acceptance criteria

- Every page has content-mode, audience, difficulty, prerequisites, outcome, expected-time, and next-step metadata.
- The site explains how the three numbering systems relate.
- Every cross-module dependency is linked.
- No superseded tutorial version appears as an equal primary choice.
- Behavioral pages expose unresolved personalization fields and pass a public-content privacy review.
- Time-sensitive technical claims have primary sources and a review date.
- Content checks reject broken internal links, unresolved public placeholders, and missing required metadata.
