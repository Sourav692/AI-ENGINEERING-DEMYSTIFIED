# Commit Message Conventions

Format: `<type>(<scope>): <subject>`

The scope is optional but very useful in an agentic AI repo, since it tells a
reviewer *which layer* changed without opening the diff — e.g. `agent`,
`retrieval`, `prompts`, `eval`, `ingestion`, `vectorstore`.

## Types

| Type       | When to use it                                                        |
|------------|------------------------------------------------------------------------|
| `feat`     | New capability — a new agent, tool, chain, or retrieval strategy       |
| `fix`      | Bug fix — wrong output, broken tool call, incorrect retrieval logic    |
| `refactor` | Restructuring code with no behavior change                             |
| `perf`     | Latency/throughput/token-cost improvements                             |
| `prompt`   | Prompt-only changes (system prompts, few-shot examples, templates)     |
| `eval`     | Added or changed evaluation harnesses, test sets, scoring logic         |
| `data`     | Changes to ingestion pipelines, chunking strategy, dataset prep         |
| `chore`    | Tooling, dependency bumps, `.gitignore` updates, CI config              |
| `docs`     | README, docstrings, architecture notes                                 |
| `test`     | Unit/integration tests unrelated to eval harnesses                     |

`prompt`, `eval`, and `data` aren't part of the standard Conventional Commits
spec, but they're worth adopting in an agentic AI repo — a prompt tweak and a
retrieval-logic change have very different blast radii and review needs, and
lumping them both under `fix` or `feat` hides that distinction.

## Examples

**Input:** Swapped the retriever from FAISS flat index to HNSW for faster lookup on the 100k-doc corpus
**Output:** `perf(retrieval): switch FAISS index to HNSW for faster top-k lookup`

**Input:** Added a new LangGraph node that classifies user intent before routing to the SQL agent vs the docs agent
**Output:** `feat(agent): add intent-classification node for SQL vs docs routing`

**Input:** Tightened the system prompt so the summarization agent stops hallucinating dates
**Output:** `prompt(summarizer): constrain date references to source-document text only`

**Input:** Added a gold-answer eval set for the Genie text-to-SQL agent
**Output:** `eval(text-to-sql): add golden-query accuracy eval set`

**Input:** Fixed .gitignore so local chroma_db folders stop getting committed
**Output:** `chore(repo): ignore local chroma_db persistence directories`

**Input:** Removed already-tracked __pycache__ files from git history going forward
**Output:** `chore(repo): stop tracking __pycache__ and .pyc artifacts`

## Body (optional second `-m`)

Use the body when the "why" isn't obvious from the subject — e.g. a
retrieval change that trades recall for latency, or a prompt change made in
response to a specific failure mode observed in eval. Skip the body for
purely mechanical changes (gitignore cleanup, formatting, dependency bumps).
