₹

# Tasks: Content architecture and editorial quality

- [X] **CONTENT-01 P0:** Define the required metadata schema: mode, audience, difficulty, prerequisites, outcomes, expected time, source status, last reviewed, and next step.
- [X] **CONTENT-02 P0:** Create a coverage map connecting the 15-module roadmap, 18 Last-Day topics, and 33 case studies.
- [X] **CONTENT-03 P0:** Update the guide and hub copy to explain Practice, Case Studies, Revision, and Behavioral Preparation as distinct learning modes.
- [X] **CONTENT-04 P0:** Publish or integrate `Roadmap.md` as the orientation path instead of leaving it only in the repository.
- [X] **CONTENT-05 P1:** Publish or integrate `Rapid_Revision_Guide.md` as the final rehearsal path.
- [X] **CONTENT-06 P0:** Add prerequisites, learning outcomes, use instructions, and next-step links to every content family through shared metadata where possible.
- [X] **CONTENT-07 P1:** Convert Last-Day cross-module references and trigger-sheet module numbers into real links.
- [X] **CONTENT-08 P1:** Add “learn first” and “go deeper” links between Last-Day modules, worksheets, and relevant case studies.
- [X] **CONTENT-09 P0:** Rename or describe Main, Deep Dive, Cheat Sheet, and Full Pack by learning purpose and recommended order.
- [X] **CONTENT-10 P0:** Select one canonical tutorial for each standalone case and move V1/uncondensed/superseded versions into an archive or changelog.
- [X] **CONTENT-11 P1:** Normalize standalone cases to Practice, Model Answer, Tutorial, and Sources where those artifacts genuinely exist.
- [X] **CONTENT-12 P0:** Decide whether behavioral preparation is private/personal or public/reusable and document the decision.
- [x] **CONTENT-13 P0:** Replace or isolate profile-specific behavioral examples before public promotion; review customer names, metrics, and internal claims for privacy.
- [X] **CONTENT-14 P0:** Turn `[FILL: …]` markers into structured personalization fields with unresolved-field counts and a clear completion state.
- [ ] **CONTENT-15 P1:** Add a reusable behavioral story bank and show which questions each story can support.
- [X] **CONTENT-16 P1:** Add a case-level source/provenance panel so every companion tab can reach references without duplicating them.
- [x] **CONTENT-17 P0:** Distinguish scenario assumptions, own construction, measured evidence, and externally sourced facts with consistent labels.
- [ ] **CONTENT-18 P0:** Fact-check security, vendor-specific behavior, quantitative targets, and API/product claims against current primary sources.
- [ ] **CONTENT-19 P1:** Add “last reviewed” and product/version context to claims that can become stale.
- [x] **CONTENT-20 P1:** Define acronyms on first use and add a shared glossary for cross-cutting terms.
- [X] **CONTENT-21 P1:** Add targeted remediation links from worksheet scorecard dimensions to the relevant tutorial section.
- [X] **CONTENT-22 P0:** Extend content validation to reject broken internal links, missing required metadata, and unresolved placeholders on public-ready pages.
- [X] **CONTENT-23 P1:** Assign a canonical owner/source for duplicated facts and add a drift review when summaries are regenerated.
- [X] **CONTENT-24 P0:** Run an editorial acceptance pass per content family using the self-containedness contract in `content-audit.md`.
- [X] **CONTENT-25 P0:** Adopt the naming principles and visible-name map in `naming-audit.md` without changing existing routes or storage keys.
- [X] **CONTENT-26 P0:** Replace global labels with Practice, Case Studies, Last-Day Review, and How It Works.
- [X] **CONTENT-27 P0:** Stop using “module” for both the 15-part roadmap and 18-part revision sequence; label the latter Review 01–18.
- [X] **CONTENT-28 P0:** Group the planned roadmap into topic, practice, project/reference, and career phases before showing it as one sequence.
- [X] **CONTENT-29 P1:** Rename practice and case-study tracks by learner topic rather than repository structure or interview scheduling.
- [X] **CONTENT-30 P0:** Replace ambiguous document labels such as Main, Full Pack, and Tutorial V2 with purpose-based labels.
- [X] **CONTENT-31 P0:** Add Practice Worksheet or Case Study qualifiers to duplicate scenario names in search, breadcrumbs, metadata, and adjacent navigation.
- [X] **CONTENT-32 P1:** Establish a British-English editorial style guide, including `and` versus `&`, hyphenation, title case, and fixed product/API terminology.
- [x] **CONTENT-33 P1:** Audit assistant, copilot, agent, and automation titles against the actual autonomy described on each page.
- [X] **CONTENT-34 P1:** Centralise display names so the registry, manifest, Last-Day hub, source headings, metadata, and search index cannot drift independently.

## Status — 2026-09-27 (branch `site/content-architecture-editorial`)

Structural slice done: 27 of 34 tasks. The decisions, metadata contract, style guide and
acceptance pass are in `site/specs/2026-09-27-content-architecture-and-editorial-style.md`.
Notes on partial items:

- **CONTENT-12:** decided. Behavioural stays public as a flagged personalisation template.
- **CONTENT-14:** done through slot rendering, counts and the Mastered lock. Fields are not individually editable inside the model answer.
- **CONTENT-23:** the ownership rules are defined. CONTENT-17 labels were applied across every family on 27 Sep 2026 (see below).
- **CONTENT-24:** a structural pass by family only, not a sentence-level read.

CONTENT-20 and CONTENT-33 were completed later on 2026-09-27 (glossary, first-use acronym expansion, title audit).
Deferred to the editorial session: CONTENT-13, 15, 17 (applying labels), 18 and 19.

**CONTENT-17/18/19 — round 1 done 27 Sep 2026.** The grouped case studies and the Last-Day reviews are covered: 220 high- and medium-priority claims verified and 128 corrected, with sources and review dates added. These tasks stay open until round 2 covers the standalone cases, practice pages, Roadmap, Rapid Revision Guide and low-priority claims. See `fact-check-followups.md`.

**CONTENT-17 — done 27 Sep 2026 (round 2).** Labels are now in the wording across every public family that round 1 left: the 22 practice answer keys, the 13 standalone cases, the Roadmap and Rapid Revision Guide, and the 143 low-priority round-1 claims (decision recorded per row in `claims-round1.csv`). About 190 label edits over 64 files. Every practice evaluation table now opens with "These are thresholds I'd set for this case, not industry standards." Unsourced external facts were not researched; 44 went to `claims-round2-queue.csv`. 15 of those were in-page arithmetic or clear errors and are already fixed; 29 stay open for CONTENT-18.

