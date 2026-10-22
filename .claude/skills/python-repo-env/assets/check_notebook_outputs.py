#!/usr/bin/env python3
"""Block commits whose *staged* notebooks carry outputs that are not from one clean run or
not safe to publish.

Notebooks are committed WITH their outputs (learners read them on GitHub). Copy this to
<repo>/scripts/check_notebook_outputs.py and run it from pre-commit (see
pre-commit-config.yaml next to this file). It checks the copy git will commit (the index
blob), not the working copy. A notebook with no outputs passes (not run yet). One with
outputs must have execution counts 1..n in cell order (cells tagged `skip-execution` and
empty cells may stay unexecuted), no error outputs, no API-key-like strings, no absolute
workstation paths, and at most MAX_OUTPUT_KB of output.

Run:  uv run python scripts/check_notebook_outputs.py      Exit 1 on any failure.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ABSOLUTE = re.compile(r"(?:/Users/[\w.-]+/|/home/[\w.-]+/|[A-Za-z]:\\\\?Users\\)")
SECRET = re.compile(
    r"(?<![\w-])(sk-(?:proj-)?[A-Za-z0-9_\-]{20,}|gsk_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_\-]{30,}"
    r"|lsv2_(?:pt|sk)_[A-Za-z0-9_]{20,}|dapi[0-9a-f]{20,}|tvly-[A-Za-z0-9\-]{16,}|hf_[A-Za-z0-9]{30,})"
)
MAX_OUTPUT_KB = 2048
FIX = ("re-run it top to bottom in a fresh kernel "
       "(e.g. `uv run python scripts/run_notebooks.py <nb>`), then `git add` it again")


def output_problems(cells: list[dict]) -> list[str]:
    """Why these saved outputs are not from one clean run or not safe to publish."""
    code = [c for c in cells if c.get("cell_type") == "code"]
    if not any(c.get("execution_count") or c.get("outputs") for c in code):
        return []  # not run yet
    expected = 1
    for c in code:
        n = c.get("execution_count")
        if n is None:
            tagged = "skip-execution" in (c.get("metadata", {}).get("tags") or [])
            if not (tagged or not "".join(c.get("source", [])).strip()):
                return [f"partial run: a code cell has no execution count ({FIX})"]
            continue
        if n != expected:
            return [f"execution counts not 1..n in order (found {n}, expected {expected}) ({FIX})"]
        expected += 1
    text = json.dumps([c.get("outputs", []) for c in code])
    problems = []
    if any(o.get("output_type") == "error" for c in code for o in c.get("outputs", [])):
        problems.append(f"has an error output ({FIX})")
    if SECRET.search(text):
        problems.append("an output contains an API-key-like string (remove it and rotate the key)")
    if len(text) > MAX_OUTPUT_KB * 1024:
        problems.append(f"outputs are {len(text) // 1024} KB (limit {MAX_OUTPUT_KB} KB)")
    return problems


def staged_notebooks() -> dict[str, str]:
    """{path: staged text} for every notebook in the index, read in one git call."""
    ls = subprocess.run(["git", "ls-files", "-s", "--", "*.ipynb"], cwd=ROOT,
                        capture_output=True, text=True, check=True).stdout.splitlines()
    entries = [(line.split()[1], line.split("\t", 1)[1]) for line in ls]
    if not entries:
        return {}
    shas = "".join(f"{sha}\n" for sha, _ in entries).encode()
    batch = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, capture_output=True,
                           input=shas, check=True).stdout
    out, pos = {}, 0
    for _, path in entries:
        header_end = batch.index(b"\n", pos)
        size = int(batch[pos:header_end].split()[2])
        start = header_end + 1
        out[path] = batch[start:start + size].decode("utf-8", errors="ignore")
        pos = start + size + 1  # blob is followed by a newline
    return out


def main() -> int:
    failures = []
    nbs = staged_notebooks()
    for path, text in sorted(nbs.items()):
        try:
            nb = json.loads(text)
        except json.JSONDecodeError as e:
            failures.append(f"{path}: invalid JSON ({e})")
            continue
        failures += [f"{path}: {p}" for p in output_problems(nb.get("cells", []))]
        m = ABSOLUTE.search(text)
        if m:
            failures.append(f"{path}: absolute workstation path -> {m.group(0)}")
    for f in failures:
        print(f"FAIL  {f}")
    print(f"{len(nbs)} staged notebooks checked, {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
