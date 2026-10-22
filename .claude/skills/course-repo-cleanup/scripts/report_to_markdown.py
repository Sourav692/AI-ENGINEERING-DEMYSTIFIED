#!/usr/bin/env python3
"""Turn run_notebooks.py's JSON report into a Markdown run report for the tracker.

Usage: report_to_markdown.py run-report.json [--title "Module 02"] [-o run-report.md]
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--title", default="Run report")
    ap.add_argument("-o", "--out", default=None)
    a = ap.parse_args()

    results = json.loads(Path(a.report).read_text())
    ok = sum(r["status"] == "ok" for r in results)
    lines = [
        f"# {a.title} — run report",
        "",
        f"Run on {date.today().isoformat()}: **{ok}/{len(results)} notebooks ran clean** "
        "(fresh kernel, top to bottom). Cells tagged `skip-execution` are listed; "
        "see `../../gaps/`.",
        "",
        "| Notebook | Result | Time (s) | Skipped cells | Error |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        name = Path(r["notebook"]).name
        mark = "✅ ok" if r["status"] == "ok" else f"❌ error (cell {r.get('cell')})"
        skipped = ", ".join(map(str, r.get("skipped_cells", []))) or "—"
        err = (r.get("error") or "").replace("|", "\\|").replace("\n", " ")[:200] or "—"
        lines.append(f"| `{name}` | {mark} | {r['seconds']} | {skipped} | {err} |")
    out = Path(a.out) if a.out else Path(a.report).with_suffix(".md")
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
