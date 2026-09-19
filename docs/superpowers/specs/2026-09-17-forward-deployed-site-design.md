# Forward Deployed — FDE Interview Prep Site

**Date:** 2026-09-17
**Status:** Approved design, pending implementation
**Tagline:** The end-to-end FDE interview prep system

## Purpose

A public website that guides anyone through end-to-end Forward Deployed Engineer
interview preparation. The content already exists as markdown in
`14_Interview_Preparation/FDE/`. The site's job is to turn static worksheets into a
practice loop: attempt a section, reveal the answer key for that section, self-score,
track progress.

Module 01 (Customer Discovery & Decomposition) ships first. Twelve further modules
already have folders on disk and will be added later, so extensibility is a
requirement of the first build, not a later concern.

## Source material

Two sets, both using a consistent schema.

| Set | Location | Count |
| --- | --- | --- |
| Core Scenarios | `1. Complete GEN AI FDE Interview System — Core + GenAI/01_CUSTOMER_DISCOVERY_AND_DECOMPOSITION/04_CASE_STUDY_WORKSHEET/` | 10 worksheets + 10 keys |
| System Design Scenarios | `FDE_System_Design_Interview_20_Scenarios/Version_3/` | 12 worksheets + 12 keys |

Only `.md` files are used. The PDFs and `.docx` files in those folders are out of scope.

**Worksheet schema** — 11 sections, ~84 lines. Sections 3–6 are deliberately blank for
the reader to fill in; section 11's `Score` column is blank.

1. Interview prompt
2. Clarify the customer problem
3. Users and workflows (blank table)
4. Requirements (blank bullets + blank `Label:` fields)
5. Data and integration map (blank table)
6. Proposed architecture (blank `Label:` fields)
7. Evaluation plan (filled table)
8. Failure modes
9. Rollout plan
10. Weak vs strong answer
11. Candidate scorecard (blank `Score` column)

**Answer key schema** — 13 sections, ~97 lines: Strong discovery questions; Strong
functional requirements; Strong non-functional requirements; Architecture explanation;
Data model / integration assumptions; Red-team risks; Rollout plan; Evaluation plan;
Weak answer; Average answer; Strong answer; Interviewer scorecard; Final 2-minute
spoken answer.

## Decisions

| Decision | Choice |
| --- | --- |
| Interaction model | Fillable worksheets, answers saved in `localStorage`; answer key gated behind a reveal |
| Section organisation | One section, two tracks (Core Scenarios, System Design Scenarios) |
| Content flow | Source `.md` stays canonical; build-time sync copies into `site/content/` |
| Audience | Public, search-indexed, with book attribution |
| Stack | Next.js 15 App Router + Tailwind + shadcn/ui, static generation |
| Visual direction | Course / learning platform — module dashboard, progress rings, lesson pages |
| Answer key reveal | Per-section inline reveal |
| Repo layout | `site/` subfolder + build-time sync script |
| Fillable detection | Heuristic — emptiness means fillable |
| V3 numbering | Renumbered 1–12 sequentially (original chapter numbers dropped) |
| Git strategy | Un-ignore the `.md` only; PDFs and `.docx` stay ignored |

## Architecture

### Layout

```
site/
├── package.json
├── next.config.ts
├── tsconfig.json
├── scripts/sync-content.mjs        # prebuild: source .md → content/
├── content/                        # GENERATED, gitignored
│   └── modules/01-customer-discovery-and-decomposition/
│       ├── core/<slug>.md
│       ├── core/answer-keys/<slug>.md
│       ├── system-design/<slug>.md
│       └── system-design/answer-keys/<slug>.md
└── src/
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx                                    # module dashboard
    │   ├── guide/page.tsx                              # how to use + attribution
    │   └── modules/[module]/
    │       ├── page.tsx                                # track + scenario listing
    │       └── [track]/[scenario]/page.tsx             # scenario page
    ├── lib/
    │   ├── registry.ts          # 13 modules, live vs coming-soon
    │   ├── content.ts           # load markdown, build Scenario model
    │   ├── parse.ts             # markdown → Block[] with fillable detection
    │   ├── mapping.ts           # worksheet § → answer key §
    │   ├── storage.ts           # safe localStorage wrapper
    │   └── search-index.ts      # build-time JSON index
    └── components/…
```

### Content pipeline

1. `scripts/sync-content.mjs` runs on `prebuild`. It copies `.md` files from the two
   source folders into `site/content/`, applying slugs and the V3 renumbering.
2. The script **fails the build** if it copies zero files. Silently shipping an empty
   site is the failure mode worth guarding against, since the sources live outside the
   app directory.
3. `content/` is gitignored. It is generated output; the source folders remain the only
   place anyone edits.
4. Next.js reads `content/` at build time in server components. All 22 scenario pages
   are statically generated. No markdown parsing happens in the browser.

### Content model

```ts
type Scenario = {
  slug: string
  title: string
  moduleId: string
  trackId: string
  order: number
  worksheet: Section[]
  answerKey: Section[]
}

type Section = { n: number; title: string; blocks: Block[] }

type Block =
  | { kind: 'prose'; html: string }
  | { kind: 'table'; headers: string[]; rows: Cell[][] }
  | { kind: 'list'; items: Item[] }
  | { kind: 'fields'; fields: { label: string; id: string }[] }
  | { kind: 'scorecard'; rows: { area: string; one: string; three: string; five: string; id: string }[] }

type Cell = { text: string } | { editable: true; id: string }
type Item = { text: string } | { editable: true; id: string }
```

### Fillable detection (heuristic)

Applied uniformly to every worksheet, with no per-file configuration:

| Source pattern | Rendered as |
| --- | --- |
| Table cell whose trimmed content is empty | Text input |
| List item that is a bare `-` | Text input |
| List item matching `^([A-Za-z][^:]{0,40}):\s*$` | Label + text input |
| Table column headed `Score` | 1 / 3 / 5 selector |

Field IDs are deterministic and position-derived:
`<scenarioSlug>:s<sectionNumber>:<blockIndex>:<row>:<col>`. Stable IDs matter because
saved answers are keyed on them; a change to a worksheet's structure will orphan
answers for that scenario, which is acceptable and preferable to mis-restoring them
into the wrong field.

This heuristic is the extensibility mechanism. Any future module whose worksheets
follow the same conventions becomes interactive with no code change.

### Answer key mapping

| Worksheet § | Answer key § |
| --- | --- |
| 1 Interview prompt | — (it is the prompt) |
| 2 Clarify the customer problem | Strong discovery questions |
| 3 Users and workflows | — no counterpart |
| 4 Requirements | Strong functional requirements + Strong non-functional requirements |
| 5 Data and integration map | Data model / integration assumptions |
| 6 Proposed architecture | Architecture explanation |
| 7 Evaluation plan | Evaluation plan |
| 8 Failure modes | Red-team risks |
| 9 Rollout plan | Rollout plan |
| 10 Weak vs strong answer | Weak answer + Average answer + Strong answer |
| 11 Candidate scorecard | Interviewer scorecard |

`Final 2-minute spoken answer` has no worksheet counterpart and is rendered as a
featured card closing the scenario page.

Section 3 gets no reveal block. This is deliberate: the alternative was to synthesise
one from other key sections, which would present recombined text as though it were the
key's own.

### Persistence

All state is per-browser `localStorage`. There is no backend and no login.

| Key | Value |
| --- | --- |
| `fd:v1:answers:<scenario>` | `{ [fieldId]: string }` |
| `fd:v1:status:<scenario>` | `not-started \| practiced \| mastered` |
| `fd:v1:scores:<scenario>` | `{ [areaId]: 1 \| 3 \| 5 }` |

Rules:

- Every read and write is wrapped in `try/catch`. Private windows and blocked site data
  throw on access; the site must render correctly with storage entirely unavailable.
- The server renders empty inputs. Saved values load in an effect after mount, avoiding
  hydration mismatch.
- Writes are debounced at 400ms, with a "Saved" indicator.
- Reset is available per scenario and globally.

## Features

**Module dashboard (`/`)** — card grid of all 13 modules. Module 01 live with a progress
ring (`n`/22 scenarios) and "Continue where you left off"; the other 12 shown locked
with their real titles, so the roadmap is visible from day one.

**Guide (`/guide`)** — the practice loop (attempt → reveal → self-score), what an FDE
interview tests, and source attribution to *The Forward Deployed Engineer System Design
Interview*. Chapter 21 of the V3 set is a custom addition, not from that book, and is
labelled as such.

**Module page** — the two tracks with all 22 scenarios, each showing status.

**Scenario page** — 11 sections; fillable regions; per-section reveals; featured final
answer card; practice timer (optional countdown); self-scored scorecard; export; print;
reset; prev/next.

**Search (⌘K)** — client-side over a build-time JSON index of every worksheet and answer
key section. No backend.

**Export** — regenerates the worksheet markdown with the reader's answers substituted
into the blanks, downloaded as `.md`. Print stylesheet for a clean PDF.

**Dark mode** — system-preference aware with a manual toggle.

## Git and deployment

`.gitignore` currently ignores the whole `1. Complete GEN AI FDE Interview System —
Core + GenAI/` folder at line 153, with no explanatory comment. The folder holds 4 PDFs
and 11 `.docx` files, so the likely original motive was binary bloat.

Change: keep that rule, add negations so `.md` files under it are tracked while binaries
stay ignored. `Version_3/` is untracked but not ignored, so it is committed as-is.
`site/content/` and `site/node_modules/` are added to the ignore list.

The repo is public, so this also publishes the worksheets on GitHub. That is consistent
with the site being public, and is why attribution is a launch requirement rather than a
follow-up.

Vercel: project root `site/`, framework preset Next.js, build runs the sync script via
`prebuild`. Deployed to a `*.vercel.app` URL; no custom domain at launch. Build locally
and review first, then deploy at the end of the work.

## Out of scope

- The PDFs and `.docx` files in the source folders
- Modules 02–13 content (registered as locked placeholders only)
- Accounts, server-side persistence, cross-device sync
- Custom domain
- The existing `docs/` static microsite in this repo, which is unrelated and untouched

## Risks

| Risk | Mitigation |
| --- | --- |
| Sync script finds no files on Vercel and ships an empty site | Script exits non-zero on zero files copied |
| `localStorage` unavailable or throws | All access wrapped; site fully functional read-only without it |
| Hydration mismatch from restored values | Server renders empty; values load post-mount |
| Worksheet edits orphan saved answers | Accepted; position-derived IDs fail safe rather than mis-restore |
| Heuristic mis-classifies a future worksheet | Detection rules are centralised in `parse.ts` and unit-tested against all 22 current files |
