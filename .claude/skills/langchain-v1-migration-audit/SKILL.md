---
name: langchain-v1-migration-audit
description: >-
  Crawls a folder of Jupyter notebooks / Python files in this AI ENGINEERING repo,
  finds every LangChain 0.x pattern that breaks or is deprecated on LangChain 1.x
  (legacy chains, AgentExecutor/initialize_agent/create_react_agent, *Memory classes,
  moved imports, .text(), agent-node renames), and produces a prioritized, per-notebook
  migration PLAN — what to change, why, in what order, and at what effort. Use whenever
  the user asks which notebooks need updating for LangChain 1.x / v1, asks to audit or
  scan a folder for deprecated LangChain code, says "what breaks on langchain 1.x",
  "plan the langchain upgrade", "check this phase for old LangChain APIs", or points at
  a folder and asks what needs migrating. Always writes the plan to
  `.plan/<folder-name>_langchain_v1_plan.md` as a tickable checklist that survives across
  sessions. Plans by default — only edits notebooks when the user explicitly asks to apply
  the changes.
---

# LangChain 1.x Migration Audit

Produce a **plan**, not a diff. The default output of this skill is a markdown report the
user reads and approves; notebook edits happen only on an explicit follow-up ask.

Background reading (the "why" behind every rule):
`02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/LangChain_v0_vs_v1_Differences.md`.
Operational "what to write instead": `references/v0-to-v1-rewrite-map.md` — read it before
producing the plan, not after.

## Why this needs judgment, not just a grep

This repo is **teaching material**, so "deprecated" does not automatically mean "change it."
A notebook whose entire subject *is* `LLMChain` may legitimately keep `LLMChain` — repointed at
`langchain-classic` and labelled as legacy. A notebook that merely *used* `LLMChain` to summarize a
document should be rewritten as LCEL, because learners copy that code. The scanner cannot tell
these apart; you can, by reading the notebook's title and markdown cells. **Every plan must make
that call per notebook and say which it chose.** See §0 of the rewrite map.

## Process

### 1. Scope the crawl

Confirm the target path. If the user said "a folder" without naming one, ask — do not default to
scanning the whole repo (it's ~500 notebooks and the report becomes unusable). Reasonable units are
one phase (`02_LangChain_Fundamentals_and_Prompting/`) or one track
(`.../LangChain_Fundamentals/04_Chains/`).

`archive/` is skipped by default and should stay skipped unless asked — it is retired content.

Once the target is fixed, derive the **plan path** — you will need it in step 4:

```
<repo root>/.plan/<target-folder-name>_langchain_v1_plan.md
```

`<target-folder-name>` is the last path segment of the scanned target, verbatim
(`04_Chains` → `.plan/04_Chains_langchain_v1_plan.md`). Two exceptions:

- **Generic or repeated segment names** (`01_Foundations`, `LangGraph`, `src`) recur across phases —
  prefix with the owning phase so plans never collide:
  `.plan/10_Alternative_Agent_Frameworks__CrewAI__01_Foundations_langchain_v1_plan.md`.
- **A single file** as target → use the file stem.
- **Multiple targets** in one run → one plan file per target folder, not one merged file.

`.plan/` lives at the repo root. Create it if absent. It is a normal tracked folder — plans are
work-tracking artifacts the user re-reads between sessions, so do **not** add it to `.gitignore`
unless asked.

### 2. Run the scanner

```bash
python .claude/skills/langchain-v1-migration-audit/scripts/scan_langchain_v1.py \
  "<target folder>" --out "<scratchpad>/langchain_v1_audit.md"
```

Stdlib only, read-only, no LangChain import, no notebook execution. Useful flags:

- `--json` — machine-readable, when you want to aggregate or sort yourself.
- `--min-severity BREAKING` — hide MODERNIZE/INFO noise on a big folder.
- `--include-archive` — only if asked.
- Multiple paths are accepted: `... path/a path/b`.

Write the raw output to the scratchpad, then **read it** — do not paste it at the user. It is input
to your plan, not the plan.

Severities the scanner assigns:

| Severity | Meaning | Default disposition |
| --- | --- | --- |
| `BLOCKING` | ImportError/AttributeError on 1.x — the notebook does not run | must fix |
| `BREAKING` | imports fine, signature/behaviour changed — silently wrong | must fix |
| `MODERNIZE` | works (often via `langchain-classic`) but teaches the old idiom | editorial call |
| `INFO` | worth a look | usually note-only |

### 3. Verify before you plan

The scan is regex over source lines and **will** produce false positives. Before writing the plan,
open the notebooks that carry the heaviest findings and check:

- Is the hit in live code or in a markdown/commented "here's the old way" block?
  (The scanner skips comment lines but not prose that got pasted into a code cell.)
- Does the notebook already have a 1.x section? The report's "already uses" column
  (`create_agent`, `content_blocks`, `checkpointer`, `langchain_classic`) flags partial migrations —
  those need a consistency pass, not a rewrite.
- `ST-stream-agent-node` and `MEM-kwarg` are the loosest rules — confirm each one manually.
- `ST-pydantic-state` only matters if that state feeds `create_agent`. A Pydantic state on a
  hand-built `StateGraph` is fine and must not be flagged in your plan.

Drop what doesn't survive. A plan that sends the user to fix a non-problem costs more than a missed
MODERNIZE hit.

### 4. Write the plan file

**Always write the plan to disk** at the `.plan/` path derived in step 1 — every run of this skill
produces a plan file, even a short one, even when almost nothing needs changing ("scanned N files,
all clean" is a useful record that stops the folder being re-audited next month). Use `Write` for a
new plan; for a re-run over a folder that already has one, see step 6.

Then summarize it in chat in a few lines and link the path. Do **not** paste the whole plan into the
conversation — the file is the deliverable.

Start the file with this frontmatter block so re-runs can diff against it:

```markdown
# LangChain 1.x Migration Plan — <target folder name>

- **Target:** `<repo-relative path>`
- **Generated:** <YYYY-MM-DD>
- **Scanner:** `.claude/skills/langchain-v1-migration-audit/scripts/scan_langchain_v1.py`
- **Pinned versions at scan time:** langchain `<x>`, langchain-core `<x>`, langgraph `<x>`
  (read from `pyproject.toml`)
- **Files scanned / needing work:** `<n>` / `<m>`

<!-- rollup:start -->
- [ ] **Plan complete** — closes automatically when every task on its board is done
**Board:** _(not yet created — run `plan-to-tasks`)_
**Task progress:** _n/a_
<!-- rollup:end -->
```

Leave the `rollup` block exactly as written, markers included: `tasks.py rollup` rewrites
everything between them, and the **Plan complete** checkbox is machine-managed — never tick it
by hand. It goes green only when every task on the plan's board is closed and no review-gated
task closed without approval.

Then structure the body as:

1. **Verdict line** — how many files run today on 1.x, how many don't, and the single biggest theme.
2. **Prerequisites** — e.g. "`langchain-classic` is not in `pyproject.toml`; N notebooks need it.
   Adding a dep means editing **three** files: `pyproject.toml` (version floors, source of
   truth for *what* is a dependency), `requirements.txt` (resolver-verified pinned mirror),
   and `requirements.lock.txt` (regenerate:
   `uv pip compile requirements.txt --python-version 3.12 -o requirements.lock.txt`)."
3. **Waves** — the scanner already groups by wave (imports → agents → memory → chains → polish).
   Keep that order: it's dependency-ordered, and each wave is one repeated decision rather than N
   separate ones.
4. **Per-notebook checklist** — the part the user actually works from. Lead each row with a
   `- [ ]` checkbox so the plan doubles as a progress tracker across sessions:

   ```markdown
   ### Wave 4 — chains

   - [ ] `04_Chains/4.0_Basics_of_Chains.ipynb` — **BLOCKING** · effort **L** · *rewrite*
         `LLMChain` ×6 → `prompt | llm | StrOutputParser()`; narrative cells describe the
         chain-class model and need rewriting alongside.
   - [ ] `04_Chains/4.2_Advanced_Chains.ipynb` — **BLOCKING** · effort **M** · *repoint*
         Module's subject IS the legacy chain API; keep it, import from `langchain_classic`,
         add a "this is legacy — see 3.5 for the 1.x way" callout.
   ```

5. **Explicitly out of scope** — list what you checked and deliberately left alone (see §7 of the
   rewrite map: LCEL, prompt templates, output parsers, partner packages, hand-built StateGraphs).
   Naming these prevents the user re-auditing them later.

Effort buckets from the scanner: **S** = find/replace only · **M** = mechanical, one concept ·
**L** = conceptual rewrite (chains/agents/memory), the notebook's narrative markdown changes too.

Order within a wave by dependency, then by effort ascending — early wins first.

### 5. Only if asked: apply

If the user says apply/fix/do it, work **one wave at a time**, confirming after each. When editing:

- Use `NotebookEdit` for `.ipynb`. Never hand-edit notebook JSON with sed.
- **Markdown cells are part of the change.** A notebook that now uses `create_agent` but whose prose
  still explains `AgentExecutor` is worse than one that was left alone. Update the narrative.
- Follow the repo's notebook conventions from `CLAUDE.md`: `# Title` first cell, `##`/`###`
  hierarchy, `# ============ SECTION ============` banners, imports grouped stdlib → third-party →
  local, summary cell last.
- Respect the per-phase model-init convention: LangGraph-phase notebooks route through
  `from helpers import get_llm, get_embeddings`; `LangChain_Fundamentals/` and
  `RAG_Demystified`-sourced content instantiate clients directly **on purpose** — don't "fix" that.
- Don't execute notebooks to verify (API keys, cost). Verify by re-running the scanner and by
  reading the diff.
- Re-run the scanner at the end of each wave and report the delta.
- **Tick the boxes as you go.** After each notebook is done, `Edit` its `- [ ]` to `- [x]` in the
  plan file. The plan is the running state of the migration — leaving it stale is the main way this
  workflow breaks across sessions.

### 6. Re-running over a folder that already has a plan

If the `.plan/` file already exists, **read it first** and preserve what it records:

- Keep every `- [x]` already ticked — a fresh scan cannot tell "done" from "never had findings",
  and silently un-ticking completed work destroys the only record of it.
- Keep any *repoint* decisions already made; they were editorial calls, not scanner output.
- Overwrite the counts, frontmatter `Generated` date, and the unticked rows from the new scan.
- Add a short `## Changelog` entry at the bottom: date, what moved, what's newly flagged.

If the previous plan's decisions no longer make sense (a LangChain release changed the answer),
say so explicitly in the changelog rather than quietly rewriting the row.

## Handing off

This skill produces the plan and stops. Two companions consume it:

| Next step | Skill | Produces |
| --- | --- | --- |
| Turn the plan into tracked work | `plan-to-tasks` | `.tasks/<board>/` + `INDEX.md` |
| Turn the concepts into lessons | `plan-to-teaching-notebook` | new explainer notebooks |

After writing a plan, offer the board — a plan on its own has no state, so multi-session
migrations drift without one. If a board already exists for this target, re-running the audit
should feed its **existing** tasks (via `plan-to-tasks` §5), not spawn a parallel set.

## Extending the rules

Rules are a flat `RULES` list in `scripts/scan_langchain_v1.py` — each is
`R(id, severity, category, regex, what, fix)`. Add a rule when you hit a real 0.x pattern the scan
missed; keep the `id` prefix aligned with its category (`IMP-`, `AGT-`, `CHN-`, `MEM-`, `MSG-`,
`ST-`, `MSC-`) since the wave grouping keys off `category`. If you add a new category, add it to a
wave predicate too or its findings won't appear in the ordered plan.

When LangChain ships a change that invalidates a rule, fix the rule **and** the corresponding row in
`references/v0-to-v1-rewrite-map.md` — they are meant to stay in sync.
