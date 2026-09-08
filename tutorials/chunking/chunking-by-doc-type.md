# Chunking Techniques Across Document Types

A practical guide to picking the right chunking strategy for RAG pipelines — grounded in LangChain's text splitters and extended to PDFs, HTML, tables, and semantic chunking.

---

## 1. Why Chunking Isn't One-Size-Fits-All

Chunking decides what a retriever *can possibly find*. Get it wrong and no amount of embedding-model quality or reranking fixes it — the answer was never inside a single chunk to begin with.

- **Prose** breaks cleanly at paragraph and sentence boundaries — sizing is the main lever.
- **Markdown/structured docs** carry a header hierarchy that *is* the semantic structure — ignoring it throws away free metadata.
- **Code** breaks a function or class in half if you split on character count alone — the chunk becomes syntactically meaningless.
- **PDFs** interleave body text, tables, headers/footers, and multi-column layouts — the extracted text stream often doesn't match reading order.
- **HTML** has tags carrying meaning (`<table>`, `<h2>`, `<nav>`) that plain-text splitting discards.
- **Tabular data** isn't prose at all — a row split across two chunks becomes two meaningless fragments.

The rule of thumb: **match the splitter's boundary awareness to the document's actual unit of meaning.**

---

## 2. Core Parameters (Recap)

Every splitter — regardless of doc type — is a variation on the same four knobs:

| Parameter | What it controls | Typical range |
|---|---|---|
| `chunk_size` | Max unit length (chars or tokens) | 200–1500 |
| `chunk_overlap` | Shared text between adjacent chunks, preserves context across a cut | 10–20% of chunk_size |
| `separators` / boundary rules | Where splits are *allowed* to happen | doc-type specific |
| metadata preservation | What structural context rides along with the chunk | headers, page numbers, row schema |

From your own `text_splitters.py`: `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, separators=["\n\n", "\n", " ", ""])` tries each separator in order — paragraph breaks first, falling back to words, falling back to raw characters only as a last resort. That fallback order *is* the boundary-awareness strategy, and it's the pattern every doc-type variant below is built on.

---

## 3. Document-Type Breakdown

### 3.1 Plain Prose / Narrative Text

- **Splitter:** `RecursiveCharacterTextSplitter`
- **Boundary priority:** paragraph → sentence → word → character
- **Chunk size:** 500–1000 chars (or ~200–400 tokens) works for most narrative content
- **Overlap:** 10–20% — prevents a sentence from being orphaned mid-thought at a boundary
- **Why this works:** prose has no structural metadata to exploit, so the splitter falls back to typography (blank lines, punctuation) as a proxy for semantic units

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", " ", ""],
)
```

**Pitfall:** overlap of 0 silently breaks retrieval for facts that straddle a chunk boundary — your own `overlap_importance()` demo shows the split mid-sentence when overlap is 0 vs. preserved when overlap is 20.

---

### 3.2 Markdown / Structured Docs

- **Splitter:** `MarkdownHeaderTextSplitter`, typically followed by `RecursiveCharacterTextSplitter` on oversized sections
- **Boundary priority:** header hierarchy (`#`, `##`, `###`) first, character-level second
- **Chunk size:** size the *second pass* (500–800 chars); the header split itself isn't size-bounded
- **Overlap:** less critical here — header metadata already carries context forward
- **Why this works:** the header hierarchy already encodes topic boundaries; splitting on anything else throws that structure away

```python
headers_to_split_on = [("#", "h1"), ("##", "h2"), ("###", "h3")]
splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
chunks = splitter.split_text(markdown_text)
# chunk.metadata now carries {"h1": "...", "h2": "..."} — free, retrievable context
```

**Pitfall:** a lone `MarkdownHeaderTextSplitter` pass can still produce a giant chunk if one section has no sub-headers and runs 5,000 characters — always chain a size-bounded second pass.

---

### 3.3 Source Code

- **Splitter:** `RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON, ...)`
- **Boundary priority:** language-aware separators — class def → function def → logical block → newline
- **Chunk size:** 300–800 chars; large enough to hold a small function whole
- **Overlap:** small (20–50 chars) — mainly to keep a trailing docstring attached
- **Why this works:** `from_language` swaps in separators specific to the language's grammar (`\nclass `, `\ndef `, `\n\tdef `, etc.) instead of generic paragraph breaks, so a function is far less likely to be split mid-body

```python
python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON, chunk_size=500, chunk_overlap=50
)
```

**Pitfall:** character-count splitters (even language-aware ones) don't understand indentation-scoped logic like a Python class with 10 methods — for large files, consider **AST-based chunking** (one chunk per function/class via `ast.parse`) instead of purely character-boundary splitting.

---

### 3.4 PDFs (Mixed Layout)

- **Loader:** `PyPDFLoader` (or layout-aware alternatives: `PyMuPDF`, `Unstructured`) → **splitter:** `RecursiveCharacterTextSplitter` on the loaded `Document` objects
- **Boundary priority:** page first (via the loader), then character/paragraph within a page
- **Chunk size:** 500–1000 chars per chunk, but **validate against extraction order** — multi-column PDFs often extract left-column-then-right-column-interleaved-wrong
- **Overlap:** 10–20%, plus **always preserve page-number metadata** — it's your only anchor back to the source when extraction quality is uncertain
- **Why this is harder:** a PDF's *visual* layout (columns, tables, headers/footers) doesn't map to a linear text stream. The splitter only sees whatever string the loader handed it — garbage layout in, garbage chunks out.

```python
loader = PyPDFLoader("./docs/langchain_demo.pdf")
docs = loader.load()  # one Document per page, metadata={"page": N, "source": path}

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = splitter.split_documents(docs)  # metadata propagates automatically
```

**Pitfall:** tables inside PDFs get flattened into disconnected text fragments by generic loaders — a table's header row and data rows can end up in different chunks with no schema linking them back together. For table-heavy PDFs, extract tables separately (e.g. `camelot`, `Unstructured`'s table mode) and chunk them as structured data (§3.6), not prose.

---

### 3.5 HTML

- **Splitter:** `HTMLHeaderTextSplitter` (analogous to the Markdown splitter, but keyed on `<h1>`–`<h6>` tags), or `HTMLSectionSplitter` for `<section>`/`<div>` based layouts
- **Boundary priority:** DOM heading hierarchy → character fallback
- **Chunk size:** 500–800 chars for the fallback pass
- **Overlap:** 10–15%
- **Why this works:** the same logic as Markdown — tags encode structure, so split on tags before falling back to raw text

```python
from langchain_text_splitters import HTMLHeaderTextSplitter

headers_to_split_on = [("h1", "Header 1"), ("h2", "Header 2")]
html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
chunks = html_splitter.split_text(html_string)
```

**Pitfall:** navigation bars, footers, and ad content get chunked right alongside real content unless you strip boilerplate DOM nodes *before* splitting — clean the HTML first (e.g. via `BeautifulSoup`, targeting `<main>`/`<article>`), then split.

---

### 3.6 Tabular / CSV / Structured Data

- **Splitter:** none of the above — chunk **by row or row-group**, not by character count
- **Boundary priority:** never split a row; group rows that share meaning (e.g. by a foreign key or time window)
- **Chunk size:** measured in *rows*, not characters — e.g. 20–50 rows per chunk, or one chunk per logical entity
- **Overlap:** usually **zero** — rows are independent records, there's no "mid-thought" to preserve across a boundary
- **Why this is different:** a row is an atomic semantic unit. Character-based splitting has no concept of "row," so it will happily cut a row in half at char 500.

```python
import pandas as pd
from langchain_core.documents import Document

df = pd.read_csv("data.csv")
docs = [
    Document(
        page_content=row.to_json(),
        metadata={"row_id": i, "source": "data.csv"},
    )
    for i, row in df.iterrows()
]
# Or group N rows per chunk if individual rows are too small to be useful alone
```

**Pitfall:** treating a CSV as plain text and running `RecursiveCharacterTextSplitter` over it is the single most common chunking mistake — it produces chunks with header row detached from data rows, or a data row missing its trailing columns.

---

### 3.7 Semantic Chunking (Cross-Cutting)

Applies *on top of* any doc type above as a size-adaptive alternative to fixed `chunk_size`.

- **Approach:** embed consecutive sentences/paragraphs, then cut where cosine similarity between neighbors drops below a threshold — i.e., split where the *topic* actually changes, not where a character counter hits zero
- **When to reach for it:** long-form prose or technical docs where topic shifts don't align with paragraph breaks (interviews, meeting transcripts, legal text)
- **Trade-off:** an extra embedding pass at chunking time (cost + latency) in exchange for boundaries that track meaning instead of character count

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

splitter = SemanticChunker(OpenAIEmbeddings(), breakpoint_threshold_type="percentile")
chunks = splitter.split_text(long_text)
```

---

## 4. Comparison Table

| Doc Type | Splitter | Boundary Priority | Typical Size | Overlap | Key Pitfall |
|---|---|---|---|---|---|
| Prose | `RecursiveCharacterTextSplitter` | paragraph → sentence → word | 500–1000 chars | 10–20% | zero overlap breaks straddling facts |
| Markdown | `MarkdownHeaderTextSplitter` + recursive | header hierarchy → char | 500–800 chars/section | low | oversized no-subheader sections |
| Code | `from_language()` recursive splitter | class → function → block | 300–800 chars | small | mid-function splits on huge classes |
| PDF | Loader + recursive splitter | page → paragraph → char | 500–1000 chars | 10–20% | tables flattened, column order scrambled |
| HTML | `HTMLHeaderTextSplitter` | DOM heading → char | 500–800 chars | 10–15% | boilerplate DOM nodes polluting chunks |
| Tabular/CSV | Row-based (custom) | row (never split) | rows, not chars | ~0% | header/data separation, mid-row cuts |
| Semantic (any) | `SemanticChunker` | embedding similarity drop | adaptive | n/a | extra embedding cost per chunking pass |

---

## 5. Decision Framework

Ask, in order:

1. **Does the document have an atomic record unit (a row, a form field)?** → chunk by record, not characters.
2. **Does it have explicit structural markup (headers, tags)?** → split on structure first, character-bound the leftovers.
3. **Is it a single language grammar (source code)?** → use a language-aware splitter.
4. **Is layout unreliable (PDF, scanned doc)?** → extract carefully first (loader/OCR/table-extraction), then apply the type-appropriate splitter above, and keep page/position metadata as a safety net.
5. **Otherwise (plain prose)?** → `RecursiveCharacterTextSplitter` with sensible size + overlap.

*(See the interactive HTML version of this doc for a clickable version of this flow, plus a live chunk-boundary playground.)*

---

## 6. Databricks RAG Considerations

Relevant to the RAG evaluation project you've been building on Databricks:

- **Vector Search index granularity:** chunk size directly determines what a single Vector Search hit returns — smaller chunks improve precision but can fragment context that a downstream LLM needs to answer well.
- **Golden dataset alignment:** if your offline RAGAS/MLflow evaluation golden set was built against one chunking strategy, re-run the evaluation whenever you change chunk size/overlap — retrieval metrics (context precision/recall) are chunking-strategy-specific, not chunking-strategy-independent.
- **Lakehouse Monitoring / drift:** a chunking strategy that worked for early documents can silently degrade as new document types (e.g. more table-heavy filings) enter the corpus — this is a legitimate drift signal worth tracking, distinct from embedding or query drift.
- **Unverified boundary:** table-heavy and multi-column PDF handling on Databricks (via `Unstructured` or custom Spark UDFs) is worth flagging as `UNVERIFIED` in your accelerator docs until tested against your actual client document set — this is exactly the kind of module your own documentation conventions call out explicitly.

---

## 7. Pitfalls & Best Practices Checklist

- [ ] Match splitter to the document's real unit of meaning — don't default to character-count splitting for structured or tabular content
- [ ] Never use zero overlap for prose; do use zero overlap for independent tabular rows
- [ ] Preserve structural metadata (headers, page numbers, row IDs) through the split — it's nearly free and critical for debugging bad retrievals
- [ ] For PDFs, validate extraction order before trusting chunk boundaries — multi-column layouts are the most common silent failure
- [ ] Re-run offline evaluation (RAGAS/MLflow) after any chunking strategy change — chunking is not a "set once" parameter
- [ ] For code, prefer language-aware or AST-based chunking over generic character splitting
- [ ] For tables embedded in prose/PDF, extract and chunk them separately from surrounding narrative text

---

## 8. Extending `text_splitters.py`

Your existing file already demonstrates `RecursiveCharacterTextSplitter`, `MarkdownHeaderTextSplitter`, and code splitting via `from_language`. Natural next additions, following the same pattern as `document_splitter()`:

```python
def html_splitter():
    from langchain_text_splitters import HTMLHeaderTextSplitter
    headers = [("h1", "Header 1"), ("h2", "Header 2")]
    splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers)
    return splitter.split_text(SAMPLE_HTML)

def tabular_splitter(csv_path, rows_per_chunk=25):
    import pandas as pd
    from langchain_core.documents import Document
    df = pd.read_csv(csv_path)
    return [
        Document(
            page_content=df.iloc[i:i+rows_per_chunk].to_json(orient="records"),
            metadata={"row_range": (i, i + rows_per_chunk)},
        )
        for i in range(0, len(df), rows_per_chunk)
    ]

def semantic_splitter(text):
    from langchain_experimental.text_splitter import SemanticChunker
    from langchain_openai import OpenAIEmbeddings
    splitter = SemanticChunker(OpenAIEmbeddings())
    return splitter.split_text(text)
```
