# Cleanup decisions template

Copy this structure verbatim into `.cleanup/<slug>_cleanup_decisions.md`. It is the file
`notebook-folder-cleanup` reads to know what it is allowed to do.

---

```markdown
---
plan: <slug>_cleanup_plan.md
slug: <slug>
decided: <YYYY-MM-DD>
round: 1
scope: per-id           # per-id | all
---

# Decisions — `<target>`

<One line: who decided what, in a sentence. E.g. "Approved the triage as proposed except
the two routing notebooks, which stay.">

## Round 1 — <YYYY-MM-DD>

| ID | Decision | Note |
| --- | --- | --- |
| NB-001 | approve | |
| NB-003 | keep | "05_router_basics is the only routing example I have — leave it" |
| NB-012 | defer | Wants to finish it first; revisit next pass |
| DUP-001 | approve | |
| MIG-002 | reject | Narrative depends on the old output; will rewrite the lesson later |
| Q-001 | answered | Finish it, don't retire — becomes keep (needs work) |

## Additional instructions

<Verbatim user instructions that don't map to any ID. One per line. Applied to the whole
run, after the per-ID decisions.>

- Don't touch anything under `03_Applied_Projects/` this pass.
```

---

## The decision vocabulary

| Decision | Meaning to the executor |
| --- | --- |
| `approve` | Do what the plan says for this ID |
| `reject` | Do nothing for this ID; leave the notebook exactly as it is |
| `keep` / `consolidate` / `retire` | Overturns the plan's verdict for an `NB-###` row |
| `defer` | Out of scope this run; survives into the next plan refresh |
| `answered` | For `Q-###` only — the Note holds the answer, and it unblocks the listed items |

## `scope: all`

When the user plainly says "approve everything", set `scope: all` in the frontmatter instead
of writing one row per ID. Still list, as rows, every ID they carved out — those rows win
over the blanket approval.

`scope: all` **does** approve retirements. That is exactly why it must come from an
unambiguous instruction, and never be inferred from "looks good" or "nice work".

## Rules

- **Only what the user actually said.** No inference from enthusiasm or silence.
- **Quote them** in the Note for any row overturning a verdict.
- **Append, never rewrite.** Round 2 gets its own `## Round 2` section; the later row for an
  ID wins, but round 1 stays visible.
- **Unknown ID = error.** Report it; do not guess which row was meant.
- **An ID with no row is not approved.** For `retire` that means it does not happen.
