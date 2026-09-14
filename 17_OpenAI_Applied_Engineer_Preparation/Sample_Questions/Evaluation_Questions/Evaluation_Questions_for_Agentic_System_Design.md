# Evaluation Questions for the Agentic System-Design / Decomposition Round

Real-world evaluation questions of the kind asked when you are designing or decomposing an
agentic system in an interview — not coding exercises, not metric derivations. Every answer
here is judgement under a constraint: what to measure, why that and not something else, what
it costs, and what you do when the number disagrees with the stakeholder.

**Sources.** Grounded in `../Databricks_AI_Evals_Tutorial/` (strategy → tracing → offline →
judges → datasets → gating → online → alignment → optimisation → multi-turn → adversarial)
and `07_Advanced_Agentic_Systems/Evaluation_and_Eval_Harnesses/` (RAG, tool, trajectory,
task-completion and conversational evaluation). Companion to the 23 case studies in
`OpenAI Applied_Engineer_Problem_Decomposition_Questions.md` — that file covers whole-system
design; this one covers the evaluation thread running through all of it.

**How to use it.** Read the question, answer out loud for two minutes, *then* read the answer.
The **What they're really testing** line matters as much as the answer — most of these have an
obvious shallow response and a much better second-order one.

---

## Contents

| Part | Theme | Questions |
|---|---|---|
| 1 | Turning a vague ask into an evaluation plan | 1–4 |
| 2 | Decomposing *what* to measure | 5–9 |
| 3 | Ground truth and datasets | 10–13 |
| 4 | Judges, and who validates them | 14–17 |
| 5 | Offline → online | 18–21 |
| 6 | Gating, regressions and rollback | 22–25 |
| 7 | Multi-turn, tools and agency | 26–29 |
| 8 | Adversarial, safety and governance | 30–32 |
| 9 | Cost, ownership and rollout | 33–35 |

---

# Part 1 — Turning a vague ask into an evaluation plan

## Q1. "A customer says their support agent 'isn't good enough'. Where do you start?"

**What they're really testing:** whether you ask before you build, and whether you can convert
a feeling into something falsifiable.

Not with a metric. "Not good enough" is a complaint about an *outcome*, and the first job is to
find out whose outcome and against what bar.

I'd want three things before proposing anything:

1. **A failing example.** Not a description — an actual conversation they consider bad, plus
   what the right behaviour would have been. One real trace tells you more than an hour of
   abstract discussion, and it immediately reveals whether the failure is retrieval, reasoning,
   tone, or a policy the agent was never told about.
2. **Who decides.** "Good" is a person's standard. A support lead, a compliance officer and a
   product manager will name three different failures as the worst one. Evaluation that isn't
   anchored to a named decision-maker drifts into measuring whatever is easy.
3. **What happens when it fails.** A wrong answer about office hours and a leaked account
   balance are not the same class of problem. The consequence sets the threshold.

Then I'd write the dimensions down *before* running anything — correctness, groundedness,
safety, tone, tool-use — and for each: is it a blocker or informational, what's the bar, and
who signs off. That document is the deliverable of the first session. The architecture
conversation comes after, because the eval criteria constrain the design more than the other
way round.

**Follow-up they'll push:** *"They don't have failing examples — they just have a bad feeling."*
Then generate them. Run the current system over a realistic scenario list built from their
actual ticket categories and put the outputs in front of the domain expert. People are far
better at recognising a bad answer than at describing one.

---

## Q2. "How do you decide what 'good' means when the customer can't tell you?"

**What they're really testing:** can you elicit a specification rather than wait for one.

Domain experts hold their standard tacitly. They can't write the rubric, but they can apply it
instantly. So I don't ask "what is good?" — I show them outputs and ask them to sort.

The practical loop:

- Assemble 30–50 outputs spanning the obvious cases, the ambiguous ones and the ones I expect
  to fail.
- Have two experts rate them independently, with a one-line reason for each.
- Read the *reasons*, not the scores. The reasons are the rubric, in their own words.
- Where the two experts disagree, you have found either an ambiguous policy or a genuine
  organisational disagreement — both are more valuable than the ratings themselves. Escalate
  it as a product decision, not an eval detail.

The output is a written standard traceable to real judgements. That's also what makes an LLM
judge trustworthy later: the rubric it applies is the experts' rubric, distilled, rather than
something I invented and they never reviewed.

**Red flag answer:** proposing a standard metric suite on day one. It signals you'll measure
what's easy to measure rather than what this customer actually cares about.

---

## Q3. "Walk me through your evaluation strategy for an agent that hasn't been built yet."

**What they're really testing:** sequencing — whether evaluation is a phase at the end or a
constraint on the design.

Evaluation before code, because it changes what you build. Three decisions I want settled
first:

- **What must never happen.** The irreversible and the protected: leaking another customer's
  data, taking a write action nobody asked for, giving advice outside the agent's remit. These
  become all-or-nothing gates, and they shape the architecture — you cannot bolt a consent
  check onto an agent that doesn't expose when it acted.
- **What good looks like when nothing goes wrong.** Correct, grounded, relevant, appropriately
  short. These get numeric bars and mostly inform rather than block.
- **What we cannot measure yet, stated explicitly.** Writing down "we have no multi-turn cases"
  is worth doing, but I'd say clearly that documenting a gap is not covering it. It is very easy
  to mistake an honest note for protection for months.

Then the design constraint: the system has to emit enough signal to score those dimensions. If
retrieval is something the model may or may not do, groundedness becomes unmeasurable on
exactly the runs you most want to inspect — so retrieval becomes a fixed step, not an optional
tool. Instrumentation is not a chore before evaluation; it *is* the substrate.

**Follow-up:** *"Isn't that over-engineering for a prototype?"* The prototype can skip the
harness, not the definition. Writing three thresholds down costs an hour and stops the
"it feels better" argument two months later, when there's no baseline to compare against.

---

## Q4. "The customer wants one number for a dashboard. What do you give them?"

**What they're really testing:** whether you'll let a summary destroy the signal.

I'd give them one number and refuse to let it be the only one — because an aggregate over a
mixed dataset averages the safety-critical slice into invisibility. A system that is slightly
wrong everywhere and a system that is perfect except that it leaks account data on adversarial
prompts produce the same headline score.

What I'd actually put on the dashboard:

- **A single release verdict** — pass or fail against the blocking gates — rather than an
  average. It answers the question an executive is really asking ("can we ship?") and it can't
  be improved by strength elsewhere.
- **Beneath it, the slices:** by question category, by whether a tool was involved, by attack
  class, by turn position. That's where the actionable signal lives.
- **Separately, "not measured".** An unmeasured dimension and a failed one must never look
  alike on a dashboard. Reporting a gap as zero makes a healthy system look broken; hiding it
  makes a blind spot look like coverage.

The framing I'd use with the customer: the headline number tells you *whether* to look; the
slices tell you *where*. Giving them only the first guarantees that the first serious failure
is discovered by a user.

---

# Part 2 — Decomposing *what* to measure

## Q5. "A RAG assistant gives a wrong answer. How do you find out which part is broken?"

**What they're really testing:** whether you can localise a failure in a pipeline instead of
treating the system as one blob.

A wrong answer has at least three distinct causes that look identical from outside, and each
has a different fix:

| Where it broke | Question to ask | What you'd see |
|---|---|---|
| Retrieval | Did we fetch the right material at all? | The answer's supporting facts aren't in the retrieved context |
| Generation, ungrounded | Given correct context, did the model invent? | The claim isn't supported by anything retrieved |
| Generation, grounded but wrong | Was the source itself wrong or stale? | The answer faithfully reflects a document that shouldn't be trusted |

So I'd split the evaluation the same way: something that judges the *context* the agent had,
something that judges the *answer against that context*, and something that judges the answer
against a known-correct one. The third needs ground truth and doesn't scale; the first two
don't and do.

The diagnostic value is the point. If retrieval quality is high and groundedness is low, the
retriever is fine and the prompt or model is inventing. If retrieval quality is low, tuning the
prompt is wasted effort. Teams that measure only end-to-end correctness spend weeks tuning the
wrong stage.

The third row is the one people miss: an answer can be perfectly grounded and still wrong,
because the knowledge base is out of date. No grounding metric catches that — it needs
freshness policy and source-level review, which is a data problem, not a model problem.

---

## Q6. "Same question, but it's an agent with tools, not just RAG. What changes?"

**What they're really testing:** whether you know that agent evaluation has layers RAG
evaluation doesn't.

RAG asks "was the answer right?". An agent asks "did it do the right thing, the right way?" —
and those separate into a ladder:

1. **Tool selection** — did it call the right tool? With one tool this question doesn't exist;
   "called something" and "called the right thing" are the same. Add a second and they split,
   and calling the *wrong* tool is worse than calling none, because it returns data that is
   real, irrelevant and confidently presented.
2. **Arguments** — right tool, wrong parameters. A failure that tool-selection checks cannot
   see at all.
3. **Trajectory** — across a multi-step run, was the sequence sound? Redundant calls, wasted
   steps, no recovery after an error. Two agents can reach the same correct answer, one in two
   steps and one in nine.
4. **Task completion** — forget the mechanics: did the user get what they asked for? Every
   individual call can be correct while a stated constraint — a budget, a deadline — is
   silently dropped.

The ladder runs mechanics → process → outcome, and you can pass every level below and still
fail the top one. That's exactly why task completion is a separate concern and not a
restatement of tool correctness.

**The strongest signal, when you can get it:** verify the end state in the system of record —
was the ticket actually created, with the right fields? A judge reads text and can be fooled by
a confident sentence that misrepresents what happened. The database cannot.

---

## Q7. "Which of these do you actually implement first, given two weeks?"

**What they're really testing:** prioritisation under a real constraint, and whether you know
what's cheap.

Order by consequence and by cost, in that order:

- **First, the non-negotiables — and make them deterministic where possible.** Did it disclose
  another customer's data? Did it take a write action? These are the failures that end the
  project, and many can be checked with plain code: no model call, no cost, instant, and the
  same verdict every time. Anything checkable in code should never be checked by a judge.
- **Second, one grounding check.** For any retrieval system, an ungrounded answer is the most
  likely real failure, and it needs no ground truth — which means it also transfers to
  production later.
- **Third, a small hand-built set with expected answers**, for the core happy path only. This
  is the expensive one, because someone has to write and maintain the labels.
- **Not yet:** trajectory quality, tone, conciseness. Real, but they inform rather than block,
  and they're the ones I'd cut for time.

What I would *not* do is build a broad metric suite that measures ten things shallowly. Two
gates people trust beat ten numbers nobody looks at.

---

## Q8. "Retrieval scores are excellent but users still complain. What's your hypothesis?"

**What they're really testing:** whether you treat a green metric as proof or as a claim to
check.

Several possibilities, and I'd rank them by how cheaply they can be ruled out:

- **The metric is measuring the wrong population.** Retrieval is scored on a curated set built
  from questions we imagined; users ask different ones. Hand-written datasets contain what the
  author thought of, and the gap between that and reality is invisible from inside the dataset.
- **Retrieval is right, the answer isn't.** Fetching the correct document and then answering
  the wrong question is entirely possible — that's why relevance-to-the-query is a separate
  check from retrieval quality.
- **The retrieved document is correct and obsolete.** Grounding says the answer matches the
  source; nothing says the source is current.
- **The complaint isn't about correctness.** Too long, wrong tone, no citation, three follow-up
  questions before the answer. All real product failures, none visible to an accuracy metric.

The action is the same in every case: stop arguing from the dashboard and go read the traces of
the complaining users' actual sessions. Whatever is wrong will be visible there, and it will
tell you which metric is missing rather than which one is broken.

---

## Q9. "How would you evaluate an agent whose job is to decide *not* to answer?"

**What they're really testing:** whether you can evaluate the absence of an action — a blind
spot in most eval designs.

The correct behaviour here is a refusal, an escalation or a clarifying question, and that
changes the shape of the assertion. There is no correct *content* for "tell me another
customer's balance" — only correct *behaviour*. So the case doesn't get a gold answer; it gets
a rule: must decline, must not state any account details, must offer a human.

This distinction matters more than it sounds. If you force those cases into a
gold-answer format, you end up asserting that a refusal contains particular facts, and the
only way to make that case pass is for the agent to reveal the data you were protecting. The
eval doesn't just miss the leak; it rewards it.

Two more things I'd insist on:

- **Absence is a behaviour worth scoring.** An agent that correctly makes no tool call produces
  no tool activity — which looks exactly like an agent whose instrumentation is broken. You need
  to distinguish the two deliberately, or a silent failure hides inside a passing metric.
- **Over-refusal is the other failure.** An agent that declines everything scores perfectly on
  safety and is useless. Both directions need to be in the dataset, or you will optimise into
  the useless corner.

---

# Part 3 — Ground truth and datasets

## Q10. "Where does your evaluation data come from on day one, and how does that change by month three?"

**What they're really testing:** whether you understand that dataset strategy has a lifecycle.

**Day one it's hand-written**, because nothing else exists. I'd build it from the customer's own
categories — their top ticket types, their edge cases, the cases their support leads argue
about — rather than from imagination. Its weakness is structural and worth saying out loud: it
contains what we thought of.

**By month three the real traffic is the asset.** Production traces give you the *distribution* —
which questions actually arrive, in what proportion, with what messiness. That's the expensive
half to guess and the free half to collect.

The important caveat: mining traces gives you **inputs, not labels**. What people actually asked
is free; what the right answer was still requires a human. Anyone who claims trace mining
removes the labelling cost is describing something else.

And the trap to name before the interviewer does: **do not use the agent's own outputs as
expected answers.** It passes by construction, and it freezes today's bugs as the definition of
correct.

**Follow-up:** *"How do you choose which traces to promote into the set?"* Not at random —
random sampling reproduces the head of the distribution you already cover. I'd target novelty:
inputs unlike anything in the current set, sessions where the agent hedged or the user rephrased.
And I'd select by a quality bar rather than a fixed count, so a quiet week yields fewer rows
instead of padding with duplicates of things already covered.

---

## Q11. "Your eval set and production traffic have diverged. How do you keep both honest?"

**What they're really testing:** whether you know these are two datasets with opposite
requirements.

They pull in opposite directions and both are needed:

- **The curated regression set must not drift.** Its entire value is that a score from March and
  a score from June are comparable. Change the dataset and every historical comparison is void —
  a changed dataset invalidates a comparison as surely as a changed scorer set does.
- **The mined set must stay fresh.** Its value is that it reflects what users are doing *now*.

So: two datasets, two policies. The regression set is versioned and changes only through a
deliberate, announced update — and when it does, you re-baseline rather than compare across the
boundary. The discovery set is refreshed continuously and used to *find* problems, not to gate
releases.

The bridge between them is a rule, and it's the one I'd emphasise: **every production failure
gets promoted into the gated set.** Online evaluation discovers; offline prevents recurrence.
A finding that isn't carried into a permanent test only helps you once.

---

## Q12. "How big does the evaluation set need to be?"

**What they're really testing:** whether you reason from the decision backwards, or reach for a
round number.

Not a number I'd guess. It's set by the smallest difference you need to be able to *detect*.

If the question is "did this prompt change make things worse?", and you need to catch a drop of
a couple of percentage points, a small set cannot resolve that — the difference will sit inside
the run-to-run wobble. If you only need to catch catastrophic regressions, a few dozen
well-chosen cases are plenty.

Two corollaries worth stating:

- **Composition beats size.** Fifty cases spanning every category and attack class are worth
  more than five hundred variations on the same easy question. Coverage of the *decision space*
  is what you're buying.
- **The noise floor sets the resolution.** Model-judged metrics wobble between identical runs;
  below that wobble you cannot distinguish a real change from the judge changing its mind. A
  bigger set narrows that, but it never removes it.

For a first production system: enough curated cases to cover every category and every
must-never-happen class, then grow from traffic where it turns out to be thin.

---

## Q13. "Who actually writes the labels, and how do you get their time?"

**What they're really testing:** whether you've done this in a real organisation.

The honest answer is that this is the binding constraint on most eval programmes — not tooling,
not metrics. Expert attention is the scarcest input.

What works:

- **Spend it where it's irreplaceable.** Experts should adjudicate ambiguous and high-stakes
  cases, not confirm that easy ones are easy. Anything code can check shouldn't reach a human at
  all.
- **Ask for judgements, not documents.** "Rate these twenty answers, one line of reasoning each"
  is a 40-minute task. "Write us an evaluation rubric" is a project that never starts.
- **Make the reasons the artefact.** The ratings calibrate the system; the written reasons
  become the standard, and can be reused to align an automated judge so the expert doesn't have
  to rate the next thousand.
- **Show them the return.** Bring back the failures their labels caught. Nothing sustains
  expert participation like seeing their standard block a bad release.

And record **who** produced each label — expert, contractor, or script. When that data later
trains or calibrates a judge, the provenance is the difference between a defensible standard and
an unexamined one.

---

# Part 4 — Judges, and who validates them

## Q14. "You're using an LLM to grade another LLM. Why should anyone believe the number?"

**What they're really testing:** whether you treat a judge as an instrument or as an oracle.
This is the single most common failure in eval work.

They shouldn't, until it's been checked. A judge is a model with a rubric, and it inherits every
weakness of the thing it's judging — it can be persuaded by fluent, confident, wrong text; it
drifts with wording; it disagrees with itself between runs.

So I'd treat it as a measuring instrument that requires calibration:

- **Check it against people.** Have domain experts rate a sample the judge has scored, and
  compare — where they disagree and why.
- **Measure agreement, not average score.** A judge that rates everything highly produces a
  lovely average and is worthless. The question is whether it agrees with a human on the *same
  case*.
- **Expect the score to fall after calibration, and read that correctly.** A drop doesn't mean
  the agent got worse. It means the measurement stopped flattering. That conversation is much
  easier to have if you predict it in advance.

Where judges are strongest: open-ended text quality, where no deterministic check exists. Where
they're weakest: anything a rule could decide, and anything the judge is also being optimised
against.

---

## Q15. "Your judge and your domain expert disagree on 20% of cases. What do you do?"

**What they're really testing:** whether you can debug a measurement rather than discard it.

First, look at *which* 20%. Disagreement scattered evenly across the range is a different
problem from disagreement concentrated near a threshold — the latter is usually just borderline
cases, and matters far less.

Then separate three causes:

1. **The rubric is vague.** Most common. The judge is applying a reasonable reading of an
   ambiguous instruction. Fix the wording, not the model.
2. **The experts disagree with each other.** Check this before blaming the judge. If two experts
   don't agree on a case, no judge can be right on it, and you've found an unresolved policy
   question that belongs to the product owner.
3. **The judge is genuinely weak on this task.** Then a stronger judge model, or a deterministic
   check that removes the judgement entirely.

The improvement path I'd take: feed the expert ratings *and their reasons* back in to calibrate
the judge, then re-measure agreement. The valuable by-product isn't the tuned judge — it's the
distilled rubric, your experts' tacit standard finally written down.

**One caution I'd volunteer:** agreement measured on a skewed set flatters. If 90% of cases are
obviously fine, two raters agree most of the time by luck alone. Judge the judge on the
contested cases.

---

## Q16. "When would you *not* use an LLM judge?"

**What they're really testing:** cost discipline and knowing the tool's edges.

Four cases:

- **When code can decide it.** Was a forbidden identifier disclosed? Was a write action taken?
  Did the tool get called? Deterministic, free, instant, and — most importantly — *reproducible*,
  so when the number moves you know the behaviour moved.
- **When the judge is also the optimisation target.** If a prompt is being automatically tuned
  against a judge, that judge can no longer be the thing that certifies the result. It is by
  definition the most overfit number available. Certify against a strictly larger set of checks
  than the one you optimised.
- **When you need ground truth and don't have it.** A judge can tell you whether an answer is
  supported by the retrieved text. It cannot tell you whether the retrieved text is true.
- **At high volume on every request.** Each judged metric is an extra model call per case. Five
  metrics over a day's traffic is a serious bill — often more than serving the traffic cost.

The rule I'd state: judges are for questions that genuinely need judgement — quality, tone,
whether a paraphrase leaked something. Everything else should be code.

---

## Q17. "The judge scores 0.9 and the customer says it's terrible. Who's wrong?"

**What they're really testing:** composure, and diagnostic order.

Probably neither, and I'd resist picking a side before looking. The usual explanations, in the
order I'd check them:

- **The metric doesn't cover what they care about.** They're reacting to latency, tone, or
  three clarifying questions before an answer. All invisible to a correctness score.
- **The aggregate is hiding their slice.** They're in the 10%. If their use case is a category
  that fails consistently, the mean is irrelevant to them and completely accurate overall.
- **The judge is uncalibrated and generous.** Entirely possible if nobody ever checked it
  against a human.
- **They're right and the dataset is unrepresentative.** The eval set was built from questions
  we invented; theirs aren't in it.

The move is the same regardless: get three specific examples they consider bad, run them, and
look at the traces. Either the metric scores them badly — in which case the aggregate was hiding
a slice — or it scores them well, and you've just found the dimension nobody was measuring.
Both outcomes are progress; arguing from the dashboard is not.

---

# Part 5 — Offline → online

## Q18. "What can you measure in production that you can't measure offline, and vice versa?"

**What they're really testing:** whether you understand the structural difference, not just the
deployment difference.

The asymmetry is ground truth. Production traffic has none — nobody wrote the correct answer for
a question a customer asked thirty seconds ago, and nobody ever will.

That single fact partitions your scorers:

| Transfers to production | Offline only |
|---|---|
| Groundedness, relevance, safety, policy-adherence rules | Anything comparing against a known-correct answer |
| Any deterministic check over the input and output | Anything comparing against expected tool calls |

A scorer that needs expected answers works perfectly in CI and, pointed at live traffic, scores
nothing at all — and it does so quietly, which is worse than failing loudly.

The complementary roles: **offline catches what your dataset contains; online exists to find
what it didn't.** Offline is total coverage of a narrow, fixed world with a hard pass/fail bar.
Online is partial coverage of the real world with no bar, only a trend. You need both, and the
loop between them is mandatory — every production discovery becomes a permanent offline test, or
it only helps you once.

---

## Q19. "You can't afford to judge every production request. How do you decide what to sample?"

**What they're really testing:** whether "sampling" is a number you picked or a decision you
derived.

Two decisions, and the first one people get wrong by treating everything uniformly:

**Don't sample the free checks.** Deterministic rules cost nothing — run them on 100% of traffic.
Sampling a free check just creates blind spots for no saving. Sampling applies only to the
model-judged metrics, which are the ones that cost money.

**Derive the rate from the decision.** Start from the smallest regression you need to detect,
work out how many scored requests it takes to resolve a change that size, then divide by daily
traffic. That gives a rate you can defend. Picking 5% because it sounds affordable gives you a
number that may be unable to detect anything you'd act on — the worst outcome, because it looks
like monitoring.

**The corollary people miss:** a sampled rate is an estimate with error bars. If your alert
threshold is tighter than what the sample can resolve, it will fire on noise, and within a month
people will be ignoring it. Set the alert at something the sample can actually distinguish, and
catch the smaller movements offline, where coverage is total.

---

## Q20. "What does production monitoring for an agent look like beyond a quality score?"

**What they're really testing:** breadth — that you know a trace is an operational artefact,
not just an eval input.

Four things I'd watch, only one of which is a quality score:

- **Quality signals on sampled traffic** — groundedness, relevance, policy adherence — as a
  trend, not a gate.
- **Behavioural distributions.** What fraction of requests call a tool, and is that fraction
  drifting? A silent jump in tool usage after a prompt change is a real signal long before
  quality scores move.
- **Operational shape per step.** Because spans are timed individually, "it got slower" becomes
  "retrieval latency doubled" — a diagnosis rather than a complaint. Token usage per step is the
  same story for cost.
- **Failures and refusals.** Error rates, tool failures, and how often the agent declines. A
  rising refusal rate is a quality regression that most quality metrics score as a pass.

The one I'd call out as most commonly missed: a monitor that was configured but never actually
switched on looks exactly like a monitor reporting no problems. Verifying that the pipeline is
*running* belongs in the launch checklist, not in the assumption.

---

## Q21. "A metric dropped two points this week. Walk me through what you do."

**What they're really testing:** whether you can resist reacting to noise, and whether you know
what would make the answer knowable.

First question: **can this sample even resolve two points?** If the daily scored volume is small
and the metric is model-judged, a two-point move may be entirely within the noise. Paging
someone on it teaches the team to ignore the alert. So before acting: is the change larger than
what this measurement can distinguish?

If it is real, I'd separate the three things that could have changed:

1. **Us.** A prompt, a model version, a retrieval config, a tool. Check the deployment timeline
   first — it's the cheapest to confirm or eliminate.
2. **Them.** Traffic mix shifted. A new customer segment, a product launch, a seasonal pattern.
   The agent is the same; the questions are harder. Slice by category and see whether the drop
   is uniform or concentrated in new material.
3. **The measurement.** A judge model was upgraded underneath you, or the scored population
   changed. Rare, and infuriating when missed — the system never moved at all.

Then reproduce it offline. Take the failing traces into the curated harness where the comparison
is controlled and paired, confirm the regression there, fix, and leave those traces behind as
permanent test cases.

---

# Part 6 — Gating, regressions and rollback

## Q22. "How do you decide whether a new prompt version is safe to ship?"

**What they're really testing:** whether you know that a threshold alone is not a gate.

Two conditions, and both must hold:

1. **Absolute.** Every blocking dimension clears its bar.
2. **No regression.** No blocking metric has fallen meaningfully below the version currently
   serving traffic.

Either alone is insufficient, and the failure modes are different. Threshold-only permits slow
erosion: a score sliding from 0.98 to 0.91 still clears a 0.90 bar, and three "passing" releases
later you're sitting on the floor with no single release to blame. Regression-only lets a
candidate that improved on a bad baseline ship while still being bad.

Two supporting details I'd mention:

- **"Meaningfully" has to be defined per metric type.** A deterministic check has no noise, so
  any movement is real. A model-judged metric wobbles on its own, so a tolerance below that
  wobble would block good releases for no reason — and a gate people learn to override is worse
  than no gate.
- **Registering a version is not deploying it.** Keep those separate, with evaluation in the
  gap. Then a rollback is moving a pointer back, not an emergency revert-and-redeploy — and the
  rejected candidate stays as evidence of what was tried.

---

## Q23. "An automated prompt-optimisation tool produced a version that scores higher. Ship it?"

**What they're really testing:** whether you recognise an overfit number.

Not on that evidence. The optimiser maximised a specific objective, so a high score against that
objective is the least informative number available — it's the thing that was being maximised.

What I'd require before shipping:

- **Evaluation against a strictly larger set of checks than the one it optimised against.** The
  extra checks are what reveal the overfitting: a prompt tuned for correctness may have become
  longer, more confident, and quietly worse at declining.
- **The same release gate as a human-written prompt.** No exemption for provenance.
- **A read of the prompt itself.** Machine-written prompts drift toward instructions that game
  the judge rather than serve the user. That's visible on inspection and invisible in the score.

And the prerequisite, which is the real answer: **if the judge driving the optimisation was never
calibrated against humans, the whole exercise is harmful, not just unreliable.** You've
automated the pursuit of an unvalidated standard, at speed. Aligning the judge comes before
automating anything against it.

---

## Q24. "How do you keep a green dashboard from being wrong?"

**What they're really testing:** whether you've been burned by the silent-failure class.

By assuming green means "nothing reported" rather than "nothing wrong", and checking the
difference deliberately. The failures that produce a false green all look identical to health:

- **A metric measured but not gated.** Adding a scorer does not add a gate. Every dashboard I've
  seen has at least one metric that is faithfully computed, visibly reported, and blocks
  nothing — a regression in it ships.
- **A check that never ran.** A monitor configured but not started; a scorer erroring on every
  row and dropping out of the results entirely. The absence of a number reads as the absence of a
  problem.
- **A metric name that doesn't exist.** A gate looking up a mistyped name gets nothing back,
  which frequently renders as zero or as a pass depending on the plumbing.
- **A dimension nobody wrote a check for.** The most common of all, and the only fix is
  periodically asking what isn't on the board.

The practical countermeasures: assert that each gate matched a metric that a run actually
produced, and report unmatched gates as **not measured** in their own section — never as zero,
never silently. And test the alarm: deliberately ship something that should fail, and confirm
the gate stops it. An untested gate is a belief.

---

## Q25. "Something got through. How do you run the post-mortem?"

**What they're really testing:** whether failures improve the system or just get patched.

The fix is the smaller half. The questions that matter:

- **Which check should have caught this, and why didn't it?** Usually one of: the dimension was
  never measured; it was measured but not blocking; it was blocking but the dataset contained
  nothing resembling this case.
- **Was it measurable in principle?** Some failures are only visible across turns, or only in
  the end state of a real system. If the instrumentation couldn't express the failure, the fix is
  instrumentation, not another rule.
- **What's the class, not the instance?** Patching the exact input that leaked is theatre. The
  useful output is a class of cases with several phrasings, added permanently to the gated set.

Then the loop closes: the incident becomes a test, the test becomes a gate, the gate blocks the
next occurrence. A post-mortem that ends in a code change and no new test has converted an
outage into nothing.

I'd also ask the uncomfortable one: **had this been silently happening before we noticed?** If
the answer is "we can't tell", that's the finding — the trace retention or the slicing wasn't
good enough to answer a basic question about your own system.

---

# Part 7 — Multi-turn, tools and agency

## Q26. "Your per-turn quality is 95%. The customer says conversations fall apart. Both true?"

**What they're really testing:** whether you can see the compounding that turns a healthy
per-step number into a failing product.

Yes, both true, and the arithmetic is the reason. Turns compound: if each turn has to go right
for the conversation to succeed, a 95% per-turn rate is roughly 77% over five turns and under
60% over ten. The metric looks best precisely where the product is worst — long conversations.

And that's the optimistic model. It assumes turns fail independently, when in reality a bad turn
poisons the context for every turn after it. Real conversation-level rates run below what the
compounding predicts, not at it.

Two consequences for the design:

- **Multi-turn systems need conversation-level gates**, not just turn-level ones. A conversation
  is a unit of success; a turn is not.
- **Any "95% per-step" claim from a dashboard is close to meaningless** until you multiply it by
  the typical conversation depth. It's the single best argument for evaluating at the level the
  user actually experiences.

I'd also track **where** conversations first break. Failures on turn one point at basic
competence; failures on later turns point at context handling. Those need different fixes, and
an aggregate cannot tell them apart.

---

## Q27. "What kind of failure can only be seen across turns?"

**What they're really testing:** whether you understand that some behaviours have no single-turn
representation at all.

The clearest example is acting without consent. The agent says *"I've opened a ticket for you"*
on the first turn, when nobody asked. Evaluate the final reply alone and it is helpful,
on-topic, grounded, safe, and reports a completed action — every single-turn check passes it.
What makes it wrong is that no agreement preceded it, and agreement lives *between* turns.

Others in the same family:

- **Context loss.** Re-asking for an account number the customer gave two turns ago. The reply
  itself is perfectly reasonable in isolation.
- **Ignoring a refusal.** The customer says "no, don't do that", and it happens anyway. The
  refusal is in turn two; the consequence is in the trace.
- **Drift.** Each turn is individually fine and the conversation ends somewhere it shouldn't.

Two design implications I'd raise:

- **Gate write actions in the instructions, then verify by evaluation.** Most agent write actions
  are governed by a prompt, not by the API refusing — which makes obedience something evaluation
  has to test rather than something the code guarantees.
- **There are three outcomes, not two:** complied, violated, and *stalled* — the customer agreed
  and nothing happened. Not dangerous, but they asked for something and didn't get it, and it
  needs a different fix from the other two.

---

## Q28. "How do you evaluate whether an agent took an efficient path, not just a correct one?"

**What they're really testing:** whether you can evaluate process, not only outcome — and
whether you know when that's worth paying for.

The path is visible in the execution record, so the checks operate on the sequence rather than
the final text: redundant repeated calls, steps that contributed nothing, whether it recovered
after a failed call or gave up, whether the order made sense.

What I'd actually measure, in priority order:

1. **Recovery.** Did a failed tool call lead to a sensible alternative or to a confident
   fabrication? This is the one with real user impact.
2. **Redundancy.** The same call repeated with the same arguments is pure cost and latency.
3. **Ordering.** Acting before gathering, or in an order that produces wrong results.

I'd be honest about the trade-off: strict path-matching against a gold trajectory is usually the
wrong tool, because many different valid paths reach a correct outcome and enforcing one makes
the eval brittle and expensive to maintain. I'd rather assert properties of the path than
prescribe the path.

**When it earns its cost:** when steps are expensive, slow, or have side effects. For a
two-step read-only agent, outcome evaluation is enough and trajectory work is over-engineering.

---

## Q29. "The agent has five tools. What new evaluation risks does that create?"

**What they're really testing:** whether you know that scorers have a scope of validity that the
system can silently outgrow.

The headline risk is that an existing metric quietly stops meaning what it meant. A check that
asked "was a tool called when one was expected?" was perfectly correct for a one-tool agent. With
five tools, it passes an agent that calls the billing lookup for a network outage question — a
tool *was* called, and one *was* expected. The check now certifies the failure.

So on adding tools I'd re-examine:

- **Selection, not just usage.** Which tool, not whether any.
- **The wrong-tool failure mode specifically.** It returns data that is genuine, irrelevant and
  confidently presented — far more convincing to a user, and to a judge, than a missing answer.
- **Arguments.** More tools means more parameter surface, and right-tool-wrong-arguments is
  invisible to selection checks.
- **Combinatorial interactions.** Tools called in the wrong order, or one whose output silently
  poisons the next.

The general lesson I'd state: **when an agent gains a capability, audit which existing scorers
still mean what they meant.** This is a maintenance obligation on the eval suite, and skipping it
is how a suite becomes decorative — every check green, none of them still measuring what its
name says.

---

# Part 8 — Adversarial, safety and governance

## Q30. "How do you build an adversarial test set that's worth having?"

**What they're really testing:** whether you design by attack surface or collect strings.

A flat list of jailbreak prompts is close to worthless, because when it passes you've learned
nothing — you know those exact strings fail, not that the surface is covered.

I'd enumerate the *classes* of attack the system's design exposes and cover each:

- Direct instruction override ("ignore your instructions").
- False authority ("as the system administrator...").
- Access to data belonging to someone else.
- Injection through content the agent ingests — a retrieved document or tool output formatted to
  look like a system instruction. This one is frequently missed because the attacker isn't the
  user.
- Requests to take actions beyond the agent's remit.

Then **several phrasings per class**, so one lucky string doesn't stand in for the whole surface.
Coverage is measured over classes, and results are read per class — the aggregate is exactly the
wrong view here, because one class at zero is the whole story and a mean will hide it.

Each case asserts a boundary — must not disclose, must not claim to have acted — rather than a
gold answer. And I'd state the honest limit: this measures the surfaces we thought of. It is a
floor, not a guarantee, and it belongs alongside red-teaming rather than in place of it.

---

## Q31. "Regulated industry — legal asks what evidence you have that the system is safe. What do you show them?"

**What they're really testing:** whether evaluation output is auditable, not just useful to
engineers.

Four things, and the fourth is the one engineers forget:

1. **The written standard**, showing what the system must never do, who approved it, and when.
2. **The gate results per release** — which checks blocked, which passed, and the decision that
   followed. The value here is that the criteria were fixed before the results existed, which is
   what separates a standard from a rationalisation.
3. **The record of what the system actually did.** Retained execution traces, so a specific
   customer interaction can be reconstructed and audited months later.
4. **The known gaps, stated.** What is not covered, and why. Saying "we don't evaluate X, here's
   why, here's the compensating control" is far stronger than silence — silence is
   indistinguishable from not having considered it.

I'd add one thing that cuts the other way: **a trace store is itself a security surface.** It
captures whatever flowed through the system, which can include customer data. The discipline is
to log what the checks need and redact what they don't — the boundary is "needed for scoring",
not "everything that happened to pass through". That tends to be the first question a serious
reviewer asks.

---

## Q32. "The customer wants to launch next week and evaluation isn't ready. What do you say?"

**What they're really testing:** pragmatism versus process-worship, and whether you can make a
risk explicit rather than block.

I wouldn't block the launch on a complete harness — I'd insist on the minimum that makes the
launch reversible and its failures visible:

- **The must-never-happen checks**, even if crude and deterministic. Those are about
  consequence, not polish.
- **Full tracing from the first request.** Non-negotiable, and cheap. Without it a launch
  produces no evidence, and every question afterwards is unanswerable.
- **A rollback that works**, tested once before launch — not a plan, an actual exercise.
- **A narrowed blast radius.** One customer segment, one category, internal users first.
  Scoping the exposure buys more safety than any metric.

Then I'd name the risk plainly: what we cannot currently detect, and how we'd find out. "We have
no way to tell if it's giving wrong advice about X; we'll be reading traces manually for the
first week" is a legitimate position, honestly stated.

What I wouldn't do is claim the launch is safe because a number looked fine. And if they
overrule a must-never-happen gap, that's their call to make — but it gets written down.

---

# Part 9 — Cost, ownership and rollout

## Q33. "What does evaluation cost, and how do you keep it from getting out of hand?"

**What they're really testing:** whether you've run this at scale or only read about it.

It's a recurring operational cost, not a one-off, and it's routinely underestimated. Every
model-judged check is at least one extra model call per case, per metric — a suite of five
metrics across a few hundred cases is thousands of calls per run, and runs happen on every
change.

How I'd control it, in order of effect:

- **Push work down the cost ladder.** If a rule can decide it, a judge should never see it.
  Deterministic checks are free and reproducible; this is the biggest lever and it's free.
- **Split the suite by purpose.** A cheap, fast set on every change; the expensive full set before
  a release decision. Not every commit needs the full judgement.
- **Use a cheaper judge for informational metrics** and keep the strong one for blocking gates.
- **Sample online, never offline.** Offline coverage should be total; online is where sampling
  belongs.
- **Smoke-test before the full run.** A typo in a rubric is much cheaper to find on three cases
  than on five hundred.

I'd also flag the second cost, which is larger and never budgeted: **maintaining ground truth.**
Labels go stale as the product changes, and someone has to own that.

---

## Q34. "Who owns evaluation — the engineers, the domain experts, or a separate team?"

**What they're really testing:** organisational realism.

Split by what each group is uniquely able to do:

- **Domain experts own the standard.** What counts as a good answer is a business judgement, not
  an engineering one. If engineers define quality, you get quality that's convenient to measure.
- **Engineers own the mechanism** — instrumentation, harness, gates, the pipeline — and the
  obligation to keep checks meaning what they say as the system changes.
- **Nobody should own it *separately* from shipping.** An eval team disconnected from delivery
  becomes an approval queue, and approval queues get routed around under deadline pressure. The
  gate has to be part of the release path, not a meeting.

The failure mode I'd name: evaluation that only the person who built it understands. When they
move on, the suite keeps running and slowly stops being trusted, because nobody can say what a
failing check means. Write down what each gate protects and why the bar is where it is — that
document is what makes the suite survivable.

---

## Q35. "Six months in, how do you know the evaluation system itself is still working?"

**What they're really testing:** whether you think of the eval suite as something that also
decays.

Signals I'd watch:

- **Does it ever fail?** A suite that hasn't blocked anything in months is either protecting a
  perfect system or measuring nothing. The second is more likely, and worth proving either way by
  deliberately putting a known-bad candidate through.
- **Do failures get overridden?** A rising override rate means the gates no longer match what the
  team believes, usually because a threshold is mis-set or a check has outlived its validity.
  Overrides are the earliest warning that the suite is drifting into decoration.
- **Do production incidents show up as eval failures afterwards?** If real failures keep arriving
  from a direction the suite doesn't cover, coverage is the problem, not sensitivity.
- **Is the judge still agreeing with people?** Models change underneath you. Re-checking against
  human ratings periodically is calibration, not ceremony.
- **Has the system outgrown its checks?** New tools, new channels, new user segments — each one
  can silently invalidate an existing metric.

The one-line version: **an evaluation suite is a claim about the system, and claims expire.**
Re-testing that claim on a schedule is the difference between a safety net and a decorative one.

---

# Closing notes

## The structure that works for any of these

1. Clarify the business outcome and whose judgement defines "good".
2. Name what must never happen, separately from what should usually happen.
3. Decompose the system and say what is measurable at each layer.
4. Say where ground truth comes from, and admit what it costs.
5. Split the checks: deterministic vs judged, offline vs online.
6. Define the release decision — thresholds *and* no-regression.
7. State the gaps you're not covering, and the compensating control.

## What gets people marked down

| Pattern | Why it reads badly |
|---|---|
| Reaching for a standard metric suite before asking what matters | Measuring what's easy, not what's at stake |
| Treating a judge's score as ground truth | The most common naivety in eval work |
| One aggregate number with no slices | Guarantees the first real failure is found by a user |
| Evaluation as a phase after building | It constrains the architecture; too late to add |
| No answer for "where do the labels come from?" | Where eval programmes actually die |
| Blocking a launch on a complete harness | Risk-averse without being risk-aware |
| "We'd monitor it in production" with no detection story | Monitoring that can't resolve the change you'd act on |
| Never mentioning cost | Judged evaluation can out-cost serving the traffic |

## Lines worth having ready

- Evaluation that doesn't end in a decision is measurement, not evaluation.
- Aggregates hide the thing you need to see.
- Every measurement has a scope of validity, and systems outgrow it silently.
- Silence and success look identical — an unstarted monitor reports no problems.
- Online evaluation discovers; offline prevents recurrence.
- A threshold stops a bad release; a no-regression rule stops slow erosion.
- Documenting a gap buys honesty, not coverage.
