%%markdown
# Structured Data RAG

Everything so far assumed your corpus is prose. Much of it is not — it is rows in a CSV, records in a JSON API response, results from a database query. The tooling will happily accept all of it: `CSVLoader` returns `Document`s, those embed fine, retrieval returns something.

That is the problem. **It works well enough to look correct and badly enough to be wrong**, and the failures are quiet ones — plausible answers to questions the retrieval never actually addressed.

This lesson covers how to do structured-data RAG properly, exactly where it stops working, and the decision that matters most: recognising the questions for which retrieval is the wrong tool entirely.

## Learning objectives

By the end of this notebook you will be able to:

1. **Serialize a record into text deliberately**, and explain how that choice changes what becomes retrievable.
2. **Split fields between content and metadata** so semantic search and exact filtering each do the job they are good at.
3. **Demonstrate the three failure classes** — aggregation, numeric comparison, exact lookup — and explain why they are structural rather than tuning problems.
4. **Handle nested JSON** without either flattening away the structure or embedding noise.
5. **Decide between RAG and a query engine**, and route accordingly.

%%markdown
## Prerequisites

**Lessons**

- `01_Foundations/02_Document_Loading_and_Metadata.ipynb` — `CSVLoader`, `metadata_columns`, the content/metadata split.
- `01_Foundations/04_Vector_Stores_and_Index_Operations.ipynb` — metadata filtering, which Part 4 depends on.

**Packages**

`langchain-chroma`, `langchain-community`, `langchain-core`, `langchain-openai`, `pandas`.

**Services**

`OPENAI_API_KEY` (embeddings) and `EXPERIENTIALLABS_API_KEY` (generation, via `helpers.get_experientiallabs_llm`).

**Input assets**

`data.csv` from `04_Retrieval_and_RAG/shared_data/`, plus a slightly larger synthetic table built inline — five rows is too few to make the failure modes visible.

%%markdown
## Provenance and runtime status

Consolidated from:

| Source | Contribution |
| --- | --- |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/2. simple_csv_rag.ipynb` | The end-to-end CSV RAG pipeline. |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/json_rag.ipynb` | Nested-JSON handling and the "text to be embedded" framing. Its original implementation builds FAISS by hand with `sentence_transformers` and imports a local `jrag` module that is not in this repository; the *approach* is carried, the implementation is not. |
| `04_Retrieval_and_RAG/06_RAG_Naive_to_Production/01_Loading_Data/3. CSV_Loader.ipynb`, `4. JSON_Loader.ipynb` | Loader mechanics — already taught in lesson 02, referenced rather than repeated. |

**Added here, present in no source:** the failure-mode demonstrations in Part 3 and the routing decision in Part 6. Every source notebook builds a structured-data RAG pipeline and stops; none shows the questions it cannot answer, which is the part that determines whether you should build one at all.

**Runtime status:** see `RAG_MIGRATION_MANIFEST.md`.

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

%%code
# ============ IMPORTS AND ENVIRONMENT ============
import json
import shutil
import tempfile

import pandas as pd
from dotenv import load_dotenv

from helpers import get_experientiallabs_llm
from langchain_chroma import Chroma
from langchain_community.document_loaders import CSVLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings

load_dotenv(repo_root() / ".env")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = get_experientiallabs_llm(temperature=0.2)
print("Ready:", embeddings.model, "|", llm.model_name)

%%code
# ============ THE DATA ============
# A property listing table. Bigger than shared_data/data.csv (5 rows) because
# the failure modes in Part 3 need enough rows to be visible.
properties = pd.DataFrame([
    {"id": 101, "address": "123 Elm St", "city": "Springfield", "state": "CA",
     "beds": 3, "baths": 2, "price": 500_000, "year_built": 1998,
     "notes": "Renovated kitchen, large south-facing garden, quiet cul-de-sac."},
    {"id": 102, "address": "456 Oak St", "city": "Rivertown", "state": "TX",
     "beds": 2, "baths": 1, "price": 350_000, "year_built": 1975,
     "notes": "Needs work. Original fixtures throughout. Walk to the river."},
    {"id": 103, "address": "789 Pine Ave", "city": "Springfield", "state": "CA",
     "beds": 4, "baths": 3, "price": 780_000, "year_built": 2015,
     "notes": "Modern build, solar panels, home office, excellent school district."},
    {"id": 104, "address": "12 Maple Ct", "city": "Rivertown", "state": "TX",
     "beds": 3, "baths": 2, "price": 420_000, "year_built": 2004,
     "notes": "Family home with a pool and a two-car garage."},
    {"id": 105, "address": "77 Cedar Ln", "city": "Lakeview", "state": "CA",
     "beds": 5, "baths": 4, "price": 1_250_000, "year_built": 2020,
     "notes": "Lakefront. Floor-to-ceiling windows, private dock, wine cellar."},
    {"id": 106, "address": "9 Birch Rd", "city": "Lakeview", "state": "CA",
     "beds": 2, "baths": 1, "price": 295_000, "year_built": 1962,
     "notes": "Compact starter home near transit. Small yard, needs a new roof."},
    {"id": 107, "address": "34 Willow Way", "city": "Springfield", "state": "CA",
     "beds": 3, "baths": 2, "price": 610_000, "year_built": 2009,
     "notes": "Open plan living, hardwood floors, walkable to downtown."},
    {"id": 108, "address": "88 Spruce Dr", "city": "Rivertown", "state": "TX",
     "beds": 4, "baths": 3, "price": 465_000, "year_built": 1988,
     "notes": "Large lot, mature trees, detached workshop, no HOA."},
])

print(properties[["id", "city", "beds", "price", "year_built"]].to_string(index=False))
print(f"\n{len(properties)} rows, {len(properties.columns)} columns")

%%markdown
---

## Part 1 — The serialization decision

A record is a set of typed fields. An embedding model takes a string. Something has to turn one into the other, and **that transformation determines everything the system can retrieve.**

`CSVLoader` makes this choice for you: `"column: value"`, one line per field, every column included. It is a reasonable default and rarely the right one.

%%code
# ============ WHAT CSVLoader PRODUCES ============
# Using shared_data/data.csv, the same shape as our table.
default_docs = CSVLoader(file_path=str(asset("data.csv"))).load()
print("CSVLoader default serialization:")
print(repr(default_docs[0].page_content))
print()
print("Everything is in the text - including Property_ID, Zip_Code and price.")
print("All of it gets embedded. All of it competes for the model's attention.")

%%code
# ============ THREE SERIALIZATIONS OF THE SAME ROW ============
row = properties.iloc[0]

serializations = {
    "everything (CSVLoader style)":
        "\n".join(f"{k}: {v}" for k, v in row.items()),

    "natural language":
        (f"A {row.beds}-bedroom, {row.baths}-bathroom home at {row.address} in "
         f"{row.city}, {row.state}, built in {row.year_built} and listed at "
         f"${row.price:,}. {row.notes}"),

    "descriptive fields only":
        f"{row.notes} Located in {row.city}, {row.state}.",
}

for name, text in serializations.items():
    print(f"--- {name} ---")
    print(text)
    print()

%%markdown
Each of these produces a different vector, and therefore a different retrieval system:

**Everything** — identifiers and numbers become part of the semantic content. `500000` is tokenized as digits with no magnitude, so it contributes noise, not meaning. Property IDs actively dilute the vector.

**Natural language** — reads well and embeds well, because it matches how questions are phrased. Costs more tokens, and still cannot make numbers comparable.

**Descriptive only** — the cleanest vector: only genuinely semantic content. The structured fields do not disappear, they move to metadata, where they can be filtered *exactly*.

The third is usually right, and it is a direct application of lesson 02's rule: **free text is meaning and belongs in `page_content`; identifiers, categories and numbers are filters and belong in `metadata`.**

%%code
# ============ BUILD THE INDEX WITH A DELIBERATE SPLIT ============
def row_to_document(row) -> Document:
    """Descriptive text in page_content; everything structured in metadata."""
    return Document(
        page_content=f"{row.notes} Located in {row.city}, {row.state}.",
        metadata={
            "id": int(row.id),
            "address": row.address,
            "city": row.city,
            "state": row.state,
            "beds": int(row.beds),
            "baths": int(row.baths),
            "price": int(row.price),
            "year_built": int(row.year_built),
        },
    )


listings = [row_to_document(r) for r in properties.itertuples()]
persist_dir = tempfile.mkdtemp(prefix="rag_lesson05_")
store = Chroma.from_documents(
    listings,
    embeddings,
    ids=[str(d.metadata["id"]) for d in listings],   # stable ids - lesson 04
    collection_name="listings",
    persist_directory=persist_dir,
)

print(f"Indexed {store._collection.count()} listings")
print(f"Sample page_content: {listings[0].page_content!r}")
print(f"Sample metadata    : {listings[0].metadata}")

%%markdown
---

## Part 2 — What structured RAG does well

Semantic search over the descriptive fields is genuinely useful. It answers questions that no `WHERE` clause could express.

%%code
# ============ SEMANTIC SEARCH OVER DESCRIPTIONS ============
for q in [
    "somewhere peaceful with outdoor space",
    "a fixer-upper I could renovate",
    "good for someone who works from home",
]:
    hit = store.similarity_search(q, k=1)[0]
    print(f"Q: {q}")
    print(f"   -> {hit.metadata['address']}, {hit.metadata['city']}  "
          f"(${hit.metadata['price']:,})")
    print(f"      {hit.page_content}")
    print()

print("None of these are expressible in SQL. 'Peaceful with outdoor space'")
print("matched a quiet cul-de-sac with a garden; nothing in the row says")
print("'peaceful'. This is what embeddings are for.")

%%code
# ============ SEMANTIC + EXACT, TOGETHER ============
# The hybrid that makes structured RAG worth doing: fuzzy intent on the text,
# hard constraints on the metadata.
results = store.similarity_search(
    "modern and well maintained",
    k=3,
    filter={"$and": [{"state": {"$eq": "CA"}}, {"price": {"$lte": 800_000}}]},
)

print("'modern and well maintained', in CA, at most $800k:")
for d in results:
    m = d.metadata
    print(f"  {m['address']:<16} {m['city']:<12} ${m['price']:>9,}  built {m['year_built']}")

print("\nThe price constraint is EXACT because price is metadata, not text.")
print("Had we embedded the price, this filter would not have been possible.")

%%markdown
---

## Part 3 — Where it breaks

Three classes of question look like ordinary retrieval and are structurally unanswerable by it. This is not a tuning problem — no chunk size, no `k`, no prompt fixes them.

%%code
# ============ FAILURE 1: AGGREGATION ============
# "What is the average price?" requires reading EVERY row. Retrieval reads k.
retriever = store.as_retriever(search_kwargs={"k": 4})

prompt = ChatPromptTemplate.from_template(
    "Answer using only the context.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"
)


def format_docs(ds):
    return "\n\n".join(
        f"{d.page_content} [{d.metadata['address']}, ${d.metadata['price']:,}, "
        f"{d.metadata['beds']}bd, built {d.metadata['year_built']}]"
        for d in ds
    )


chain = ({"context": retriever | format_docs, "question": RunnablePassthrough()}
         | prompt | llm | StrOutputParser())

q = "What is the average listing price across all properties?"
print(f"Q: {q}")
print(f"RAG says     : {chain.invoke(q)}")
print(f"Truth        : ${properties.price.mean():,.0f}")
print(f"\nRetrieval saw {4} of {len(properties)} rows. The model averaged those and")
print("reported it confidently. The answer is wrong and nothing signals that.")

%%code
# ============ FAILURE 2: NUMERIC COMPARISON IN THE QUERY ============
# The constraint is in the text of the question, so it never becomes a filter.
q = "Which properties cost less than $400,000?"
print(f"Q: {q}")
print(f"RAG says: {chain.invoke(q)}")

truth = properties[properties.price < 400_000]
print(f"\nTruth: {', '.join(truth.address)} "
      f"({', '.join(f'${p:,}' for p in truth.price)})")

print("\nWhat retrieval actually did - the top 4 by SEMANTIC similarity to the")
print("phrase 'cost less than $400,000':")
for d in retriever.invoke(q):
    print(f"  ${d.metadata['price']:>9,}  {d.metadata['address']}")
print("\nThe number in the question was embedded as text. It did not filter.")

%%code
# ============ FAILURE 3: EXACT LOOKUP ============
q = "Tell me about property 108."
print(f"Q: {q}")
print(f"RAG says: {chain.invoke(q)}")
print(f"\nTruth   : {properties[properties.id == 108].iloc[0].address}, "
      f"{properties[properties.id == 108].iloc[0].city}")

print("\nRetrieved for that query:")
for d in retriever.invoke(q):
    print(f"  id={d.metadata['id']}  {d.metadata['address']}")
print("\nWe deliberately kept `id` out of page_content, so it is unsearchable")
print("semantically - correctly. An ID lookup is a database GET, not a search.")

%%markdown
### Why these are structural

| Failure | Cause | Not fixable by |
| --- | --- | --- |
| **Aggregation** (average, count, sum, "how many") | Retrieval reads `k` rows; aggregation needs all N | Raising `k` — that just moves the cliff and blows the context window |
| **Numeric / date comparison** ("under $400k", "since 2020") | The constraint sits in the query text and is embedded, not evaluated | Prompting — the model never sees the rows that were filtered out |
| **Exact lookup** (by ID, SKU, order number) | Embeddings encode similarity, and identifiers have no meaningful similarity | A better embedding model |
| **Ranking** ("the three cheapest") | Requires a total order over all rows | Anything within retrieval |

The common thread: **retrieval returns a sample, and these questions need the population.**

Note also how each failure *presented*: a fluent, confident, specific answer. Nothing in the output distinguished the wrong answers from the right ones. That is the real hazard.

%%markdown
---

## Part 4 — Two ways to fix it

### Fix 1: turn the query's constraints into metadata filters

If you can extract structured constraints from the question, you can apply them as filters — which is exact — and let the semantic part handle the rest. That is **self-querying retrieval**, and it fixes the comparison failure.

%%code
# ============ EXTRACTING FILTERS FROM THE QUESTION ============
# A minimal version of self-query: ask the model for a filter, not an answer.
from pydantic import BaseModel, Field


class ListingQuery(BaseModel):
    """Structured form of a natural-language property query."""

    semantic_query: str = Field(description="The descriptive part, for semantic search")
    max_price: int | None = Field(default=None, description="Maximum price, if stated")
    min_beds: int | None = Field(default=None, description="Minimum bedrooms, if stated")
    city: str | None = Field(default=None, description="City, if stated")


extractor = llm.with_structured_output(ListingQuery)

for q in ["Which properties cost less than $400,000?",
          "A modern 4-bedroom house in Springfield under $800k"]:
    parsed = extractor.invoke(f"Convert this property search into structured form: {q}")
    conds = []
    if parsed.max_price:
        conds.append({"price": {"$lte": parsed.max_price}})
    if parsed.min_beds:
        conds.append({"beds": {"$gte": parsed.min_beds}})
    if parsed.city:
        conds.append({"city": {"$eq": parsed.city}})
    flt = conds[0] if len(conds) == 1 else ({"$and": conds} if conds else None)

    print(f"Q: {q}")
    print(f"   parsed -> semantic={parsed.semantic_query!r}  filter={flt}")
    hits = store.similarity_search(parsed.semantic_query or q, k=5, filter=flt)
    for d in hits:
        print(f"     ${d.metadata['price']:>9,}  {d.metadata['beds']}bd  "
              f"{d.metadata['city']:<12} {d.metadata['address']}")
    print()

%%markdown
That is now correct — the price constraint is evaluated exactly, against every row, before similarity is considered. The full treatment, including how to describe your metadata schema to the model and what happens when extraction fails, is `03_Retrieval/02_Metadata_Filtering_and_Self_Query.ipynb`.

It still does not fix aggregation. Nothing in the retrieval paradigm does.

### Fix 2: stop retrieving

For aggregation and ranking, the right tool is a query engine. Give the model the *schema* and let it write a query that the database executes over all rows.

%%code
# ============ QUERY GENERATION INSTEAD OF RETRIEVAL ============
# The model writes pandas; pandas reads every row. No embeddings involved.
schema = "\n".join(f"  {c}: {properties[c].dtype}" for c in properties.columns)

query_prompt = ChatPromptTemplate.from_template(
    "DataFrame `df` with columns:\n{schema}\n\n"
    "Write ONE line of pandas returning the answer to: {question}\n"
    "Output only the expression, no backticks, no explanation."
)
query_chain = query_prompt | llm | StrOutputParser()

for q in ["What is the average listing price?",
          "How many properties are in California?",
          "Which three properties are cheapest? Return address and price."]:
    expr = query_chain.invoke({"schema": schema, "question": q}).strip().strip("`")
    # In production this must be sandboxed - see the warning below.
    result = eval(expr, {"df": properties, "pd": pd})   # noqa: S307
    print(f"Q: {q}")
    print(f"   pandas: {expr}")
    print(f"   result: {result}\n")

%%markdown
> **That `eval` is unsafe.** It executes model-generated code with full interpreter access. It is here to show the shape of the technique in the fewest lines. In anything real: generate **SQL** against a read-only connection with a query timeout, or use a sandboxed executor — never `eval` a string from an LLM. Prompt injection through a data field is a working attack against this pattern.

Compare the two approaches directly:

| | Retrieval (RAG) | Query generation |
| --- | --- | --- |
| Rows considered | `k` | All |
| "Peaceful with a garden" | **Yes** | No |
| "Average price" | No | **Yes** |
| "Cheapest three" | No | **Yes** |
| "Under $400k" | Only with filter extraction | **Yes** |
| Fails by | Answering from a sample | Raising, or returning an empty set |

Note that last row. Query generation fails *loudly* — a bad query errors. Retrieval fails *quietly* — it answers from whatever it happened to retrieve. For structured data that difference matters more than the accuracy numbers.

%%markdown
---

## Part 5 — Nested JSON

JSON adds a problem CSV does not have: **structure with depth**. A record can contain lists and nested objects, and neither embeds meaningfully.

%%code
# ============ NESTED RECORDS ============
api_response = {
    "results": [
        {"id": "TKT-4471", "status": "resolved", "priority": 2,
         "customer": {"name": "Acme Corp", "tier": "enterprise", "region": "EMEA"},
         "subject": "Export to CSV times out on large datasets",
         "tags": ["export", "performance", "timeout"],
         "messages": [{"from": "customer", "body": "Exports over 50k rows never finish."},
                      {"from": "agent", "body": "Raised the worker timeout; please retry."}]},
        {"id": "TKT-4472", "status": "open", "priority": 1,
         "customer": {"name": "Globex", "tier": "startup", "region": "AMER"},
         "subject": "SSO login loop after password reset",
         "tags": ["auth", "sso"],
         "messages": [{"from": "customer", "body": "Resetting my password logs me out again."}]},
        {"id": "TKT-4473", "status": "resolved", "priority": 3,
         "customer": {"name": "Initech", "tier": "enterprise", "region": "APAC"},
         "subject": "Invoice PDF shows the wrong currency symbol",
         "tags": ["billing", "i18n"],
         "messages": [{"from": "customer", "body": "Euro invoices render with a dollar sign."},
                      {"from": "agent", "body": "Locale fix shipped in 4.2.1."}]},
    ]
}
print(json.dumps(api_response["results"][0], indent=2)[:400], "...")

%%code
# ============ SERIALIZING A NESTED RECORD ============
# Two independent decisions:
#   1. What text conveys this record's MEANING?  -> page_content
#   2. What must be exactly filterable?          -> metadata, FLATTENED
def ticket_to_document(t: dict) -> Document:
    conversation = "\n".join(f"{m['from']}: {m['body']}" for m in t["messages"])
    return Document(
        page_content=f"{t['subject']}\n{conversation}",
        metadata={
            "id": t["id"],
            "status": t["status"],
            "priority": t["priority"],
            # Nested object -> dotted, flat keys. Chroma rejects dicts.
            "customer_name": t["customer"]["name"],
            "customer_tier": t["customer"]["tier"],
            "customer_region": t["customer"]["region"],
            # List -> a delimited string. See the caveat below.
            "tags": ",".join(t["tags"]),
        },
    )


tickets = [ticket_to_document(t) for t in api_response["results"]]
print("page_content:")
print(tickets[0].page_content)
print("\nmetadata:", tickets[0].metadata)
print("\nEvery metadata value is str or int - no dicts, no lists.")

%%code
# ============ QUERY THE TICKETS ============
ticket_dir = tempfile.mkdtemp(prefix="rag_lesson05_tickets_")
ticket_store = Chroma.from_documents(
    tickets, embeddings, ids=[t.metadata["id"] for t in tickets],
    collection_name="tickets", persist_directory=ticket_dir,
)

hit = ticket_store.similarity_search("customer cannot sign in", k=1)[0]
print(f"'customer cannot sign in' -> {hit.metadata['id']}: "
      f"{hit.page_content.splitlines()[0]}")

print("\nEnterprise customers only:")
for d in ticket_store.similarity_search(
    "problem with reports", k=3, filter={"customer_tier": "enterprise"}
):
    print(f"  {d.metadata['id']}  {d.metadata['customer_name']:<12} "
          f"{d.page_content.splitlines()[0]}")

%%markdown
**The `tags` field is a compromise, and worth being honest about.** Joining a list into `"export,performance,timeout"` makes it storable, but filtering becomes substring matching, not set membership — and `$eq` on that string only matches the exact full string in the exact order.

The options, none of them free:

- **A boolean column per tag** (`tag_export: True`) — exact filtering, but the schema grows with your vocabulary.
- **A delimited string plus `$contains`** where the backend supports it — approximate, and matches substrings across tag boundaries.
- **A separate relational store for tags**, with the vector store holding only IDs — correct, and now you are maintaining two systems.

There is no clean answer, which is itself the signal: when your filtering needs are genuinely relational, a vector store is the wrong primary home for that data.

%%markdown
---

## Part 6 — Choosing the tool

Route by the *kind of question*, not by the kind of data.

| The question is… | Use | Because |
| --- | --- | --- |
| Descriptive, fuzzy, subjective — "cosy", "similar to X" | **Retrieval** | Only embeddings capture this |
| An aggregate — count, sum, average, max | **Query engine** | Needs every row |
| A comparison or range — "under $400k", "since 2020" | **Filter, or a query engine** | Must be evaluated, not embedded |
| An exact lookup by identifier | **Database GET** | Identifiers have no useful similarity |
| A ranking — "the three cheapest" | **Query engine** | Needs a total order |
| Fuzzy *and* constrained — "modern homes in CA under $800k" | **Both** — filter + semantic search | Each does the half it is good at |

In a real system you route: classify the question, then dispatch to retrieval, to SQL, or to both. That classifier is `04_Query_Transformation_and_Routing/07_Classifier_Routing.ipynb`, and an agent choosing between a retrieval tool and a SQL tool is `07_Agentic_RAG/01_Retrieval_as_an_Agent_Tool.ipynb`.

%%code
# ============ A MINIMAL ROUTER ============
route_prompt = ChatPromptTemplate.from_template(
    "Classify this question about a property database.\n"
    "Reply with exactly one word:\n"
    "  AGGREGATE - needs counting, averaging, ranking, or every row\n"
    "  LOOKUP    - asks for one record by its identifier\n"
    "  SEMANTIC  - describes qualities or preferences\n\n"
    "Question: {question}"
)
router = route_prompt | llm | StrOutputParser()

for q in ["What is the average price?",
          "Tell me about property 108",
          "Somewhere quiet with a garden",
          "How many houses are in Texas?",
          "A modern place near good schools"]:
    print(f"{router.invoke(q).strip():<10} <- {q}")

print("\nEach route goes somewhere different: AGGREGATE to a query engine,")
print("LOOKUP to a database GET, SEMANTIC to the vector store. Sending all")
print("three to retrieval is what produced Part 3's confident wrong answers.")

%%code
# ============ CLEANUP ============
for d in (persist_dir, ticket_dir):
    shutil.rmtree(d, ignore_errors=True)
print("Temporary indexes removed.")

%%markdown
---

## Limitations and tradeoffs

**Eight rows and three tickets.** Enough to demonstrate the failure modes, nowhere near enough to characterize them. On a million-row table the aggregation failure is worse, not better.

**Query generation has its own failure modes** this lesson only gestured at: the model writes a query that runs but computes the wrong thing, silently. It needs its own validation — and the `eval` used here is genuinely unsafe outside a demo.

**The serialization guidance is a default, not a law.** Sometimes a number *should* be in the text — "built in 1962" carries real semantic weight in a way that "295000" does not. Judge per field: does this value have meaning, or only magnitude?

**Row-per-document is not always right.** For wide tables with many nulls, or for records that only make sense joined with another table, pre-joining or grouping before serialization often works better.

**Nothing here addresses freshness.** Structured data changes constantly, and re-embedding on every row update is expensive. That is `02_Chunking_and_Indexing/05_Incremental_Indexing_and_Record_Management.ipynb`.

%%markdown
---

## Exercise

Build a `StructuredRAG` that routes rather than assuming, so that questions it cannot answer by retrieval do not get answered by retrieval.

%%code
# ============ EXERCISE: A ROUTING STRUCTURED-DATA ASSISTANT ============
class StructuredRAG:
    """Route a question to retrieval or refuse it, instead of always retrieving."""

    def __init__(self, df: pd.DataFrame, store: Chroma, llm):
        self.df = df
        self.store = store
        self.llm = llm

    def classify(self, question: str) -> str:
        out = (route_prompt | self.llm | StrOutputParser()).invoke(question)
        return out.strip().upper().split()[0]

    def answer(self, question: str) -> str:
        route = self.classify(question)

        if route == "SEMANTIC":
            hits = self.store.similarity_search(question, k=3)
            listed = "\n".join(
                f"- {d.metadata['address']}, {d.metadata['city']} "
                f"(${d.metadata['price']:,}): {d.page_content}" for d in hits
            )
            return (ChatPromptTemplate.from_template(
                "Recommend from these listings only.\n\n{listings}\n\nRequest: {q}"
            ) | self.llm | StrOutputParser()).invoke({"listings": listed, "q": question})

        # Honest refusal beats a confident wrong number.
        return (
            f"[{route}] This needs a query over the whole table, which retrieval "
            f"cannot do. Route it to the query engine instead."
        )

    # TODO 1: implement the AGGREGATE branch with generated pandas or SQL.
    #         Do NOT use eval - use df.query, a whitelist of operations, or a
    #         sandboxed executor. What happens when the generated query errors?
    #
    # TODO 2: implement LOOKUP as a direct metadata get (store.get(ids=[...])),
    #         not a similarity search. How do you extract the id from the text?
    #
    # TODO 3: add a HYBRID route for "modern homes in CA under $800k" - reuse
    #         the ListingQuery extractor from Part 4. How should the router
    #         distinguish HYBRID from SEMANTIC?


demo_dir = tempfile.mkdtemp(prefix="rag_lesson05_demo_")
demo_store = Chroma.from_documents(
    listings, embeddings, ids=[str(d.metadata["id"]) for d in listings],
    collection_name="demo", persist_directory=demo_dir,
)
assistant = StructuredRAG(properties, demo_store, llm)

for q in ["I want somewhere quiet with outdoor space",
          "What is the average price of all listings?"]:
    print(f"Q: {q}")
    print(f"A: {assistant.answer(q)}\n")

shutil.rmtree(demo_dir, ignore_errors=True)

%%markdown
---

## Summary

**Serialization is the whole design.** Turning a record into text decides what is retrievable. Descriptive text belongs in `page_content`; identifiers, categories, numbers and dates belong in `metadata`, where they can be filtered exactly.

**What structured RAG is good at:** fuzzy, descriptive, subjective queries over free-text fields — and those combined with hard constraints via metadata filters. That combination is genuinely powerful and hard to get any other way.

**What it cannot do**, structurally, because retrieval returns a sample and these need the population:

- Aggregation — count, sum, average, max
- Numeric and date comparison stated in the query
- Exact lookup by identifier
- Ranking over all rows

**Two fixes.** Extract constraints from the question into metadata filters (self-query) — this handles comparison. For aggregation and ranking, stop retrieving and generate a query instead; the database reads every row. Sandbox any generated code.

**Route by question type, not data type.** The most valuable thing in this lesson is the refusal: a system that says "this needs a query engine" is more useful than one that confidently averages four of eight rows.

**Nested JSON** flattens into dotted metadata keys. Lists have no good answer — if your filtering is genuinely relational, the vector store is the wrong primary home for that data.

### Next section

This completes `01_Foundations/`. Next is `02_Chunking_and_Indexing/01_Document_Splitting_and_Chunking.ipynb` — how documents get divided before they are embedded, and why that decision drives retrieval quality more than almost anything else.

%%markdown
---

### Migration record

Canonical lesson for concept `RAG-F-05` (structured-data RAG), Foundations batch, and the final lesson of `01_Foundations/`.

The failure-mode demonstrations (Part 3) and the routing decision (Part 6) appear in no source notebook — every source builds a structured-data pipeline and stops at the point where it works. `json_rag.ipynb`'s hand-rolled FAISS + `sentence_transformers` implementation was not carried: it imports a local `jrag` module absent from this repository, and its approach is covered here on the repository's standard stack. See `RAG_MIGRATION_MANIFEST.md` for per-source disposition.
