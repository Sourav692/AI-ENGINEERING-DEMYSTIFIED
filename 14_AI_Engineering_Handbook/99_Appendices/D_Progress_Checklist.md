# Appendix D · Progress Checklist

Tick a box only when you can pass the module's checkpoint **without looking**. The checkpoints are in each module's `README.md`; the questions are the ones an interviewer or a senior colleague would ask.

## 🟢 Level 1 — Foundations

- [ ] **00 · Orientation** — I can name the four levels, the three lenses, and the five question areas of the first ten minutes.
- [ ] **01 · LLM Systems Foundations** — I can draw the RAG query pipeline with its two security positions; explain hybrid search and RRF; write the ReAct loop with its guard and pause exit; say what `add_messages` does.
  - [ ] Lab: `project/` tests pass; I have run the from-scratch and LangGraph notebooks.
- [ ] **02 · System Design Fundamentals** — I can walk the 12 parts naming each component's cost; explain a circuit breaker's three states; spot the five travel-agent mistakes; write the six-step time budget.

## 🟡 Level 2 — Building Production Systems

- [ ] **03 · Robust Agents** — I can write `execute_tool` and defend its order; explain why a fallback goes through the same gate; name the three scopes of state; list the eight guard checks.
- [ ] **04 · Enterprise RAG** — I can explain the two failures of post-filtering; draw the seven ABAC checks and name the four things that cannot be pushed into the index; draw the eight-node graph; say why security is a gate and tell the false-alarm story; point at the code for any ✅ row.
  - [ ] Lab: index built; visibility matrix produced; `evaluate.py --kinds security` passes with zero leaks; I have worked through all eleven notebook parts.
- [ ] **05 · Agentic Workflow Platforms** — I can restate the problem in one breath; draw the orchestrator loop and explain why run and resume share it; say why the idempotency key is on the action and what "every side effect" includes; list the five guardrail rules; name the four rollout gates and who may promote.
  - [ ] Lab: happy path and negative-control demos run; tests pass.

## 🟠 Level 3 — Scale, Security, Operations

- [ ] **06 · Cross-Cutting Concerns** — I can explain what sits in front of authorisation; distinguish breaker, bulkhead, backup provider and kill switch; state the semantic-cache risk; give the three injection fixes and the egress list; say what is free at 20M documents.
- [ ] **07 · Multi-Agent Systems** — I can define multi-agent and say why Module 04's graph is not one; name the two triggers and describe them firing; write the handoff package; walk the nine layers of the research platform.
- [ ] **08 · AgentOps and Platform** — I can describe the prompt-change pipeline end to end; map each AgentOps concept to its Databricks mechanism; state the two Vector Search facts and draw the two-object design; list the five obligations of escalation; name the six architectural and four adversarial attacks.
  - [ ] Lab (optional, needs a workspace): the Databricks notebook runs end to end.

## 🔴 Level 4 — Design Mastery and the FDE Role

- [ ] **09 · AI System Design Casebook** — For each of the five prompts I can state the framing sentence and the hardest part; I can walk the agentic spine and raise the four gaps unprompted.
  - [ ] I have delivered at least one whiteboard script from the method alone, timed.
- [ ] **10 · FDE Delivery and Operating Model** — I can deliver the day-in-the-life closing line; walk a delivery story through six stages with numbers; draw the gate/stage state machine with signing roles; explain why a real gate can still be a rubber stamp; give a RACI and a tiered cadence.
  - [ ] Lab: engagement demo and negative-control demo run; tests pass.
- [ ] **11 · Telling the Story** — For a project of my own: I have written the cold-open sentence, five beats, the trust story, the honest limitation and a follow-up crib sheet; I have a coverage map with "what to say" for every gap; I can deliver a 15-minute deep-dive from headers alone.

## The handbook is finished when

- [ ] Every box above is ticked.
- [ ] I have run every lab that runs without a workspace.
- [ ] I have a coverage map, a "read these numbers honestly" paragraph, and a "what it does not do" list for at least one system I built myself.
