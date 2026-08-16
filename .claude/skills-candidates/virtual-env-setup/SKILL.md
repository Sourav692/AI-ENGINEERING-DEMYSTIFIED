---
name: virtual-env-setup
description: >-
  Create and manage Python virtual environments using uv with pyproject.toml.
  Use when setting up the project, installing dependencies, adding new packages,
  or when the user mentions virtual env, venv, uv, or dependency management.
---

# Virtual Environment Setup with uv

## Prerequisites

- `uv` must be installed. If not found, install via: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- This project requires Python **>=3.12** (defined in `pyproject.toml`)

## Creating the Virtual Environment

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Common Operations

**Add a new dependency:**

```bash
# 1. Add to pyproject.toml under [project.dependencies]
# 2. Then sync:
uv pip install -e ".[dev]"
```

**Install only production deps:**

```bash
uv pip install -e .
```

**Recreate from scratch (if env is corrupted):**

```bash
rm -rf .venv
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"
```

**Check installed packages:**

```bash
uv pip list
```

**Add Additional Packages:**
Also install Dev dependencies and helpers/packages automatically. 

## Important Notes

- Always use `uv` instead of `pip` or `virtualenv` directly.
- The `pyproject.toml` at the project root is the single source of truth for all dependencies.
- Dev dependencies (pytest, jupyter, ipython) are in `[project.optional-dependencies.dev]` — install them with `.[dev]`.
- The project includes a `helpers/` package installed in editable mode via `-e`.
- Never commit the `.venv/` directory (already in `.gitignore`).
