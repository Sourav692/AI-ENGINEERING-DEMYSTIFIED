%%markdown
# Document Loading and Metadata

Lesson 01 loaded one text file and moved on. Real corpora are not one text file. They are PDFs with page numbers, CSVs with columns, JSON with nested structure, Word documents with headings, directories with hundreds of mixed files, and web pages wrapped in navigation chrome.

This lesson is about turning all of that into `Document` objects — and about the half of the job that gets neglected: **the metadata you attach while loading.** Metadata is not decoration. It is the only thing that makes filtering, citation, access control, and debugging possible later, and it is far cheaper to attach now than to reconstruct afterwards.

## Learning objectives

By the end of this notebook you will be able to:

1. **Explain the `Document` contract** — `page_content` plus `metadata` — and why every loader in the ecosystem returns the same shape.
2. **Load the common formats**: text, Markdown, CSV, JSON, JSONL, PDF, Word, whole directories, and web pages.
3. **Choose between competing loaders for the same format**, especially the three main PDF loaders, based on what each preserves and discards.
4. **Control the split granularity a loader imposes** — one document per file, per row, per page, or per record — and understand that this is a retrieval decision, not a formatting one.
5. **Design a metadata schema** deliberately, and attach it at load time.
6. **Handle loading failures** — encodings, missing files, network and SSL problems — without silently ingesting nothing.

%%markdown
## Prerequisites

**Lessons**

- `01_Foundations/01_RAG_Lifecycle_and_Baseline.ipynb` — you should know where loading sits in the pipeline and what a `Document` is.

**Packages**

`langchain-community`, `langchain-core`, `pypdf`, `pymupdf`, `pandas`, `beautifulsoup4`, `docx2txt`, and optionally `unstructured` + `markdown` for the structure-preserving loaders.

**`jq` is deliberately not required.** `JSONLoader` depends on the `jq` Python bindings, which need a C toolchain and **do not install on Windows** without significant effort. Part 3 shows the `JSONLoader` API — you will meet it constantly in other people's code — but every JSON cell falls back to plain `json` + manual `Document` construction, which is portable, dependency-free, and frequently clearer than a jq expression. That fallback is not a workaround for a broken environment; on Windows it is the recommended path.

Network cells in Part 6 are off by default behind a flag.

**Services**

None. **This entire lesson runs without an API key** — loading is not a model operation. Only the last section touches a network, and it is optional.

**Input assets**

All from `04_Retrieval_and_RAG/shared_data/`, resolved by `rag_paths.asset()`: `dummy.txt`, `README.md`, `data.csv`, `chat_data.json`, `facebook_chat_messages.jsonl`, `layoutparser_paper.pdf`, `Intel Strategy.docx`.

%%markdown
## Provenance and runtime status

Consolidated from the eleven loader notebooks in `04_Retrieval_and_RAG/06_RAG_Naive_to_Production/01_Loading_Data/` (`1. Text_Loader` through `11. Custom_Loader`), which are the canonical source for this concept.

**A defect those eleven notebooks share:** every one of them addresses its inputs as `../../data/…` or `../../docs/…`. Neither directory exists. From `01_Loading_Data/`, `../../` resolves to `04_Retrieval_and_RAG/`, which contains `shared_data/` — not `data/` or `docs/`. **All eleven are therefore unrunnable as written**, and have been since the folder was reorganized. Every file they need does exist, in `shared_data/`. This lesson reaches them through `rag_paths.asset()`, which is exactly the class of problem that resolver was built for.

They also repeat an identical "Document Loaders / Examples of Document Loaders / Functionality" preamble in eight of eleven notebooks. That boilerplate is consolidated into Part 1 here and not repeated.

**Runtime status:** filled in after this notebook's validation run — see the migration manifest for the authoritative record.

%%markdown
---

## Part 0 — Setup

%%code
# ============ BOOTSTRAP: DEPTH-INDEPENDENT PATHS ============
import pathlib
import sys

_p = pathlib.Path.cwd()
while not (_p / "RAG_Curriculum").is_dir() and _p != _p.parent:
    _p = _p.parent
sys.path.insert(0, str(_p / "RAG_Curriculum" / "_support" / "helpers"))

from rag_paths import asset, repo_root

print("Repository root:", repo_root())

%%code
# ============ IMPORTS ============
# stdlib -> third-party -> LangChain
import json
from pathlib import Path

import pandas as pd

from langchain_community.document_loaders import (
    CSVLoader,
    DirectoryLoader,
    JSONLoader,
    PyMuPDFLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

print("Imports ready. No API key needed for this lesson.")

%%code
# ============ HELPER: COMPACT DOCUMENT INSPECTION ============
# Used throughout, so each loader section can stay focused on the loader
# itself rather than on printing.
def show(docs, label="", n=2, chars=160):
    """Print how many Documents a loader returned, and what the first few look like."""
    print(f"{label}  ->  {len(docs)} Document(s)")
    for i, d in enumerate(docs[:n]):
        text = " ".join(d.page_content.split())          # collapse whitespace for display
        print(f"  [{i}] {text[:chars]}{'...' if len(text) > chars else ''}")
        print(f"      metadata: {d.metadata}")
    if len(docs) > n:
        print(f"  ... and {len(docs) - n} more")
    print()

%%markdown
---

## Part 1 — The `Document` contract

Every loader in LangChain — for every format, from every source — returns a list of the same object:

```python
Document(page_content="the text", metadata={"source": "where it came from", ...})
```

Two fields, and they have very different jobs.

| Field | Job | Consumed by |
| --- | --- | --- |
| `page_content` | The text that will be embedded and shown to the model | The embedding model, then the prompt |
| `metadata` | Everything *about* that text | Filters, citations, access control, debugging — **never embedded** |

That last point is the one people miss. **Metadata is not embedded and is not searched semantically.** Putting a document's title only in metadata means no query will ever match on it. Conversely, `metadata` is the only thing you can filter on exactly, so anything you need to filter by — tenant, date, department, permission level — must be there.

The uniformity is the whole point of the abstraction: swap a `CSVLoader` for a `PyPDFLoader` and nothing downstream changes.

%%code
# ============ THE CONTRACT, BY HAND ============
# A Document does not have to come from a file. Constructing one directly is
# the right move when your data is already in memory - from a database, an
# API, a message queue.
doc = Document(
    page_content="Bella Vista does not currently offer delivery.",
    metadata={
        "source": "ops_handbook",       # provenance - where this came from
        "section": "services",          # for filtering
        "updated": "2026-09-01",        # for recency filtering / staleness checks
        "verified": True,               # your own trust signal
    },
)

print("page_content:", doc.page_content)
print("metadata    :", doc.metadata)
print("\nNote: none of that metadata will be embedded or semantically searchable.")
print("It is for filtering, citation and provenance only.")

%%markdown
---

## Part 2 — Text and Markdown

The simplest case, and the one that shows the first real decision: **what counts as one document?**

%%code
# ============ LOAD: PLAIN TEXT ============
# TextLoader returns the WHOLE file as a single Document. Always. It does not
# split - that is the chunker's job in lesson 02_Chunking_and_Indexing/01.
docs = TextLoader(str(asset("dummy.txt")), encoding="utf-8").load()
show(docs, "TextLoader(dummy.txt)", n=1)

print(f"Whole file arrived as {len(docs)} Document of {len(docs[0].page_content)} characters.")

%%markdown
**Always pass `encoding` explicitly.** The default depends on the platform locale — on Windows that is often cp1252, which raises `UnicodeDecodeError` on perfectly ordinary UTF-8 text containing an em dash or an accented name. A corpus that loads on one machine and fails on another is almost always this.

`TextLoader` also accepts `autodetect_encoding=True`, which tries `chardet`. Useful for a messy mixed corpus, slower, and still a guess.

%%code
# ============ LOAD: MARKDOWN ============
# UnstructuredMarkdownLoader has a mode= parameter, and it controls the single
# most consequential choice in loading: granularity.
#
#   mode="single"    -> one Document for the whole file (the default)
#   mode="elements"  -> one Document PER STRUCTURAL ELEMENT (heading, paragraph,
#                       list item, table), each tagged with its category
md_path = str(asset("README.md"))

try:
    single = UnstructuredMarkdownLoader(md_path, mode="single").load()
    show(single, 'mode="single"', n=1, chars=120)

    elements = UnstructuredMarkdownLoader(md_path, mode="elements").load()
    show(elements, 'mode="elements"', n=3, chars=80)

    # The element category is the useful part - it survives into metadata.
    cats = pd.Series([d.metadata.get("category", "?") for d in elements]).value_counts()
    print("Element categories found:")
    print(cats.to_string())
except ImportError as e:
    print(f"SKIPPED - needs the optional `unstructured` package: {e}")

%%markdown
`mode="elements"` is worth understanding because it is the first time a loader makes a **retrieval** decision for you.

One document per file means retrieval returns the entire file — precise only if files are tiny. One document per element means retrieval can return a single paragraph, but a heading and the paragraph it introduces become separate documents that may never be retrieved together.

Neither is right in general. The question to ask is: *what is the smallest unit that still answers a question on its own?*

> Chunking, in the next lesson, is the other half of this decision. Loading granularity and chunk size interact — a loader that already emits one document per paragraph needs very different chunking from one that emits a 400-page blob.

%%markdown
---

## Part 3 — Structured text: CSV, JSON, JSONL

Structured formats force the granularity question immediately, because the structure already suggests an answer: **one record, one document.**

%%code
# ============ LOAD: CSV ============
# CSVLoader emits ONE DOCUMENT PER ROW. The page_content is the row rendered
# as "column: value" lines - which means the column names get embedded along
# with the values, and that is usually what you want for retrieval.
csv_path = str(asset("data.csv"))
rows = CSVLoader(file_path=csv_path).load()
show(rows, "CSVLoader(data.csv)", n=2, chars=200)

print("Note `row` in the metadata - the source row index. That is your citation handle.")

%%code
# ============ CSV: CHOOSING WHICH COLUMNS BECOME TEXT ============
# Embedding every column is often wrong. Numeric IDs and prices add noise to
# the vector without adding meaning. source_column and metadata_columns let you
# split the row: some fields become searchable text, others become filters.
selective = CSVLoader(
    file_path=csv_path,
    source_column="Address",                       # which column identifies the row
    metadata_columns=["City", "State", "Listing_Price"],  # kept as metadata, NOT embedded
).load()
show(selective, "CSVLoader with metadata_columns", n=2, chars=200)

print("Listing_Price is now a metadata field. You can filter on `price < 400000`")
print("exactly - something semantic search over the digits could never do reliably.")

%%markdown
This is the central skill of structured-data loading: **decide, per column, whether it is meaning or a filter.** Free text (descriptions, notes, titles) is meaning and belongs in `page_content`. Identifiers, categories, dates and numbers are filters and belong in `metadata`.

Getting this wrong is a common and quiet failure. A price embedded as text makes "houses under $400k" match on the digit patterns, not the magnitude.

> Structured retrieval gets its own treatment in `01_Foundations/05_Structured_Data_RAG.ipynb`, including where this whole approach breaks down.

%%code
# ============ LOAD: JSON ============
# JSONLoader uses a jq-style path to say WHICH parts of the document to load.
# jq_schema=".messages[]" means: iterate the `messages` array, one Document each.
json_path = str(asset("chat_data.json"))

try:
    msgs = JSONLoader(
        file_path=json_path,
        jq_schema=".messages[]",
        content_key="content",     # which field of each record becomes page_content
        text_content=False,        # allow non-string values without erroring
    ).load()
    show(msgs, 'JSONLoader jq_schema=".messages[]"', n=3, chars=80)
except ImportError as e:
    # Expected on Windows: the `jq` bindings need a C toolchain. This is not a
    # degraded path - plain json + Document is portable and often clearer.
    print(f"jq unavailable ({e.__class__.__name__}); using the portable equivalent.")
    raw = json.loads(Path(json_path).read_text(encoding="utf-8"))
    msgs = [
        Document(page_content=m.get("content", ""), metadata={"source": json_path, "seq": i})
        for i, m in enumerate(raw["messages"])
    ]
    show(msgs, 'json + Document (equivalent of jq_schema=".messages[]")', n=3, chars=80)

%%code
# ============ JSON: LIFTING FIELDS INTO METADATA ============
# content_key picks the text. Everything ELSE in the record is discarded unless
# you ask for it - metadata_func is how you keep the fields you need to filter on.
def message_metadata(record: dict, metadata: dict) -> dict:
    """Promote per-record JSON fields into Document metadata."""
    metadata["sender"] = record.get("sender_name")
    metadata["timestamp_ms"] = record.get("timestamp_ms")
    return metadata


try:
    enriched = JSONLoader(
        file_path=json_path,
        jq_schema=".messages[]",
        content_key="content",
        metadata_func=message_metadata,
        text_content=False,
    ).load()
    show(enriched, "JSONLoader with metadata_func", n=3, chars=60)
    print("Now every message carries its sender - so you can filter to one person's")
    print("messages, or cite who said what. Without metadata_func, that is lost.")
except ImportError:
    # The portable equivalent: just build the dict you want. metadata_func
    # exists because JSONLoader controls construction; when you construct the
    # Document yourself there is nothing to hook.
    raw = json.loads(Path(json_path).read_text(encoding="utf-8"))
    enriched = [
        Document(
            page_content=m.get("content", ""),
            metadata={"source": json_path, "seq": i,
                      "sender": m.get("sender_name"), "timestamp_ms": m.get("timestamp_ms")},
        )
        for i, m in enumerate(raw["messages"])
    ]
    show(enriched, "json + Document with per-record metadata", n=3, chars=60)
    print("Same result, no jq: every message carries its sender, so you can filter")
    print("to one person's messages or cite who said what.")

%%code
# ============ LOAD: JSONL (JSON LINES) ============
# One JSON object per line. json_lines=True switches the parser; the jq_schema
# then applies to EACH LINE rather than to the file as a whole.
jsonl_path = str(asset("facebook_chat_messages.jsonl"))

try:
    lines = JSONLoader(
        file_path=jsonl_path,
        jq_schema=".content",
        json_lines=True,
        text_content=False,
    ).load()
    show(lines, "JSONLoader(json_lines=True)", n=3, chars=60)
    print("Note the `seq_num` metadata - the line number, i.e. your citation handle.")
except ImportError:
    # JSONL is the easiest format to handle by hand: one JSON object per line.
    rows_ = [json.loads(l) for l in Path(jsonl_path).read_text(encoding="utf-8").splitlines() if l.strip()]
    lines = [
        Document(page_content=r.get("content", ""),
                 metadata={"source": jsonl_path, "seq_num": i + 1, "sender": r.get("sender_name")})
        for i, r in enumerate(rows_)
    ]
    show(lines, "json + Document, one per line", n=3, chars=60)
    print("`seq_num` is the line number - your citation handle.")

%%markdown
---

## Part 4 — PDF, and choosing between loaders

PDF is where "just use the loader" stops being adequate, because **several loaders handle the same format very differently** and the choice materially changes what your corpus contains.

A PDF is a description of marks on a page, not a document with structure. Anything a loader tells you about paragraphs, columns or tables is reconstruction — and different libraries reconstruct differently.

%%code
# ============ LOAD: PDF WITH PyPDFLoader ============
# The default choice. Pure Python, no system dependencies. Returns ONE
# DOCUMENT PER PAGE, with the page number in metadata.
pdf_path = str(asset("layoutparser_paper.pdf"))
pypdf_docs = PyPDFLoader(pdf_path).load()

print(f"PyPDFLoader -> {len(pypdf_docs)} Documents (one per page)")
print(f"Page 0 metadata keys: {sorted(pypdf_docs[0].metadata)}")
print(f"Page 0 first 200 chars:\n{pypdf_docs[0].page_content[:200]!r}")

%%code
# ============ LOAD: THE SAME PDF WITH PyMuPDFLoader ============
# Backed by MuPDF (C). Faster, generally better at text ordering in
# multi-column layouts, and returns richer metadata.
try:
    mupdf_docs = PyMuPDFLoader(pdf_path).load()
    print(f"PyMuPDFLoader -> {len(mupdf_docs)} Documents")
    print(f"Page 0 metadata keys: {sorted(mupdf_docs[0].metadata)}")

    # Compare what each actually extracted from the same page.
    a = " ".join(pypdf_docs[0].page_content.split())
    b = " ".join(mupdf_docs[0].page_content.split())
    print(f"\nSame page, characters extracted:  PyPDF={len(a)}  PyMuPDF={len(b)}")
    print(f"Identical text? {a == b}")
    print(f"\nPyPDF  : {a[:180]!r}")
    print(f"PyMuPDF: {b[:180]!r}")
except ImportError as e:
    print(f"SKIPPED - needs the optional `pymupdf` package: {e}")

%%markdown
Run that comparison on your own documents before committing to a loader. On a simple single-column PDF the two agree closely. On an academic paper with two columns, headers, footnotes and figure captions they can differ substantially — and the differences land directly in your embeddings.

| Loader | Needs | Granularity | Good at | Weak at |
| --- | --- | --- | --- | --- |
| `PyPDFLoader` | `pypdf` (pure Python) | Page | Simple, dependency-light, predictable | Multi-column ordering, tables |
| `PyMuPDFLoader` | `pymupdf` (C library) | Page | Speed, layout fidelity, rich metadata | Licensing (AGPL) matters for some projects |
| `UnstructuredPDFLoader` | `unstructured` + system deps | Page **or element** | Structure — titles, tables, lists as typed elements | Heavy install, slow, sometimes needs OCR |

**Scanned PDFs contain no text at all.** Every loader above will return empty or near-empty pages, silently. Always check: if `len(page_content)` is near zero across many pages, you need OCR, not a different loader.

%%code
# ============ VALIDATE THE LOAD - DO NOT SKIP THIS ============
# Silent empty extraction is the most common PDF failure. Check before you
# spend money embedding nothing.
lengths = [len(d.page_content.strip()) for d in pypdf_docs]
empty = sum(1 for n in lengths if n < 50)

print(f"Pages loaded      : {len(lengths)}")
print(f"Median chars/page : {sorted(lengths)[len(lengths) // 2]}")
print(f"Near-empty pages  : {empty} ({empty / len(lengths):.0%})")

if empty / len(lengths) > 0.5:
    print("\nWARNING: most pages extracted almost no text.")
    print("This PDF is probably scanned images - you need OCR, not another loader.")
else:
    print("\nOK: text extraction looks healthy.")

%%markdown
---

## Part 5 — Directories and Office documents

%%code
# ============ LOAD: A WHOLE DIRECTORY ============
# DirectoryLoader walks a tree, matches a glob, and delegates each file to a
# loader class. Two arguments matter more than they look:
#   loader_cls    - default is UnstructuredFileLoader (heavy); override it
#   silent_errors - default False means ONE bad file aborts the entire load
data_dir = str(asset("dummy.txt").parent)

txt_docs = DirectoryLoader(
    data_dir,
    glob="**/*.txt",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},   # passed through to each TextLoader
    silent_errors=True,                    # skip unreadable files, keep going
    show_progress=False,
).load()

show(txt_docs, f"DirectoryLoader('{Path(data_dir).name}', glob='**/*.txt')", n=2, chars=90)
print("Sources loaded:")
for d in txt_docs:
    print("  -", Path(d.metadata["source"]).name)

%%markdown
`silent_errors` is a genuine trade-off, not a convenience flag.

- `False` (default): one corrupt file raises, and you load **nothing**. Loud, and safe against partial ingestion.
- `True`: bad files are skipped silently, and you load a corpus that is quietly missing documents — with nothing in the result to tell you which.

For a production ingest, prefer `True` **plus your own accounting**: count the files the glob matched, compare against the documents returned, and log the difference. A corpus silently missing 8% of its documents produces retrieval failures that look like model problems.

%%code
# ============ ACCOUNTING: WHAT DID THE GLOB MISS? ============
matched = sorted(Path(data_dir).glob("*.txt"))
loaded = {Path(d.metadata["source"]).resolve() for d in txt_docs}

print(f"Files matched by glob : {len(matched)}")
print(f"Documents returned    : {len(txt_docs)}")
missing = [p for p in matched if p.resolve() not in loaded]
print(f"Silently skipped      : {len(missing)}")
for p in missing:
    print("   !", p.name)
if not missing:
    print("   (none - every matched file loaded)")

%%code
# ============ LOAD: MICROSOFT WORD ============
# .docx is a zip of XML, so extraction is reliable - unlike PDF.
#
# Docx2txtLoader is the lightweight choice: one small pure-Python dependency,
# fast, and it returns the whole document as a single Document.
from langchain_community.document_loaders import Docx2txtLoader

docx_path = str(asset("Intel Strategy.docx"))
word_docs = Docx2txtLoader(docx_path).load()
show(word_docs, "Docx2txtLoader", n=1, chars=140)
print(f"Whole document as {len(word_docs)} Document of {len(word_docs[0].page_content)} characters.")
print("Flat text: the heading structure is gone. See the note below.")

%%markdown
`Docx2txtLoader` gives you the text and nothing else — the heading hierarchy that made the document navigable is flattened away.

`UnstructuredWordDocumentLoader(mode="elements")` preserves it, tagging each element as `Title`, `NarrativeText`, `ListItem` and so on, which is excellent metadata: attach the enclosing `Title` to each body chunk and retrieval gains section context for free.

The cost is real, though. `unstructured` installed 34 transitive packages here (spacy, numba, llvmlite among them), needs a per-format extra (`unstructured[docx]`, `unstructured[md]`), and **its .docx path did not complete on this file in this environment** — it hung past a 110-second timeout rather than raising.

That is the tradeoff in miniature: richer structure, heavier and less predictable machinery. Reach for `unstructured` when you actually need the element types, and benchmark it on *your* documents before committing an ingestion pipeline to it. The Markdown path, which the next cell uses, is well-behaved.

%%code
# ============ WORD/MARKDOWN: STRUCTURE-PRESERVING ALTERNATIVE ============
# Same idea as mode="elements" for Word, demonstrated on Markdown because the
# Markdown path is reliable here. `category` is what you came for.
try:
    elements = UnstructuredMarkdownLoader(str(asset("README.md")), mode="elements").load()
    cats = pd.Series([d.metadata.get("category", "?") for d in elements]).value_counts()
    print(f"{len(elements)} typed elements:")
    print(cats.to_string())

    print("\nThe document's heading structure, recovered from metadata:")
    for d in elements:
        if d.metadata.get("category") == "Title":
            print("  #", " ".join(d.page_content.split())[:70])
    print("\nAttach the enclosing Title to each body chunk and every retrieved")
    print("passage arrives knowing which section it came from.")
except ImportError as e:
    print(f"SKIPPED - needs `unstructured` plus the `markdown` package: {e}")

%%markdown
---

## Part 6 — Web sources *(optional — requires network)*

Remote loaders introduce failure modes that local files do not have: the network, rate limits, SSL certificates, and content that changes underneath you.

The cells below are **optional** and guarded. Skip the whole section if you are offline.

%%code
# ============ LOAD: A WEB PAGE ============
# WebBaseLoader fetches HTML and strips tags. Without a filter you also ingest
# navigation, cookie banners, footers and ads - noise that will be embedded and
# retrieved. bs_kwargs with a SoupStrainer restricts parsing to the real content.
RUN_NETWORK_CELLS = False   # flip to True to actually fetch

if RUN_NETWORK_CELLS:
    import bs4
    from langchain_community.document_loaders import WebBaseLoader

    try:
        loader = WebBaseLoader(
            web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
            bs_kwargs={
                "parse_only": bs4.SoupStrainer(
                    class_=("post-content", "post-title", "post-header")
                )
            },
        )
        web_docs = loader.load()
        show(web_docs, "WebBaseLoader (filtered)", n=1, chars=200)
    except Exception as e:
        print(f"Network load failed ({type(e).__name__}): {e}")
else:
    print("Network cells disabled. Set RUN_NETWORK_CELLS = True to fetch.")
    print()
    print("What to know when you do enable it:")
    print("  - Without a SoupStrainer you will embed site navigation and footers.")
    print("  - Check the extracted length; a JS-rendered page often yields ~0 chars,")
    print("    because WebBaseLoader does not execute JavaScript.")
    print("  - Respect robots.txt and rate limits; set a real User-Agent.")

%%markdown
**On SSL errors.** Several of the source notebooks this lesson replaces carried long troubleshooting sections about `SSLCertVerificationError`, mostly from the YouTube transcript loader. The fix is to install proper CA certificates — `pip install certifi`, and on macOS run the `Install Certificates.command` that ships with Python.

The workaround those notebooks reached for, disabling verification globally:

```python
ssl._create_default_https_context = ssl._create_unverified_context   # DO NOT DO THIS
```

turns off certificate checking for **every** HTTPS request in the process, including your API calls. It converts a loading inconvenience into a security hole. Fix the certificates instead.

%%markdown
---

## Part 7 — Writing a custom loader

When no loader exists for your source — an internal API, a database, a proprietary format — subclass `BaseLoader`. The only method you must implement is `lazy_load`, yielding `Document`s.

Implement `lazy_load` rather than `load`: `BaseLoader` derives `load()` from it for free, and yielding means a million-record source never has to fit in memory at once.

%%code
# ============ CUSTOM LOADER ============
from collections.abc import Iterator


class LineLoader(BaseLoader):
    """Load a text file as one Document per non-empty line.

    A deliberately simple example: the useful part is the shape, not the parsing.
    Note that every Document gets `source` and `line_number` - enough to cite
    the exact line an answer came from.
    """

    def __init__(self, file_path: str, encoding: str = "utf-8"):
        self.file_path = file_path
        self.encoding = encoding

    def lazy_load(self) -> Iterator[Document]:
        with open(self.file_path, encoding=self.encoding) as f:
            for i, line in enumerate(f, start=1):
                line = line.strip()
                if not line:                      # skip blanks rather than emit empty docs
                    continue
                yield Document(
                    page_content=line,
                    metadata={
                        "source": self.file_path,
                        "line_number": i,
                        "loader": type(self).__name__,   # provenance: how it was parsed
                    },
                )


custom = LineLoader(str(asset("dummy.txt"))).load()   # load() comes free from lazy_load()
show(custom, "LineLoader(dummy.txt)", n=3, chars=90)

# The point of lazy_load: stream without materializing everything.
first = next(iter(LineLoader(str(asset("dummy.txt"))).lazy_load()))
print(f"Streamed one Document without loading the file: line {first.metadata['line_number']}")

%%markdown
---

## Part 8 — Designing the metadata schema

Everything so far produced metadata incidentally. Now do it deliberately, because **the questions you can ask later are limited by the metadata you attach now** — and re-ingesting a large corpus to add a field is expensive.

Four categories are worth planning:

| Category | Examples | Enables |
| --- | --- | --- |
| **Provenance** | `source`, `page`, `row`, `line_number`, `loader`, `ingested_at` | Citation, debugging, re-ingestion |
| **Filtering** | `department`, `doc_type`, `date`, `language`, `version` | Narrowing retrieval before similarity search |
| **Access control** | `tenant_id`, `visibility`, `owner` | Multi-tenant isolation — **never optional** |
| **Quality** | `confidence`, `extraction_method`, `verified` | Excluding low-quality text; auditing |

Two hard constraints to design against:

- **Vector stores restrict metadata value types.** Chroma accepts `str`, `int`, `float`, `bool` — not lists or nested dicts. Flatten before you index, or the write fails.
- **Filtering is exact, not semantic.** `{"department": "Engineering"}` will not match `"engineering"`. Normalize values at load time.

%%code
# ============ A DELIBERATE METADATA SCHEMA ============
from datetime import date


def enrich(doc: Document, **extra) -> Document:
    """Apply a consistent metadata schema, flattening for vector-store limits."""
    src = Path(doc.metadata.get("source", "unknown"))

    doc.metadata.update(
        {
            # Provenance
            "source": str(src),
            "filename": src.name,
            "file_type": src.suffix.lstrip(".").lower() or "unknown",
            "ingested_at": date.today().isoformat(),
            # Access control - a default that denies nothing is a bug waiting to happen
            "visibility": extra.pop("visibility", "internal"),
            # Quality
            "char_count": len(doc.page_content),
        }
    )
    doc.metadata.update(extra)

    # Flatten anything a vector store will reject.
    for k, v in list(doc.metadata.items()):
        if not isinstance(v, (str, int, float, bool)) and v is not None:
            doc.metadata[k] = json.dumps(v) if isinstance(v, (list, dict)) else str(v)
    return doc


enriched_docs = [enrich(d, department="Legal", doc_type="reference") for d in rows[:2]]
for d in enriched_docs:
    print(json.dumps(d.metadata, indent=2, default=str))
    print()

bad = [k for d in enriched_docs for k, v in d.metadata.items()
       if not isinstance(v, (str, int, float, bool)) and v is not None]
print(f"Metadata values incompatible with a vector store: {len(bad)}  {'OK' if not bad else bad}")

%%markdown
---

## Part 9 — Limitations and tradeoffs

**Loading is lossy, always.** Every loader discards something: PDF loses layout and reading order, HTML loses visual hierarchy, Word loses comments and tracked changes, CSV loses column types. Know what your loader drops, because you cannot retrieve what was never extracted.

**Granularity is a retrieval decision made at load time.** One document per file, page, row or element determines the smallest thing retrieval can return. It interacts with chunking and is expensive to change later — it means re-ingesting.

**Failures are quiet.** Scanned PDFs yield empty text. `silent_errors=True` skips files. JS-rendered pages yield nothing. None of these raise. Validate counts and content lengths after every load, as Parts 4 and 5 did.

**Optional dependencies are a real constraint.** `unstructured` pulls in a large tree (34 packages here, including spacy and numba) and sometimes system binaries; `jq` needs a C toolchain and does not install on Windows; `pymupdf` is AGPL-licensed, which matters for some commercial projects. Prefer the lightest loader that preserves what you need — and note that for JSON, "no loader at all" is a perfectly good answer.

**Encodings.** Always pass `encoding` explicitly. Platform-default encoding is the most common cause of a corpus that loads on one machine and not another.

**What this lesson did not cover:** OCR for scanned documents, audio/video transcription, images, and incremental re-ingestion (detecting which documents changed — that is `02_Chunking_and_Indexing/05_Incremental_Indexing_and_Record_Management.ipynb`). Multimodal document intelligence is `09_Multimodal_RAG/`.

%%markdown
---

## Exercise

Build a `CorpusLoader` that ingests a directory of mixed file types, dispatching each to an appropriate loader, applying one metadata schema, and — critically — **reporting what it failed to load**.

%%code
# ============ EXERCISE: A MIXED-FORMAT CORPUS LOADER ============
class CorpusLoader:
    """Load a mixed-format directory, with a consistent schema and a load report."""

    LOADERS = {
        ".txt": lambda p: TextLoader(p, encoding="utf-8"),
        ".md": lambda p: TextLoader(p, encoding="utf-8"),   # plain-text fallback
        ".csv": lambda p: CSVLoader(file_path=p),
        ".pdf": lambda p: PyPDFLoader(p),
    }

    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.report = {"loaded": [], "skipped": [], "failed": []}

    def load(self) -> list[Document]:
        docs = []
        for path in sorted(self.directory.iterdir()):
            if not path.is_file():
                continue
            factory = self.LOADERS.get(path.suffix.lower())
            if factory is None:
                self.report["skipped"].append((path.name, "no loader for this extension"))
                continue
            try:
                loaded = factory(str(path)).load()
                docs.extend(enrich(d, doc_type=path.suffix.lstrip(".")) for d in loaded)
                self.report["loaded"].append((path.name, len(loaded)))
            except Exception as e:                  # record, never swallow
                self.report["failed"].append((path.name, f"{type(e).__name__}: {e}"))
        return docs

    def print_report(self):
        print(f"Loaded  : {len(self.report['loaded'])} files")
        for name, n in self.report["loaded"]:
            print(f"    {name}  ->  {n} docs")
        print(f"Skipped : {len(self.report['skipped'])} files")
        for name, why in self.report["skipped"][:5]:
            print(f"    {name}  ({why})")
        print(f"Failed  : {len(self.report['failed'])} files")
        for name, why in self.report["failed"]:
            print(f"    {name}  {why}")

    # TODO 1: add empty-extraction detection. A PDF that loads "successfully"
    #         but yields 20 blank pages should land in `failed`, not `loaded`.
    #
    # TODO 2: add a `visibility` argument that maps directory names to access
    #         levels, so a `public/` subfolder is tagged differently from `hr/`.
    #         Think about what the DEFAULT should be if a folder is unmapped.
    #
    # TODO 3: make it incremental - skip files whose content hash matches a
    #         previous run. Which metadata field would you store the hash in,
    #         and what happens to the old chunks when a file changes?


corpus = CorpusLoader(data_dir)
all_docs = corpus.load()
print(f"=== {len(all_docs)} Documents from {corpus.directory.name}/ ===\n")
corpus.print_report()

%%markdown
---

## Summary

**One contract.** Every loader returns `Document(page_content, metadata)`. `page_content` is embedded and searched; `metadata` is filtered and cited, and is never embedded.

**Granularity is the real decision.** Whole file, page, row, record or element — set at load time, it bounds the smallest unit retrieval can return, and changing it means re-ingesting.

**Format guide**

| Format | Default choice | Granularity | Watch for |
| --- | --- | --- | --- |
| Text | `TextLoader` | Whole file | Pass `encoding` explicitly |
| Markdown | `UnstructuredMarkdownLoader` | `single` or `elements` | Needs `unstructured` + `markdown` |
| CSV | `CSVLoader` | Per row | Split columns into content vs `metadata_columns` |
| JSON / JSONL | `JSONLoader`, or plain `json` | Per record | `jq` will not install on Windows — build `Document`s directly |
| PDF | `PyPDFLoader`, or `PyMuPDFLoader` for layout | Per page | Scanned PDFs yield nothing — check |
| Word | `Docx2txtLoader` (light) or `Unstructured…` (structure) | Doc or elements | `unstructured` is heavy and hung on .docx here |
| Directory | `DirectoryLoader` | Per file | Set `loader_cls`; reconcile counts |
| Web | `WebBaseLoader` | Per page | Filter with `SoupStrainer`; no JS |
| Anything else | Subclass `BaseLoader` | Yours | Implement `lazy_load` |

**Validate every load.** Compare files matched against documents returned; check content lengths for silent empty extraction. Loading failures do not raise — they produce a corpus that is quietly wrong, and the symptom appears much later as bad retrieval.

**Design metadata deliberately** across four axes — provenance, filtering, access control, quality — and flatten values to `str`/`int`/`float`/`bool` before indexing.

### Next lesson

`01_Foundations/03_Embeddings_and_Model_Selection.ipynb` — turning the text you just loaded into vectors, and choosing the model that does it.

%%markdown
---

### Migration record

Canonical lesson for concept `RAG-F-02` (document loading and metadata), from the Foundations batch in `RAG_MIGRATION_MANIFEST.md`.

Consolidates the eleven notebooks of `04_Retrieval_and_RAG/06_RAG_Naive_to_Production/01_Loading_Data/`, all of which reference input paths (`../../data/`, `../../docs/`) that do not exist and therefore cannot run as written. Their inputs live in `04_Retrieval_and_RAG/shared_data/` and are reached here through `rag_paths.asset()`. Consult the manifest for per-source disposition before assuming any of them is superseded.
