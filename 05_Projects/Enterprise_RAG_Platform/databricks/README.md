# Databricks validation scripts

Live-workspace proof for the claims in `../docs/03-theory-databricks.md`. Everything creates
throwaway objects and drops them afterwards.

**Auth:** reads `host` + `token` from the `[DEFAULT]` section of `~/.databrickscfg`. No SDK install
needed — plain `requests` against the REST API, so it works on any CLI version. (The workspace CLI is
v0.249.0, below the v0.292.0 floor the Databricks skills assume, and its `experimental aitools` SQL
path does not exist — hence the direct REST approach.)

**Before running:** set `WAREHOUSE_ID` in `dbx_sql.py` and `ENDPOINT` in
`validate_vector_search_acl.py` to match your workspace.

| Script | Proves |
|---|---|
| `dbx_sql.py` | Shared SQL runner (Statement Execution API) |
| `validate_uc_governance.py` | The 7-rule **row filter**, the conditional **column mask**, live entitlement changes, embargo, external-principal rule, CDF |
| `validate_vector_search_syntax.py` | Hybrid search; dict filter operators; SQL-string filters rejected on Standard; reranker parameter |
| `validate_vector_search_acl.py` | **The ABAC group-overlap filter** — builds a real Delta Sync index and checks 6 personas return exactly the right documents |

```bash
python databricks/validate_uc_governance.py
python databricks/validate_vector_search_syntax.py
python databricks/validate_vector_search_acl.py   # creates + deletes an index; takes ~3 min
```

## Results as of 2026-08-22

**Unity Catalog governance — all passed.** Tier-1 saw 2 of 5 rows; contract and post-mortem returned
`count(*) = 0`; a clearance change took effect on the next query with no DDL and no reindex; the
embargoed advisory stayed hidden even at restricted clearance with the right compartment; the column
mask redacted one row and left another untouched in the same query.

**Vector Search — passed, with one correction to the design.** 6 of 6 personas returned exactly the
expected document sets, including a cross-tenant principal with every group and top clearance
returning zero rows. Hybrid search and the dict filter operators all work, and SQL-string filters are
correctly rejected on a Standard endpoint.

**The correction:** the multi-column `OR` filter is **positional** — it needs an array with one value
per clause, not a scalar:

```python
{"grp_a OR grp_b": True}          # 400: "input must be an array"
{"grp_a OR grp_b": [True]}        # 400: "length of value != number of clauses"
{"grp_a OR grp_b": [True, True]}  # ✅
```

**Not verified:** the managed reranker (the API accepted the parameter shape, but this workspace
returned *"a workspace-level configuration is preventing us from accessing the reranker model"*), and
on-behalf-of-user auth (public preview, needs admin enablement).
