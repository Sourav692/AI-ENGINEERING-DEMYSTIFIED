---
name: Format_Python_Notebook
description: >-
  Reformat Jupyter notebooks for educational readability. Use when the user asks
  to clean up, reformat, restructure, or improve a .ipynb notebook. Applies
  consistent heading hierarchy, section banners in code cells, markdown
  narrative between code, and removes duplicates.
---

# Reformat a Jupyter Notebook for Educational Use

Transform raw or messy Jupyter notebooks into clean, well-structured educational
materials following the conventions established in this project.

## When to Use

- User asks to "reformat", "clean up", "restructure", or "improve" a notebook.
- A notebook has been imported from Databricks or another platform and needs
  local cleanup (e.g., stripping `application/vnd.databricks.v1+cell` metadata).
- Notebook cells lack explanatory markdown or have inconsistent formatting.

## Formatting Rules

### 1. Title Cell (Cell 0 — Markdown)

Every notebook must start with a single markdown cell containing:

```markdown
# <Emoji> <Title>

## Learning Objectives
In this notebook, you will learn:
1. **<Topic>** - <one-line description>
2. ...

## Prerequisites
- <prerequisite 1>
- <prerequisite 2>
```

- Use a single relevant emoji in the H1 title.
- Keep learning objectives to 3-5 items, each bolded with a dash description.
- List real prerequisites (packages, API keys, prior notebooks).

### 2. Section Headers (Markdown Cells)

Insert a **markdown cell before every logical section** of code. Use this
hierarchy:

| Level | Use for | Example |
|-------|---------|---------|
| `##`  | Major parts (Part 1, Part 2…) | `## 🔧 Part 1: Built-in Tools` |
| `###` | Sub-sections within a part | `### 1.1 📚 Wikipedia Tool` |
| `####`| Minor sub-topics | `#### 🎨 Customizing Built-in Tools` |

Rules:
- Always prefix with `---` on its own line at the top for major (`##`) sections
  to create a visual separator.
- Use one emoji per heading — pick from the set relevant to the content.
- Include a 2-4 sentence description after each heading explaining *what* and *why*.
- For key concept sections, add a "Key Concepts" or "Key Insight" callout:

```markdown
### Key Concepts:
- **Term**: Definition
```

or

```markdown
> **Note**: Important callout here.
```

### 3. Code Cells

#### Banner Comments

Start every code cell with a section banner:

```python
# ============================================================================
# SECTION_NAME: Brief Description
# ============================================================================
```

- `SECTION_NAME` should be UPPER_CASE, e.g., `ENVIRONMENT SETUP`, `WIKIPEDIA TOOL`,
  `CUSTOM TOOLS`, `TOOL CALLING`.
- Follow the banner with a 1-2 line comment explaining the purpose (only when
  the code is non-obvious).

#### Inline Comments

- Add comments only where the *why* is non-obvious. Do NOT narrate obvious code.
- Use `# ---` separator lines between logical blocks within a single cell.
- For configuration parameters, add inline comments explaining each option:

```python
wiki_api_wrapper = WikipediaAPIWrapper(
    top_k_results=3,           # Number of Wikipedia pages to return
    doc_content_chars_max=8000  # Max characters per document
)
```

#### Confirmation Prints

End setup/initialization cells with a confirmation print:

```python
print("✅ Warnings suppressed successfully!")
```

Use emoji prefixes for different output types:
- `✅` — success/completion
- `🤖` — LLM-related output
- `📋` — tool attributes / metadata
- `🔍` — search results
- `📄` — document content
- `⚠️` — warnings
- `❌` — errors (in try/except blocks)
- `🧮` — computation results
- `🔧` — tool execution

### 4. Import Organization

Group imports in this order within setup cells:

1. Standard library (`os`, `sys`, `warnings`)
2. Third-party libraries (`pydantic`, `requests`, `rich`)
3. LangChain core (`langchain_core`, `langchain_community`)
4. Project helpers (`helpers.utils`)

Add the `sys.path.append` pattern when importing from `helpers/`:

```python
import os, sys
sys.path.append(os.path.abspath(".."))
from helpers.utils import get_llm
```

### 5. LLM Initialization

Use the project's helper functions. Show the active choice and list alternatives
as comments:

```python
llm = get_databricks_llm("databricks-gemini-2-5-pro")
# llm = get_groq_llm()
# llm = get_openai_llm()
```

Always print which model was loaded after initialization.

### 6. Summary Cell (Final Cell — Markdown)

End every notebook with a markdown summary:

```markdown
---
## 📝 Summary

In this notebook, we learned:

### 1. <Section Title>
- **Key point**: Brief explanation
- ...

### Next Steps
- <What to do next, link to next notebook if applicable>
```

### 7. Cleanup Rules

| Action | Details |
|--------|---------|
| **Delete duplicates** | Remove cells with identical or near-identical content. Keep the more complete version. |
| **Remove stale setup** | Delete commented-out `getpass`/`os.environ` blocks for API keys — the project uses `.env` via `python-dotenv`. |
| **Strip platform metadata** | Remove `application/vnd.databricks.v1+cell` metadata from cell metadata objects. |
| **Merge tiny cells** | Combine consecutive code cells that logically belong together (e.g., an import cell immediately followed by a one-line usage cell). |
| **Split overloaded cells** | If a single code cell does multiple unrelated things (e.g., defines a tool AND tests it AND customizes it), split into separate cells with markdown in between. |
| **Clear outputs** | Reset `execution_count` to `null` and clear `outputs` arrays so the notebook is clean for the learner to run fresh. |
| **Normalize formatting** | Ensure consistent quote style, trailing newlines, and no trailing whitespace in source lines. |

### 8. Optional Install Cell

If the notebook uses packages beyond `pyproject.toml`, include a commented-out
pip install cell right after the environment setup cell:

```python
# ============================================================================
# OPTIONAL: Install Required Packages
# ============================================================================
# Uncomment and run if packages are not installed
# !pip install <package1> <package2>
```

## Checklist (Use as TodoWrite Items)

1. Add or fix the **title cell** (H1 + learning objectives + prerequisites)
2. Insert **markdown section headers** before each logical code group
3. Add **banner comments** to every code cell
4. **Delete duplicate cells** and **merge/split** cells as needed
5. **Remove stale setup** (getpass, os.environ for keys)
6. **Strip Databricks metadata** from cell metadata
7. Organize **imports** (stdlib → third-party → langchain → helpers)
8. Add **confirmation prints** to setup cells
9. Add the **summary cell** at the end
10. **Clear outputs** and reset execution counts
11. Final read-through for consistency and typos

## Reference

See the fully formatted sample notebook at `./notebook/sample.ipynb` for a
concrete example of all conventions applied to a Tools & Functions notebook.
