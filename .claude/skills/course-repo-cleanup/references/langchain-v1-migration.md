# LangChain 0.x → 1.x migration

Use this when a module's notebooks still use LangChain 0.x patterns. The scanner finds them; you
decide what to change. Rewrite rules live in `references/langchain-v1-rewrite-map.md`.

## Why this needs judgment, not just a grep

Course notebooks are **teaching material**, so "deprecated" does not automatically mean "change it."
A notebook whose entire subject *is* `LLMChain` may legitimately keep `LLMChain` — repointed at
`langchain-classic` and labelled as legacy. A notebook that merely *used* `LLMChain` to summarize a
document should be rewritten as LCEL, because learners copy that code. The scanner cannot tell
these apart; you can, by reading the notebook's title and markdown cells. **Make that call per
notebook and record it in the module's `plan.md`.** See §0 of the rewrite map.

## Run the scanner

```bash
python <skills-root>/course-repo-cleanup/scripts/scan_langchain_v1.py \
  "<module folder>" --out "<scratchpad>/langchain_v1_audit.md"
```

Stdlib only, read-only, no LangChain import, no notebook execution. Useful flags:

- `--json` — machine-readable, when you want to aggregate or sort yourself.
- `--min-severity BREAKING` — hide MODERNIZE/INFO noise on a big folder.
- `--include-archive` — only if asked.
- Multiple paths are accepted: `... path/a path/b`.

Write the raw output to the scratchpad, then **read it** — it is input to the module plan, not the plan.

| Severity | Meaning | Default disposition |
| --- | --- | --- |
| `BLOCKING` | ImportError/AttributeError on 1.x — the notebook does not run | must fix |
| `BREAKING` | imports fine, signature/behaviour changed — silently wrong | must fix |
| `MODERNIZE` | works (often via `langchain-classic`) but teaches the old idiom | editorial call |
| `INFO` | worth a look | usually note-only |

## Verify before you plan

The scan is regex over source lines and **will** produce false positives. Open the notebooks with
the heaviest findings and check:

- Is the hit in live code or in a markdown/commented "here's the old way" block?
  (The scanner skips comment lines but not prose pasted into a code cell.)
- Does the notebook already have a 1.x section? The report's "already uses" column
  (`create_agent`, `content_blocks`, `checkpointer`, `langchain_classic`) flags partial migrations —
  those need a consistency pass, not a rewrite.
- `ST-stream-agent-node` and `MEM-kwarg` are the loosest rules — confirm each one manually.
- `ST-pydantic-state` only matters if that state feeds `create_agent`. A Pydantic state on a
  hand-built `StateGraph` is fine.

Drop what doesn't survive. A plan that sends the user to fix a non-problem costs more than a missed
MODERNIZE hit. Apply the surviving fixes during the module's consolidate/format steps, then the
module run (step 9) proves them.

## Extending the rules

Rules are a flat `RULES` list in `scripts/scan_langchain_v1.py` — each is
`R(id, severity, category, regex, what, fix)`. Add a rule when you hit a real 0.x pattern the scan
missed; keep the `id` prefix aligned with its category (`IMP-`, `AGT-`, `CHN-`, `MEM-`, `MSG-`,
`ST-`, `MSC-`) since the wave grouping keys off `category`. When LangChain ships a change that
invalidates a rule, fix the rule **and** the matching row in `references/langchain-v1-rewrite-map.md`.
