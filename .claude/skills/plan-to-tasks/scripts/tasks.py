#!/usr/bin/env python3
"""Task-file bookkeeping for `.tasks/<board>/` boards.

The model decides HOW work splits into tasks (judgment). This script owns the
mechanical half: creating task files with a visible TODO checkbox and valid
frontmatter, flipping statuses, enforcing the review gate, regenerating INDEX.md,
and rolling completion back up into the source `.plan/` file.

Subcommands:
    new     create a task file
    set     update fields on an existing task (status, review, output, ...)
    index   regenerate <board>/INDEX.md from every task file's frontmatter
    list    print tasks as a table (filterable)
    next    print the next actionable task (unblocked, lowest id, todo)
    rollup  update the source plan file(s): task progress + plan-complete checkbox

Review gate: tasks of type `explainer` or `migration` cannot be set to
`status: done` unless `review: approved`. Use --force only to override
deliberately; it records the override in the log.

Examples:
    python tasks.py new .tasks/04_Chains --title "Repoint legacy chain imports" \\
        --type migration --wave 1 --effort S --plan .plan/04_Chains_langchain_v1_plan.md \\
        --targets 04_Chains/4.0_Basics_of_Chains.ipynb --rules IMP-chains
    python tasks.py set .tasks/04_Chains/T-003_*.md --review approved --review-rounds 2
    python tasks.py set .tasks/04_Chains/T-003_*.md --status done
    python tasks.py index .tasks/04_Chains
    python tasks.py rollup .tasks/04_Chains

Stdlib only. Never touches notebooks.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import glob
import re
import sys
from pathlib import Path

# Windows consoles default to cp1252; box-drawing and em dashes in output would
# raise UnicodeEncodeError. Force UTF-8 and degrade gracefully if unavailable.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


STATUSES = ["todo", "in-progress", "in-review", "blocked", "done", "wontfix"]
TYPES = ["prereq", "migration", "explainer"]
REVIEWS = ["n/a", "pending", "changes-requested", "approved"]
REVIEW_GATED_TYPES = {"explainer", "migration"}

STATUS_MARK = {"todo": "[ ]", "in-progress": "[~]", "in-review": "[?]",
               "blocked": "[!]", "done": "[x]", "wontfix": "[-]"}
REVIEW_MARK = {"n/a": "—", "pending": "⏳ pending",
               "changes-requested": "✗ changes requested", "approved": "✓ approved"}

LIST_FIELDS = {"targets", "rules", "depends_on"}
FIELD_ORDER = ["id", "title", "type", "status", "review", "review_rounds", "wave",
               "effort", "disposition", "plan", "targets", "rules", "depends_on",
               "output", "created", "updated"]

TODO_LINE_RE = re.compile(r"^- \[[ x~!?\-]\] .*$", re.M)


# --------------------------------------------------------------------------
# Frontmatter
# --------------------------------------------------------------------------
def parse_task(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path}: missing frontmatter")
    _, fm, body = text.split("---", 2)
    meta: dict = {}
    for line in fm.strip().splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if k in LIST_FIELDS:
            meta[k] = [x.strip() for x in v.strip("[]").split(",") if x.strip()]
        else:
            meta[k] = v
    return meta, body.lstrip("\n")


def render_task(meta: dict, body: str) -> str:
    lines = ["---"]
    for key in FIELD_ORDER:
        if key not in meta:
            continue
        val = meta[key]
        if key in LIST_FIELDS:
            val = "[" + ", ".join(val) + "]"
        lines.append(f"{key}: {val}")
    for key in sorted(set(meta) - set(FIELD_ORDER)):
        lines.append(f"{key}: {meta[key]}")
    lines += ["---", ""]
    return "\n".join(lines) + body.rstrip("\n") + "\n"


def todo_line(meta: dict) -> str:
    """The visible TODO checkbox at the top of every task file."""
    mark = STATUS_MARK.get(meta.get("status", "todo"), "[ ]")
    bits = [f"`{meta.get('status', 'todo')}`"]
    if meta.get("review", "n/a") != "n/a":
        bits.append(f"review: {REVIEW_MARK.get(meta['review'], meta['review'])}")
    rounds = meta.get("review_rounds", "0")
    if rounds and rounds != "0":
        bits.append(f"round {rounds}")
    return f"- {mark} **{meta.get('title', '')}** — " + " · ".join(bits)


def sync_todo_line(body: str, meta: dict) -> str:
    """Rewrite the first checkbox line so it always matches frontmatter."""
    new = todo_line(meta)
    lines = body.split("\n")
    for i, ln in enumerate(lines[:4]):
        if TODO_LINE_RE.match(ln):
            lines[i] = new
            return "\n".join(lines)
    return new + "\n\n" + body


def load_board(board: Path) -> list[tuple[Path, dict, str]]:
    out = []
    for f in sorted(board.glob("T-*.md")):
        try:
            out.append((f, *parse_task(f)))
        except ValueError as exc:
            print(f"warning: {exc}", file=sys.stderr)
    return out


def _slug(title: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", title).strip("_")[:48]


def _today() -> str:
    return _dt.date.today().isoformat()


# --------------------------------------------------------------------------
# new
# --------------------------------------------------------------------------
BODY_TEMPLATE = """{todo}

## Objective

{objective}

## Scope

Files in scope:

{files_block}

Findings this task closes: {rules}

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for {rules}
- [ ] Notebook narrative (markdown cells) matches the new code
{review_criteria}
## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_
"""


def cmd_new(args) -> int:
    board = Path(args.board)
    board.mkdir(parents=True, exist_ok=True)
    nums = [int(m.group(1)) for _, meta, _ in load_board(board)
            if (m := re.match(r"T-(\d+)", meta.get("id", "")))]
    tid = f"T-{max(nums) + 1 if nums else 1:03d}"
    gated = args.type in REVIEW_GATED_TYPES

    meta = {
        "id": tid,
        "title": args.title,
        "type": args.type,
        "status": "todo",
        "review": "pending" if gated else "n/a",
        "review_rounds": "0",
        "wave": args.wave or "-",
        "effort": args.effort or "-",
        "disposition": args.disposition or "n/a",
        "plan": args.plan or "-",
        "targets": args.targets.split(",") if args.targets else [],
        "rules": args.rules.split(",") if args.rules else [],
        "depends_on": args.depends_on.split(",") if args.depends_on else [],
        "output": args.output or "-",
        "created": _today(),
        "updated": _today(),
    }
    review_criteria = (
        "- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified\n"
        "- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close\n"
        if gated else
        "- [ ] No notebook executed by this task; no saved outputs committed\n"
    )
    body = BODY_TEMPLATE.format(
        todo=todo_line(meta),
        objective=args.objective or "_(fill in)_",
        files_block="\n".join(f"- `{t}`" for t in meta["targets"])
                    or "- _(none listed — fill in)_",
        rules=", ".join(f"`{r}`" for r in meta["rules"]) or "_n/a_",
        review_criteria=review_criteria,
    )
    path = board / f"{tid}_{_slug(args.title)}.md"
    path.write_text(render_task(meta, body), encoding="utf-8")
    print(f"Created {path}" + ("  [review-gated]" if gated else ""))
    return 0


# --------------------------------------------------------------------------
# set
# --------------------------------------------------------------------------
def cmd_set(args) -> int:
    paths = [Path(p) for pat in args.task for p in glob.glob(pat)]
    paths = paths or [Path(p) for p in args.task]
    missing = [p for p in paths if not p.exists()]
    if not paths or missing:
        print(f"error: no task files matched: {missing or args.task}", file=sys.stderr)
        return 2

    for path in paths:
        meta, body = parse_task(path)

        # --- review gate -------------------------------------------------
        if args.status == "done" and meta.get("type") in REVIEW_GATED_TYPES:
            if meta.get("review") != "approved" and not args.force:
                print(f"error: {path.name} is type '{meta.get('type')}' and cannot close "
                      f"with review='{meta.get('review', 'pending')}'.\n"
                      f"  Run the notebook-review skill, then:\n"
                      f"    tasks.py set {path} --review approved\n"
                      f"    tasks.py set {path} --status done\n"
                      f"  (--force overrides, and is recorded in the log)",
                      file=sys.stderr)
                return 3
            if meta.get("review") != "approved" and args.force:
                body = body.rstrip("\n") + (
                    f"\n\n- {_today()}: ⚠️ closed with --force, bypassing review "
                    f"(review was '{meta.get('review', 'pending')}')\n")

        for field in ("status", "review", "output", "effort", "wave",
                      "disposition", "type"):
            if (val := getattr(args, field)):
                meta[field] = val
        if args.review_rounds is not None:
            meta["review_rounds"] = str(args.review_rounds)
        if args.bump_round:
            meta["review_rounds"] = str(int(meta.get("review_rounds", "0") or 0) + 1)
        if args.add_depends:
            meta.setdefault("depends_on", [])
            meta["depends_on"] += [d for d in args.add_depends.split(",")
                                   if d not in meta["depends_on"]]
        if args.note:
            body = body.rstrip("\n") + f"\n\n- {_today()}: {args.note}\n"

        meta["updated"] = _today()
        body = sync_todo_line(body, meta)
        path.write_text(render_task(meta, body), encoding="utf-8")
        print(f"Updated {path.name} -> status={meta.get('status')} "
              f"review={meta.get('review')} round={meta.get('review_rounds')}")
    return 0


# --------------------------------------------------------------------------
# index
# --------------------------------------------------------------------------
def _bar(done: int, total: int, width: int = 24) -> str:
    if not total:
        return "n/a"
    filled = round(width * done / total)
    return "`" + "█" * filled + "░" * (width - filled) + f"` {done}/{total}"


def cmd_index(args) -> int:
    board = Path(args.board)
    tasks = load_board(board)
    if not tasks:
        print(f"error: no task files in {board}", file=sys.stderr)
        return 2

    counts: dict[str, int] = {}
    for _, meta, _ in tasks:
        s = meta.get("status", "todo")
        counts[s] = counts.get(s, 0) + 1
    total = len(tasks)
    done = counts.get("done", 0) + counts.get("wontfix", 0)
    done_ids = {m["id"] for _, m, _ in tasks if m.get("status") in ("done", "wontfix")}
    plans = sorted({m.get("plan", "-") for _, m, _ in tasks} - {"-"})

    out = [f"# Task board — {board.name}", ""]
    if plans:
        out.append("**Source plan(s):** " + ", ".join(f"`{p}`" for p in plans))
    out += [f"**Updated:** {_today()}", "",
            f"**Progress:** {_bar(done, total)}", ""]
    if done == total:
        out += ["> ✅ **Board complete** — every task closed. "
                "Run `tasks.py rollup` to close the plan.", ""]
    out += ["| Status | Count |", "| --- | --- |"]
    for s in STATUSES:
        if counts.get(s):
            out.append(f"| `{s}` | {counts[s]} |")
    out.append("")

    by_wave: dict[str, list] = {}
    for f, meta, _ in tasks:
        by_wave.setdefault(str(meta.get("wave", "-")), []).append((f, meta))

    for wave in sorted(by_wave, key=lambda w: (w == "-", w)):
        out += [f"## {'Wave ' + wave if wave != '-' else 'Unassigned'}", "",
                "| | ID | Task | Type | Effort | Disp. | Review | Blocked by | Output |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for f, meta in sorted(by_wave[wave], key=lambda x: x[1].get("id", "")):
            blockers = [d for d in meta.get("depends_on", []) if d not in done_ids]
            out.append(
                f"| {STATUS_MARK.get(meta.get('status', 'todo'), '[ ]')} "
                f"| [`{meta.get('id')}`]({f.name}) | {meta.get('title', '')} "
                f"| {meta.get('type', '-')} | {meta.get('effort', '-')} "
                f"| {meta.get('disposition', 'n/a')} "
                f"| {REVIEW_MARK.get(meta.get('review', 'n/a'), meta.get('review', '-'))} "
                f"| {', '.join(blockers) or '—'} | {meta.get('output', '-')} |")
        out.append("")

    out += ["---", "",
            "Regenerate with `python .claude/skills/plan-to-tasks/scripts/tasks.py index "
            f"{board.as_posix()}` — do not hand-edit this file; edit the task files' "
            "frontmatter instead."]
    (board / "INDEX.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Wrote {board / 'INDEX.md'} — {total} tasks, {done} closed.")
    return 0


# --------------------------------------------------------------------------
# rollup: board state -> plan file
# --------------------------------------------------------------------------
PLAN_STATUS_BLOCK = """<!-- rollup:start -->
- {mark} **Plan complete** — closes automatically when every task on its board is done
**Board:** `{board}`
**Task progress:** {bar}
**Last rollup:** {date}
<!-- rollup:end -->"""


def cmd_rollup(args) -> int:
    board = Path(args.board)
    tasks = load_board(board)
    if not tasks:
        print(f"error: no task files in {board}", file=sys.stderr)
        return 2

    by_plan: dict[str, list[dict]] = {}
    for _, meta, _ in tasks:
        by_plan.setdefault(meta.get("plan", "-"), []).append(meta)

    rc = 0
    for plan_path, metas in by_plan.items():
        if plan_path == "-":
            print("warning: tasks with no `plan:` field — not rolled up", file=sys.stderr)
            continue
        p = Path(plan_path)
        if not p.exists():
            print(f"warning: plan file not found: {p}", file=sys.stderr)
            rc = 1
            continue

        total = len(metas)
        closed = sum(1 for m in metas if m.get("status") in ("done", "wontfix"))
        # A gated task only counts as genuinely complete if review approved it.
        unapproved = [m["id"] for m in metas
                      if m.get("status") == "done"
                      and m.get("type") in REVIEW_GATED_TYPES
                      and m.get("review") != "approved"]
        complete = closed == total and not unapproved
        block = PLAN_STATUS_BLOCK.format(
            mark="[x]" if complete else "[ ]",
            board=board.as_posix(),
            bar=_bar(closed, total),
            date=_today(),
        )

        text = p.read_text(encoding="utf-8")
        if "<!-- rollup:start -->" in text:
            text = re.sub(r"<!-- rollup:start -->.*?<!-- rollup:end -->",
                          block.replace("\\", "\\\\"), text, flags=re.S)
        else:  # insert after the H1 title
            lines = text.split("\n")
            i = next((n for n, ln in enumerate(lines) if ln.startswith("# ")), -1)
            lines.insert(i + 1, "\n" + block)
            text = "\n".join(lines)
        p.write_text(text, encoding="utf-8")

        state = "COMPLETE" if complete else f"{closed}/{total} tasks closed"
        print(f"{p}: {state}")
        if unapproved:
            print(f"  blocked: {', '.join(unapproved)} marked done without review approval",
                  file=sys.stderr)
            rc = 1
    return rc


# --------------------------------------------------------------------------
# list / next
# --------------------------------------------------------------------------
def cmd_list(args) -> int:
    rows = [(m.get("id"), m.get("status"), m.get("type"), m.get("wave"),
             m.get("effort"), m.get("review"), m.get("title"))
            for _, m, _ in load_board(Path(args.board))
            if (not args.status or m.get("status") == args.status)
            and (not args.type or m.get("type") == args.type)
            and (not args.review or m.get("review") == args.review)]
    if not rows:
        print("(no matching tasks)")
        return 0
    for r in sorted(rows):
        # ASCII only: this goes to a Windows console that may be cp1252.
        print(f"{r[0]}  {STATUS_MARK.get(r[1], '[ ]')} {r[1]:<12} {r[2]:<10} "
              f"w{r[3]:<3} {r[4]:<2} {str(r[5]):<18} {r[6]}")
    return 0


def cmd_next(args) -> int:
    tasks = load_board(Path(args.board))
    done = {m["id"] for _, m, _ in tasks if m.get("status") in ("done", "wontfix")}
    cands = [(f, m) for f, m, _ in tasks
             if m.get("status") in ("todo", "changes-requested")
             or (m.get("status") == "in-progress" and m.get("review") == "changes-requested")]
    cands = [(f, m) for f, m in cands
             if all(d in done for d in m.get("depends_on", []))]
    if not cands:
        print("(nothing actionable — all open tasks are blocked, or board is complete)")
        return 0
    cands.sort(key=lambda x: (str(x[1].get("wave", "9")), x[1].get("id", "")))
    f, m = cands[0]
    print(f"{m['id']}  {m.get('title')}")
    print(f"  file:    {f}")
    print(f"  type:    {m.get('type')}   wave: {m.get('wave')}   "
          f"effort: {m.get('effort')}   disposition: {m.get('disposition')}")
    print(f"  review:  {m.get('review')} (round {m.get('review_rounds', '0')})")
    print(f"  targets: {', '.join(m.get('targets', [])) or '-'}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new")
    p.add_argument("board")
    p.add_argument("--title", required=True)
    p.add_argument("--type", choices=TYPES, default="migration")
    p.add_argument("--objective")
    p.add_argument("--wave")
    p.add_argument("--effort", choices=["S", "M", "L"])
    p.add_argument("--disposition", choices=["repoint", "rewrite", "n/a"])
    p.add_argument("--plan")
    p.add_argument("--targets")
    p.add_argument("--rules")
    p.add_argument("--depends-on")
    p.add_argument("--output")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("set")
    p.add_argument("task", nargs="+")
    p.add_argument("--status", choices=STATUSES)
    p.add_argument("--review", choices=REVIEWS)
    p.add_argument("--review-rounds", type=int)
    p.add_argument("--bump-round", action="store_true",
                   help="increment review_rounds by 1")
    p.add_argument("--output")
    p.add_argument("--effort", choices=["S", "M", "L"])
    p.add_argument("--wave")
    p.add_argument("--disposition", choices=["repoint", "rewrite", "n/a"])
    p.add_argument("--type", choices=TYPES)
    p.add_argument("--add-depends")
    p.add_argument("--note")
    p.add_argument("--force", action="store_true",
                   help="close a review-gated task without approval (logged)")
    p.set_defaults(func=cmd_set)

    for name, fn in (("index", cmd_index), ("rollup", cmd_rollup)):
        p = sub.add_parser(name)
        p.add_argument("board")
        p.set_defaults(func=fn)

    p = sub.add_parser("list")
    p.add_argument("board")
    p.add_argument("--status", choices=STATUSES)
    p.add_argument("--type", choices=TYPES)
    p.add_argument("--review", choices=REVIEWS)
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("next")
    p.add_argument("board")
    p.set_defaults(func=cmd_next)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
