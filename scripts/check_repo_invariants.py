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
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = (".git/", "node_modules/", ".venv/", ".ipynb_checkpoints", "archive/")

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


# --------------------------------------------------------------------------
# 4. The path-anchored config root CLAUDE.md warns about. It broke silently
#    during the 2026-09-19 restructure and was caught only by hand.
# --------------------------------------------------------------------------
def check_path_anchors() -> None:
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
        notes.append("path-anchors        pyproject.toml")


# --------------------------------------------------------------------------
# 5. Interview prep and its website have one home: the separate
#    Forward-Deployed-Engineer-Interview-Prep repo (extracted 2026-09-29). That
#    folder held purchased vendor material and client stories behind .gitignore
#    rules, so a copy creeping back here is both a second home and a leak risk.
# --------------------------------------------------------------------------
EXTRACTED_PATHS = ("06_Interview_Prep", "site", ".website_plan")


def check_extracted_paths() -> None:
    try:
        tracked = subprocess.run(
            ["git", "ls-files", "--", *EXTRACTED_PATHS],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.splitlines()
    except Exception:  # noqa: BLE001
        return
    if tracked:
        fail(
            "extracted-paths",
            f"{len(tracked)} files tracked under an extracted path (first: {tracked[0]}) "
            "— interview prep lives in Forward-Deployed-Engineer-Interview-Prep",
        )
    notes.append(f"extracted-paths     {', '.join(EXTRACTED_PATHS)} hold no tracked files")


# --------------------------------------------------------------------------
# 6. Client names stay out of the public repo. Interview stories were written
#    from real engagements; on 2026-09-27 the raw stories were moved out of git
#    and every tracked copy was anonymised. This keeps
#    a name from creeping back. The names are stored as truncated SHA-256 hashes
#    so the check itself does not publish them. To add one:
#      python3 -c "import hashlib;print(hashlib.sha256(b'name').hexdigest()[:16])"
# --------------------------------------------------------------------------
PRIVATE_TERM_HASHES = {
    "4c0a5662800fe143",
    "1244b3bff02ad090",
    "71f566aba763fb76",
    "1c06dac3445835d5",
    "448d652ce23d269a",
    "0833a440e485344d",
}
# Files where a match is a different, public use of the same word (a vehicle maker
# in a Wikipedia dataset; a public card product in fictional shop data).
PRIVATE_TERM_ALLOW = {
    "02_Core/04_Retrieval_and_RAG/shared_data/wikidata_rag_demo.jsonl",
    "05_Projects/ShopUNow_Agentic_RAG_Capstone/data/billing_payments_data.json",
    "05_Projects/ShopUNow_Agentic_RAG_Capstone/sample_data.py",
}
TEXT_SUFFIXES = (
    ".md", ".py", ".ts", ".tsx", ".js", ".mjs", ".json", ".jsonl", ".html", ".css",
    ".ipynb", ".txt", ".yaml", ".yml", ".toml", ".excalidraw", ".csv", ".sql",
)


def check_private_terms() -> None:
    import hashlib

    try:
        tracked = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.splitlines()
    except Exception:  # noqa: BLE001
        return
    scanned = 0
    for rel in tracked:
        if rel in PRIVATE_TERM_ALLOW or not rel.lower().endswith(TEXT_SUFFIXES):
            continue
        path = ROOT / rel
        try:
            if path.stat().st_size > 3_000_000:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        scanned += 1
        for token in set(re.findall(r"[a-z0-9]+", text)):
            if 3 <= len(token) <= 12 and hashlib.sha256(token.encode()).hexdigest()[:16] in PRIVATE_TERM_HASHES:
                fail("private-terms", f"{rel}: contains a client name listed in PRIVATE_TERM_HASHES")
                break
    notes.append(f"private-terms       {scanned} tracked text files scanned for client names")


def main() -> int:
    nbs = live_notebooks()
    check_notebooks_valid(nbs)
    check_titles(nbs)
    check_data_refs(nbs)
    check_doc_paths()
    check_path_anchors()
    check_extracted_paths()
    check_private_terms()

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
