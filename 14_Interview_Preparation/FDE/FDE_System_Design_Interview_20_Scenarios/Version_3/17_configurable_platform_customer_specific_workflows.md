# Configurable Platform for Customer-Specific Workflows - Case Study Worksheet

## 1. Interview prompt
Design a GenAI FDE solution for a **Configurable Platform for Customer-Specific Workflows**: ten customers vary fields, approvals, branding, and integrations on one platform. The danger is fragmenting into ten forks.

## 2. Clarify the customer problem
- Which differences recur, and which are genuine one-offs?
- Who authors configuration: engineers, customer admins, or both?
- Must configurations survive core releases untouched?
- Where does custom code stop — core, sandbox, or adapters only?
- What is the time-to-configure target for a new customer?

## 3. Users and workflows
| User | Workflow | Current pain | AI assist opportunity | Human approval needed? |
|---|---|---|---|---|
| Customer administrator |  |  |  |  |
| FDE / delivery team |  |  |  |  |
| Core platform engineer |  |  |  |  |
| Support and release team |  |  |  |  |

## 4. Requirements
### Functional
-
-
-

### Non-functional
- Latency target:
- Availability target:
- Cost budget:
- Security/privacy constraints:
- Audit/compliance requirement:

## 5. Data and integration map
| Data source | Format | Owner | Freshness | Permission model | Risk |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## 6. Proposed architecture
Use one of the rendered diagrams as a base, then customize:
- Workflow runtime:
- Configuration registry:
- Schema validation:
- Adapter SDK:
- Sandbox and flags:
- Migration and rollback:

## 7. Evaluation plan
| Metric | Good threshold | Bad threshold | Test dataset | Owner |
|---|---:|---:|---|---|
| Fork count | 0 | Any irremovable fork | Repo analysis | Engineering lead |
| Handled by configuration | High and rising | Falling | Change-request tags | Platform eng |
| Time to launch customer | Falling | Rising | Release tracking | Delivery lead |
| Tenant incident rate | Isolated per tenant | Spreads across tenants | Incident system | Support and SRE |

## 8. Failure modes
- Approval graph loops infinitely
- Adapter contract changes downstream
- Upgrade breaks an old field mapping
- Untested feature-flag combination
- Custom code escapes the sandbox
- A validation rule exhausts resources

## 9. Rollout plan
1. Find the recurring pattern.
2. Encode it in shared primitives.
3. First customer admin configures it.
4. Pilot run through real support.
5. Baseline launch speed and defects.
6. Expand only if forks stay zero.

## 10. Weak vs strong answer
**Weak:** "I'd build a flexible system with configurable forms, approvals, and hooks."

**Strong:** "I'd keep one engine on one release train, express variation declaratively in immutable versioned configs validated before publish, deny arbitrary code by default, scope adapters and secrets per tenant, and measure success as variations shipped without a fork."

## 11. Candidate scorecard
| Area | 1 | 3 | 5 | Score |
|---|---|---|---|---|
| Problem framing | "Make it flexible" | Shared core named | Fork-free variation as outcome |  |
| Architecture | Engine plus settings | Registry and validator | Sandbox, flags, migration |  |
| Evaluation | "Customers happy" | Incidents tracked | Fork count, config share |  |
| Production thinking | Onboard all ten | Pilot one | Rollback, baselines, gates |  |
| Communication | Lists features | Mostly clear | Fragmentation risk first |  |
