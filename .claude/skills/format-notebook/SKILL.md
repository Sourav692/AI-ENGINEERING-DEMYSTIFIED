---
name: format-notebook
description: >-
  The single owner of the educational Jupyter notebook format. Use when the user asks
  to clean up, reformat, restructure, or improve a .ipynb notebook, or when another
  skill (e.g. course-repo-cleanup) needs the format contract. Applies the title/objectives cell, a
  setup cell, one Part per learning objective, banner comments in code cells, markdown
  narrative between code, a summary with the next notebook, and removes duplicates.
---

# Reformat a Jupyter Notebook for Educational Use

Every teaching notebook follows the same skeleton, so a learner always knows where they are:
what they will learn, what they need, how to set up, the concept in small runnable parts, and a
recap that points to the next notebook. The skeleton is fixed; the content, emoji choices and
number of parts adapt to the topic.

This skill is the only definition of the format. Other skills link here instead of keeping their
own copy. Rules are numbered 1–9 and other skills cite them by number, so keep the numbering stable.

## When to Use

- User asks to "reformat", "clean up", "restructure", or "improve" a notebook.
- A notebook has been imported from Databricks or another platform and needs local cleanup
  (e.g., stripping `application/vnd.databricks.v1+cell` metadata).
- Notebook cells lack explanatory markdown or have inconsistent formatting.

## Formatting Rules

### 1. Title Cell (Cell 0 — Markdown)

Every notebook starts with a single markdown cell:

```markdown
# <Emoji> <Title: the one concept this notebook teaches>

## Learning Objectives
In this notebook, you will learn:
1. **<Concept>** - <one line: what the learner will be able to do>
2. ...

## Where this fits            ← optional; use when the notebook builds on / hands off to a neighbour
<2–3 sentences: what the previous notebook did, the one thing this one adds, what comes next>

## Prerequisites
- <concepts from earlier notebooks, named by file name — as reading, never as runtime dependencies>
- Dependencies installed with the repo's env command (e.g. `uv sync`) at the repository root
- `<API_KEY_NAME>` in the project-root `.env` (say which keys are optional, and when none are needed)
```

- Use a single relevant emoji in the H1 title.
- Keep learning objectives to 3-5 items, each bolded with a dash description. Each maps to a Part (rule 2).

### 2. Section Headers (Markdown Cells)

After the setup cell (rule 4), the body is **one Part per learning objective**. Insert a markdown
cell before every logical section of code. Use this hierarchy:

| Level | Use for | Example |
|-------|---------|---------|
| `##`  | Setup and major parts | `## 📦 Step 1: Environment Setup`, `## 🔧 Part 1: Built-in Tools` |
| `###` | Sub-sections within a part | `### 1.1 📚 Wikipedia Tool` |
| `####`| Minor sub-topics | `#### 🎨 Customizing Built-in Tools` |

Rules:
- Always put `---` on its own line at the top of a major (`##`) section to create a visual separator.
- Use one emoji per heading — pick from the set relevant to the content.
- Follow each heading with 2-5 sentences: the idea, why it matters, what the code below shows.
- For key concept sections, add a "Key Concepts" list or a "Key Insight" callout:

```markdown
### Key Concepts:
- **Term**: Definition

> **Key Insight**: <one-liner the learner should remember>
```

- Where a code cell's output needs interpretation, follow it with a short markdown cell that reads
  the output ("Compare the two schemas…", "Notice that…").

### 3. Code Cells

#### Banner Comments

Start every code cell with a section banner:

```python
# ============================================================================
# SECTION_NAME: Brief Description
# ============================================================================
```

- `SECTION_NAME` is UPPER_CASE, e.g., `ENVIRONMENT SETUP`, `WIKIPEDIA TOOL`, `TOOL CALLING`.
- Follow the banner with a 1-2 line comment explaining the purpose only when the code is non-obvious.

#### Inline Comments

- Comment for a learner, not a maintainer: only where the *why* is non-obvious. Do NOT narrate obvious code.
- Use `# ---` separator lines between logical blocks within a single cell.
- For configuration parameters, add inline comments explaining each option:

```python
wiki_api_wrapper = WikipediaAPIWrapper(
    top_k_results=3,           # Number of Wikipedia pages to return
    doc_content_chars_max=8000  # Max characters per document
)
```

#### Every cell shows something

Every cell ends by showing a result, a shape, or a confirmation line. Use emoji prefixes for output types:
- `✅` — success/completion
- `🤖` — LLM-related output
- `📋` — tool attributes / metadata
- `🔍` — search results
- `📄` — document content
- `⚠️` — warnings
- `❌` — errors (in try/except blocks)
- `🧮` — computation results
- `🔧` — tool execution

### 4. Setup Cell and Imports

The first section after the title is the setup: a short markdown intro, then one code cell.

```markdown
---
## 📦 Step 1: Environment Setup

<one sentence: what the setup cell does>
```
```python
# ============================================================================
# ENVIRONMENT SETUP: Load API keys and suppress warnings
# ============================================================================
import warnings

from dotenv import find_dotenv, load_dotenv

warnings.filterwarnings("ignore")

# Reads <KEY_NAMES> from the project-root .env
load_dotenv(find_dotenv(usecwd=True))

print("✅ Environment ready")
```

Group imports in this order:
1. Standard library (`os`, `sys`, `warnings`)
2. Third-party libraries (`pydantic`, `requests`, `rich`)
3. LangChain core (`langchain_core`, `langchain_community`)
4. Project helpers

Import project helpers from the installed helper package (installed by the env command). Use a
`sys.path.append(os.path.abspath(".."))` import only when the repo has no installable helper package.

### 5. LLM Initialization

If the notebook uses an LLM, the next code cell creates it through **the repo's single LLM factory**,
with the model named explicitly, and prints what it created. The repo's `CLAUDE.md` names the factory
(e.g. AIED repos: `aied_helpers.get_openai_llm(model="gpt-4o-mini")`).

```python
# ============================================================================
# LLM INITIALIZATION: <what the model is used for>
# ============================================================================
from <helpers_package> import <factory>

llm = <factory>(model="<model>")
# llm = <factory>(model="<alternative>")   ← optional: alternatives as comments

print(f"✅ LLM initialized: {llm.model_name}")
```

### 6. Summary Cell (Final Cell — Markdown)

End every notebook with a markdown summary:

```markdown
---
## 📝 Summary

In this notebook, we learned:

### 1. <Part 1 title>
- <1–3 bullets: the takeaway, not a replay of the steps>

### 2. <Part 2 title>
- ...

### Next Steps
- **`<next_notebook_file_name>`**: <what it adds>
```

Name the next notebook by file name, never by an old numbering scheme ("Notebook 6.2", "Chapter 3")
that doesn't exist in the repo.

### 7. Cleanup Rules

| Action | Details |
|--------|---------|
| **Delete duplicates** | Remove cells with identical or near-identical content. Keep the more complete version. |
| **Remove stale setup** | Delete commented-out `getpass`/`os.environ` blocks for API keys — keys come from `.env` via `python-dotenv`. |
| **Strip platform metadata** | Remove `application/vnd.databricks.v1+cell` metadata from cell metadata objects. |
| **Merge tiny cells** | Combine consecutive code cells that logically belong together (e.g., an import cell immediately followed by a one-line usage cell). |
| **Split overloaded cells** | If a single code cell does multiple unrelated things (e.g., defines a tool AND tests it AND customizes it), split into separate cells with markdown in between. |
| **Outputs** | Follow the repo's output policy. Default: reset `execution_count` to `null` and clear `outputs`. If the repo commits notebooks **with** outputs from one clean run (see the `python-repo-env` skill), re-run the notebook top to bottom instead of clearing. |
| **Normalize formatting** | Ensure consistent quote style, trailing newlines, and no trailing whitespace in source lines. |

### 8. No Installs in Notebooks

No `!pip install`, `%pip install` or `!uv pip install` cells — not even commented out. Dependencies
come from the repo's root environment (`pyproject.toml`; see `python-repo-env`). If the notebook needs
a package the environment lacks, add it to the environment and say so in Prerequisites.

### 9. Notebook-Level Rules

- **One concept per notebook.** If two notebooks teach the same thing, merge them; if one notebook teaches two unrelated things, split it or move one part to where it belongs.
- **Self-contained.** Every notebook has its own setup cell and defines every function, tool, class and variable it uses. It runs top to bottom in a fresh kernel without another notebook having run. References to other notebooks are for reading only.
- **Runnable, deterministic where possible.** Prefer stubs/simulated data for anything that isn't the point of the lesson; real APIs only where the lesson is about them.
- **No platform-specific code** (no Colab/Kaggle secrets).
- **Cells that must not run in automated runs** (paid heavy calls, interactive `input()`, long loops) get the cell tag `skip-execution` and a markdown note above them saying why and how to run them by hand.
- **Keep what works.** Restructure headings and add the missing skeleton pieces around existing, good content; do not rewrite explanations that are already clear.

## Checklist (Use as TodoWrite Items)

1. Add or fix the **title cell** (H1 + learning objectives + optional "Where this fits" + prerequisites) — rule 1
2. Add the **setup cell** and organize **imports** — rule 4
3. Create the **LLM** through the repo's factory, if used — rule 5
4. One **Part per objective**, with markdown headers before each logical code group — rule 2
5. Add **banner comments** and make every cell show something — rule 3
6. **Delete duplicate cells**, **merge/split** cells, remove stale setup, strip Databricks metadata — rule 7
7. Remove every **install** line — rule 8
8. Add the **summary cell** naming the next notebook by file name — rule 6
9. Apply the repo's **output policy** — rule 7
10. Check the **notebook-level rules** (one concept, self-contained, `skip-execution` tags) — rule 9
11. Final read-through for consistency and typos

## Reference

See the fully formatted sample notebook at `./notebook/sample.ipynb` for a concrete example of the
conventions applied to a Tools & Functions notebook.
