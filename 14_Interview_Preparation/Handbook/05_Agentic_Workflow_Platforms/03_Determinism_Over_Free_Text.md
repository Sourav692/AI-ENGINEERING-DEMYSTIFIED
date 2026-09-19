# Determinism Over Free Text

> **Level** 🟡 Building Production Systems · **Module** 05 · **Doc** 3 of 7 · **Time** ~30 min
> **Prerequisites:** [Canonical Events, Channels and Routing](02_Canonical_Events_And_Channels.md)
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise Agentic Workflow Automation Platform/docs/01-theory.md` §A.6, §B.3, §B.4; `docs/03-src-modules-reference.md` (`tools.py`, `workflows.py`, `models.py`); `README.md`
> **Lab:** `project/src/agent_platform/tools.py`, `workflows.py`

## Why this matters

This is the section the whole project is actually about. The signal being tested by the prompt is whether you **split deterministic control flow from probabilistic reasoning** — so a user without an engineering background can configure something dependable without writing or reading code. The model may choose *which value* goes into an argument. It never improvises *what happens next*.

## Five controls, all built and tested

| Control | What it prevents | Where |
|---|---|---|
| **Constrained tool schemas over free-text arguments** | A hallucinated or wrong-typed argument reaching a real system | `tools.py::validate_args()` — type-checked against a declared schema before execution |
| **Idempotency keys on side-effecting calls** | A retried step applying its side effect twice | `orchestrator.py` — doc 4 |
| **Max-step and max-cost budgets — halt and escalate, not loop** | A runaway run | `guardrails.py::authorize_step()` — the tighter of the workflow's own budget and the tenant policy's — doc 5 |
| **Confirmation gates on destructive actions, configurable per tenant and tool** | An irreversible action without authority | `guardrails.py` — role-gated approval; an explicit per-tenant allow-list for what autonomous status may skip — doc 5 |
| **Split deterministic control flow from probabilistic reasoning** | The model improvising the control flow at runtime | The orchestrator's step sequence is fixed, declarative data; only *which value* goes into an argument is templated from the event |

This document is the first and last of those five. The middle three get their own documents.

## The workflow is data, not code

```python
@dataclass
class Step:
    name: str
    tool: str                 # a name in the registry
    args_template: dict       # {"ticket_id": "{target_entity_id}", "amount_usd": "{payload.refund_amount}"}

@dataclass
class WorkflowSpec:
    workflow_id: str
    version: int
    status: WorkflowStatus    # DRAFT | TESTING | SHADOW | LIVE | AUTONOMOUS
    triggers: List[Trigger]
    steps: List[Step]
    max_steps: int
    max_cost_usd: float
```

A `WorkflowSpec` is a declarative document. The orchestrator does not *execute* it as code; it *walks* it — take the step at the current index, resolve its argument template from the event, validate, authorise, apply. The control flow is the list. Nobody, human or model, changes the list at runtime.

This is exactly the reviewable artefact a non-technical user needs. When someone types *"refund anyone under $50"*, the system should not wire that sentence into an execution engine and hope. It converts it into a structured spec — `trigger: refund request`, `condition: amount < $50`, `action: issue_refund` — and shows it back for confirmation *before anything runs*. You are approving a form, not trusting a black box. The project builds the spec directly in Python; the natural-language-to-spec compiler is the named gap (doc 7), and the point is that the data model already *is* what such a compiler would emit.

## The tool registry: typed, scoped, flagged

```python
@dataclass
class ToolDefinition:
    name: str
    schema: Dict[str, type]   # param -> type
    required: List[str]
    destructive: bool
    scopes: List[str]
```

Four tools in the registry — `draft_reply`, `issue_refund`, `close_ticket`, `tag_ticket` — two destructive, two not. Three properties do the work:

- **`schema` + `required`** — `validate_args(tool, args)` checks every required field is present and every field's type matches, and **denies before any execution is attempted**. Module 03's argument-validation check, implemented. A `type_mismatch` or missing argument is a negative-control test.
- **`destructive`** — declared once at registration; the guardrail asks "is this one of the tagged ones?", never "does this call look risky?"
- **`scopes`** — what the tool is permitted to touch; the beginning of a connector permission model.

## Templates, not a blank canvas

The five constraints the source names for the non-technical-user half of the problem, and where each stands:

| Constraint | In plain language | Built? |
|---|---|---|
| **Templates, not a blank canvas** | Nobody starts from zero — clone "Auto-refund small orders" and change the numbers | ❌ No template library yet; a `clone()` over pre-built specs is the low-effort fix |
| **Plain English compiles to a reviewable spec** | The sentence becomes a form you confirm; it never runs directly | 🟡 The spec *is* that form; the compiler is not built |
| **A test mode where nothing actually happens** | Shadow mode: it watches real traffic and decides what it *would* do, but every write is faked — a fire drill | ✅ `SHADOW` status blocks every destructive step unconditionally, even for an admin |
| **Run history in human words** | "Refunded 12, escalated 2, denied 1 for exceeding the cap" — not a JSON log | ❌ The trace is structured; a sentence-per-step summary is low effort on top of it |
| **Staged rollout, like a driving test with levels** | `draft → test → shadow → live → autonomous`, one stage at a time, and the author cannot grade their own test | ✅ `promote()` — doc 5 |

Two of the five are unbuilt, both low effort, both named. That is the coverage-map discipline at work.

## Versioning a live workflow

`WorkflowStore` keeps every published version per `workflow_id`. A `Run` pins to the `workflow_version` it started on, so editing a workflow mid-flight never changes the behaviour of runs already in progress. Routing uses `all_live()` — each workflow's current latest version for the tenant. What is *not* built is gradual migration between two live versions (a traffic split); the coverage map sizes it.

## The honest gap in the "agent runtime"

The loop shape — plan → select tool → call → observe → iterate, with a hard step cap — is real. The **planner is a fixed step list**, not an LLM choosing the next tool dynamically from the run's observed state. Swapping the list for a real planner is a moderate change that keeps the architecture: a reasoning loop with deterministic guardrails around it. It was left out so that every property could be tested deterministically. Say that plainly when asked; do not imply the demo proves an LLM planner is safe.

## In the code

| Concept | Where |
|---|---|
| Step and spec | `models.py` → `Step`, `WorkflowSpec`, `WorkflowStatus`, `STATUS_ORDER` |
| Tool definitions and validation | `tools.py` → `REGISTRY`, `get_tool`, `validate_args` |
| Version store | `workflows.py` → `WorkflowStore.publish`, `latest`, `get_version`, `all_live` |
| Args resolved from the event | `orchestrator.py` → `_continue` (template resolution) |
| Negative controls | `scripts/demo_guardrail_failure.py`; tests for `type_mismatch` / missing args |

## Interview lens

> *"The orchestrator walks a declarative step list; it never executes code the user wrote and never lets a model improvise the control flow. The model's only latitude is which value goes into a typed, schema-validated argument. That's what lets a non-technical user review a form instead of trusting a black box — and it's why shadow mode can be unconditional: there's a fixed list of steps to dry-run."*

## Checkpoint

- State the five determinism controls and where each lives.
- Why is a `WorkflowSpec` the right artefact for a non-technical user to review?
- What three properties of `ToolDefinition` do the safety work, and at what moment does each apply?
- Which two of the five non-technical-user constraints are unbuilt, and what would it take?
- What exactly is the "fixed step list" gap, and how would you describe it without overclaiming?

**Next →** [Durability and Idempotency](04_Durability_And_Idempotency.md)
