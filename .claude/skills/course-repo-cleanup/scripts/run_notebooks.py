#!/usr/bin/env python3
"""Execute notebooks end to end, the way Jupyter would, and report what failed.

Each notebook runs in its own folder (Jupyter's working directory) on the given kernel.
Cells tagged ``skip-execution`` (cell metadata ``tags``) are not run — use it for cells
that are deliberately not executed in automated runs (expensive API calls, interactive
input, long loops); the report lists them so they can be tracked.

Outputs are written back into the notebook, ready to commit when the run is clean (execution
counts 1..n, no errors); pass --no-write to leave files untouched.

Usage:
  uv run python run_notebooks.py NB.ipynb [NB2.ipynb ...] [--timeout 900] [--kernel python3]
                                 [--report report.json] [--no-write]
Exit 1 if any notebook failed.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError, CellTimeoutError, DeadKernelError

SKIP_TAG = "skip-execution"
SKIP_SOURCE = (
    'print("⏭️ Skipped in automated runs (tag: skip-execution) '
    '— see the notes above this cell.")'
)


def run_one(path: Path, kernel: str, timeout: int, write: bool) -> dict:
    nb = nbformat.read(path, as_version=4)
    runnable = copy.deepcopy(nb)
    skipped = []
    for i, cell in enumerate(runnable.cells):
        if cell.cell_type == "code" and SKIP_TAG in cell.get("metadata", {}).get("tags", []):
            cell.source = SKIP_SOURCE
            skipped.append(i)

    client = NotebookClient(
        runnable, timeout=timeout, kernel_name=kernel,
        resources={"metadata": {"path": str(path.parent)}}, allow_errors=False,
    )
    started = time.time()
    result = {"notebook": str(path), "status": "ok", "skipped_cells": skipped}
    try:
        client.execute()
    except (CellExecutionError, CellTimeoutError, DeadKernelError) as e:
        result["status"] = "error"
        failing = next(
            (i for i, c in enumerate(runnable.cells)
             if c.cell_type == "code"
             and any(o.get("output_type") == "error" for o in c.get("outputs", []))),
            None,
        )
        result["cell"] = failing
        if failing is not None:
            outs = runnable.cells[failing].outputs
            err = next(o for o in outs if o.get("output_type") == "error")
            result["error"] = f"{err.get('ename')}: {err.get('evalue')}"[:1500]
            result["cell_source"] = runnable.cells[failing].source[:1200]
        else:
            result["error"] = f"{type(e).__name__}: {str(e)[-1500:]}"
    result["seconds"] = round(time.time() - started, 1)

    if write:
        # copy outputs back, keeping the original source of skipped cells
        for orig, ran in zip(nb.cells, runnable.cells):
            if orig.cell_type == "code":
                orig.outputs = ran.get("outputs", [])
                orig.execution_count = ran.get("execution_count")
        nbformat.write(nb, path)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("notebooks", nargs="+")
    ap.add_argument("--kernel", default="python3")
    ap.add_argument("--timeout", type=int, default=900, help="seconds per cell")
    ap.add_argument("--report", default=None)
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()

    results = []
    for nb in a.notebooks:
        p = Path(nb).resolve()
        print(f"▶ {nb}", flush=True)
        r = run_one(p, a.kernel, a.timeout, not a.no_write)
        r["notebook"] = nb  # as given: reports get committed, absolute paths do not belong
        mark = "✅" if r["status"] == "ok" else "❌"
        extra = f" — skipped cells {r['skipped_cells']}" if r["skipped_cells"] else ""
        print(f"  {mark} {r['status']} in {r['seconds']}s{extra}", flush=True)
        if r["status"] != "ok":
            print(f"     cell {r.get('cell')}: {r.get('error', '')[:400]}", flush=True)
        results.append(r)

    if a.report:
        Path(a.report).write_text(json.dumps(results, indent=2, ensure_ascii=False))
    bad = [r for r in results if r["status"] != "ok"]
    print(f"\n{len(results) - len(bad)}/{len(results)} notebooks ran clean")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
