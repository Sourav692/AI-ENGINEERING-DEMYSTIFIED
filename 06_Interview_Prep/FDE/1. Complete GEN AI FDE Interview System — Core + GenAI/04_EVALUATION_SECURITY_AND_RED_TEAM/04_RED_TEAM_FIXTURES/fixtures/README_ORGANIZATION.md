# Fixture Organization Manifest

Generated: 2026-07-08T11:18:50

This package reorganizes the 25 red-team fixtures from `fixtures.zip` into the folder layout provided by `fixtures-1.zip`.

## Folder mapping

### expected_safe_outputs (0 files)
- No original attack fixtures mapped here. This folder contains derived expected-safe-output files where applicable.

### malicious_csv_spreadsheets (1 files)
- `00_poisoned_csv.json` — Poisoned CSV cell

### malicious_docs (7 files)
- `00_prompt_injection_retrieved_doc.json` — Prompt injection inside retrieved policy document
- `01_hidden_pdf_instruction.json` — Hidden PDF instruction
- `02_misleading_citation.json` — Misleading citation attack
- `03_malicious_url_summary.json` — Malicious web page summary
- `04_long_context_distraction.json` — Long-context distraction
- `05_citation_forgery.json` — Citation forgery
- `06_data_poisoning.json` — Data poisoning

### malicious_emails (2 files)
- `00_indirect_email_injection.json` — Indirect prompt injection from email
- `01_social_engineering.json` — Social engineering

### malicious_support_tickets (4 files)
- `00_jailbreak_support_bot.json` — Jailbreak attempt
- `01_pii_extraction.json` — PII extraction attempt
- `02_policy_conflict.json` — Policy conflict injection
- `03_multi_turn_leak.json` — Multi-turn gradual leakage

### tool_call_abuse_prompts (11 files)
- `00_malicious_tool_request.json` — Malicious tool-call request
- `01_cross_tenant_leakage.json` — Cross-tenant leakage attempt
- `02_role_escalation.json` — Role escalation attempt
- `03_sql_injection_nl_sql.json` — Natural-language SQL injection
- `04_unsafe_writeback.json` — Unsafe write-back action
- `05_approval_bypass.json` — Approval bypass
- `06_secret_exfiltration.json` — Secret exfiltration
- `07_tool_schema_abuse.json` — Tool schema abuse
- `08_tenant_id_tampering.json` — Tenant ID tampering
- `09_memory_poisoning.json` — Memory poisoning
- `10_agent_loop_hijack.json` — Agent loop hijack
