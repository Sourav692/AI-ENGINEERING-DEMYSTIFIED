# -*- coding: utf-8 -*-
"""Validate the design doc's Vector Search claims against the live STANDARD endpoint."""
import configparser
import json
import os

import requests

cfg = configparser.ConfigParser()
cfg.read(os.path.expanduser("~/.databrickscfg"))
HOST = cfg["DEFAULT"]["host"].rstrip("/")
H = {"Authorization": f"Bearer {cfg['DEFAULT']['token']}", "Content-Type": "application/json"}

INDEX = "agents.main.rag_demo_vs_index"
URL = f"{HOST}/api/2.0/vector-search/indexes/{INDEX}/query"


def q(label, body):
    r = requests.post(URL, headers=H, json=body, timeout=120)
    if r.status_code != 200:
        print(f"[FAIL] {label}")
        print(f"       HTTP {r.status_code}: {r.text[:300]}")
        return None
    d = r.json()
    rows = d.get("result", {}).get("data_array", []) or []
    cols = [c["name"] for c in d.get("manifest", {}).get("columns", [])]
    print(f"[OK  ] {label}  -> {len(rows)} rows, columns={cols}")
    for row in rows[:3]:
        preview = str(row[1])[:60].replace("\n", " ") if len(row) > 1 else str(row)[:60]
        print(f"         id={row[0]}  {preview}...  score={row[-1]}")
    return rows


BASE = {"columns": ["chunk_id", "content"], "num_results": 3}

print("=" * 78)
print("VECTOR SEARCH CLAIM VALIDATION - endpoint type: STANDARD")
print("=" * 78)

print("\n--- 1. baseline semantic (ANN) query ---")
q("ANN query_text", {**BASE, "query_text": "how do I fix ingestion problems"})

print("\n--- 2. CLAIM: hybrid search is a single parameter ---")
q("query_type=HYBRID", {**BASE, "query_text": "MRD-5031 backpressure",
                        "query_type": "HYBRID"})

print("\n--- 3. CLAIM: dictionary filter syntax on a STANDARD endpoint ---")
q("equality  {'chunk_id': 3}",
  {**BASE, "query_text": "ingestion", "filters_json": json.dumps({"chunk_id": 3})})
q("IN list   {'chunk_id': [1,2,3]}",
  {**BASE, "query_text": "ingestion", "filters_json": json.dumps({"chunk_id": [1, 2, 3]})})
q("range     {'chunk_id >=': 20}",
  {**BASE, "query_text": "ingestion", "filters_json": json.dumps({"chunk_id >=": 20})})
q("negation  {'chunk_id NOT': 1}",
  {**BASE, "query_text": "ingestion", "filters_json": json.dumps({"chunk_id NOT": 1})})

print("\n--- 4. CLAIM: SQL-string filters are REJECTED on a STANDARD endpoint ---")
print("      (the design says SQL-string filters are a Storage-Optimized feature)")
q("SQL string 'chunk_id >= 20'",
  {**BASE, "query_text": "ingestion", "filters_json": "chunk_id >= 20"})

print("\n--- 5. CLAIM: managed reranker is a parameter ---")
q("databricks_reranker",
  {**BASE, "query_text": "ingestion problems",
   "reranker": {"model": "databricks_reranker",
                "parameters": {"columns_to_rerank": ["content"]}}})
