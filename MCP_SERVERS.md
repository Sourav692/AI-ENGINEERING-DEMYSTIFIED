# MCP Servers for This Repo

Recommendations for streamlining work on this AI Engineering roadmap, based on what's
actually built here (LangChain/LangGraph, RAG pipelines with Chroma, heavy notebook-based
iteration, LangSmith tracing already wired into dozens of notebooks).

## Status

| Server | Purpose | Scope | Status |
|---|---|---|---|
| [`langsmith`](#1-langsmith--already-configured) | Inspect traces/runs from notebooks that set `LANGCHAIN_TRACING_V2` | project | ✅ Already configured (you set this up) |
| [`chroma`](#2-chroma--configured) | Inspect Chroma collections built by RAG notebooks directly | project | ✅ Configured, connected |
| [`jupyter`](#3-jupyter--configured-needs-a-running-jupyterlab) | Execute notebook cells live and see real output/errors | local (private) | ⚠️ Configured, needs JupyterLab running to connect |
| [`github`](#4-github--not-configured-optional) | Richer PR/issue querying | — | ⏭️ Skipped — `gh` CLI via Bash already covers this |

Run `claude mcp list` any time to check live connection status.

## 1. LangSmith — already configured

```
langsmith: https://api.smith.langchain.com/mcp (HTTP)
```

**Why it matters here:** `LANGCHAIN_TRACING_V2` / `LANGCHAIN_API_KEY` setup appears across
dozens of notebooks in Phases 4, 5, 7, 8, 12 (e.g. `RAG_Fusion.ipynb`, `Multi_Query.ipynb`,
the `Agent_Evaluation/` notebooks). With this connected, traces/runs from those chains can be
inspected directly instead of relying on pasted error output.

## 2. Chroma — configured

```
chroma: uvx chroma-mcp --client-type persistent --data-dir D:/AI ENGINEERING/.mcp_data/chroma
```

Added at **project scope** (in `.mcp.json`, shareable if you commit that file) since it needs
no secrets — just a local data directory.

**Why it matters here:** nearly every RAG notebook across Phases 4, 5, 8, 13 builds a Chroma
collection. This lets a collection's contents be inspected directly (what got embedded,
dimensions, whether a `doc_id`/`parent_id` metadata link actually landed) instead of writing
one-off Python scripts through Bash to check — which is what happened twice while fixing
`Multi_Representation_Indexing.ipynb` and `Parent_Document_Retrieval.ipynb`.

**Important caveat:** most notebooks in this repo create Chroma **in-memory** (no
`persist_directory` passed to `Chroma(...)`), so their collections vanish when the kernel
stops and were never visible to this MCP connection in the first place. To make a notebook's
collection inspectable via this server, point it at the same data directory:

```python
vectorstore = Chroma(
    collection_name="summaries",
    embedding_function=OpenAIEmbeddings(),
    persist_directory=r"D:\AI ENGINEERING\.mcp_data\chroma",
)
```

`.mcp_data/chroma/` is already covered by this repo's `.gitignore` (matched by the existing
`chroma/` pattern), so nothing there gets committed.

## 3. Jupyter — configured, needs a running JupyterLab

```
jupyter: uvx jupyter-mcp-server@latest
env: JUPYTER_URL=http://localhost:8888, JUPYTER_TOKEN=REPLACE_WITH_YOUR_TOKEN, ALLOW_IMG_OUTPUT=true
```

Added at **local scope** (private to you, not written into the shared `.mcp.json`) because it
needs a token tied to your running Jupyter instance.

**Why it matters here:** a lot of the debugging done in this repo so far (the `langchain.storage`
import fix, the `UnicodeDecodeError` on Windows cp1252, the `shared_data` relative-path bug)
followed the same loop — edit a cell, ask you to restart the kernel and re-run, wait for you to
paste back the traceback. A live connection lets cells actually execute and their real
output/errors come back in the same turn.

**To finish setup — this server can't connect until JupyterLab is actually running:**

1. One-time package install into whichever environment runs your notebooks:
   ```bash
   pip install jupyterlab jupyter-collaboration jupyter-mcp-tools ipykernel
   ```
2. Start JupyterLab with a fixed token (pick your own token, don't reuse the example):
   ```bash
   jupyter lab --port 8888 --IdentityProvider.token YOUR_TOKEN_HERE --ip 0.0.0.0
   ```
3. Update the placeholder token already configured:
   ```bash
   claude mcp remove jupyter
   claude mcp add --scope local jupyter \
     -e JUPYTER_URL=http://localhost:8888 \
     -e JUPYTER_TOKEN=YOUR_TOKEN_HERE \
     -e ALLOW_IMG_OUTPUT=true \
     -- uvx jupyter-mcp-server@latest
   ```
4. Confirm real-time collaboration is active: open a notebook in JupyterLab, make an edit —
   the unsaved-change indicator should flip from `×` to `●` within a few seconds.

Until step 2–3 are done, `claude mcp list` will keep showing `jupyter` as failed to connect —
that's expected, not a misconfiguration.

## 4. GitHub — not configured (optional)

Considered but skipped: `gh` CLI already works fine via Bash in this session for the
PR/issue/commit workflows used so far. Only worth adding if PR/issue querying becomes frequent
enough that the CLI round-trip is the bottleneck — not currently the case here.
