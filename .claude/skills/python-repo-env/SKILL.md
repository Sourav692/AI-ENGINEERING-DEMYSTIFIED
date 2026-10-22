---
name: python-repo-env
description: Set up or repair one root-level uv environment for Python and notebook repositories. Use for environment setup, dependency repair, LangChain 1.x migration, notebook import failures, requirements exports, Jupyter kernels, or notebook-output hygiene. It centralizes dependencies, removes notebook installs, and verifies imports.
---

> **Paths:** `<skills-root>` means the folder that holds this skill — the parent of its base directory (e.g. `~/.claude/skills`, or a repo's `.claude/skills`). Sibling skills referenced below live there too.

# Python repo environment: one root uv env on LangChain 1.x, verified by real imports

This skill works from any install location (`~/.claude/skills`, or a repo's `.claude/skills`). Run its scripts as `<skills-root>/python-repo-env/scripts/...` with the target repo as the working directory.

## Non-negotiables (the user's standing rules)

1. **uv only.** Create, lock, sync, add and export with `uv` (`uv sync`, `uv add`, `uv lock`, `uv export`, `uv run`, `uv pip`). Don't use `pip install`, `python -m venv`, or conda anywhere — not in commands you run, not in README instructions, not in notebook cells you write. Mixing installers is how envs end up with packages the lock doesn't know about.
2. **LangChain 1.x.** `langchain`, `langchain-core`, `langgraph` (and partner packages like `langchain-openai`) must resolve to their 1.x lines. Never pin or downgrade to 0.x to make an old notebook work — migrate the notebook's code instead (table below). 0.x-era APIs that were removed from `langchain` 1.x live in **`langchain-classic`**; add it as a dependency when code needs them.
3. **No installs inside notebooks.** Not `!pip install`, `%pip install`, or `!uv pip install` — not even commented out, not even as markdown instructions. Every dependency is declared at the root (step 4).
4. **No Colab.** Notebooks run locally against the root `.venv`; no `google.colab` code, secrets or metadata (step 5 triage).
5. **Notebooks are committed with their outputs, from one clean run.** Learners read results on GitHub without API keys. An `nbstripout --keep-output --keep-count` *pre-commit hook* drops only metadata noise; a staged-copy check blocks partial runs, error outputs, key-like strings, workstation paths and oversized outputs (step 8). No nbstripout *git filter* — its flags live in `.git/config`, which clones don't share.
6. **One root env and one dependency definition.** `pyproject.toml` + `uv.lock` + `./.venv` at the repo root; `requirements.txt` at the root is *generated* by `uv export`. No per-module `requirements.txt` or `.venv`.
7. **Install the shared course helpers from GitHub.** Every environment created or repaired by this skill includes the public, immutable `aied-helpers` release tag. It supplies shared provider utilities such as `from aied_helpers import get_llm`; it is a normal root dependency, never copied into notebooks or installed ad hoc.

Why root-only: per-module files duplicate the root and drift (every fix made N times); any local package must be installed into every env; LLM stacks are hundreds of MB each; N envs means N Jupyter kernels. Optional extras go in `[dependency-groups]` (`uv sync --group X`). If the user asks for per-folder files, explain this briefly and recommend the root setup.

## Quick operations (repo already set up)

For a one-off request, run just the command — the full workflow below is for setting up or repairing a repo.

| Task | Command |
|---|---|
| Install / refresh everything | `uv sync` |
| Add a dependency | `uv add <pkg>` (dev tool: `uv add --dev <pkg>`) |
| Remove a dependency | `uv remove <pkg>` |
| Recreate a broken env | `rm -rf .venv && uv sync` |
| List installed packages | `uv pip list` |
| Run anything in the env | `uv run <cmd>` |
| No uv yet | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

Never commit `.venv/`.

## Workflow

### 1. Survey
- Read `pyproject.toml`, `uv.lock`, any `requirements*.txt` / `setup.py` / `environment.yml`, the README setup section, `requires-python`.
- Note local importable code (`src/<pkg>`) and whether pyproject builds it — `uv sync` then installs it editable.
- `git status` first, so you don't mix your edits with the user's uncommitted work (mention unrelated modified files; don't touch them).

### 2. Make pyproject the single source of truth
- No pyproject? `uv init --bare`, then `uv add -r requirements.txt` to import existing deps.
- Ensure the LangChain floor: `uv add "langchain>=1.0" "langchain-core>=1.0" "langgraph>=1.0"` (plus `langchain-classic>=1.0` if legacy agents/chains/hub are used). Remove any `<1` / `==0.x` constraints.
- Add the shared helpers package at its tested release tag:
  ```bash
  uv add "aied-helpers @ git+https://github.com/Sourav692/ai-engineering-demystified-shared.git@v0.1.0"
  ```
  For Hatch projects, allow this direct Git reference before locking:
  ```toml
  [tool.hatch.metadata]
  allow-direct-references = true
  ```
  Keep the tag pinned rather than tracking a branch. Update the tag only after testing the new shared-package release across the affected course repositories.
- Choose whether the repository itself is a distributable package before syncing. If it is notebooks, scripts, or documentation only and has no local importable package to ship, add:
  ```toml
  [tool.uv]
  package = false
  ```
  This prevents Hatch from trying to build an editable wheel with no package files. Do not set it for a repository that deliberately distributes local Python code; keep that project's explicit build-target configuration instead.
- Dev tooling (`jupyterlab`, `ipykernel`, `pytest`, `ruff`) → `uv add --dev`; niche extras → `uv add --group <name>`.
- Lower bounds in pyproject; exact pins come from the lock.

### 3. Build and confirm versions
```bash
uv lock && uv sync
uv run python -c "import langchain, langchain_core, langgraph; from importlib.metadata import version as v; print(v('langchain'), v('langchain-core'), v('langgraph'))"
uv run python -c "from aied_helpers import get_llm; print('aied-helpers available')"
```
All three LangChain packages must start with `1.`, and the shared-helper import must succeed. For a notebook-only project, `uv sync` must complete without attempting to build the repository itself; if Hatch reports that it cannot determine files to ship, confirm the repository has no local package and set `package = false` as above. If LangChain verification fails, find what's holding it back (`uv tree --invert --package langchain`) and fix that constraint. Do not invoke an LLM as part of environment verification: `get_llm()` needs `OPENROUTER_API_KEY` only when a notebook actually uses the default OpenRouter provider. The package intentionally does not load `.env`; notebooks should call `load_dotenv(find_dotenv(usecwd=True))` themselves before provider use.

### 4. Remove every install from notebooks
Notebooks never install packages — dependencies are handled only at the root (pyproject → uv.lock → requirements.txt). An install cell either downgrades the shared env (`!pip install langchain==0.3.14`) or adds packages the lock doesn't know about. Remove all of them, active *and* commented-out (learners uncomment them):
```bash
python3 <skills-root>/python-repo-env/scripts/strip_pip_installs.py --dry-run --all .   # review first
python3 <skills-root>/python-repo-env/scripts/strip_pip_installs.py --all .
```
The script strips `!pip`/`%pip`/`pip`/`!uv pip` install lines from code cells (with continuations and an orphaned `%%capture`), replaces them with a two-line pointer to `uv sync`, and clears stale install output. Before relying on the removal, handle what it reports:
- **Packages not in uv.lock** — for each, check the notebook actually uses it (grep for imports *and* runtime use; an import that's never instantiated doesn't count). Used → `uv add` it (to a group if it's niche), unused → drop it. Tell the user which you dropped and why.
- **Markdown mentions** — prose isn't auto-edited. Rewrite each by hand: packages already in the root env → "installed by `uv sync`"; optional ones → `uv add <pkg>` (plus e.g. `uv run playwright install chromium`). Also fix code comments that say "uncomment the pip installs".

Finish with `grep -lE 'pip3? install' $(git ls-files '*.ipynb')` returning nothing.

### 5. Prove it: execute every import
```bash
python3 <skills-root>/python-repo-env/scripts/audit_imports.py <repo-root-or-subfolder> [--exclude dir ...]
```
Parses every notebook code cell and `.py` file and actually runs each distinct import statement in the nearest `.venv` at or above the path, with the file's directory on `sys.path` (as Jupyter does). Reading imports by eye isn't enough — importing executes package `__init__`s, which is how hidden undeclared deps surface (e.g. `langchain_community`'s `load_tools` imports `mypy_extensions` without declaring it). Also grep for runtime-only deps no import reveals: `load_tools(["llm-math"])` → `numexpr`; `pd.read_excel` → `openpyxl`; `to_parquet` → `pyarrow`; Playwright browsers; `nltk.download`.

~1 min per few hundred statements. Triage:

| Result | Usually means | Action |
|---|---|---|
| MISSING, real PyPI package | undeclared dependency | `uv add <pip name>` (script suggests it; verify) |
| MISSING, matches a file the notebook writes (`%%writefile`) | created at runtime | ignore |
| MISSING, package is in an optional group | expected | ignore, or confirm the group lists it |
| `google.colab`, `kaggle_secrets` | hosted-notebook-only code | remove it: replace `userdata.get('KEY')` with `os.getenv('KEY')` after `load_dotenv()` (keys live in the root `.env`), delete unused imports, and strip `"colab"` metadata blocks from notebook and cell metadata |
| BROKEN (`ImportError`, submodule gone) | API moved in 1.x | migrate the import (table below) |

### LangChain 0.x → 1.x import migrations

| Old (fails on 1.x) | New |
|---|---|
| `from langchain.agents import AgentExecutor, create_tool_calling_agent, create_react_agent, create_structured_chat_agent` | `from langchain_classic.agents import ...` (or rewrite to `langchain.agents.create_agent`) |
| `from langchain import hub` | `from langchain_classic import hub` |
| `from langchain.chains import LLMChain, create_sql_query_chain, ...` | `from langchain_classic.chains import ...` |
| `from langchain.agents import load_tools` | `from langchain_community.agent_toolkits.load_tools import load_tools` |
| `from langchain.schema.runnable import X` | `from langchain_core.runnables import X` |
| `from langchain.schema import HumanMessage, ...` | `from langchain_core.messages import ...` |
| `from langchain.prompts import ...` | `from langchain_core.prompts import ...` |
| `from langchain_core.pydantic_v1 import BaseModel, Field` | `from pydantic import BaseModel, Field` (check for v1-only calls: `.dict()`, `@validator`, `class Config`) |
| `from langchain.memory import ...` | `from langchain_classic.memory import ...` (or LangGraph checkpointers) |

Verify every new path by importing it in the env before editing, and check current docs (Context7) for anything not in this table. `from langchain.tools import tool` still works in 1.x.

Editing notebooks: exact string replacement on the raw `.ipynb` JSON (or NotebookEdit), then re-parse the JSON. Never regenerate a notebook — it destroys outputs and metadata. Outputs are committed, so after editing a notebook's code re-run it top to bottom (`uv run python scripts/run_notebooks.py <nb>`) before committing — stale outputs next to changed code mislead learners, and a partial run fails step 8's check. Run the repo's tests (`uv run pytest`). After fixes: `uv lock && uv sync`, rerun the audit until only expected items remain.

### 6. Jupyter kernel
With `ipykernel` in the dev group, VS Code / Jupyter pick up `./.venv` directly. For a named kernel:
```bash
uv run python -m ipykernel install --user --name <repo-name> --display-name "Python (<repo-name>)"
```

### 7. Export requirements.txt
```bash
uv export --format requirements-txt --no-hashes --no-dev --no-emit-project -o requirements.txt
grep -E '^(langchain|langchain-core|langgraph)==' requirements.txt   # must all be 1.x
```
`--no-emit-project` keeps the local package out; it's installed with `uv pip install -e .`. Delete per-module requirement files the root now covers (show the user which first).

### 8. Notebook hygiene: outputs committed from a clean run + pre-commit
Goal: notebooks are committed **with** their outputs so learners can read results on GitHub; those outputs come from one clean top-to-bottom run and are safe to publish; metadata noise never reaches a commit — the same in every clone.

1. **Dev deps:** `uv add --dev nbstripout pre-commit`.
2. **No git filter.** `nbstripout --install` ignores `--keep-output`/`--keep-count`, and the filter command lives in `.git/config` (not shared), so a clone set up the old way silently strips outputs again. If the repo has one: `uv run nbstripout --uninstall --attributes .gitattributes` (removes the `.git/config` entries and the `.gitattributes` lines; delete `.gitattributes` if it ends up empty). Tell collaborators to run `uv run nbstripout --uninstall` once in existing clones.
3. **pre-commit config** — start from `<skills-root>/python-repo-env/assets/pre-commit-config.yaml` or merge it:
   - the `kynan/nbstripout` hook with `args: [--keep-output, --keep-count]` (keeps outputs and counts, drops kernel/widget metadata and timings; it may rewrite the file on disk — harmless, outputs stay — then `git add` again);
   - local hooks use `entry: uv run python scripts/...`, never bare `python` (missing on macOS outside a venv);
   - then `uv run pre-commit install`.
4. **Output check on the staged copy.** Repo has no notebook check → copy `assets/check_notebook_outputs.py` to `scripts/` (index-based, one `git cat-file --batch` call). Repo has its own check → replace any "has saved outputs" failure with the same rules: a notebook with no outputs passes (not run yet); with outputs, execution counts 1..n in cell order (cells tagged `skip-execution` and blank cells may be unexecuted), no `error` outputs, no API-key-like strings (anchor patterns with `(?<![\w-])` — URLs like `elon-musk-…` contain `sk-`), no workstation paths, ≤ ~2 MB of output. Read the index copy for tracked files, disk for untracked:
   ```python
   def committed_text(p: Path) -> str:
       rel = p.relative_to(ROOT).as_posix()
       r = subprocess.run(["git", "show", f":{rel}"], cwd=ROOT, capture_output=True)
       return r.stdout.decode("utf-8", "ignore") if r.returncode == 0 else p.read_text("utf-8", errors="ignore")
   ```
5. **A runner in the repo.** Contributors need a scripted clean run: ship `scripts/run_notebooks.py` (fresh kernel per notebook, run in its own folder, honours `skip-execution`, writes outputs back). Run with tracing switched off (`LANGSMITH_TRACING=false LANGCHAIN_TRACING_V2=false`).
6. **First commit of outputs:** run every notebook with the runner, check the working copies with the same rules (the check's function on disk files), fix or re-run what fails, then `git add` the notebooks and commit them separately from content changes. Never commit outputs from a half-run IDE session.
7. **Prove it** on one notebook (back it up, restore after): give it outputs with a gap in execution counts (`nbformat.read` → edit → `nbformat.write`) and a `/Users/<you>/x` stream output → `git add` → the check fails with both messages; restore and `git add` → passes.
8. **Docs:** README / CONTRIBUTING / docs setup: `uv run pre-commit install` next to `uv sync`; "notebooks ship with the outputs of a clean run"; how to regenerate outputs.

### 9. Document and report
- README setup, uv only: `uv sync` (main path), optional groups table, and the requirements.txt path:
  ```bash
  uv venv --python 3.12 && uv pip install -r requirements.txt && uv pip install -e .
  ```
  plus the `uv export` command that regenerates the file.
- Tell the user: what changed and why, LangChain/LangGraph versions resolved, final audit result, what remains expected-failing and why, what wasn't verified (notebooks needing API keys were import-checked, not executed). Don't commit unless asked.
