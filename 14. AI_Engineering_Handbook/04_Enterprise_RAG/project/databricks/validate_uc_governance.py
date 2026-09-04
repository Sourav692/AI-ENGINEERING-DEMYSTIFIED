# -*- coding: utf-8 -*-
"""Validate the Databricks design doc's SQL against the real workspace.

Everything is created inside a throwaway schema and dropped at the end.
"""
from dbx_sql import run, sql

CAT = "main"
SCH = "rag_acl_validation"

print("=" * 78)
print("STEP 0 - environment")
print("=" * 78)
run("identity functions available",
    "SELECT current_user() AS u, is_account_group_member('kb_admins') AS in_grp, "
    "current_date() AS today")

run("create throwaway schema", f"CREATE SCHEMA IF NOT EXISTS {CAT}.{SCH}", show=False)

print()
print("=" * 78)
print("STEP 1 - the SILVER chunks table exactly as the design doc declares it")
print("=" * 78)

run("create chunks table", f"""
CREATE OR REPLACE TABLE {CAT}.{SCH}.chunks (
  chunk_id        STRING NOT NULL,
  doc_id          STRING,
  title           STRING,
  section         STRING,
  content         STRING,
  tenant_id       STRING,
  source_system   STRING,
  sensitivity     STRING,
  sensitivity_lvl INT,
  region          STRING,
  contains_pii    BOOLEAN,
  need_to_know    STRING,
  valid_from      DATE,
  valid_until     DATE,
  grp_public      BOOLEAN,
  grp_support_t1  BOOLEAN,
  grp_support_t3  BOOLEAN,
  grp_engineering BOOLEAN,
  grp_sales       BOOLEAN,
  grp_legal       BOOLEAN,
  grp_security    BOOLEAN,
  updated_at      TIMESTAMP
) TBLPROPERTIES (delta.enableChangeDataFeed = true)
""", show=False)

run("CDF actually enabled",
    f"SELECT key, value FROM (DESCRIBE DETAIL {CAT}.{SCH}.chunks) "
    f"LATERAL VIEW explode(properties) AS key, value "
    f"WHERE key LIKE '%changeDataFeed%'")

run("seed rows mirroring the corpus", f"""
INSERT INTO {CAT}.{SCH}.chunks VALUES
 ('HC-002#0','HC-002','Error MRD-5031','What it means','Data was not durably stored. Contact ops@meridiancloud.example.',
  'meridian','helpcenter','public',0,'GLOBAL',false,NULL,NULL,NULL,
  true,false,false,false,false,false,false,current_timestamp()),
 ('PM-2026-03-14#0','PM-2026-03-14','Post-mortem EU Ingest','Root cause','Cardinality explosion saturated compaction.',
  'meridian','postmortem','confidential',2,'EU',false,NULL,NULL,NULL,
  false,false,true,true,false,false,false,current_timestamp()),
 ('CT-VTX-001#0','CT-VTX-001','Vertex MSA','Service credits','Below 99.5%: 25% credit. ACV EUR 1,240,000.',
  'meridian','contract','confidential',2,'EU',false,NULL,NULL,NULL,
  false,false,false,false,true,true,false,current_timestamp()),
 ('SA-2026-07#0','SA-2026-07','Advisory EMBARGOED','Summary','Write key scoping flaw. Fixed in 4.12.4.',
  'meridian','advisory','restricted',3,'GLOBAL',false,'vuln-response',DATE'2026-09-01',NULL,
  false,false,false,false,false,false,true,current_timestamp()),
 ('TK-4488#0','TK-4488','Ticket 4488','Customer','Reporter dan.okafor@northgateretail.example reports timeouts.',
  'meridian','ticket','internal',1,'US',true,NULL,NULL,NULL,
  false,true,true,false,false,false,false,current_timestamp())
""", show=False)

run("row count", f"SELECT count(*) AS n FROM {CAT}.{SCH}.chunks")

print()
print("=" * 78)
print("STEP 2 - entitlements table + THE ROW FILTER from the design doc")
print("=" * 78)

run("create entitlements table", f"""
CREATE OR REPLACE TABLE {CAT}.{SCH}.user_entitlements (
  user_email STRING, clearance_lvl INT, region STRING,
  compartment STRING, is_external BOOLEAN)
""", show=False)

run("seed my own identity as a Tier-1 agent (clearance=internal, EU)", f"""
INSERT INTO {CAT}.{SCH}.user_entitlements
SELECT current_user(), 1, 'EU', NULL, false
""", show=False)

r = run("CREATE the row filter UDF (7 rules)", f"""
CREATE OR REPLACE FUNCTION {CAT}.{SCH}.chunk_row_filter(
  tenant_id STRING, sensitivity_lvl INT, region STRING,
  need_to_know STRING, valid_from DATE, valid_until DATE, source_system STRING)
RETURN
  is_account_group_member('kb_admins')
  OR EXISTS (
    SELECT 1 FROM {CAT}.{SCH}.user_entitlements e
    WHERE e.user_email = current_user()
      AND tenant_id = 'meridian'
      AND sensitivity_lvl <= e.clearance_lvl
      AND (region = 'GLOBAL' OR region = e.region)
      AND (valid_from  IS NULL OR valid_from  <= current_date())
      AND (valid_until IS NULL OR valid_until >= current_date())
      AND (need_to_know IS NULL OR need_to_know = e.compartment)
      AND (NOT e.is_external OR source_system NOT IN ('contract','pricing','postmortem'))
  )
""", show=False)

r2 = run("ATTACH the row filter to the table", f"""
ALTER TABLE {CAT}.{SCH}.chunks SET ROW FILTER {CAT}.{SCH}.chunk_row_filter
  ON (tenant_id, sensitivity_lvl, region, need_to_know, valid_from, valid_until, source_system)
""", show=False)

if r2["ok"]:
    print()
    run("*** ROWS VISIBLE AS A TIER-1 AGENT (clearance=internal, EU) ***",
        f"SELECT chunk_id, sensitivity, region FROM {CAT}.{SCH}.chunks ORDER BY chunk_id")
    run("leak assertion: can I see the contract?",
        f"SELECT count(*) AS must_be_zero FROM {CAT}.{SCH}.chunks WHERE doc_id='CT-VTX-001'")
    run("leak assertion: can I see the post-mortem?",
        f"SELECT count(*) AS must_be_zero FROM {CAT}.{SCH}.chunks WHERE doc_id='PM-2026-03-14'")

    print()
    print("--- now promote myself to confidential clearance (simulating a group change) ---")
    run("update entitlement", f"""
        UPDATE {CAT}.{SCH}.user_entitlements SET clearance_lvl = 2
        WHERE user_email = current_user()""", show=False)
    run("*** ROWS VISIBLE AFTER PROMOTION (no reindex, no DDL) ***",
        f"SELECT chunk_id, sensitivity, region FROM {CAT}.{SCH}.chunks ORDER BY chunk_id")

    print()
    print("--- embargo: the advisory is restricted AND embargoed until 2026-09-01 ---")
    run("promote to restricted + vuln-response compartment", f"""
        UPDATE {CAT}.{SCH}.user_entitlements
        SET clearance_lvl = 3, compartment = 'vuln-response'
        WHERE user_email = current_user()""", show=False)
    run("advisory still hidden? (today < 2026-09-01)",
        f"SELECT count(*) AS embargoed_should_be_zero FROM {CAT}.{SCH}.chunks WHERE doc_id='SA-2026-07'")

    print()
    print("--- external contractor rule ---")
    run("mark myself external", f"""
        UPDATE {CAT}.{SCH}.user_entitlements SET is_external = true
        WHERE user_email = current_user()""", show=False)
    run("commercial sources now blocked despite max clearance",
        f"SELECT source_system, count(*) AS n FROM {CAT}.{SCH}.chunks "
        f"GROUP BY source_system ORDER BY source_system")
    run("reset", f"""
        UPDATE {CAT}.{SCH}.user_entitlements SET is_external = false, clearance_lvl = 1,
        compartment = NULL WHERE user_email = current_user()""", show=False)

print()
print("=" * 78)
print("STEP 3 - THE COLUMN MASK (PII obligation)")
print("=" * 78)

r3 = run("create the mask UDF", f"""
CREATE OR REPLACE FUNCTION {CAT}.{SCH}.pii_mask(content STRING, contains_pii BOOLEAN)
RETURN CASE
  WHEN NOT contains_pii THEN content
  WHEN is_account_group_member('pii_readers') THEN content
  ELSE regexp_replace(content, '[\\\\w.+-]+@[\\\\w-]+\\\\.[\\\\w.-]+', '[REDACTED_EMAIL]')
END
""", show=False)

r4 = run("attach the mask to content USING COLUMNS (contains_pii)", f"""
ALTER TABLE {CAT}.{SCH}.chunks
  ALTER COLUMN content SET MASK {CAT}.{SCH}.pii_mask USING COLUMNS (contains_pii)
""", show=False)

if r4["ok"]:
    run("*** PII redacted for a non-pii_reader, untouched where contains_pii=false ***", f"""
        SELECT chunk_id, contains_pii, substr(content, 1, 78) AS content
        FROM {CAT}.{SCH}.chunks ORDER BY chunk_id""")

print()
print("=" * 78)
print("STEP 4 - does the design's DESCRIBE show the policies attached?")
print("=" * 78)
run("row filter + mask visible in metadata",
    f"DESCRIBE EXTENDED {CAT}.{SCH}.chunks")

print()
print("=" * 78)
print("CLEANUP")
print("=" * 78)
run("drop schema", f"DROP SCHEMA IF EXISTS {CAT}.{SCH} CASCADE", show=False)
run("confirm gone", f"SHOW SCHEMAS IN {CAT} LIKE 'rag_acl_validation'")
