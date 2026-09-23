# G11 — Deep Research Agent: Cheat Sheet

[Main](G11_Deep_Research_Agent_Main.md) · [Deep Dive](G11_Deep_Research_Agent_Deep_Dive.md) · [Unchanged source](G11_Deep_Research_Agent.md)

## Ask first

What counts as a valid citation? Which documents are private? What is the partial-answer rule? Is $0.20/run hard? What do failed tools mean?

## Whiteboard path

`Auth → bounded LLM plan → parallel public-web + user-scoped document agents → typed evidence ledger → coverage check / capped replan → LLM synthesis → claim verification → egress sanitizer → cited answer + gaps`

Keep web and private-doc credentials separate. Append branch evidence; never last-write-wins a shared summary.

## Numbers and limits

40K runs/day ≈ 28/min; 3× peak ≈ 100/min. Roughly 120 concurrent at 70s, ~170 slots at 70% utilization. p95 <90s, first signal <3s, about $0.20/run. Hard hop, tool, time and budget caps.

## Fail safely

`EMPTY` ≠ `UNAVAILABLE`. If evidence is thin or a branch fails, state the gap. Strip image/markup fetches and unapproved links in the final answer. Private caches are user-scoped.

## Evaluate

Check claim-citation support, coverage, cross-user leaks, p95, first signal, cost, hops, routing and no-progress loops. Test poisoned pages and missing tools.

**60-second close:** “I use multiple agents only where parallel research and permission isolation help. A bounded planner delegates, a typed ledger merges findings, and a verifier plus egress filter turns them into a cited answer with explicit uncertainty.”
