#!/usr/bin/env python3
"""Inventory a folder of notebooks: completeness signals + duplicate clustering.

Usage:
    python inventory.py <folder> [--json] [--threshold 0.55]

Produces the evidence a triage decision needs — it does NOT decide. Nothing is
deleted, moved, or modified; this is read-only.

Per notebook it reports:
  * size          — total / code / markdown cell counts, source bytes
  * completeness  — title cell, summary cell, markdown-to-code ratio,
                    empty cells, cells that are only a banner comment
  * abandonment   — TODO/FIXME/XXX/HACK markers, `pass`-only cells, scratch
                    variable names, commented-out cell bodies, saved error
                    outputs, non-monotonic execution counts (ran out of order)
  * fingerprint   — imports, defined names, called symbols, headings

Then it clusters notebooks by fingerprint similarity (Jaccard over imports +
symbols + normalized headings) so near-duplicate coverage surfaces as pairs
above --threshold.

Exit 0 always (this is a report, not a gate).
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from itertools import combinations
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__",
             ".ipynb_checkpoints", ".databricks"}
ABANDON_MARKERS = re.compile(r"\b(TODO|FIXME|XXX|HACK|WIP|BROKEN|DOESN'?T WORK|"
                             r"not working|scratch|temp test|delete me)\b", re.I)
SCRATCH_NAMES = re.compile(r"\b(foo|bar|baz|tmp|temp|test123|asdf|xxx|aaa)\b")
STOPWORDS = {"the", "a", "an", "to", "of", "and", "with", "in", "for", "your",
             "part", "using", "how", "what", "why", "intro", "introduction"}


def strip_magics(src: str) -> str:
    out = []
    for line in src.split("\n"):
        s = line.lstrip()
        out.append("pass" if s.startswith(("!", "%", "?")) else line)
    return "\n".join(out)


def norm_heading(h: str) -> str:
    h = re.sub(r"[^a-z0-9 ]", " ", h.lower())
    return " ".join(w for w in h.split() if w not in STOPWORDS and len(w) > 2)


class Symbols(ast.NodeVisitor):
    def __init__(self):
        self.imports, self.defined, self.called = set(), set(), set()

    def visit_Import(self, n):
        for a in n.names:
            self.imports.add(a.name.split(".")[0])

    def visit_ImportFrom(self, n):
        if n.module:
            self.imports.add(n.module.split(".")[0])
        for a in n.names:
            self.called.add(a.name)

    def visit_FunctionDef(self, n):
        self.defined.add(n.name)
        self.generic_visit(n)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, n):
        self.defined.add(n.name)
        self.generic_visit(n)

    def visit_Call(self, n):
        f = n.func
        name = f.id if isinstance(f, ast.Name) else (
            f.attr if isinstance(f, ast.Attribute) else None)
        if name:
            self.called.add(name)
        self.generic_visit(n)


def analyse(path: Path) -> dict:
    try:
        nb = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"path": str(path), "unreadable": str(exc)}

    cells = nb.get("cells", [])
    sym = Symbols()
    headings: list[str] = []
    code_n = md_n = empty_n = banner_only_n = 0
    markers: list[str] = []
    err_outputs: list[int] = []
    exec_counts: list[int] = []
    commented_cells = 0
    src_bytes = 0
    syntax_errors = 0

    for i, c in enumerate(cells):
        raw = c.get("source", "")
        raw = "".join(raw) if isinstance(raw, list) else raw
        src_bytes += len(raw)
        body = raw.strip()

        if c.get("cell_type") == "markdown":
            md_n += 1
            if not body:
                empty_n += 1
            headings += [norm_heading(m) for m in
                         re.findall(r"^#{1,4}\s+(.+)$", raw, re.M)]
            continue

        code_n += 1
        if not body:
            empty_n += 1
            continue

        lines = [ln for ln in body.split("\n") if ln.strip()]
        if lines and all(ln.lstrip().startswith("#") for ln in lines):
            if len(lines) <= 4:
                banner_only_n += 1
            else:
                commented_cells += 1

        if (m := ABANDON_MARKERS.search(raw)):
            markers.append(f"cell {i}: {m.group(0)}")
        if SCRATCH_NAMES.search(raw):
            markers.append(f"cell {i}: scratch identifier")

        if c.get("execution_count") is not None:
            exec_counts.append(c["execution_count"])
        for out in c.get("outputs", []) or []:
            if out.get("output_type") == "error":
                err_outputs.append(i)
                break

        try:
            sym.visit(ast.parse(strip_magics(raw)))
        except SyntaxError:
            syntax_errors += 1

    first = cells[0] if cells else {}
    first_src = "".join(first.get("source", "")) if first else ""
    last = cells[-1] if cells else {}
    last_src = "".join(last.get("source", "")) if last else ""

    out_of_order = sum(1 for a, b in zip(exec_counts, exec_counts[1:]) if b < a)

    return {
        "path": str(path),
        "name": path.name,
        "cells": len(cells),
        "code_cells": code_n,
        "md_cells": md_n,
        "bytes": src_bytes,
        "has_title": first.get("cell_type") == "markdown"
                     and first_src.lstrip().startswith("# "),
        "has_summary": last.get("cell_type") == "markdown"
                       and bool(re.search(r"summary|recap|takeaway|next steps",
                                          last_src, re.I)),
        "md_ratio": round(md_n / len(cells), 2) if cells else 0,
        "empty_cells": empty_n,
        "banner_only_cells": banner_only_n,
        "fully_commented_cells": commented_cells,
        "syntax_error_cells": syntax_errors,
        "abandonment_markers": markers[:10],
        "cells_with_error_outputs": err_outputs,
        "executed_out_of_order": out_of_order,
        "imports": sorted(sym.imports),
        "defined": sorted(sym.defined),
        "called": sorted(s for s in sym.called if s[:1].isupper())[:40],
        "headings": [h for h in headings if h][:40],
    }


def dead_end_score(r: dict) -> tuple[int, list[str]]:
    """Heuristic only — the model decides. Higher = more suspicious."""
    score, why = 0, []
    if r.get("code_cells", 0) <= 2:
        score += 2; why.append("almost no code")
    if not r.get("has_title"):
        score += 1; why.append("no title cell")
    if not r.get("has_summary"):
        score += 1; why.append("no summary cell")
    if r.get("md_cells", 0) == 0:
        score += 2; why.append("zero markdown — no narrative")
    elif r.get("md_ratio", 0) < 0.15:
        score += 1; why.append("very little narrative")
    if r.get("abandonment_markers"):
        score += 2; why.append(f"{len(r['abandonment_markers'])} abandonment marker(s)")
    if r.get("cells_with_error_outputs"):
        score += 2; why.append(f"saved error outputs in "
                               f"{len(r['cells_with_error_outputs'])} cell(s)")
    if r.get("syntax_error_cells"):
        score += 3; why.append(f"{r['syntax_error_cells']} cell(s) don't parse")
    if r.get("fully_commented_cells", 0) >= 2:
        score += 1; why.append("multiple fully commented-out cells")
    if r.get("empty_cells", 0) >= 3:
        score += 1; why.append(f"{r['empty_cells']} empty cells")
    if r.get("bytes", 0) < 1200:
        score += 1; why.append("very small")
    return score, why


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a or b) else 0.0


def similarity(x: dict, y: dict) -> dict:
    imp = jaccard(set(x["imports"]), set(y["imports"]))
    sym = jaccard(set(x["called"]) | set(x["defined"]),
                  set(y["called"]) | set(y["defined"]))
    hed = jaccard(set(x["headings"]), set(y["headings"]))
    # symbols carry the most signal for "same concept"; imports are noisy
    # (every notebook imports os + dotenv), headings confirm.
    return {"imports": round(imp, 2), "symbols": round(sym, 2),
            "headings": round(hed, 2),
            "combined": round(0.25 * imp + 0.5 * sym + 0.25 * hed, 2)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=Path)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--threshold", type=float, default=0.55,
                    help="combined similarity above which a pair is reported")
    args = ap.parse_args()

    if not args.folder.exists():
        print(f"error: no such folder: {args.folder}", file=sys.stderr)
        return 2

    files = [p for p in sorted(args.folder.rglob("*.ipynb"))
             if not any(part in SKIP_DIRS for part in p.parts)]
    reports = [analyse(p) for p in files]
    good = [r for r in reports if "unreadable" not in r]

    for r in good:
        r["dead_end_score"], r["dead_end_reasons"] = dead_end_score(r)

    pairs = []
    for a, b in combinations(good, 2):
        s = similarity(a, b)
        if s["combined"] >= args.threshold:
            pairs.append({"a": a["name"], "b": b["name"], "scores": s,
                          "a_bytes": a["bytes"], "b_bytes": b["bytes"],
                          "shared_headings": sorted(
                              set(a["headings"]) & set(b["headings"]))[:8]})
    pairs.sort(key=lambda p: -p["scores"]["combined"])

    result = {"folder": str(args.folder), "notebooks": len(files),
              "unreadable": [r for r in reports if "unreadable" in r],
              "reports": reports, "duplicate_pairs": pairs}

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print(f"{args.folder}: {len(files)} notebook(s)\n")
    print("=== completeness / dead-end signals (higher score = more suspect) ===")
    for r in sorted(good, key=lambda x: -x["dead_end_score"]):
        flag = "!!" if r["dead_end_score"] >= 5 else ("! " if r["dead_end_score"] >= 3 else "  ")
        print(f"{flag} {r['dead_end_score']:>2}  {r['name']:<52} "
              f"{r['cells']:>3} cells ({r['code_cells']}c/{r['md_cells']}m)")
        for w in r["dead_end_reasons"]:
            print(f"          - {w}")
    for r in result["unreadable"]:
        print(f"!! ??  {r['path']}  UNREADABLE: {r['unreadable']}")

    print(f"\n=== possible duplicate coverage (combined >= {args.threshold}) ===")
    if not pairs:
        print("  none")
    for p in pairs:
        s = p["scores"]
        keep = p["a"] if p["a_bytes"] >= p["b_bytes"] else p["b"]
        print(f"  {s['combined']:.2f}  {p['a']}  <->  {p['b']}")
        print(f"          imports={s['imports']} symbols={s['symbols']} "
              f"headings={s['headings']}  (larger: {keep})")
        if p["shared_headings"]:
            print(f"          shared topics: {', '.join(p['shared_headings'][:5])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
