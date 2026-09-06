# Cleanup plan template

Copy this structure verbatim into `.cleanup/<slug>_cleanup_plan.md`. Angle-bracket text is
a placeholder; everything else — headings, column order, ID prefixes — is the contract
`notebook-folder-cleanup` parses.

---

```markdown
---
target: <path/to/folder>
slug: <slug>
generated: <YYYY-MM-DD>
status: draft            # draft -> decided -> applied
notebooks: <n>
decisions: <slug>_cleanup_decisions.md    # may not exist yet
---

# Cleanup plan — `<target>`

<One paragraph: what this folder is, what shape it is in, and the single biggest problem.>

## Summary

| Verdict | Count |
| --- | --- |
| keep | <n> |
| keep (needs work) | <n> |
| consolidate | <n> |
| retire | <n> |

Blocking questions: <n> (see [Open questions](#open-questions))

## 1. Triage

One row per notebook. `Verdict` is a **proposal**; the decisions file overrides it.

| ID | Notebook | Verdict | Evidence | Superseded by |
| --- | --- | --- | --- | --- |
| NB-001 | `04_chains_scratch.ipynb` | retire | 3 cells with saved tracebacks; TODO on core path; no summary cell | `4.2_Advanced_Chains.ipynb` |
| NB-002 | `4.2_Advanced_Chains.ipynb` | keep | Complete, runs clean, 41% markdown | — |
| NB-003 | `05_router_basics.ipynb` | keep (needs work) | Only coverage of routing; 2 deprecated imports | — |

Evidence is facts from the inventory and from reading the notebook. Not adjectives.

## 2. Consolidations

One block per group. Say exactly what gets ported, cell by cell where it matters.

### DUP-001 — `<keep target>` ← `<to retire>`

- **Similarity**: <score>, driven by <what overlaps>
- **Keep**: `<notebook>` — <why this one>
- **Port across**: <the specific cells / examples / explanation that only exist in the other>
- **Then retire**: `<notebook>` (NB-###)

## 3. Library migrations

| ID | Notebook | Library | Old API | New API | Effort | Note |
| --- | --- | --- | --- | --- | --- | --- |
| MIG-001 | `03_agents.ipynb` | LangChain | `initialize_agent` | `create_agent` | M | Subject is agents, so rewrite — not a repoint |
| MIG-002 | `07_data.ipynb` | pandas | `df.append` | `pd.concat` | S | Narrative in cell 4 must change with it |
| MIG-003 | `09_torch.ipynb` | PyTorch | — | — | — | already current (pinned) — do not change |

Mark each as **rewrite** or **repoint**: a notebook whose *subject* is the legacy API keeps
it, repointed at `langchain-classic` and labelled. One that merely *used* it gets rewritten.

Flag any migration that changes behaviour or output numbers — that goes in the notebook too.

## 4. Formatting

| ID | Notebook | Missing / wrong |
| --- | --- | --- |
| FMT-001 | `03_agents.ipynb` | No H1 title cell; no Summary; 6 code cells without banners |

## 5. Open questions

Things a human has to answer. Each blocks only the items listed.

| ID | Question | Blocks |
| --- | --- | --- |
| Q-001 | `06_eval.ipynb` is the only coverage of RAGAS but is half-finished — retire or finish? | NB-012 |
| Q-002 | `08_crew.ipynb` needs `crewai>=0.90`, which the root env deliberately excludes | MIG-014 |

## 6. Not planned

What was deliberately left alone, and why. (Wrong-phase notebooks, `archive/` contents,
`langchain-0x-contrast` cells, anything gated on a pin.)

## Changelog

| Date | Change |
| --- | --- |
| <YYYY-MM-DD> | Initial plan, <n> notebooks |
```

---

## Rules that outlive the template

- **IDs are permanent.** Assigned once; never reused, never renumbered. A refresh adds new
  ones and marks vanished notebooks `(gone)` — it does not compact the numbering, because
  the decisions file points at these strings.
- **Rows are `- [ ]`-free on purpose here** — the tick state lives in the decisions file and
  the execution report, so the plan stays a stable description of *findings*.
- **Every `retire` row needs a `Superseded by`**, or an explicit `—` plus a matching `Q-###`.
- **A refresh preserves prose.** Keep any evidence or note text the user edited by hand.
