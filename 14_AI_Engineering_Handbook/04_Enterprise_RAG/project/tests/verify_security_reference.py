# -*- coding: utf-8 -*-
"""Assert every factual claim made in docs/04-security-checks-reference.md.

Run after changing the corpus, the personas, or the policy - the reference doc quotes
concrete counts and denial rules, and this is what stops them going stale.

    python tests/verify_security_reference.py
"""
import sys
from collections import Counter
from pathlib import Path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from enterprise_rag.authz.policy import decide
from enterprise_rag.identity import list_principals
from enterprise_rag.ingest.loader import load_corpus

TODAY = "2026-08-22"
docs = {d.attrs.doc_id: d.attrs for d in load_corpus()}
people = {p.user_id: p for p in list_principals()}
D = lambda u, d, as_of=TODAY: decide(people[u], docs[d], {"as_of": as_of})

fails = []
def check(label, cond):
    print(("  OK   " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)

print("== corpus / persona counts ==")
check("22 documents", len(docs) == 22)
check("9 personas", len(people) == 9)

print("\n== rule counts across the matrix ==")
counts = Counter()
for u in people:
    for d in docs:
        dec = D(u, d)
        if not dec.allowed:
            counts[dec.rule] += 1
expected = {"default_deny": 41, "data_residency": 29, "clearance": 28,
            "tenant_isolation": 22, "external_restriction": 5, "embargo": 2,
            "need_to_know": 1}
for rule, n in expected.items():
    check(f"{rule} = {n}", counts.get(rule) == n)

print("\n== per-persona readable counts ==")
pool = {u: sum(1 for d in docs if D(u, d).allowed) for u in people}
for u, n in [("u_marco_t3",14),("u_jin_us_t3",12),("u_ravi_sec",11),("u_sofia_am",8),
             ("u_dana_ext",8),("u_lena_t1",7),("u_tom_contractor",6),
             ("u_erin_secmgr",4),("u_attacker_other_tenant",0)]:
    check(f"{u} reads {n}/22", pool[u] == n)

print("\n== check 1: tenant isolation ==")
check("attacker denied CT-KST-003 by tenant_isolation",
      D("u_attacker_other_tenant","CT-KST-003").rule == "tenant_isolation")
check("attacker reads nothing at all", pool["u_attacker_other_tenant"] == 0)

print("\n== check 2: clearance ==")
check("lena denied CT-KST-003 by clearance", D("u_lena_t1","CT-KST-003").rule == "clearance")

print("\n== check 3: residency (marco vs jin, identical role) ==")
m, j = people["u_marco_t3"], people["u_jin_us_t3"]
check("marco/jin same clearance+groups", m.clearance == j.clearance and sorted(m.groups) == sorted(j.groups))
check("marco EU, jin US", m.region == "EU" and j.region == "US")
check("PM-2026-03-14: marco ALLOW", D("u_marco_t3","PM-2026-03-14").allowed)
check("PM-2026-03-14: jin residency", D("u_jin_us_t3","PM-2026-03-14").rule == "data_residency")
check("TK-4471: jin residency", D("u_jin_us_t3","TK-4471").rule == "data_residency")
check("TK-4488: marco residency", D("u_marco_t3","TK-4488").rule == "data_residency")
check("TK-4488: jin ALLOW", D("u_jin_us_t3","TK-4488").allowed)
check("RB-101 GLOBAL: both allow", D("u_marco_t3","RB-101").allowed and D("u_jin_us_t3","RB-101").allowed)
check("ravi (GLOBAL) denied EU postmortem by residency",
      D("u_ravi_sec","PM-2026-03-14").rule == "data_residency")

print("\n== check 4: embargo ==")
check("ravi denied SA-2026-07 today by embargo", D("u_ravi_sec","SA-2026-07").rule == "embargo")
check("ravi ALLOWED SA-2026-07 on 2026-09-01", D("u_ravi_sec","SA-2026-07","2026-09-01").allowed)
check("erin still denied on 2026-09-01 by need_to_know",
      D("u_erin_secmgr","SA-2026-07","2026-09-01").rule == "need_to_know")
check("nobody reads SA-2026-07 today",
      all(not D(u,"SA-2026-07").allowed for u in people))

print("\n== check 5: need-to-know (ravi vs erin) ==")
check("ravi ALLOW SA-2026-05", D("u_ravi_sec","SA-2026-05").allowed)
check("erin denied SA-2026-05 by need_to_know", D("u_erin_secmgr","SA-2026-05").rule == "need_to_know")
check("both restricted clearance",
      people["u_ravi_sec"].clearance == "restricted" and people["u_erin_secmgr"].clearance == "restricted")
check("both in security group",
      "security" in people["u_ravi_sec"].groups and "security" in people["u_erin_secmgr"].groups)

print("\n== check 6: external ==")
check("dana denied CT-KST-003 by external_restriction",
      D("u_dana_ext","CT-KST-003").rule == "external_restriction")
check("dana is confidential + sales group",
      people["u_dana_ext"].clearance == "confidential" and "sales" in people["u_dana_ext"].groups)
check("dana reads runbooks", D("u_dana_ext","RB-101").allowed)

print("\n== check 7 / default deny ==")
check("lena denied RB-101 by default_deny", D("u_lena_t1","RB-101").rule == "default_deny")
check("sofia denied PM-2026-03-14 by default_deny",
      D("u_sofia_am","PM-2026-03-14").rule == "default_deny")
check("marco denied CT-VTX-001 by default_deny",
      D("u_marco_t3","CT-VTX-001").rule == "default_deny")
check("sofia ALLOW CT-VTX-001", D("u_sofia_am","CT-VTX-001").allowed)

print("\n== obligations ==")
check("tom TK-4488 -> redact_pii", "redact_pii" in D("u_tom_contractor","TK-4488").obligations)
check("jin TK-4488 -> no redaction", "redact_pii" not in D("u_jin_us_t3","TK-4488").obligations)
check("marco PM-2025-11-03 -> audit_access",
      "audit_access" in D("u_marco_t3","PM-2025-11-03").obligations)
check("sofia CT-VTX-001 -> audit_access",
      "audit_access" in D("u_sofia_am","CT-VTX-001").obligations)

print("\n== PM-2026-03-14 walkthrough table ==")
for u, expect in [("u_marco_t3","ALLOW"),("u_lena_t1","clearance"),
                  ("u_sofia_am","default_deny"),("u_jin_us_t3","data_residency"),
                  ("u_ravi_sec","data_residency"),("u_dana_ext","data_residency"),
                  ("u_attacker_other_tenant","tenant_isolation")]:
    dec = D(u,"PM-2026-03-14")
    got = "ALLOW" if dec.allowed else dec.rule
    check(f"{u} -> {expect}", got == expect)

print("\n== sensitivity ladder ==")
from enterprise_rag.models import SENSITIVITY_RANK
check("ladder 0..3 public<internal<confidential<restricted",
      SENSITIVITY_RANK == {"public":0,"internal":1,"confidential":2,"restricted":3})

print("\n" + "=" * 60)
print(f"{'ALL CLAIMS VERIFIED' if not fails else str(len(fails)) + ' CLAIMS FAILED'}")
for f in fails:
    print("  -", f)

sys.exit(1 if fails else 0)
