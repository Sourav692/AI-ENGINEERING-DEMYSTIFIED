# Final GenAI FDE Readiness Assessment

## How to use this exam
Timebox yourself to 120 minutes. Score honestly. Passing threshold: **80/100**. Strong premium-readiness threshold: **90/100**.

## Section A - Customer Discovery and Decomposition (20 points)
### Prompt
A global enterprise wants an internal AI assistant for support, sales, and compliance teams. They say: “We want ChatGPT over all company knowledge.”

Answer:
1. What clarification questions do you ask?  
2. How do you identify the first workflow?  
3. What metrics define success?  
4. What risks must be constrained before pilot?  

## Section B - Architecture Design (25 points)
Design the production architecture. Your answer must include:
- auth and tenant context
- ingestion and freshness
- permission-aware retrieval
- model/LLM gateway
- tool-use boundary
- human approval
- observability
- evaluation and launch gate

## Section C - Evaluation and Red Teaming (20 points)
Create an eval plan with:
- 20 golden Q&A examples
- 10 red-team cases
- citation accuracy metric
- permission leakage metric
- regression testing approach
- launch threshold

## Section D - Production Debugging (15 points)
Incident: after a prompt update, users report confident wrong answers with citations. Explain:
1. First mitigation
2. Trace data to inspect
3. Root-cause possibilities
4. Regression test to add
5. Customer communication

## Section E - Coding/System Implementation (10 points)
Sketch pseudocode for permission-aware retrieval. It must filter by tenant and role before context reaches the model.

## Section F - Executive Communication (10 points)
Explain the solution to a non-technical VP in 90 seconds. Include value, risk controls, rollout, and success metrics.

# Scoring Rubric
| Area | Points | 5-star answer signal |
|---|---:|---|
| Discovery | 20 | Workflow, users, ROI, risk, success metrics |
| Architecture | 25 | Secure, observable, scalable, practical |
| Evals/red-team | 20 | Golden set, regression, abuse cases, thresholds |
| Debugging | 15 | Trace-based, mitigates first, adds tests |
| Coding | 10 | Permission filtering before generation |
| Communication | 10 | Clear, executive-ready, not jargon-heavy |

# Pass/Fail Guidance
- **<70:** Not ready. Too much theory or missing production controls.
- **70-79:** Basic readiness. Needs more structured practice.
- **80-89:** Interview-ready for many roles.
- **90-100:** Strong FDE/GenAI candidate signal.
