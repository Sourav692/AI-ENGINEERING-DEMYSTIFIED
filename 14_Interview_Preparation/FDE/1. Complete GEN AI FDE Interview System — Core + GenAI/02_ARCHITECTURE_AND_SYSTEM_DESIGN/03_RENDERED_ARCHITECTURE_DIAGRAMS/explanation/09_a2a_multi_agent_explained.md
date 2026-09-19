# 09. Agent-to-Agent Multi-Agent Workflow
## What the diagram shows

This diagram shows a multi-agent system where a user request is handled by an orchestrator agent, broken into tasks, assigned to specialized agents such as research, data, and policy agents, stored in shared memory, reviewed by a reviewer agent, and turned into a final response.

The diagram represents coordinated specialization rather than one large general-purpose agent.

## How to explain it in an interview

A strong spoken explanation could be:

> I would use multi-agent design only when specialization adds value. The orchestrator decomposes the request and assigns work to agents with narrow responsibilities. The research agent gathers external or document evidence, the data agent performs structured analysis, and the policy agent checks constraints. Shared memory stores intermediate findings, but it must be scoped and validated. A reviewer agent checks consistency, evidence, and policy compliance before the final response.

## Key trade-offs

- **Specialization vs complexity:** Specialized agents improve quality for complex workflows but add coordination overhead.
- **Shared memory vs isolation:** Shared memory helps collaboration but can propagate incorrect or unsafe information.
- **Parallelism vs consistency:** Parallel agents reduce latency but may produce conflicting outputs.
- **Reviewer agent vs human review:** Automated review scales but may miss subtle business risks.

## Failure modes

- Orchestrator decomposes the task incorrectly.
- Agents duplicate work or contradict each other.
- Shared memory stores unverified assumptions as facts.
- Policy agent is ignored by the final answer generator.
- Reviewer agent approves unsupported claims.
- One agent's hallucination contaminates the whole workflow.
- No trace links final answer back to agent-level evidence.

## Security concerns

- Scope each agent’s tool access by role.
- Treat shared memory as untrusted until verified.
- Prevent agents from escalating privileges through delegation.
- Log agent decisions, tool calls, and memory writes.
- Add policy checks before final response.
- Avoid storing sensitive data in long-term memory unless explicitly allowed.

## What a weak candidate misses

A weak candidate says: “Use multiple agents to solve the task.” That answer does not explain why multiple agents are needed, how they coordinate, how memory is controlled, or how final output is verified.

## What a strong candidate says

A strong candidate justifies multi-agent design only for complex tasks. They define agent roles, tool permissions, memory scope, conflict resolution, reviewer checks, and traceability from final answer to intermediate evidence.

## Visual improvement suggestion

Represent this as a swimlane diagram:

- **Orchestration Lane:** User Request, Orchestrator, Task Queue
- **Specialist Agent Lane:** Research Agent, Data Agent, Policy Agent
- **Memory/Evidence Lane:** Shared Memory, Evidence Store, Conflict Flags
- **Review Lane:** Reviewer Agent, Final Response

Add conflict-resolution and verification arrows before final response.
