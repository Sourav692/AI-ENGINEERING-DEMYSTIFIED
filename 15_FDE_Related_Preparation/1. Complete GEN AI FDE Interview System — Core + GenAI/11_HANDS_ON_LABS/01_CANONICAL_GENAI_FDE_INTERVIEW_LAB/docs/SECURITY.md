# Security

## Authentication assumptions

The lab uses fake users for local testing. Production systems should integrate with OIDC/SAML through providers such as Google Cloud Identity, Okta, Azure AD, or Auth0.

## Authorization model

Each document chunk has `allowed_roles`. The retriever filters chunks before answer generation. This prevents unauthorized context from entering the model prompt.

## Permission-aware retrieval

The important rule is:

> Do not retrieve first and filter later in the prompt. Filter before context assembly.

Tests in `tests/test_auth_permissions.py` and `backend/evals/test_permission_leakage.py` prove that a sales user cannot retrieve restricted security-policy content.

## PII redaction

The lab redacts common patterns:

- Emails
- Phone numbers
- Customer IDs
- Account numbers
- Simple personal-name patterns

Production systems should use stronger PII services, domain-specific detectors, and human review for high-risk workflows.

## Prompt injection risks

Prompt injection can appear in documents, tickets, emails, Slack messages, or customer-provided text. Defenses include:

- Treat retrieved documents as untrusted input.
- Keep system instructions separate from context.
- Refuse instructions inside retrieved content that attempt to override policy.
- Use allowlisted tools.
- Log suspicious attempts without storing sensitive raw text.

## Data leakage risks

Primary leakage paths:

- Retrieval returns documents from the wrong tenant.
- Prompt includes restricted context.
- Logs store raw sensitive content.
- Evaluation datasets contain production customer data.
- Frontend displays hidden debug traces to unauthorized users.

## Secure logging rules

Log:

- Request ID
- User ID or stable pseudonymous ID
- Role
- Intent
- Source IDs
- Latency
- Safety flags

Never log:

- Raw prompts containing secrets
- Full retrieved context
- Access tokens
- API keys
- Private keys
- Unredacted PII
- Full customer conversations unless explicitly approved and protected

## Secrets management

The `.env.example` file is only for local development. Use managed secret storage in production.

## Compliance considerations

For finance, healthcare, and legal deployments, add:

- Data retention policies
- Audit log integrity
- Access reviews
- Human approval workflows
- Regional data residency controls
- Incident notification procedures
