---
name: fde-case-study-worksheet-v3
description: Converts a long-form FDE system-design tutorial (a `_v2` chapter in `06_Interview_Prep/FDE/FDE_System_Design_Interview_20_Scenarios/Version_2/`) into a Version_3 case-study PAIR — a short blank practice worksheet plus a filled answer key — matching the format and ~100-line length of the Phase-01 CASE_STUDY_WORKSHEET reference docs. Use when the user asks to "make version 3", "convert Version_2 into the worksheet/answer-key format", "turn chapter N into a case study worksheet", "generate the answer keys for the 20 scenarios", or otherwise asks for the short worksheet+answer-key form of a scenario tutorial. Do NOT use to produce the long bullet-cram tutorials — that is `fde-tutorial-interview-format`.
---

# FDE Case Study Worksheet + Answer Key (v3)

Compresses a ~1,400-line `_v2` chapter tutorial into the two-file case-study format the
repo already uses in Phase 01. The v2 tutorial is the **only** source — never re-read the
Kindle/PDF book, and never invent facts the v2 chapter does not support.

**v3 is a compression, not a summary.** Every claim in the answer key must be traceable to
a specific v2 section. The job is selecting the highest-signal 7% of the chapter and
recasting it in the reference format — not paraphrasing the whole thing shorter.

## Canonical reference files (read these first, every run)

Treat these two as the format contract. Read them before generating anything; match their
section names, ordering, table columns, tone, and length.

- Worksheet: `06_Interview_Prep/FDE/1. Complete GEN AI FDE Interview System — Core + GenAI/01_CUSTOMER_DISCOVERY_AND_DECOMPOSITION/04_CASE_STUDY_WORKSHEET/01_internal_knowledge_assistant.md`
- Answer key: `.../04_CASE_STUDY_WORKSHEET/answer_keys/answer-keys-in-md/01_internal_knowledge_assistant_answer_key.md`

If a rule below ever conflicts with those files, the files win.

## Output layout

```
FDE_System_Design_Interview_20_Scenarios/Version_3/
  NN_<scenario_slug>.md                              <- blank practice worksheet
  answer_keys/
    NN_<scenario_slug>_answer_key.md                 <- filled answer key
```

- `NN` is the **chapter number from the v2 filename, zero-padded to 2** — preserve the
  original numbering, do not renumber sequentially. Chapters present: 01, 02, 03, 04, 07,
  09, 10, 11, 13, 15, 17, 21.
- `<scenario_slug>` is snake_case from the chapter title, with `chapter-N-`, `-tutorial`,
  `-condensed`, and `_v2` stripped. `chapter-3-natural-language-to-sql-analytics-assistant-tutorial_v2.md`
  → `03_natural_language_to_sql_analytics_assistant.md`.
- Never write into `Version_1/` or `Version_2/`. Never modify the v2 source file.
- If a target file already exists, ask before overwriting.

## Length and density targets (hard)

Line count alone is the **wrong instrument** and will let you ship a bad draft. In the
Chapter 1 trial run, both files matched the reference's line count exactly while running
1.3-1.9x too wordy per bullet — the shape was right and the writing was bloated. Always
check density, not just length.

| File | Lines | Bytes (vs reference) |
|---|---:|---:|
| Worksheet | 80-95 | ~3.0-3.4 KB |
| Answer key | 90-110 | ~12.4-13.5 KB |

Per-bullet word budgets, measured off the canonical reference. Stay within ~1.2x of these:

| Section | Words per bullet |
|---|---:|
| Worksheet §2 discovery questions | ~10 |
| Worksheet §6 architecture stage labels | ~4 (bare labels: `Citations:`, not `Grounding and citations:`) |
| Worksheet §8 failure modes | ~6 |
| Worksheet §9 rollout steps | ~5 |
| Worksheet §11 scorecard cells | ~3 |
| Key: discovery / functional / non-functional | ~19-20 |
| Key: architecture explanation | ~22 |
| Key: data model assumptions | ~25 |
| Key: red-team risks | ~19 |
| Key: rollout plan | ~17 |
| Key: weak / average / strong answer | ~44 / ~58 / ~103 words total |
| Key: final spoken answer | ~211 words total |

**Hard caps on the four sections that overshoot every single time.** In the Chapter 1, 2
and 3 runs, these same four failed the checker on the first draft. Write them at the cap
from the start rather than trimming later:

| Section | Cap | Example at the cap |
|---|---|---|
| Worksheet §1 prompt | 32 words total, 2 sentences | "Design a GenAI FDE solution for **X**. <one clause naming this chapter's pressure>." |
| Worksheet §8 failure modes | 6 words per bullet | `- Valid SQL, wrong business question` |
| Worksheet §9 rollout steps | 5 words per step | `- Ten governed metrics, named owners.` |
| Worksheet §10 weak / strong | 13 / 37 words | quote only, no trailing explanation |
| Key: weak answer | 50 words total | claim, then one `This is weak because...` sentence |

**The rule that produces these numbers: one clause per bullet, not two.** The most common
failure is writing a correct bullet and then appending a second clause explaining it. The
reference states and stops. If a bullet has an em-dash or a "because" in the middle, ask
whether the second half earns its place.

The worksheet in particular is **telegraphic prompts, not prose** — it is a form the
learner fills in, so its filled sections are terser than the answer key's, not just
shorter versions of the same sentences.

A v2 chapter is ~1,400 lines. Landing at ~180 lines total means **ruthless** cutting. If a
draft runs long, cut supporting detail — never drop a section.

## Part A — the worksheet (11 sections, exact order)

Mirror the reference exactly. Critically: **some sections ship pre-filled, some ship blank.**
The blank ones are what the learner practices on; the pre-filled ones are the answer
scaffold they check themselves against.

| # | Section | State | Contents |
|---|---|---|---|
| 1 | `## 1. Interview prompt` | Filled | One paragraph: "Design a GenAI FDE solution for **\<Scenario Name\>**." + one sentence naming this chapter's specific pressure (multi-tenancy, air-gap, batch scale, release gating…), drawn from v2 §1. |
| 2 | `## 2. Clarify the customer problem` | Filled | 5 discovery-question bullets, tailored to this scenario. |
| 3 | `## 3. Users and workflows` | **Blank** | Table `User \| Workflow \| Current pain \| AI assist opportunity \| Human approval needed?` — row labels filled from this chapter's real personas (v2 §1 stakeholder map), all other cells empty. |
| 4 | `## 4. Requirements` | **Blank** | `### Functional` with 3 empty `-` bullets; `### Non-functional` with labelled empty bullets: `Latency target:`, `Availability target:`, `Cost budget:`, `Security/privacy constraints:`, `Audit/compliance requirement:`. |
| 5 | `## 5. Data and integration map` | **Blank** | Table `Data source \| Format \| Owner \| Freshness \| Permission model \| Risk` with one empty row. |
| 6 | `## 6. Proposed architecture` | **Blank** | Lead line `Use one of the rendered diagrams as a base, then customize:` then empty labelled bullets. Relabel the 6 stages to this chapter's actual pipeline (v2 §4) rather than copying the RAG labels — e.g. for Chapter 10: `Batch intake:`, `Sharding:`, `Inference workers:`, `Retry/DLQ:`, `Evaluation:`, `Monitoring:`. Keep labels to 1-3 words; they are form field names, not descriptions. |
| 7 | `## 7. Evaluation plan` | Filled | Table `Metric \| Good threshold \| Bad threshold \| Test dataset \| Owner`, 4 rows, thresholds pulled from v2 §7 metrics. Right-align the two threshold columns (`---:`). |
| 8 | `## 8. Failure modes` | Filled | 6 bullets, this chapter's real failure modes from v2 §6. |
| 9 | `## 9. Rollout plan` | Filled | 6 numbered steps, condensed from v2 §7. |
| 10 | `## 10. Weak vs strong answer` | Filled | `**Weak:**` one quoted sentence; `**Strong:**` one quoted sentence. |
| 11 | `## 11. Candidate scorecard` | Filled, Score blank | Table `Area \| 1 \| 3 \| 5 \| Score`, 5 rows: Problem framing, Architecture, Evaluation, Production thinking, Communication. Score column empty. |

Title line: `# <Scenario Name> - Case Study Worksheet` (ASCII hyphen, matching the reference).

## Part B — the answer key (13 sections, exact order)

Title: `# <Scenario Name> - Answer Key`, then the standing intro paragraph:

> This answer key is designed for interview preparation. It shows what a strong GenAI FDE
> candidate should ask, design, evaluate, secure, and communicate before moving from demo
> to production.

Then, in order:

1. `## Strong discovery questions` — 8 bullets. Sharper than worksheet §2: each must be a
   question whose answer *changes the architecture*. Source: v2 §2.
2. `## Strong functional requirements` — 6 bullets. First bullet always states the core
   end-to-end workflow in one sentence. Source: v2 §2 + §4.
3. `## Strong non-functional requirements` — 6 bullets, each opening with a bold-free label
   and colon: `Latency:`, `Availability:`, `Security:`, `Compliance:`, `Reliability:`,
   `Cost:`. Put this chapter's real numbers here (v2 §3 SLOs/capacity).
4. `## Architecture explanation` — 8 bullets walking the request end-to-end in order
   (entry → auth/policy → ingestion/connectors → retrieval or core processing → reasoning →
   tool/action layer → evaluation → observability). Name this chapter's actual components
   and real vendor/system names from v2 §4. This is the densest section; still 8 bullets.
5. `## Data model / integration assumptions` — 5 bullets. **First bullet is the compressed
   schema line**: entity names with parenthesised fields, semicolon-separated, e.g.
   `Document(id, source, version, owner, acl, ...); Chunk(id, document_id, ...); AuditLog(...)`.
   Condense v2 §5's full DDL/Pydantic into that one line. Remaining 4 bullets each start
   with `Assume ` and state an integration assumption plus its consequence.
6. `## Red-team risks` — 6 bullets. First is a compact comma-separated list of this
   chapter's headline risks, written as a lowercase sentence fragment with no closing
   period (the reference does this deliberately — it reads as a tag list, not a sentence); the next 5 are one specific attack class each (injection,
   permission-boundary, exfiltration, unsafe automation, staleness/conflict — swap any that
   do not apply to this scenario for ones that do). Source: v2 §6.
7. `## Rollout plan` — 7 bullets on a week timeline: `Week 0-1:`, `Week 1-2:`, `Week 2-3:`,
   `Week 3-4:`, `Week 5:`, `Week 6-8:`, `After pilot:`. Source: v2 §7.
8. `## Evaluation plan` — table `Metric | What it proves | Strong threshold | Dataset / method`,
   6 rows. Distinct from the worksheet's 4-row table: more metrics, and a "what it proves"
   column instead of bad-thresholds. Last row is always latency/cost. Source: v2 §7.
9. `## Weak answer` — one paragraph in first person, then a closing sentence beginning
   `This is weak because it ignores ...` naming 5-6 omissions.
10. `## Average answer` — one paragraph, then `This is better, but still incomplete because ...`.
11. `## Strong answer` — one paragraph, first person, ending on the "the key is not just
    using GenAI, but ..." beat.
12. `## Interviewer scorecard` — table `Area | 1 - Weak | 3 - Average | 5 - Strong`, 8 rows:
    Problem framing, Requirements, Architecture, Data/integration, Evaluation,
    Safety/security, Rollout, Communication. (Note: 8 rows here vs. the worksheet's 5.)
13. `## Final 2-minute spoken answer` — ONE unbroken paragraph, ~200-260 words, written to
    be said aloud. Opens with `I would not start with the model.`, walks discovery →
    architecture → evaluation → rollout, and closes on production trustworthiness. This is
    the single most valuable artifact in the file — write it last, after everything above
    is settled, so it reflects the finished content.

## Diagrams

The reference docs carry none, and the default is none — Version_2 stays the home for the
chapter's ~12 diagrams. Add **at most one** mermaid diagram, in answer-key section 4
(`## Architecture explanation`), and only when the scenario's topology genuinely cannot be
followed from 8 ordered bullets — a fan-out/fan-in, a multi-plane split, a gated loop.

- Good candidates: Ch. 2 (tenant isolation planes), Ch. 10 (batch shard fan-out/fan-in),
  Ch. 13 (orchestration retry/compensation loop), Ch. 9 (release gate decision fork).
- Poor candidates: any linear request pipeline — the bullets already convey it.
- Keep it under 12 nodes and ~15 lines. Condense from the v2 diagram; do not paste it.
- Never add one to the worksheet — §6 there is deliberately blank for the learner.

## v2 → v3 source map

Every v2 chapter has the same skeleton. Pull from these sections:

| v2 section | Feeds |
|---|---|
| §1 Customer Problem and Discovery | Worksheet §1, §3 persona labels; key §1 |
| §2 Clarifying Questions, Requirements, Constraints | Worksheet §2, §4; key §1, §2, §3 |
| §3 Scale Estimates, SLOs, Capacity | Key §3 (real latency/availability/cost numbers) |
| §4 Architecture and End-to-End Flow | Worksheet §6 stage labels; key §4, optional diagram |
| §5 Data Model, APIs, Working Code | Key §5 (compressed to one schema line + assumptions) |
| §6 Security, Reliability, Failure Handling | Worksheet §8; key §6 |
| §7 Delivery Plan, Observability, Business Impact | Worksheet §7, §9; key §7, §8 |
| §8 Interview Walkthrough, Trade-Offs, Practice | Worksheet §10, §11; key §9-§13 |
| Coverage Notes | **Dropped** — v3 is a study artifact, not a self-review |

Chapter 21 is the condensed variant and additionally has a `## 0. The 60-Second Version` —
it is the best raw material for key §13 (final spoken answer).

## Anti-patterns

- **Reusing the reference's RAG content.** The reference is Chapter-1-shaped. A Chapter 7
  (air-gapped) key must not talk about Confluence connectors; a Chapter 10 (batch) key must
  not claim a 3-8 second interactive latency target. Re-derive every number and system name
  from the actual v2 chapter.
- **Keeping v2's code blocks.** No code in v3. Section 5's schema line replaces all of it.
- **Generic thresholds.** `>= 90%` is only correct if v2 says so. Go find the number.
- **Losing the tone.** The reference is declarative and calm — "Assume X", "Fail closed on
  Y". No hype, no second-person coaching, no emoji, no `🎯 Interview Pointer` callouts
  (those belong to the v2 format, not this one).
- **Padding to hit a section.** If v2 genuinely lacks material for a bullet slot, write a
  shorter section rather than inventing a fact.
- **The second clause.** The single most likely way this skill goes wrong: writing a
  correct bullet, then appending a clause that explains, justifies, or elaborates it. Every
  such bullet is individually defensible and the document still ends up 40% overweight.
  Compare against the budget table, not against your sense of whether the sentence is good.
- **Inventing numbers the chapter withholds.** Chapter 1 never states an absolute latency
  figure or groundedness percentage — it says "state it as a percentile against an agreed
  target" and "no sustained drop over 5 points from baseline." Reproduce that shape. Do not
  import the reference's `>= 90%` / `3-8 seconds`, which belong to a different scenario.

## Working order (per chapter)

1. Read the two canonical reference files (once per session is enough).
2. Read the full v2 chapter. Do not skim — the compression decisions need the whole thing.
3. Draft the **answer key** first — it forces the substantive decisions.
4. Derive the worksheet from it: the worksheet's filled sections are the key's content
   further compressed; its blank sections are the key's sections 2, 3, 4, 5 withheld.
5. Write key §13 last.
6. Run `scripts/check_density.py` and iterate until it prints `PASS`. Expect to tighten on
   the first pass — the draft that feels right is reliably too wordy.
7. Report per-chapter: line and byte counts for both files, the density result, and any v2
   content deliberately dropped.

## Verification (run before delivering each pair)

Run the bundled checker, which compares both new files against the canonical reference
pair on section names, bullet counts, and prose density:

```bash
python3 .claude/skills/fde-case-study-worksheet-v3/scripts/check_density.py \
  "06_Interview_Prep/FDE/1. Complete GEN AI FDE Interview System — Core + GenAI/01_CUSTOMER_DISCOVERY_AND_DECOMPOSITION/04_CASE_STUDY_WORKSHEET/01_internal_knowledge_assistant.md" \
  "06_Interview_Prep/FDE/1. Complete GEN AI FDE Interview System — Core + GenAI/01_CUSTOMER_DISCOVERY_AND_DECOMPOSITION/04_CASE_STUDY_WORKSHEET/answer_keys/answer-keys-in-md/01_internal_knowledge_assistant_answer_key.md" \
  "06_Interview_Prep/FDE/FDE_System_Design_Interview_20_Scenarios/Version_3/NN_<slug>.md" \
  "06_Interview_Prep/FDE/FDE_System_Design_Interview_20_Scenarios/Version_3/answer_keys/NN_<slug>_answer_key.md"
```

It exits non-zero and names every offending section. Iterate until it prints `PASS`.
Missing/extra sections, wrong bullet counts, any section over 1.25x the reference's
words-per-bullet, and an oversized file all fail. Table **row** counts only warn — a
chapter may genuinely have 4 personas or 6 data sources where the reference has 3.

Then run these content checks the script cannot do:

```bash
K=<answer-key-path>; W=<worksheet-path>
grep -c '^```' "$K"                                          # 0, unless the one allowed mermaid
grep -cE "Interview Pointer|Coverage Notes|Table of Contents" "$W" "$K"   # 0 0 — no v2 leftovers
grep -nE '^\|[^|]*\|\s*\|' "$W"                              # worksheet blanks really blank
```

Finally read both files end to end and confirm no sentence names a system, number, or
threshold the v2 chapter never states, and that §13 reads aloud in about two minutes.

## Batch mode

When asked to convert all of Version_2:

- Process one chapter at a time, in ascending chapter number, writing both files before
  moving on. Do not batch all 12 at the end.
- Create `Version_3/` and `Version_3/answer_keys/` on the first chapter.
- After the last chapter, write `Version_3/README.md`: one line of provenance (`Derived
  from Version_2 tutorials; source book: The Forward Deployed Engineer System Design
  Interview`), a one-line explanation of the worksheet/answer-key split, and an index table
  of `Chapter | Scenario | Worksheet | Answer key` with relative links.
