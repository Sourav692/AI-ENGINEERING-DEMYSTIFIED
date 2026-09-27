# Content architecture audit

## What was reviewed

The website content audit has two levels:

1. **Corpus-wide structural review:** all 191 Markdown files consumed by the Next.js application and all 21 Last-Day Prep source files were scanned for document type, length, headings, links, reference sections, placeholders, and repeated structures.
2. **Editorial close read by content family:** representative technical worksheets and keys, behavioral worksheets and keys, four-tab case studies, one-/two-/five-tab standalone cases, Last-Day modules, the rapid guide, roadmap, and trigger sheet were read for learning flow and self-containedness.

This is not yet a sentence-by-sentence technical fact check of all 212 files. Product-specific and time-sensitive claims still need verification against current primary sources before the site is presented as an authoritative reference.

## Executive assessment

The material is substantial and often technically strong. The main problem is not missing volume. It is that the site does not tell users which documents are complete lessons, which are practice prompts, which are condensed recall aids, which depend on companion tabs, and which require the user to add personal evidence.

The site should define “self-contained” by content mode instead of applying one rule to every page:

| Mode | Self-contained when it includes |
| --- | --- |
| Practice | Prompt, assumptions, answer surface, rubric, model answer, and next practice step |
| Tutorial | Learning outcome, prerequisites, explanation, worked example, checks, sources, and next lesson |
| Case study | Scenario, requirements, architecture, trade-offs, failure modes, evaluation, rollout, and interview summary |
| Revision | Prior-knowledge statement, recall model, gotchas, triggers, self-check, and links to deeper material |
| Behavioral | Question, story-selection guidance, editable personal evidence, answer structure, rubric, and completion status |

## Findings by content family

### Technical practice: 22 worksheet/key pairs

**Assessment: self-contained for a practice session, with small editorial gaps.**

All 22 worksheets use the same 11-part flow: prompt, discovery, users, requirements, data, architecture, evaluation, failures, rollout, answer quality, and scorecard. All 22 answer keys consistently provide discovery questions, requirements, architecture, risks, rollout, evaluation, a scorecard, and a final spoken answer. This is the cleanest content system in the site.

Recommended changes:

- Add a short prerequisite and learning outcome to the page introduction.
- Explain whether users should complete every field or time-box the exercise.
- Add “review next” links from weak rubric areas to a relevant tutorial or Last-Day module.
- Add source/provenance notes to model answers where claims, numeric targets, or vendor behavior are presented as facts.
- Distinguish stated scenario assumptions from generally recommended production targets.

### Behavioral practice: 19 worksheet/key pairs

**Assessment: useful scaffolding, but not self-contained for a general public user.**

The pages correctly avoid inventing personal experience, but they depend on a private story inventory. There are 78 `[FILL: …]` markers across 25 behavioral files. Many answer keys reference named projects, employers/customers, a STAR deck, or details that only the original author can verify. This is appropriate for a personal preparation system, but it should not look like a complete public model answer.

Recommended changes:

- Decide whether this section is private/personal or a reusable public tutorial.
- For a public site, replace profile-specific details with a neutral worked example and put personal prompts in editable fields.
- Add a “Personalization required” status and count unresolved evidence fields.
- Create a reusable story bank: situation, role, constraint, decision, evidence, result, lesson, and questions it can answer.
- Block “Mastered” status while required personal evidence remains unresolved, or explain that mastery is self-attested.
- Add privacy review before publishing names, client details, metrics, or internal project claims.

### Grouped case studies: 20 four-tab pages

**Assessment: collectively self-contained; individual tabs have implicit dependencies.**

The Main, Deep Dive, Cheat Sheet, and Full Pack pattern supports progressive depth. The Main documents generally establish the problem and architecture; Full Packs contain detailed source sections; Cheat Sheets work as recall aids. However, labels do not explain the intended order, some Main pages are themselves long, and references often live only in Full Pack.

Recommended changes:

- Rename or describe tabs by purpose: Start Here, Technical Deep Dive, Quick Recall, Sources & Full Design.
- State that references and source provenance are shared across the tab set.
- Give every tab a one-sentence purpose, expected time, and next action.
- Keep Main independently understandable; deep dives may assume Main but should link back to the exact prerequisite section.
- Surface “own construction,” assumptions, and source-backed claims with consistent visual labels.
- Add a case-level completion summary so four tab read states feel like one learning unit.

### Standalone case studies: 13 pages with one to five documents

**Assessment: content-rich but structurally inconsistent.**

Some pages are single guides, some pair a casebook with a design, and some expose Worksheet, Answer Key, Tutorial V2, Tutorial V1, and an uncondensed V1. The Enterprise Chatbot page alone offers roughly 560 worksheet words, 1,900 answer-key words, 10,000+ Tutorial V2 words, 8,800 Tutorial V1 words, and 17,000+ uncondensed V1 words. Version history is being presented as a learning choice.

Recommended changes:

- Choose one canonical tutorial per case.
- Move superseded versions into an archive or changelog instead of the primary tab row.
- Normalize standalone cases to Practice, Model Answer, Tutorial, and Sources when those artifacts exist.
- Add the missing artifact deliberately when a case should support a full learning loop; do not create empty tabs merely for consistency.
- Explain why a one-document guide is complete without companion tabs.

### Last-Day Prep: 18 modules, 18 memory cards, and one trigger sheet

**Assessment: self-contained for revision, not for first-time learning.**

The 18 source modules are unusually consistent. Each has an interviewer goal, mental model, essential concepts, requirement-to-component reasoning, gotchas, triggers, interview phrases, practice questions, and memory card. Length ranges from roughly 1,300 to 2,050 words, which is suitable for condensed review.

The missing context is product-level. A new user is not told that these pages assume prior study. Cross-module dependencies are written as prose rather than links. The trigger sheet is a strong synthesis artifact but does not act as a clickable index. `Roadmap.md` and `Rapid_Revision_Guide.md` exist in the source folder but are not available in the website flow.

Recommended changes:

- Label the collection “revision for users who already know the concepts.”
- Publish or integrate the Roadmap as the orientation page.
- Publish or integrate the Rapid Revision Guide as the final end-to-end rehearsal.
- Convert module references and trigger-sheet module numbers into links.
- Add “learn first” and “go deeper” links to practice/case-study material.
- Add a small glossary or inline definitions for terms that cannot be assumed across all audiences.

### Guide and learning-path content

**Assessment: the usage guide explains mechanics, but the curriculum relationship remains unclear.**

Users see a 15-module product roadmap, three available app modules, an 18-module Last-Day sequence, and 33 case studies. The numbering systems describe different things but look like one curriculum. The website needs a coverage map that explains depth and purpose:

- Practice modules teach and assess a skill.
- Case studies show the skill in complete systems.
- Last-Day modules compress concepts for recall.
- The guide explains the learning loop.

## Cross-cutting editorial risks

### Accuracy and freshness

Architecture principles are relatively stable. Vendor capabilities, supported security behavior, product names, performance figures, and API details are not. Add source links, a “last reviewed” date, and product/version context to time-sensitive claims. Fact-check these claims against primary documentation on a scheduled cadence.

### Source transparency

Twenty Full Packs and seven standalone guides contain references sections, but companion Main, Deep Dive, Cheat Sheet, worksheets, and answer keys often do not show where their claims came from. A case-level source drawer can avoid repeating references while keeping provenance one click away.

### Duplication and maintenance

Progressive summaries are useful; version duplication is not. Keep intentional Main → Deep Dive → Cheat Sheet compression, but remove tutorial versions from primary navigation once a canonical version is selected. Every duplicated fact should have one canonical source to prevent drift.

### Terminology and audience

The corpus shifts between beginner definitions, staff-level interview shorthand, vendor-specific implementation notes, and personal leadership material. Add audience and difficulty metadata at the page level. Define acronyms on first use in each independently reachable page.

## Priority recommendation

Before rewriting individual paragraphs, make the content modes explicit and fix the two highest-risk areas:

1. Clarify the curriculum map and publish the missing orientation/rapid-revision material.
2. Decide how behavioral content is made safe and useful for a public audience.
3. Consolidate standalone tutorial versions into one canonical learning path.
4. Add prerequisites, outcomes, sources, freshness, and next-step links as shared content metadata.
5. Then run a technical fact check by topic, starting with security, vendor-specific claims, and quantitative targets.
