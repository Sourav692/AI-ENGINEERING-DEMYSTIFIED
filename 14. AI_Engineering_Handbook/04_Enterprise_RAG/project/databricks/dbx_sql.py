# -*- coding: utf-8 -*-
"""Minimal SQL runner against the DEFAULT Databricks profile via the REST API.

No SDK install required - reads host/token straight from ~/.databrickscfg and calls
the SQL Statement Execution API. Used only to validate the design's SQL against a
real Unity Catalog metastore.
"""
import configparser
import json
import os
import sys
import time

import requests

WAREHOUSE_ID = "4a98b5426511d377"

cfg = configparser.ConfigParser()
cfg.read(os.path.expanduser("~/.databrickscfg"))
HOST = cfg["DEFAULT"]["host"].rstrip("/")
TOKEN = cfg["DEFAULT"]["token"]
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def sql(statement, catalog=None, schema=None, timeout=300):
    body = {
        "warehouse_id": WAREHOUSE_ID,
        "statement": statement,
        "wait_timeout": "30s",
        "on_wait_timeout": "CONTINUE",
    }
    if catalog:
        body["catalog"] = catalog
    if schema:
        body["schema"] = schema

    r = requests.post(f"{HOST}/api/2.0/sql/statements", headers=H, json=body, timeout=120)
    if r.status_code != 200:
        return {"ok": False, "error": f"HTTP {r.status_code}: {r.text[:400]}"}
    d = r.json()

    sid = d["statement_id"]
    deadline = time.time() + timeout
    while d["status"]["state"] in ("PENDING", "RUNNING") and time.time() < deadline:
        time.sleep(2)
        d = requests.get(f"{HOST}/api/2.0/sql/statements/{sid}", headers=H, timeout=60).json()

    state = d["status"]["state"]
    if state != "SUCCEEDED":
        err = d["status"].get("error", {})
        return {"ok": False, "error": f"{state}: {err.get('error_code','')} "
                                      f"{err.get('message','')[:500]}"}
    cols = [c["name"] for c in d.get("manifest", {}).get("schema", {}).get("columns", [])]
    rows = d.get("result", {}).get("data_array", []) or []
    return {"ok": True, "columns": cols, "rows": rows}


def run(label, statement, catalog=None, schema=None, show=True):
    res = sql(statement, catalog, schema)
    status = "OK  " if res["ok"] else "FAIL"
    print(f"[{status}] {label}")
    if not res["ok"]:
        print(f"         {res['error']}")
    elif show and res["rows"]:
        print(f"         {res['columns']}")
        for row in res["rows"][:12]:
            print(f"         {row}")
    return res


if __name__ == "__main__":
    stmt = sys.argv[1] if len(sys.argv) > 1 else "SELECT current_user() AS me"
    print(json.dumps(sql(stmt), indent=2)[:3000])
