# Capability Status

This document describes the implementation status of the **Canonical
GenAI FDE Interview Lab**.

The purpose of this file is to clearly distinguish capabilities that are
fully implemented in the offline reference implementation from optional
integrations and advanced extension exercises.

The canonical lab is intentionally designed to be:

-   Runnable on a local machine
-   Deterministic for interview practice
-   Independent of paid cloud services
-   Suitable for architecture discussions and portfolio demonstrations
-   Production-aware without claiming enterprise certification

------------------------------------------------------------------------

# Status Definitions

  -----------------------------------------------------------------------
  Status                              Meaning
  ----------------------------------- -----------------------------------
  **Implemented**                     Fully included in the repository
                                      and available in the canonical
                                      offline workflow.

  **Implemented & Tested**            Included and covered by the
                                      automated offline test suite.

  **Optional Integration**            Supported through an adapter or
                                      extension point but requires
                                      additional dependencies,
                                      credentials, or provider-specific
                                      configuration.

  **Extension Exercise**              Intentionally left for candidates
                                      to design or implement as an
                                      advanced interview exercise.

  **Not Included**                    Outside the scope of the compact
                                      interview-preparation lab.
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# Capability Matrix

  ------------------------------------------------------------------------
  Capability                      Status                Notes
  ------------------------------- --------------------- ------------------
  FastAPI application             **Implemented &       Canonical REST API
                                  Tested**              for the interview
                                                        lab.

  Browser demonstration UI        **Implemented**       Lightweight static
                                                        interface for
                                                        demonstrations.

  Local document ingestion        **Implemented &       Demonstrates
                                  Tested**              ingestion and
                                                        indexing workflow.

  Document chunking               **Implemented &       Supports retrieval
                                  Tested**              preparation.

  Local lexical-vector retrieval  **Implemented &       Deterministic
                                  Tested**              offline retrieval
                                                        without requiring
                                                        neural-model
                                                        downloads.

  Cosine similarity search        **Implemented &       Used for local
                                  Tested**              retrieval ranking.

  In-memory vector store          **Implemented &       Suitable for
                                  Tested**              deterministic
                                                        local execution.

  Embedding cache                 **Implemented &       Demonstrates
                                  Tested**              reusable embedding
                                                        generation.

  Permission-aware retrieval      **Implemented &       Prevents
                                  Tested**              unauthorized
                                                        document
                                                        retrieval.

  Role-based access control       **Implemented &       Demonstrates
                                  Tested**              user-specific
                                                        document access.

  PII redaction                   **Implemented &       Removes supported
                                  Tested**              sensitive
                                                        information before
                                                        responses are
                                                        returned.

  Prompt registry                 **Implemented**       Versioned prompt
                                                        templates are
                                                        included.

  Prompt versioning               **Implemented**       Supports
                                                        controlled prompt
                                                        evolution.

  Retrieval pipeline              **Implemented &       Complete retrieval
                                  Tested**              flow from
                                                        ingestion through
                                                        response
                                                        generation.

  Guardrails                      **Implemented &       Demonstrates basic
                                  Tested**              response safety
                                                        controls.

  Provider fallback               **Implemented &       Handles controlled
                                  Tested**              provider failures
                                                        gracefully.

  Evaluation framework            **Implemented &       Offline evaluation
                                  Tested**              pipeline for
                                                        interview
                                                        practice.

  Permission-leakage evaluation   **Implemented &       Ensures restricted
                                  Tested**              content is not
                                                        exposed.

  Retrieval-quality evaluation    **Implemented &       Validates
                                  Tested**              retrieval
                                                        behaviour.

  Audit logging                   **Implemented**       Runtime audit
                                                        logging for
                                                        demonstration
                                                        purposes.

  Metrics abstraction             **Implemented**       Demonstrates
                                                        observability
                                                        concepts.

  Tracing abstraction             **Implemented**       Illustrates
                                                        request tracing
                                                        patterns.

  Docker support                  **Implemented**       Dockerfile
                                                        included.

  Docker Compose                  **Implemented**       Local development
                                                        environment
                                                        included.

  GitHub Actions CI               **Implemented**       Linting, security
                                                        scanning and
                                                        automated tests.
  ------------------------------------------------------------------------

------------------------------------------------------------------------

# Optional Integrations

  -------------------------------------------------------------------------
  Capability                      Status                Notes
  ------------------------------- --------------------- -------------------
  Sentence Transformer embeddings **Optional            Requires local
                                  Integration**         model installation.

  Vertex AI embeddings            **Optional            Requires Google
                                  Integration**         Cloud configuration
                                                        and credentials.

  External LLM provider           **Optional            Requires
                                  Integration**         provider-specific
                                                        API configuration.
  -------------------------------------------------------------------------

------------------------------------------------------------------------

# Advanced Extension Exercises

  Capability                                 Status
  ------------------------------------------ --------------------
  Managed vector database integration        Extension Exercise
  OAuth / OpenID Connect authentication      Extension Exercise
  Production identity provider integration   Extension Exercise
  Multi-tenant architecture                  Extension Exercise
  Production secrets management              Extension Exercise
  Kubernetes deployment                      Extension Exercise
  Prometheus & Grafana deployment            Extension Exercise
  OpenTelemetry backend integration          Extension Exercise
  Distributed tracing platform               Extension Exercise
  Rate limiting                              Extension Exercise
  Circuit breaker implementation             Extension Exercise
  Background task queue                      Extension Exercise
  Persistent production database             Extension Exercise

------------------------------------------------------------------------

# Intentionally Not Included

-   Enterprise production frontend
-   Managed cloud deployment
-   Commercial LLM subscriptions
-   Enterprise IAM integration
-   Production SRE tooling
-   Regulatory certification
-   SOC 2 / ISO 27001 compliance implementation
-   Enterprise disaster recovery platform
-   Multi-region deployment
-   High-availability production infrastructure

------------------------------------------------------------------------

# Validation Status

The canonical offline configuration has been validated successfully.

-   20 automated tests pass
-   API endpoint tests
-   Retrieval pipeline tests
-   Permission filtering tests
-   Permission-leakage tests
-   PII-redaction tests
-   Provider-failure tests
-   Vector-store tests
-   Ingestion tests

Run the complete test suite:

``` bash
pytest
```

Expected result:

``` text
20 passed
```

------------------------------------------------------------------------

# Scope of Validation

The automated test suite validates the canonical offline implementation
included in this repository.

The following are **not** automatically validated by the offline tests
and require separate configuration and verification:

-   External cloud providers
-   Managed vector databases
-   Commercial LLM APIs
-   Vertex AI services
-   Enterprise identity providers
-   Production deployment environments

------------------------------------------------------------------------

# Purpose

The Canonical GenAI FDE Interview Lab is designed to help candidates:

-   Explain production-oriented GenAI architectures
-   Demonstrate hands-on engineering skills
-   Practice permission-safe Retrieval-Augmented Generation (RAG)
-   Understand evaluation-driven development
-   Discuss observability, security, and failure handling
-   Build an interview-ready portfolio project

It is an educational, production-aware reference implementation intended
for interview preparation rather than direct enterprise deployment.


| Capability | Status | Evidence |
|---|---|---|
| Streamlit frontend | Implemented | `frontend/streamlit/app.py` |
| Backend API integration | Implemented and Tested | `frontend/streamlit/api_client.py` |
| Tenant/user context input | Implemented | Streamlit sidebar or input form |
| Retrieved evidence display | Implemented | Frontend evidence component |
| Next.js frontend | Optional Extension | Not required for the canonical offline configuration |