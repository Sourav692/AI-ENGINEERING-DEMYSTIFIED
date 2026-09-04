#!/usr/bin/env python3
"""Resolve every path and pre-existing artifact for one end-to-end pipeline run.

Usage:
    python preflight.py "<target folder>" [--json] [--repo-root .]

Deterministic setup so the orchestrator never has to re-derive naming rules or
guess what already exists. Emits:

  * target        — resolved, repo-relative
  * board_name    — the shared slug for plan + board (phase-prefixed if generic)
  * plan_path     — .plan/<slug>_langchain_v1_plan.md      (exists? tasks already boarded?)
  * board_dir     — .tasks/<slug>/                          (exists? how many open tasks?)
  * run_log       — .plan/runs/<date>_<slug>.md
  * resume        — what a re-run should continue from rather than redo
  * scripts       — absolute paths to the four stage scripts, each verified present

Read-only apart from creating `.plan/`, `.plan/runs/` and `.tasks/` if missing.
Exit 0 on success, 2 if the target or a required script is missing.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


# Folder names that repeat across phases — a bare slug would collide, so these
# get prefixed with their owning phase (matches the audit skill's naming rule).
GENERIC_NAMES = {
    "01_foundations", "02_core_capabilities", "03_multi_agent_patterns",
    "04_applications", "src", "app", "notebooks", "examples", "langgraph",
    "langchain", "docs", "code", "codes", "data",
}

STAGE_SCRIPTS = {
    "scan": ".claude/skills/langchain-v1-migration-audit/scripts/scan_langchain_v1.py",
    "tasks": ".claude/skills/plan-to-tasks/scripts/tasks.py",
    "md_to_notebook": ".claude/skills/plan-to-teaching-notebook/scripts/md_to_notebook.py",
    "static_check": ".claude/skills/notebook-review/scripts/static_check.py",
}


def slug_for(target: Path, repo_root: Path) -> str:
    """Board/plan slug: the folder name, phase-prefixed when it would collide."""
    try:
        rel = target.resolve().relative_to(repo_root.resolve())
    except ValueError:
        rel = Path(target.name)
    parts = list(rel.parts)
    if target.is_file():
        parts[-1] = Path(parts[-1]).stem
    name = parts[-1]
    if name.lower() in GENERIC_NAMES and len(parts) > 1:
        name = "__".join(parts)
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")


def board_state(board_dir: Path) -> dict:
    if not board_dir.is_dir():
        return {"exists": False, "tasks": 0, "open": 0, "explainer_open": 0,
                "awaiting_review": 0}
    tasks, open_, expl, await_ = 0, 0, 0, 0
    for f in sorted(board_dir.glob("T-*.md")):
        text = f.read_text(encoding="utf-8", errors="replace")
        fm = text.split("---")[1] if text.startswith("---") else ""
        get = lambda k: (m.group(1).strip()  # noqa: E731
                         if (m := re.search(rf"^{k}:\s*(.*)$", fm, re.M)) else "")
        tasks += 1
        status, ttype, review = get("status"), get("type"), get("review")
        if status not in ("done", "wontfix"):
            open_ += 1
            if ttype == "explainer":
                expl += 1
        if ttype in ("explainer", "migration") and review != "approved" \
                and status not in ("wontfix",):
            await_ += 1
    return {"exists": True, "tasks": tasks, "open": open_,
            "explainer_open": expl, "awaiting_review": await_}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", type=Path)
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = args.repo_root.resolve()
    target = args.target if args.target.is_absolute() else root / args.target
    if not target.exists():
        print(f"error: target does not exist: {target}", file=sys.stderr)
        return 2

    missing = [s for s in STAGE_SCRIPTS.values() if not (root / s).exists()]
    if missing:
        print("error: pipeline stage script(s) missing:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        return 2

    slug = slug_for(target, root)
    plan_path = root / ".plan" / f"{slug}_langchain_v1_plan.md"
    board_dir = root / ".tasks" / slug
    run_log = root / ".plan" / "runs" / f"{_dt.date.today().isoformat()}_{slug}.md"

    for d in (root / ".plan", root / ".plan" / "runs", root / ".tasks"):
        d.mkdir(parents=True, exist_ok=True)

    bs = board_state(board_dir)
    plan_exists = plan_path.exists()

    if not plan_exists:
        resume = "stage-1"          # nothing yet: full run
    elif not bs["exists"]:
        resume = "stage-2"          # plan written, no board
    elif bs["open"]:
        resume = "stage-3"          # board has open work
    else:
        resume = "complete"         # everything closed; re-run only refreshes the scan

    ctx = {
        "target": str(target.relative_to(root)).replace("\\", "/")
                  if target.is_relative_to(root) else str(target),
        "target_abs": str(target),
        "is_file": target.is_file(),
        "slug": slug,
        "plan_path": str(plan_path.relative_to(root)).replace("\\", "/"),
        "plan_exists": plan_exists,
        "board_dir": str(board_dir.relative_to(root)).replace("\\", "/"),
        "board": bs,
        "run_log": str(run_log.relative_to(root)).replace("\\", "/"),
        "resume_from": resume,
        "scripts": {k: v for k, v in STAGE_SCRIPTS.items()},
        "date": _dt.date.today().isoformat(),
    }

    if args.json:
        print(json.dumps(ctx, indent=2))
    else:
        print(f"target      : {ctx['target']}")
        print(f"slug        : {slug}")
        print(f"plan        : {ctx['plan_path']}  "
              f"({'exists' if plan_exists else 'new'})")
        print(f"board       : {ctx['board_dir']}  "
              f"({bs['tasks']} tasks, {bs['open']} open, "
              f"{bs['explainer_open']} explainer open, "
              f"{bs['awaiting_review']} awaiting review)")
        print(f"run log     : {ctx['run_log']}")
        print(f"resume from : {resume}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
