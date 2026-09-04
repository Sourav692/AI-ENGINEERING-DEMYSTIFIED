# -*- coding: utf-8 -*-
"""THE critical claim: can a Vector Search filter express ABAC group-overlap?

Creates a tiny Delta table with the design's ACL columns, indexes it on the EXISTING
endpoint (no new billable endpoint), runs the exact filters the design doc prescribes,
then deletes the index and schema.
"""
import configparser
import json
import os
import time

import requests

from dbx_sql import run, sql

cfg = configparser.ConfigParser()
cfg.read(os.path.expanduser("~/.databrickscfg"))
HOST = cfg["DEFAULT"]["host"].rstrip("/")
H = {"Authorization": f"Bearer {cfg['DEFAULT']['token']}", "Content-Type": "application/json"}

ENDPOINT = "rag_demo_endpoint"
CAT, SCH = "agents", "acl_filter_test"
TABLE = f"{CAT}.{SCH}.chunks"
INDEX = f"{CAT}.{SCH}.chunks_idx"

print("=" * 78)
print("STEP 1 - source table with the design's ACL columns")
print("=" * 78)
run("schema", f"CREATE SCHEMA IF NOT EXISTS {CAT}.{SCH}", show=False)
run("table", f"""
CREATE OR REPLACE TABLE {TABLE} (
  chunk_id STRING NOT NULL, doc_id STRING, content STRING,
  tenant_id STRING, sensitivity_lvl INT, region STRING, source_system STRING,
  grp_public BOOLEAN, grp_support_t1 BOOLEAN, grp_support_t3 BOOLEAN,
  grp_engineering BOOLEAN, grp_sales BOOLEAN
) TBLPROPERTIES (delta.enableChangeDataFeed = true)
""", show=False)

run("seed 5 chunks across the access matrix", f"""
INSERT INTO {TABLE} VALUES
 ('HC#0','HC-002','Error MRD-5031 means backpressure; data was not durably stored.',
  'meridian',0,'GLOBAL','helpcenter', true,false,false,false,false),
 ('RB#0','RB-101','Runbook: scale compaction workers, never ingest workers first.',
  'meridian',1,'GLOBAL','runbook',     false,false,true,true,false),
 ('PM#0','PM-2026-03-14','Post-mortem: cardinality explosion saturated compaction in EU.',
  'meridian',2,'EU','postmortem',      false,false,true,true,false),
 ('CT#0','CT-VTX-001','Vertex MSA: below 99.5% availability yields a 25% service credit.',
  'meridian',2,'EU','contract',        false,false,false,false,true),
 ('TK#0','TK-4488','Ticket: Northgate query timeouts after no customer-side change.',
  'meridian',1,'US','ticket',          false,true,true,false,false)
""", show=False)
run("rows", f"SELECT count(*) AS n FROM {TABLE}")

print()
print("=" * 78)
print("STEP 2 - build the Delta Sync index on the EXISTING endpoint")
print("=" * 78)
body = {
    "name": INDEX,
    "endpoint_name": ENDPOINT,
    "primary_key": "chunk_id",
    "index_type": "DELTA_SYNC",
    "delta_sync_index_spec": {
        "source_table": TABLE,
        "pipeline_type": "TRIGGERED",
        "embedding_source_columns": [
            {"name": "content", "embedding_model_endpoint_name": "databricks-gte-large-en"}
        ],
        "columns_to_sync": ["chunk_id", "doc_id", "content", "tenant_id", "sensitivity_lvl",
                            "region", "source_system", "grp_public", "grp_support_t1",
                            "grp_support_t3", "grp_engineering", "grp_sales"],
    },
}
r = requests.post(f"{HOST}/api/2.0/vector-search/indexes", headers=H, json=body, timeout=120)
print(f"create index -> HTTP {r.status_code} {r.text[:300] if r.status_code != 200 else 'OK'}")

print("waiting for sync...")
for _ in range(60):
    time.sleep(10)
    g = requests.get(f"{HOST}/api/2.0/vector-search/indexes/{INDEX}", headers=H, timeout=60).json()
    st = g.get("status", {})
    state = st.get("detailed_state", "?")
    if st.get("ready"):
        print(f"  ready. state={state}  indexed={st.get('indexed_row_count')}")
        break
    print(f"  ... {state}")
else:
    print("  TIMED OUT waiting for index")

QURL = f"{HOST}/api/2.0/vector-search/indexes/{INDEX}/query"
COLS = ["chunk_id", "doc_id", "sensitivity_lvl", "region", "source_system"]


def q(label, filters, expect=None):
    body = {"columns": COLS, "num_results": 10,
            "query_text": "ingestion incident credits runbook"}
    if filters is not None:
        body["filters_json"] = json.dumps(filters)
    r = requests.post(QURL, headers=H, json=body, timeout=120)
    if r.status_code != 200:
        print(f"[FAIL] {label}\n       HTTP {r.status_code}: {r.text[:260]}")
        return None
    rows = r.json().get("result", {}).get("data_array", []) or []
    got = sorted(row[0] for row in rows)
    verdict = ""
    if expect is not None:
        verdict = "  <-- MATCHES EXPECTED" if got == sorted(expect) else \
                  f"  <-- MISMATCH, expected {sorted(expect)}"
    print(f"[OK  ] {label}\n       returned {got}{verdict}")
    return got


print()
print("=" * 78)
print("STEP 3 - THE ABAC FILTERS FROM THE DESIGN DOC")
print("=" * 78)

print("\n-- no filter (what an unfiltered index would leak) --")
q("no filter at all", None, expect=["CT#0", "HC#0", "PM#0", "RB#0", "TK#0"])

print("\n-- Tier-1 agent: clearance=1(internal), region=EU, groups={public,support_t1} --")
q("tier1 ABAC filter", {
    "tenant_id": "meridian",
    "sensitivity_lvl <=": 1,
    "region": ["GLOBAL", "EU"],
    "grp_public OR grp_support_t1": [True, True],
}, expect=["HC#0"])

print("\n-- Tier-3 engineer: clearance=2, region=EU, groups={support_t3,engineering} --")
q("tier3 ABAC filter", {
    "tenant_id": "meridian",
    "sensitivity_lvl <=": 2,
    "region": ["GLOBAL", "EU"],
    "grp_support_t3 OR grp_engineering": [True, True],
}, expect=["RB#0", "PM#0"])

print("\n-- Account manager: clearance=2, region=EU, groups={sales} --")
q("sales ABAC filter", {
    "tenant_id": "meridian",
    "sensitivity_lvl <=": 2,
    "region": ["GLOBAL", "EU"],
    "grp_sales": True,
}, expect=["CT#0"])

print("\n-- US Tier-3: same role as EU Tier-3 but region=US (data residency) --")
q("us tier3 - EU docs must vanish", {
    "tenant_id": "meridian",
    "sensitivity_lvl <=": 2,
    "region": ["GLOBAL", "US"],
    "grp_support_t3 OR grp_engineering": [True, True],
}, expect=["RB#0", "TK#0"])

print("\n-- Cross-tenant principal with EVERY group and max clearance --")
q("other tenant - must be empty", {
    "tenant_id": "acme",
    "sensitivity_lvl <=": 3,
    "grp_public OR grp_support_t1 OR grp_support_t3 OR grp_engineering OR grp_sales": [True, True, True, True, True],
}, expect=[])

print("\n-- External contractor: source exclusion via NOT --")
q("external - no commercial sources", {
    "tenant_id": "meridian",
    "sensitivity_lvl <=": 2,
    "source_system NOT": ["contract", "pricing", "postmortem"],
    "grp_support_t3 OR grp_engineering": [True, True],
}, expect=["RB#0"])

print()
print("=" * 78)
print("CLEANUP")
print("=" * 78)
d = requests.delete(f"{HOST}/api/2.0/vector-search/indexes/{INDEX}", headers=H, timeout=120)
print(f"delete index -> HTTP {d.status_code}")
run("drop schema", f"DROP SCHEMA IF EXISTS {CAT}.{SCH} CASCADE", show=False)
run("confirm gone", f"SHOW SCHEMAS IN {CAT} LIKE 'acl_filter_test'")
