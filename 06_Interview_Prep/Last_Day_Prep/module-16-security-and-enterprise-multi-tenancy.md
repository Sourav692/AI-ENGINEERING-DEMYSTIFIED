# Module 16 — Security & Enterprise Multi-Tenancy

## CONCISE INTERVIEW MODULE

### 1. What the Interviewer Is Testing

- Can you enforce user and tenant boundaries across data, tools, and actions?
- Can you separate authentication, authorization, and business policy?
- Can you protect secrets and sensitive data throughout the request path?
- Can you identify deployment constraints such as approved providers and residency?

### 2. Core Mental Model

```text
Authenticate identity → Resolve trusted tenant/scope
                                  ↓
               Authorize data and tool operations
                                  ↓
                 Policy → Approval if required
                                  ↓
                      Execute → Audit
```

**Security checks apply at each relevant boundary. A model prompt is not an access-control system.**

### 3. Essential Concepts

#### 1. Authentication — Establish Identity

Verify who or what is calling, including users, services, and workers. Derive trusted tenant context from verified identity or controlled membership, not model-generated fields.

> “I’d establish user and tenant identity before retrieval or tool execution.”

```text
Verified identity → Trusted tenant membership → Request context
```

#### 2. Authorization and RBAC — Decide Permitted Operations

Authorization asks what that identity may do. Role-based access control (RBAC) assigns permissions through roles; resource ownership and tenant scope may require additional checks.

> “An authenticated support user is not automatically authorized to read every account or issue every refund.”

```text
Identity + role + resource + operation + tenant → Allow / deny
```

Check resource-level access, not only whether a tool name is permitted.

#### 3. Permission-Aware RAG — Keep Restricted Evidence Out

Retrieval-augmented generation (RAG) must enforce current access before restricted content enters model context. Preserve source permissions through ingestion and query execution.

```text
Employee identity → Allowed document scope
                          ↓
                Authorized retrieval → Context
```

> “Employee B's prompt should never receive HR evidence that only Employee A may access.”

Update permissions, deletions, and cache scope; filtering the final answer is too late to prevent unauthorized context exposure.

#### 4. Least-Privilege Tools — Limit Enterprise Reach

Expose only necessary operations and use scoped credentials outside model context. Separate reads from writes and enforce access again at execution.

> “A refund task needs permitted order/payment operations, not unrestricted CRM or database administration.”

```text
Model proposes → Validate inputs → Authorize resource/action
                                     ↓
                              Controlled executor
```

Agent recommends → Policy decides → Executor acts. Human approval, where required, does not grant unrelated access.

#### 5. Tenant Isolation — Cover More Than the Database

Scope documents/indexes, caches, state, queues, tool credentials, logs, audit records, and results. Choose shared or separated resources according to required isolation and operational trade-offs.

> “I’d trace tenant context end to end, including cache keys and background workers.”

```text
Tenant scope → Data / cache / state / jobs / tools / output
```

Data isolation and resource fairness are separate needs. A tenant can harm others' latency without accessing their data.

#### 6. Secrets — Keep Credentials in Trusted Execution

Manage credentials through controlled secret storage and scoped runtime access. Do not embed them in prompts, retrieved documents, tool descriptions, or unrestricted telemetry.

> “The tool service uses the credential; the model only requests the approved operation.”

Define rotation and access ownership appropriate to the integration.

#### 7. Sensitive Data — Minimize Across the Whole Lifecycle

Confirm what data is necessary, which providers may process it, and retention/access requirements for prompts, outputs, caches, logs, and backups. Mask or redact where it preserves required functionality.

```text
Collect necessary data → Approved processing
                              ↓
                    Controlled storage / retention
```

> “I’d inspect every copy of sensitive data, not only the primary database.”

#### 8. Data Residency — Follow Data Through Dependencies

Confirm the exact regional boundary and processing/storage restrictions with the customer. Include models, retrieval, tools, telemetry, backups, failover, and support access where relevant.

> “If data must stay in-region, fallback and logging must respect that restriction too.”

```text
Regional application → Approved regional data/model paths
                                  ↓
                         Compatible failover only
```

Do not infer a universal legal requirement from geography; translate the stated customer constraint into architecture.

#### 9. Defense in Depth — Do Not Let Text Grant Authority

Treat user text, retrieved documents, and tool outputs as untrusted input. Use validation, permissions, policy, and execution controls outside model discretion.

> “A document telling the agent to expose secrets cannot change the user's authorization.”

```text
Input checks + scoped retrieval + tool authorization
             + policy + audit + execution controls
```

Test denied-access, cross-tenant, credential-exposure, and instruction-bypass cases alongside normal workflows.

### 4. Requirement → Component Reasoning

| Requirement | Pattern / component | Why | Trade-off |
|---|---|---|---|
| Verified user/tenant context | Authentication + membership resolution | Trusted identity boundary | Identity integration |
| Enforce resource access | Authorization/RBAC + resource checks | Limit permitted operations | Permission-model maintenance |
| Restricted document access | Permission-aware retrieval | Keep unauthorized context out | Source ACL integration |
| Scoped enterprise writes | Controlled tools + policy/executor | Limit actions and authority | Integration and approval overhead |
| Prevent cross-tenant leaks | Scoped storage, caches, jobs, logs/results | Preserve boundaries across copies | Isolation complexity |
| Protect credentials | Trusted secret management | Keep secrets outside model context | Rotation and runtime access |
| In-region processing | Approved regional dependencies/failover | Respect customer data boundary | Provider and availability options |

```text
API Gateway   = User → Application control
Model Gateway = Application → Model control
```

Application-entry checks establish identity and tenant context. Model-call controls select permitted providers. Retrieval, state access, and enterprise tools still enforce their own resource boundaries.

**Support example:** authenticate the customer, resolve tenant/account scope, retrieve only allowed policy content, read only their permitted orders, and execute a policy-approved refund through scoped credentials. Keep the same scope in caches, async jobs, and audit records.

### 5. Important Distinctions and Gotchas

1. **Authentication vs authorization:** established identity vs permitted resource and operation.
2. **Authorization vs policy:** allowed to request an action vs action meets business rules; both can be required.
3. **Pre-context access vs final-output filtering:** keeping restricted evidence out is stronger than asking the model not to reveal it.
4. **Tenant isolation vs fairness:** preventing data leaks vs preventing capacity monopolization.
5. **Regional hosting vs end-to-end residency:** remote models, logs, backups, or fallback can cross the boundary.

### 6. Trigger → Concept Table

| Hear… | Think… | Inspect… |
|---|---|---|
| “HR access differs by employee” | Resource authorization | Retrieval permissions and updates |
| “Model hides restricted content” | Weak boundary | Access before context construction |
| “Refund agent needs credentials” | Least privilege/secrets | Scoped executor, no prompt secrets |
| “Fifty enterprise tenants” | End-to-end isolation | Cache, state, jobs, logs, outputs |
| “One tenant hurts others” | Fairness | Limits and scheduling |
| “Data cannot leave region” | Residency | Model, telemetry, backup, failover |
| “Tool output says bypass rules” | Untrusted instructions | No authority from external text |

### 7. Interview Phrases

> “Authentication establishes identity; authorization decides access to this resource and operation.”

> “I’d enforce document access before evidence enters model context.”

> “Tenant isolation must include caches, jobs, state, logs, and results, not just database rows.”

> “I’d trace residency through models and failover as well as the application host.”

### 8. Practice Questions

1. Employee A can read HR documents and B cannot. How do ingestion, retrieval, caches, and permission updates preserve this?
2. Why is final-answer filtering insufficient after unauthorized documents enter context?
3. What operations, credentials, and resource checks should a refund executor receive?
4. A shared platform serves fifty tenants. Which data and execution surfaces need isolation, and which need fairness?
5. A customer requires all processing in one region. How do model fallback, logging, backups, and tool dependencies affect the design?

---

## ONE-PAGE MEMORY CARD — Security & Enterprise Multi-Tenancy

**Core question:** Who may access which data and operations, and how do those boundaries survive every stage of the task?

### Recall Flow

```text
IDENTITY → TRUSTED TENANT → AUTHORIZATION
                               ↓
           DATA / TOOL PERMISSIONS → POLICY
                               ↓
                 APPROVAL → EXECUTE → AUDIT
```

Agent recommends → Policy decides → Executor acts.

### Checklist

| Concept | Remember |
|---|---|
| Authentication | Verify user/service identity; establish trusted tenant membership |
| Authorization | Check role, resource, operation, ownership, tenant |
| RBAC | Role-based access control; resource-level scope may need extra checks |
| RAG permissions | Enforce before model context; update source access/deletion changes |
| Least privilege | Specific necessary read/write operations, scoped credentials |
| Tenant isolation | Documents, indexes, cache, state, queues, tools, logs, audit/results |
| Secrets | Trusted runtime storage/use; never unrestricted prompt or telemetry content |
| Sensitive data | Necessary collection, approved providers, retention/access for every copy |
| Residency | Application, models, retrieval, tools, logs, backups, failover |
| Defense in depth | Validation + authorization + policy + execution controls + audit |

### Trigger → Concept

| Hear… | Think… |
|---|---|
| “Different employee access” | Resource authorization and scoped retrieval |
| “Filter secrets after answer” | Unauthorized context already exposed |
| “Agent needs production access” | Specific tools and least privilege |
| “Shared tenants” | Scope every data/execution surface |
| “Noisy neighbor” | Resource fairness, separate from data isolation |
| “Stay in-region” | End-to-end dependency and fallback boundary |
| “Document says ignore policy” | External text is data, not authority |

### Do Not Confuse

1. **Authentication vs authorization:** who you are vs what you may access or do.
2. **Authorization vs business policy:** resource permission vs whether this action meets the rule.
3. **Isolation vs fairness:** no cross-tenant data exposure vs no shared-capacity monopolization.
4. **Regional app vs residency:** external model, logging, backup, or failover can still cross the boundary.

### Enforcement Rules

Derive tenant scope from trusted identity, not caller/model claims alone. Authorize the specific resource and operation. Do not retrieve restricted evidence and rely on a prompt to hide it. Keep permissions and cache scope current when access changes.

Use scoped tool credentials outside model context. Approval must refer to the action, and execution still rechecks access and business policy. Carry trusted scope through background workers and result retrieval. Review logs, audit, backups, and caches as additional sensitive-data copies.

API Gateway = User → Application control.
Model Gateway = Application → Model control.
Neither replaces resource checks in retrieval or enterprise tools. Provider selection and fallback must respect the customer's data restrictions.

### 30-Second Answer

> “I’d establish verified identity and tenant scope, then enforce resource-level access in retrieval, state, and tools. The agent would receive only necessary operations, while credentials remain in trusted execution. I’d isolate tenant data across caches, jobs, logs, and results, check business policy and approval for writes, and trace sensitive data and residency through providers, telemetry, backups, and failover.”
