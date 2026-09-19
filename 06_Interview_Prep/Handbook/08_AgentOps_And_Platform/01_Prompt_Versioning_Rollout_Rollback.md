# Prompt Versioning, Rollout and Rollback

> **Level** 🟠 Scale, Security, Operations · **Module** 08 · **Doc** 1 of 6 · **Time** ~20 min
> **Prerequisites:** Module 04 doc 7 (the release gate), Module 05 doc 5 (staged rollout), Module 06 doc 3 (nightly runs, A/B)
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/10-agent-ops-and-channels.md` §1

## Why this matters

The "after it works once" question: how do you change a prompt safely? Most teams ship a prompt change the way they would ship a quick config tweak — edit it, deploy it, hope. But a prompt change is a behaviour change to a system that may move money or answer contractual questions. This document is the discipline that treats it as what it is: a versioned, gated, staged deployment with an instant rollback. The next document names the real tools that implement each step.

## Prompts as versioned, deployable artefacts

Every prompt — and the surrounding configuration: tool definitions, safety rules — is a **versioned, deployable artefact**, never a mutable string silently overwritten in source. Module 04's `PROMPT_VERSION` stamped on every trace is the smallest version of this; the full version gives each prompt an immutable identity, a history, and a pointer that says which one is live.

Why it matters: when answer quality shifts, the first question is "did the prompt change?" With versioned artefacts that question has an answer. Without them, it has an archaeology project.

## The gate before promotion

A new version reuses the same evaluation bar a full release would have to pass — Module 04's harness, unchanged:

- **A safety/security gate that must hit zero.** No acceptable rate of leaked information, no acceptable rate of unsafe output. A hard block, not a review comment — for the same reason a security incident is never averaged into a quality score.
- **A quality gate.** Accuracy and groundedness must not regress past a threshold versus the *current live version*, measured on the same fixed test set.
- **A version that fails either gate never reaches even a small slice of real traffic**, let alone full rollout.

The comparison is against a named baseline — the version currently serving — not an ad-hoc rerun, so "did this regress?" is a tracked comparison rather than two numbers eyeballed.

## Staged rollout

Module 05's four gates, applied to a prompt version rather than a workflow:

| Stage | What happens | Risk to a real user |
|---|---|---|
| **Shadow** | The new version runs alongside the live one on real traffic; both outputs are logged; compared offline | Zero — nobody sees the new output |
| **Small-scale release** | A small percentage of traffic, or a small set of low-risk customers, actually sees the new version; the same metrics are watched *live*, not only at the initial gate | Bounded to the slice |
| **Promote or roll back** | Based on the live metrics | — |

**Rollback must be instant and cheap:** switch which version handles new requests — not a full redeploy. The version that was live five minutes ago is still sitting there, ready to take traffic immediately. If rollback requires a build, it is not a rollback; it is a hot-fix under pressure.

## A/B testing, with the safety gate held constant

Two versions serve concurrently, split by something **stable per user** — not randomly per request — so one person's experience does not flicker between versions mid-conversation. Compare on real outcome metrics: did the answer resolve the issue, did it need escalation, was it rated up — not only an internal quality score. And the safety gate is **identical (zero) across both versions**. You are never testing a difference in leak rate; both arms must already be at zero to be in the test at all.

Module 06 doc 3 covers the statistical side: decide the effect size that matters, test on enough examples, do not call it early.

## The whole loop

```
  edit prompt
      │
      ▼
  new version (immutable, hashed)
      │
      ▼
  prompt unit tests ──fail──▶ fix
      │ pass
      ▼
  golden-set eval vs named baseline
      │  security gate = 0 ?  quality no-regression ?
      │──fail──▶ never reaches traffic
      │ pass
      ▼
  SHADOW  (log both, compare offline)
      │
      ▼
  CANARY  (small slice, watch live)
      │
      ├──regress──▶ ROLLBACK = repoint the live pointer (instant)
      │
      ▼
  PROMOTE  (repoint the live pointer)
      │
      ▼
  nightly eval keeps running against the live version   ← catches provider drift
```

## Interview lens

> *"The same evaluation gate that would block a full release also has to gate a new prompt version before it can reach a small slice of traffic — the safety bar doesn't get softer because it's framed as an A/B test. Shadow first, then a canary slice watched live, then promote — and rollback is a pointer flip to a version that never went away, not a redeploy."*

## Checkpoint

- Why is a prompt change a deployment rather than a config tweak?
- What two gates must a version pass, and what is the comparison baseline?
- Distinguish shadow from canary by the risk each exposes a real user to.
- What property must rollback have, and what disqualifies a mechanism from being called rollback?
- Why is an A/B split done per user rather than per request, and what must be identical across arms?

**Next →** [AgentOps on Databricks](02_AgentOps_On_Databricks.md)
