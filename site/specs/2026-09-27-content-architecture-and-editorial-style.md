# Content architecture and editorial style

**Date:** 2026-09-27 · **Plan:** `.website_plan/09-content-architecture-editorial-quality/`
**Source of truth for names and metadata:** `src/lib/editorial.ts`

This records the decisions behind the Plan 09 structural slice, the metadata contract
every page now meets, and the house style that editorial work should follow from here.

## Decisions

| # | Decision | Why |
| --- | --- | --- |
| D1 | **Behavioural pages stay public, as personalisation templates.** Each page shows "Personalisation required" with the number of `[FILL]` details in its model answers; those details render as highlighted "Your detail" slots. "Mastered" stays locked until every worksheet field has an answer (a status already saved stays selectable). | The model answers are one candidate's engagements. They teach the shape of a strong answer, but reciting them would be wrong, and any "mastered" state has to come from the reader's own evidence. A privacy scrub of names and metrics is still owed (CONTENT-13). |
| D2 | **One canonical tutorial per standalone case.** Tutorial V2 is the only "Tutorial" tab. Tutorial V1 and the uncondensed V1 leave the tab row, search and progress. They stay in the repo, linked on GitHub from the page's "Before you start" block. | Version history was being offered as a learning choice: the Enterprise Chatbot page had 36,000+ words over five tabs. Saved read-state for a removed tab is ignored and corrected on load. |
| D3 | **Visible names come from `editorial.ts`; ids never change.** Tab ids, track ids, slugs, file names, anchors and `fd:v1:*` keys are untouched. The sync scripts read names from the same module, so the manifest, the static Last-Day pages, search and page headers cannot drift. `check:content` fails when a manifest name differs from the registry. | Renaming a tab used to rename its id (ids were derived from labels), which would have broken `#deep-dive` links and read progress. |
| D4 | **Metadata is a sidecar, not frontmatter.** Family defaults per track in `FAMILY_META`, plus fixed records for revision, orientation and final rehearsal. | Keeps ~200 source files and both parsers untouched. Per-page overrides can be added to the same file when a page genuinely differs from its family. |
| D5 | **The Last-Day sequence is "Review 01–18", never "Module".** Applied to the hub, the static HTML (titles, headings, doc ids, trigger-sheet column) and the two markdown guides, at sync time. The sources keep their wording. | "Module" already means one of the 15 roadmap parts. `check:content` fails a static page that still says "Module N". |
| D6 | **The Roadmap and Rapid Revision Guide are app reading pages** at `/fde-last-day-prep/roadmap` and `/fde-last-day-prep/rapid-revision`, synced from `06_Interview_Prep/Last_Day_Prep/`. Their top-level `#` sections are demoted one level so the reading pipeline can split and index them. | They get the site theme, a contents list and search, which the static pages cannot. |
| D7 | **The static Last-Day HTML is now generated.** `scripts/last-day.mjs` copies `06_Interview_Prep/Last_Day_Prep/html/` into `public/fde-last-day-prep/` and applies the renames and links. Edit the sources, then `npm run sync`. Hand edits under `public/fde-last-day-prep/` are overwritten. | One place to edit, as with every other content family. |

## Content modes

| Mode | Label | Self-contained when it has |
| --- | --- | --- |
| `orientation` | Orientation | where to start, the mental model, what comes next |
| `practice` | Practice | prompt, answer surface, model answer, scorecard, remediation links |
| `behavioural` | Behavioural practice | question, answer structure, personal-evidence slots, completion rule |
| `case-study` | Case study | reading order, per-tab purpose and time, sources location, related practice |
| `revision` | Revision | prior-knowledge statement, recall material, learn-first and go-deeper links |

## Metadata contract

Every published page resolves an `EditorialMeta` record. `REQUIRED_META_FIELDS` lists the
fields `check:content` enforces:

| Field | Meaning |
| --- | --- |
| `mode` | one of the five modes above |
| `audience` | who it is for, in one sentence |
| `difficulty` | Foundation, Intermediate or Advanced |
| `prerequisites` | what the reader should already know |
| `outcomes` | what they will be able to do afterwards |
| `howToUse` | how to work through it, including time-boxing |
| `minutes` | expected time; reading pages compute it from word count at 180 wpm |
| `sourceStatus` | original, derived, sourced or personal |
| `lastReviewed` | ISO date of the last primary-source fact check, or `null`. It is never guessed; nothing is shown while it is null. |

Pages render it as a one-line strip under the title (mode · level · time), a "Before
you start" block, and a "Where next" block linking the reviews that cite the page and
its practice or case-study counterpart.

## Cross-linking

- `REVIEWS[n].learnFirst` / `goDeeper` map each review to practice worksheets and case
  studies. These drive the review pages' site bar, the hub cards, the learning map and
  every page's "Where next". **Every practice and case-study page must be cited by at
  least one review**; `check:content` enforces this.
- `RELATED_CASE` pairs practice worksheets with the case study covering the same problem
  space. Its first five entries are the same scenario published twice.
- Title qualifiers ("· Practice Worksheet", "· Case Study") are computed from actual title
  collisions in the manifest and applied in search, breadcrumbs, browser titles and
  prev/next. The canonical title stays unqualified.
- `SCORECARD_REMEDIATION` links each scorecard row to the reviews that cover it.

## Validation added to `npm run check:content`

- Every track has display names and complete family metadata. Manifest names and tab labels match the registry.
- Every review reference and `RELATED_CASE` entry resolves to a published page, and every non-behavioural page is cited by a review.
- Every site-internal markdown link, and every internal and relative link in the static Last-Day HTML, resolves to a route, a tab of a route, or a public file.
- No `[FILL]`, `TODO`, `TBD`, `XXX` or lorem ipsum on a public page, except behavioural pages, where `[FILL]` is the deliberate personalisation marker. The match is case-sensitive, so prose like "the agent's todo list" passes.
- No static review still says "Module N".

## Editorial style guide

**Voice — the rule everything else serves.** This is interview prep, not a textbook.
Write the way you would say it to an interviewer: short sentences, plain words, "you"
and "I" are fine. Lead with the one-line version someone could say out loud, then add
depth only if it earns its place. "Say it like this" lines and concrete examples beat
polished definitions. Applies to every page, blurb, glossary entry and editorial pass.

**Dialect.** British English in editorial copy: *practise* (verb) / *practice* (noun),
*behavioural*, *judgement*, *organisation*, *prioritise*, *authorisation*, *neighbour*.
Fixed product and API names keep their own spelling (`Unity Catalog`, `ServiceNow`,
`LangGraph`), as do quoted source titles.

**Titles.** Title case for page and section titles; sentence case for controls, metadata
and descriptions. Use "and", not "&", in titles. Keep the serial comma in lists of three or
more ("Delivery, Evaluation, and Operations"). Reserve "&" for cramped metadata.

**Compounds.** multi-tenant, air-gapped, customer-facing, tool-using, real-time,
post-training, human-in-the-loop, fail-closed, end-to-end (as a modifier).

**Acronyms (CONTENT-20, done).** `src/lib/glossary.ts` defines every acronym and cross-cutting
term in spoken form, grouped, with "say it like" lines for the big ones, published at
`/glossary` and in search. `src/lib/acronyms.ts` spells an acronym out the first time it
appears on each page — each tab, each worksheet, each static review — and puts the full
definition in hover text. It leaves headings, links and code alone, skips uses that are
already spelled out nearby, and in table cells and on recall cards puts the definition in
hover text only. Sources are not edited. `check:content` fails when a capitalised term
appears on three or more pages without a glossary entry, unless it is listed in
`NOT_ACRONYMS` or also used as an ordinary lower-case word (shouted labels such as MODEL).
Well-known acronyms (API, JSON, GPU) are in the glossary with `expand: false`.

**Autonomy nouns (CONTENT-33, done).** Choose by behaviour. An *assistant* answers or
recommends. A *copilot* drafts inside someone's workflow, and that person commits. An
*agent* picks and runs actions within limits. An *automation* follows a fixed workflow.
All 28 titled systems were audited against what their pages actually allow. Titles are
changed through `TITLE_OVERRIDES` in `editorial.ts`, never in source headings.

| Page | Was | Now | Why |
| --- | --- | --- | --- |
| core/executive-dashboard-copilot | Executive Dashboard Copilot | Executive Dashboard Assistant | only answers over governed metrics; never drafts or acts |
| core/service-now-ticket-agent | ServiceNow Ticket Automation Agent | ServiceNow Ticket Agent | two nouns; it proposes and performs actions within policy |
| core/financial-compliance-reviewer | Financial Compliance Document Reviewer | Financial Compliance Review Copilot | drafts remediation for a human, like G08 and the legal copilot |
| track agents-that-act | Tool-Using and Action-Taking Agents | Agents and Copilots in Real Workflows | G05, G09 and G16 draft for a human; they do not act |

The following were deliberately kept:

- **G15 Agent Platform for Non-Technical Users.** The page designs a fixed-workflow platform, but the title is the interview question's own wording, and candidates need to recognise it. The design's point is that the right answer is workflows, not open-ended agents.
- **G09 Enterprise Coding Assistant** and **G16 Real-Time Call Assistant.** These are borderline copilots, but the names are established industry usage.

Also noted:

- The ten Discovery Foundations answer keys share boilerplate autonomy text ("read-only tools can run automatically, but any write-back… needs preview and human approval"), so the noun is the main per-scenario signal.
- `core/internal-knowledge-assistant` allows a gated ticket-note write, while its siblings G01 and system-design RAG are strictly read-only.

**Content-type words.** "Module" means a roadmap part only. The Last-Day sequence is
"Review". Use "practice", "case study", "review" and "guide" as type labels. Avoid
"standalone" and other file-organisation words in visible copy.

**Claim labels (vocabulary for CONTENT-17).** Mark a claim as one of:

- **Scenario assumption** — given by the prompt.
- **Own construction** — the author's design choice.
- **Measured** — with its source and date.
- **External fact** — with a primary-source link.

Numeric targets presented as "typical" are own construction unless sourced.

**Canonical owners (CONTENT-23).** Each fact lives in one source document and is summarised
elsewhere:

- A grouped case's Sources and Full Design tab owns its facts. The Interview Guide, Deep Dive and Quick Review compress it.
- A standalone case's Tutorial owns its facts.
- Each Last-Day source `module-NN-*.md` owns its review. The trigger sheet and Rapid Revision Guide summarise it.

When a summary is regenerated, diff its claims against its owner before publishing.

## Editorial acceptance pass — structural (CONTENT-24)

Status of each family against its self-containedness contract after this slice.
"✓" means the site now supplies the element; "owed" means the element needs editorial
work in the source text.

| Family | Pages | Purpose/audience/prereqs/outcome/time | Use instructions | Next step | Sources | Remaining |
| --- | --- | --- | --- | --- | --- | --- |
| Discovery Foundations | 10 | ✓ | ✓ (45-min time-box) | ✓ reviews + remediation | original | provenance notes on numeric targets |
| System Design Practice | 12 | ✓ | ✓ | ✓ reviews + case counterpart | credited on How It Works | assumption vs recommendation labels |
| Behavioural (2 tracks) | 19 | ✓ | ✓ | track prev/next | personal | privacy scrub (13), story bank (15) |
| Grouped case studies | 20 | ✓ | ✓ reading order + per-tab purpose | ✓ | ✓ located per case | claim labels, freshness dates |
| Additional designs / judgement | 13 | ✓ | ✓ | ✓ | located where present | "why one document is enough" copy is family-level only |
| Last-Day reviews | 18 + trigger sheet | ✓ hub + site bar | ✓ | ✓ learn-first / go-deeper / prev-next | original | glossary, inline acronym expansion |
| Roadmap, Rapid Revision | 2 | ✓ | ✓ | ✓ | original | — |

## Deferred to the editorial session

- CONTENT-13, the privacy scrub (done later on 2026-09-27; see "Privacy" below).
- CONTENT-15, the story bank.
- CONTENT-17, applying the claim labels in the source text.
- CONTENT-18/19, the primary-source fact check and review dates.

## Privacy (CONTENT-13, done 2026-09-27)

The behavioural answers and some case studies were written from real client engagements.

**What changed**

- Raw client stories moved to the gitignored `06_Interview_Prep/_private/`. Unredacted originals of every file edited in the scrub are kept there too, under `originals/`. Nothing in `_private/` is ever committed.
- Tracked copies were anonymised, which also cleans the website:
  - Clients became "a large Asian life insurer", "a large Indian consumer lender" and "a global tier-1 bank".
  - Identifying details were generalised: superlatives, cloud and region, exact durations, ticket counts and schema names.
  - Commercial figures, product-availability claims, internal codenames and employer coaching notes were removed.
  - The employer is now "the platform vendor I worked for".
- The "leak false alarm" story is anchored to the Meridian Assist reference build, where it actually happened.
- The Deep Agents demo now uses a fictional insurer, "Acme Life", with `insurer-*` skills.

**Guard.** `scripts/check_repo_invariants.py` (the private-terms check, run on every commit) fails if a client name reappears in any tracked text file. The names are stored as truncated SHA-256 hashes, so the check does not publish them.

**Not done, on purpose**

- Git history still holds the originals. Rewriting it would need a force-push to a public repo.
- The sibling repo `Agent_Evaluation_Demystified` still tracks the raw stories. It is private.
