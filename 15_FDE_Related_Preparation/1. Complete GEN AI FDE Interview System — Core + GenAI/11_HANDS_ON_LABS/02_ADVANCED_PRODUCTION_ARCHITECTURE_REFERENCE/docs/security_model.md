# Security Model

Every request carries user_id, tenant_id, roles, permission_scopes, request_id, and trace_id. Retrieval must filter before LLM context assembly.
