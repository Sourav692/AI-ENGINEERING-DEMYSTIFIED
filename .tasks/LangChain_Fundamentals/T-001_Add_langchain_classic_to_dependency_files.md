---
id: T-001
title: Install already-pinned langchain-classic + text-splitters into .venv
type: prereq
status: done
review: n/a
review_rounds: 0
wave: 0
effort: S
disposition: n/a
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: []
rules: []
depends_on: []
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Install already-pinned langchain-classic + text-splitters into .venv** — `done`

## Objective

`import langchain_classic` and `import langchain_text_splitters` both succeed in `.venv`.

**Correction (2026-09-05):** the pipeline first recorded this as "add to the dependency
files". That was wrong. Both are already pinned — `langchain-classic==1.0.8` and
`langchain-text-splitters==1.1.2` in `requirements.txt`, with matching floors in
`pyproject.toml`. They are simply **absent from the installed `.venv`**. No dependency
file needs editing; the venv needs syncing:

```bash
uv pip install langchain-classic==1.0.8 langchain-text-splitters==1.1.2
# or re-sync everything: uv pip install -r requirements.txt
```

Left `todo` because an unattended run does not change the environment.

## Scope

Files in scope:

- _(none listed — fill in)_

Findings this task closes: _n/a_

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for _n/a_
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] No notebook executed by this task; no saved outputs committed

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: Installed via: uv pip install --python .venv/Scripts/python.exe langchain-classic==1.0.8 langchain-text-splitters==1.1.2. Dry-run first: 4 additions (+greenlet, +sqlalchemy), nothing downgraded or removed; langchain stayed 1.4.0, langchain-core 1.6.1, langgraph 1.2.11. Verified: import langchain_classic OK, import langchain_text_splitters OK, langchain_classic.chains.LLMChain/RetrievalQA OK, 'from langchain_classic import hub' OK, langchain_text_splitters.RecursiveCharacterTextSplitter OK. All 0.x paths still ModuleNotFoundError, so notebook 1.8's claims still hold. DISCOVERED: langchain_classic.memory exists and exports ConversationBufferMemory et al - contradicts the 'memory has no classic home' claim in notebook 1.8 and in three reference docs. Raised as a correction.
