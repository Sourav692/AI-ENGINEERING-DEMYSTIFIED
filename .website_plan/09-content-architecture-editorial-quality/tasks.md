# Tasks: Content architecture and editorial quality

- [x] **CONTENT-01 P0:** Define the required metadata schema: mode, audience, difficulty, prerequisites, outcomes, expected time, source status, last reviewed, and next step.
- [x] **CONTENT-02 P0:** Create a coverage map connecting the 15-module roadmap, 18 Last-Day topics, and 33 case studies.
- [x] **CONTENT-03 P0:** Update the guide and hub copy to explain Practice, Case Studies, Revision, and Behavioral Preparation as distinct learning modes.
- [x] **CONTENT-04 P0:** Publish or integrate `Roadmap.md` as the orientation path instead of leaving it only in the repository.
- [x] **CONTENT-05 P1:** Publish or integrate `Rapid_Revision_Guide.md` as the final rehearsal path.
- [x] **CONTENT-06 P0:** Add prerequisites, learning outcomes, use instructions, and next-step links to every content family through shared metadata where possible.
- [x] **CONTENT-07 P1:** Convert Last-Day cross-module references and trigger-sheet module numbers into real links.
- [x] **CONTENT-08 P1:** Add “learn first” and “go deeper” links between Last-Day modules, worksheets, and relevant case studies.
- [x] **CONTENT-09 P0:** Rename or describe Main, Deep Dive, Cheat Sheet, and Full Pack by learning purpose and recommended order.
- [x] **CONTENT-10 P0:** Select one canonical tutorial for each standalone case and move V1/uncondensed/superseded versions into an archive or changelog.
- [x] **CONTENT-11 P1:** Normalize standalone cases to Practice, Model Answer, Tutorial, and Sources where those artifacts genuinely exist.
- [x] **CONTENT-12 P0:** Decide whether behavioral preparation is private/personal or public/reusable and document the decision.
- [ ] **CONTENT-13 P0:** Replace or isolate profile-specific behavioral examples before public promotion; review customer names, metrics, and internal claims for privacy.
- [x] **CONTENT-14 P0:** Turn `[FILL: …]` markers into structured personalization fields with unresolved-field counts and a clear completion state.
- [ ] **CONTENT-15 P1:** Add a reusable behavioral story bank and show which questions each story can support.
- [x] **CONTENT-16 P1:** Add a case-level source/provenance panel so every companion tab can reach references without duplicating them.
- [ ] **CONTENT-17 P0:** Distinguish scenario assumptions, own construction, measured evidence, and externally sourced facts with consistent labels.
- [ ] **CONTENT-18 P0:** Fact-check security, vendor-specific behavior, quantitative targets, and API/product claims against current primary sources.
- [ ] **CONTENT-19 P1:** Add “last reviewed” and product/version context to claims that can become stale.
- [ ] **CONTENT-20 P1:** Define acronyms on first use and add a shared glossary for cross-cutting terms.
- [x] **CONTENT-21 P1:** Add targeted remediation links from worksheet scorecard dimensions to the relevant tutorial section.
- [x] **CONTENT-22 P0:** Extend content validation to reject broken internal links, missing required metadata, and unresolved placeholders on public-ready pages.
- [x] **CONTENT-23 P1:** Assign a canonical owner/source for duplicated facts and add a drift review when summaries are regenerated.
- [x] **CONTENT-24 P0:** Run an editorial acceptance pass per content family using the self-containedness contract in `content-audit.md`.
- [x] **CONTENT-25 P0:** Adopt the naming principles and visible-name map in `naming-audit.md` without changing existing routes or storage keys.
- [x] **CONTENT-26 P0:** Replace global labels with Practice, Case Studies, Last-Day Review, and How It Works.
- [x] **CONTENT-27 P0:** Stop using “module” for both the 15-part roadmap and 18-part revision sequence; label the latter Review 01–18.
- [x] **CONTENT-28 P0:** Group the planned roadmap into topic, practice, project/reference, and career phases before showing it as one sequence.
- [x] **CONTENT-29 P1:** Rename practice and case-study tracks by learner topic rather than repository structure or interview scheduling.
- [x] **CONTENT-30 P0:** Replace ambiguous document labels such as Main, Full Pack, and Tutorial V2 with purpose-based labels.
- [x] **CONTENT-31 P0:** Add Practice Worksheet or Case Study qualifiers to duplicate scenario names in search, breadcrumbs, metadata, and adjacent navigation.
- [x] **CONTENT-32 P1:** Establish a British-English editorial style guide, including `and` versus `&`, hyphenation, title case, and fixed product/API terminology.
- [ ] **CONTENT-33 P1:** Audit assistant, copilot, agent, and automation titles against the actual autonomy described on each page.
- [x] **CONTENT-34 P1:** Centralise display names so the registry, manifest, Last-Day hub, source headings, metadata, and search index cannot drift independently.

## Status — 2026-09-27 (branch `site/content-architecture-editorial`)

Structural slice done: 27 of 34 tasks. The decisions, metadata contract, style guide and
acceptance pass are in `site/specs/2026-09-27-content-architecture-and-editorial-style.md`.
Notes on partial items:

- **CONTENT-12:** decided. Behavioural stays public as a flagged personalisation template.
- **CONTENT-14:** done through slot rendering, counts and the Mastered lock. Fields are not individually editable inside the model answer.
- **CONTENT-17 and CONTENT-23:** the vocabulary and ownership rules are defined. Applying the labels in the source text is still owed.
- **CONTENT-24:** a structural pass by family only, not a sentence-level read.

Deferred to the editorial session: CONTENT-13, 15, 17 (applying labels), 18, 19, 20, 33.
