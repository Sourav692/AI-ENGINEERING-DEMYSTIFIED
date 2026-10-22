#!/usr/bin/env python3
"""Actually execute every import statement found in a repo's notebooks and .py files.

Runs each directory's imports inside the target interpreter (normally the repo's .venv),
with that directory on sys.path so sibling modules (e.g. `from math_utils import add`)
resolve like they do in Jupyter. Reports two kinds of failure:

  MISSING  ModuleNotFoundError  -> a package is not installed (possibly a hidden/undeclared
                                   transitive dependency; the missing name is reported)
  BROKEN   ImportError/other    -> the package is installed but the API moved
                                   (e.g. `from langchain import hub` on LangChain 1.x)

Usage:
  audit_imports.py [ROOT] [--python .venv/bin/python] [--exclude DIR ...] [--json]
Exit code 1 if anything failed.
"""

import argparse
import ast
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

DEFAULT_EXCLUDES = {".venv", "venv", ".git", "node_modules", "__pycache__", ".ipynb_checkpoints",
                    "build", "dist", ".tox", ".mypy_cache", ".ruff_cache", "site-packages"}

# import name -> PyPI name, for the common cases where they differ
PIP_NAMES = {
    "PIL": "pillow", "cv2": "opencv-python", "sklearn": "scikit-learn", "yaml": "pyyaml",
    "dotenv": "python-dotenv", "bs4": "beautifulsoup4", "faiss": "faiss-cpu",
    "mypy_extensions": "mypy-extensions", "dateutil": "python-dateutil", "docx": "python-docx",
    "pptx": "python-pptx", "fitz": "pymupdf", "Crypto": "pycryptodome", "jwt": "pyjwt",
    "magic": "python-magic", "serial": "pyserial", "google.generativeai": "google-generativeai",
    "attr": "attrs", "skimage": "scikit-image", "Levenshtein": "python-Levenshtein",
}

RUNNER = r"""
import importlib, importlib.util, json, sys, warnings
warnings.filterwarnings("ignore")
stmts = json.loads(sys.stdin.read())
out = []
for s in stmts:
    try:
        exec(s, {})
        out.append({"stmt": s, "ok": True})
    except ModuleNotFoundError as e:
        top = (e.name or "").split(".")[0]
        try:
            top_installed = bool(top) and importlib.util.find_spec(top) is not None
        except BaseException:
            top_installed = False
        # package present but submodule gone -> the API moved, not a missing install
        kind = "BROKEN" if top_installed and e.name != top else "MISSING"
        out.append({"stmt": s, "ok": False, "kind": kind, "module": e.name, "error": str(e)})
    except BaseException as e:
        out.append({"stmt": s, "ok": False, "kind": "BROKEN", "error": f"{type(e).__name__}: {e}"})
print(json.dumps(out))
"""


def source_chunks(path: Path):
    if path.suffix == ".py":
        yield path.read_text(errors="ignore")
        return
    try:
        nb = json.loads(path.read_text(errors="ignore"))
    except json.JSONDecodeError:
        return
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", "")
        src = "".join(src) if isinstance(src, list) else src
        # drop IPython magics / shell escapes so ast can parse the rest
        lines = ["" if l.lstrip().startswith(("!", "%", "?")) else l for l in src.splitlines()]
        yield "\n".join(lines)


def import_statements(code: str):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield ast.unparse(node)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module != "__future__":
            yield ast.unparse(node)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--python", default=None, help="interpreter to test with (default: nearest .venv at or above ROOT)")
    ap.add_argument("--exclude", nargs="*", default=[])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    py = args.python
    if not py:  # nearest .venv at or above ROOT, so auditing a subfolder uses the repo-root env
        for d in [root, *root.parents]:
            if (d / ".venv" / "bin" / "python").exists():
                py = str(d / ".venv" / "bin" / "python")
                break
        py = py or str(root / ".venv" / "bin" / "python")
    if not Path(py).exists():
        sys.exit(f"interpreter not found: {py} (run `uv sync` first or pass --python)")
    excludes = DEFAULT_EXCLUDES | set(args.exclude)

    by_dir = defaultdict(lambda: defaultdict(set))  # dir -> stmt -> {files}
    for f in list(root.rglob("*.ipynb")) + list(root.rglob("*.py")):
        if any(part in excludes for part in f.relative_to(root).parts):
            continue
        # files inside a local package import it by its top-level name, so run them from
        # the directory that *contains* the outermost package
        run_dir = f.parent
        while (run_dir / "__init__.py").exists() and run_dir != root:
            run_dir = run_dir.parent
        for chunk in source_chunks(f):
            for stmt in import_statements(chunk):
                by_dir[run_dir][stmt].add(str(f.relative_to(root)))

    failures = []
    for d, stmts in sorted(by_dir.items()):
        ordered = sorted(stmts)
        runner = f"import sys; sys.path.insert(0, {str(d)!r})\n" + RUNNER
        proc = subprocess.run([py, "-c", runner], input=json.dumps(ordered), cwd=d,
                              capture_output=True, text=True, timeout=900)
        if proc.returncode != 0:
            failures.append({"kind": "RUNNER", "dir": str(d.relative_to(root)), "error": proc.stderr[-2000:]})
            continue
        for r in json.loads(proc.stdout.strip().splitlines()[-1]):
            if not r["ok"]:
                r["files"] = sorted(stmts[r["stmt"]])
                if r["kind"] == "MISSING" and r.get("module"):
                    top = r["module"].split(".")[0]
                    r["pip_name"] = PIP_NAMES.get(r["module"], PIP_NAMES.get(top, top.replace("_", "-")))
                failures.append(r)

    if args.json:
        print(json.dumps(failures, indent=2))
    else:
        total = sum(len(s) for s in by_dir.values())
        print(f"Checked {total} import statements across {len(by_dir)} directories with {py}\n")
        for kind in ("MISSING", "BROKEN", "RUNNER"):
            items = [f for f in failures if f["kind"] == kind]
            if not items:
                continue
            print(f"== {kind} ({len(items)})")
            if kind == "MISSING":
                by_pkg = defaultdict(set)
                for f in items:
                    by_pkg[(f["module"], f["pip_name"])].update(f["files"])
                for (mod, pip), files in sorted(by_pkg.items()):
                    print(f"  {mod}  -> pip name: {pip}")
                    for src in sorted(files):
                        print(f"      in {src}")
                print()
                continue
            for f in items:
                if kind == "RUNNER":
                    print(f"  {f['dir']}: {f['error']}")
                    continue
                print(f"  {f['stmt']}\n      {f['error']}")
                for src in f["files"]:
                    print(f"      in {src}")
            print()
        if not failures:
            print("All imports succeed.")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
