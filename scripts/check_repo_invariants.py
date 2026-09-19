#!/usr/bin/env python3
"""Assert the structural invariants this repo keeps breaking silently.

Every check here exists because the thing it guards actually broke, and broke
without any error surfacing — a folder rename, a half-finished migration, a
doc that kept claiming a path long after it stopped existing.

Run manually:   python3 scripts/check_repo_invariants.py
Wired into:     .pre-commit-config.yaml (local hook, runs on every commit)

Exit 0 = all good. Exit 1 = at least one invariant broken; each failure prints
the file and what it expected.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = (".git/", "node_modules/", ".venv/", ".ipynb_checkpoints", "archive/", "site/")

failures: list[str] = []
notes: list[str] = []


def fail(check: str, msg: str) -> None:
    entry = f"{check}: {msg}"
    if entry not in failures:  # the same anchor can appear on several lines
        failures.append(entry)


def live_notebooks() -> list[Path]:
    out = []
    for nb in ROOT.rglob("*.ipynb"):
        rel = str(nb.relative_to(ROOT))
        if any(s in rel for s in SKIP_DIRS):
            continue
        out.append(nb)
    return out


# --------------------------------------------------------------------------
# 1. Notebooks are openable. A 0-byte .ipynb sat in the repo for weeks.
# --------------------------------------------------------------------------
def check_notebooks_valid(nbs: list[Path]) -> None:
    for nb in nbs:
        rel = nb.relative_to(ROOT)
        if nb.stat().st_size == 0:
            fail("notebook-valid", f"{rel} is 0 bytes")
            continue
        try:
            json.loads(nb.read_text())
        except Exception as e:  # noqa: BLE001
            fail("notebook-valid", f"{rel} is not valid JSON ({type(e).__name__})")
    notes.append(f"notebook-valid      {len(nbs)} notebooks parsed")


# --------------------------------------------------------------------------
# 1b. Every notebook opens on a title. The convention in CLAUDE.md is a
#     '# Title' in the FIRST MARKDOWN CELL — cell 0 may legitimately be code
#     (imports, env setup). 142 notebooks were brought into line on 2026-09-19;
#     this keeps new ones from drifting back out.
#     A styled HTML <h1> counts: five notebooks title themselves that way
#     deliberately and there is no reason to rewrite them.
# --------------------------------------------------------------------------
H1_HTML = re.compile(r"<h1[ >]", re.I)


def check_titles(nbs: list[Path]) -> None:
    ok = 0
    for nb in nbs:
        try:
            doc = json.loads(nb.read_text())
        except Exception:  # noqa: BLE001
            continue
        mds = [c for c in doc.get("cells", []) if c.get("cell_type") == "markdown"]
        if not mds:
            fail("notebook-title", f"{nb.relative_to(ROOT)} has no markdown cell at all")
            continue
        src = "".join(mds[0].get("source", [])).strip()
        if src.startswith("# ") or H1_HTML.search(src):
            ok += 1
        else:
            fail(
                "notebook-title",
                f"{nb.relative_to(ROOT)} first markdown cell is not a '# Title' "
                f"(starts {src[:40]!r})",
            )
    notes.append(f"notebook-title      {ok} notebooks open on a title")


# --------------------------------------------------------------------------
# 2. Relative data/ references resolve. Content moved a directory deeper than
#    the paths inside it assumed — twice, in two different tracks.
#    URLs are stripped first: https://.../main/data/x.csv is not a local path.
# --------------------------------------------------------------------------
DATA_REF = re.compile(r"(?<![\w./-])((?:\.\./)*[A-Za-z_]*data)/(\S*)")
URL = re.compile(r"https?://\S+")

# Prose that happens to contain "<word>/<word>". These are English, not paths.
# Keyed on the whole matched token so a real path can never be silenced by accident.
PROSE_NOT_PATHS = {
    "data/AI",  # "Search a knowledge base for information about data/AI technologies."
}


def check_data_refs(nbs: list[Path]) -> None:
    ok = 0
    for nb in nbs:
        try:
            doc = json.loads(nb.read_text())
        except Exception:  # noqa: BLE001
            continue  # already reported by check_notebooks_valid
        for cell in doc.get("cells", []):
            if cell.get("cell_type") != "code":
                continue
            for line in cell.get("source", []):
                for m in DATA_REF.finditer(URL.sub("", line)):
                    token = (m.group(1) + "/" + m.group(2)).rstrip("\"'`),.;:")
                    if token in PROSE_NOT_PATHS:
                        continue
                    target = (nb.parent / m.group(1)).resolve()
                    if target.exists():
                        ok += 1
                    else:
                        fail(
                            "data-refs",
                            f"{nb.relative_to(ROOT)} -> {m.group(1)}/ does not exist "
                            f"(in {token!r})",
                        )
    notes.append(f"data-refs           {ok} references resolve")


# --------------------------------------------------------------------------
# 3. Index documents point at paths that exist. NOTEBOOK_INDEX and
#    THEORY_DOCS_INDEX both spent weeks naming folders that had been renamed.
# --------------------------------------------------------------------------
def check_doc_paths() -> None:
    idx = ROOT / "NOTEBOOK_INDEX.md"
    if idx.exists():
        headings = re.findall(r"^# Phase .*?\(`([^`]+)`\)", idx.read_text(), re.M)
        for h in headings:
            if not (ROOT / h).exists():
                fail("doc-paths", f"NOTEBOOK_INDEX.md phase heading -> {h} missing")
        notes.append(f"doc-paths           {len(headings)} phase headings checked")

    theory = ROOT / "THEORY_DOCS_INDEX.md"
    if theory.exists():
        heads = [
            h.split(" (")[0]
            for h in re.findall(r"^## (.+)$", theory.read_text(), re.M)
        ]
        for h in heads:
            if not (ROOT / h).exists():
                fail("doc-paths", f"THEORY_DOCS_INDEX.md heading -> {h} missing")
        notes.append(f"doc-paths           {len(heads)} theory headings checked")

    tmap = ROOT / "06_Interview_Prep/Study_Guides/TOPIC_DOCS_MAP.md"
    if tmap.exists():
        links = re.findall(r"\]\((\.\./\.\./[^)]+)\)", tmap.read_text())
        for link in links:
            target = (tmap.parent / urllib.parse.unquote(link)).resolve()
            if not target.exists():
                fail("doc-paths", f"TOPIC_DOCS_MAP.md link -> {link} missing")
        notes.append(f"doc-paths           {len(links)} topic-map links checked")


# --------------------------------------------------------------------------
# 4. The three path-anchored configs root CLAUDE.md warns about. All three
#    broke silently during the 2026-09-19 restructure and were caught only by
#    hand. A .gitignore rule whose path no longer exists is not an error —
#    it just quietly stops protecting anything.
# --------------------------------------------------------------------------
def check_path_anchors() -> None:
    gi = ROOT / ".gitignore"
    if gi.exists():
        for line in gi.read_text().splitlines():
            s = line.strip().lstrip("!")
            if not s or s.startswith("#"):
                continue
            if "06_Interview_Prep/FDE/" not in s:
                continue
            folder = s.split("/**")[0]
            if not (ROOT / folder).exists():
                fail(".gitignore", f"FDE anchor points at a missing folder: {folder}")

    sync = ROOT / "site/scripts/sync-content.mjs"
    if sync.exists():
        text = sync.read_text()
        m = re.search(r"join\(REPO_ROOT,\s*'([^']+)'\)", text)
        if m and not (ROOT / m.group(1)).exists():
            fail("sync-content.mjs", f"SOURCE_ROOT -> {m.group(1)} does not exist")
        for frag in re.findall(r"^\s*'([^']*Complete GEN AI FDE[^']*)',", text, re.M):
            if not (ROOT / "06_Interview_Prep/FDE" / frag).exists():
                fail("sync-content.mjs", f"hardcoded folder missing: {frag}")

    pyproject = ROOT / "pyproject.toml"
    if pyproject.exists():
        block = re.search(
            r"extend-exclude\s*=\s*\[(.*?)\]", pyproject.read_text(), re.S
        )
        if block:
            for p in re.findall(r'"([^"]+)"', block.group(1)):
                if p.strip("/").startswith(("archive", ".")):
                    continue
                if not (ROOT / p).exists():
                    fail("pyproject.toml", f"ruff extend-exclude -> {p} does not exist")
        notes.append("path-anchors        .gitignore / sync-content.mjs / pyproject.toml")


# --------------------------------------------------------------------------
# 5. Purchased third-party material stays out of git. The .gitignore anchor
#    that protects it broke once already; when it does, nothing complains —
#    the files simply become committable.
# --------------------------------------------------------------------------
def check_purchased_material() -> None:
    try:
        tracked = subprocess.run(
            ["git", "ls-files", "06_Interview_Prep/FDE"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.splitlines()
    except Exception:  # noqa: BLE001
        return
    binaries = [f for f in tracked if f.lower().endswith((".pdf", ".docx", ".pptx"))]
    if binaries:
        fail(
            "purchased-material",
            f"{len(binaries)} vendor binaries are tracked under 06_Interview_Prep/FDE "
            f"(first: {binaries[0]}) — the .gitignore anchor is not protecting them",
        )
    notes.append(f"purchased-material  {len(tracked)} FDE files tracked, 0 binaries expected")


def main() -> int:
    nbs = live_notebooks()
    check_notebooks_valid(nbs)
    check_titles(nbs)
    check_data_refs(nbs)
    check_doc_paths()
    check_path_anchors()
    check_purchased_material()

    for n in notes:
        print(f"  ok    {n}")
    if failures:
        print(f"\n  {len(failures)} invariant(s) broken:\n")
        for f in failures:
            print(f"  FAIL  {f}")
        print("\nThese are structural, not style. Fix the path or the doc, not the check.")
        return 1
    print("\n  all invariants hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
