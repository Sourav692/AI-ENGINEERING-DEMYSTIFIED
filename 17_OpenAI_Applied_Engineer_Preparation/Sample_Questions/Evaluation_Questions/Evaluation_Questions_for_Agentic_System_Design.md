# Evaluation Questions for the Agentic System-Design / Decomposition Round

Real-world evaluation questions of the kind asked when you are designing or decomposing an
agentic system in an interview — not coding exercises, not metric derivations. Every answer
here is judgement under a constraint: what to measure, why that and not something else, what
it costs, and what you do when the number disagrees with the stakeholder.

**Sources.** Grounded in `../../Databricks_AI_Evals_Tutorial/` (strategy → tracing → offline →
judges → datasets → gating → online → alignment → optimisation → multi-turn → adversarial) and
`07_Advanced_Agentic_Systems/Evaluation_and_Eval_Harnesses/` (RAG, tool, trajectory,
task-completion and conversational evaluation). Companion to the 23 case studies in
`../OpenAI Applied_Engineer_Problem_Decomposition_Questions.md` — that file covers whole-system
design; this one covers the evaluation thread running through all of it.

---

## How each question is structured

| Field | What it gives you |
|---|---|
| **The issue** | What is actually going on underneath the question — the real problem being described |
| **What they're checking** | The competency being probed. Usually the gap between the obvious answer and the good one |
| **Strong answer** | The substance, in the order you'd say it |
| **Weak answer** | What a mediocre candidate says, and precisely why it reads badly |
| **If they push** | The follow-up you should expect, and how to take it |

**How to use it.** Read the question, answer out loud for two minutes, *then* read on. If your
answer matched the **weak** one, that's the useful signal — most weak answers here are not wrong,
they're shallow, which is harder to notice in yourself.

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

## Q1 — "A customer says their support agent 'isn't good enough'. Where do you start?"

**The issue**
A complaint about an *outcome*, with no failing example attached and nobody named as the owner
of "good". Until both exist, any metric you propose is a guess dressed as rigour.

**What they're checking**
- Whether you ask before you build.
- Whether you can convert a feeling into something falsifiable.

**Strong answer**
Not with a metric. I'd want three things first:

1. **A failing example.** Not a description — an actual conversation they consider bad, plus what
   the right behaviour would have been. One real trace reveals immediately whether the failure is
   retrieval, reasoning, tone, or a policy the agent was never told about.
2. **Who decides.** "Good" is a person's standard. A support lead, a compliance officer and a PM
   will each name a different failure as the worst one. Evaluation not anchored to a named
   decision-maker drifts into measuring whatever is easy.
3. **What happens when it fails.** A wrong answer about office hours and a leaked account balance
   are different classes of problem. Consequence sets the threshold.

Then write the dimensions down *before* running anything — correctness, groundedness, safety,
tone, tool use — and for each: blocking or informational, what bar, who signs off. That document
is the deliverable of session one. Architecture comes after, because the eval criteria constrain
the design more than the reverse.

**Weak answer**
> "I'd set up a standard eval suite — correctness, relevance, groundedness, safety — get a
> baseline, and see where it's low."

Reasonable-sounding and it skips the entire problem. You've chosen what to measure before
learning what they care about, so you'll measure what's easy rather than what's at stake — and
when the suite comes back at 0.88, you still won't know whether that's good.

**If they push**
*"They don't have failing examples — just a bad feeling."* Then generate them: run the current
system over a scenario list built from their real ticket categories and put the outputs in front
of the domain expert. People recognise a bad answer far better than they describe one.

---

## Q2 — "How do you decide what 'good' means when the customer can't tell you?"

**The issue**
Domain experts hold their standard tacitly. They can apply it instantly and cannot write it down,
so asking them to specify it produces either silence or platitudes.

**What they're checking**
- Can you elicit a specification rather than wait for one?
- Do you know that disagreement between experts is information, not noise?

**Strong answer**
Don't ask "what is good?" — show outputs and ask them to sort.

- Assemble 30–50 outputs spanning obvious cases, ambiguous ones, and ones I expect to fail.
- Two experts rate them independently, one line of reasoning each.
- Read the *reasons*, not the scores. The reasons are the rubric, in their own words.
- Where the two disagree, you've found either an ambiguous policy or a genuine organisational
  disagreement. Both are more valuable than the ratings. Escalate as a product decision, not an
  eval detail.

The output is a written standard traceable to real judgements. That's also what makes an
automated judge trustworthy later: it applies the experts' distilled rubric rather than something
I invented and they never reviewed.

**Weak answer**
> "I'd work with stakeholders to define success criteria and turn those into metrics."

It describes the goal, not a method, and it assumes the criteria are available for the asking.
In practice this produces a workshop that generates adjectives — "accurate", "helpful",
"on-brand" — none of which is measurable and none of which anybody can apply consistently.

**If they push**
*"What if the two experts disagree a lot?"* Then stop and surface it. A judge cannot be right on
a case two humans score differently, and no amount of eval engineering resolves an unmade policy
decision.

---

## Q3 — "Walk me through your evaluation strategy for an agent that hasn't been built yet."

**The issue**
Evaluation is being treated as a phase that follows building. It isn't — the criteria constrain
the architecture, and some of them cannot be retrofitted at all.

**What they're checking**
- Sequencing: do you know evaluation is a design input?
- Do you understand that a system has to *emit* the signal its scorers need?

**Strong answer**
Evaluation before code, because it changes what gets built. Three decisions first:

- **What must never happen.** The irreversible and the protected: leaking another customer's
  data, taking a write action nobody asked for, advising outside the agent's remit. These become
  all-or-nothing gates and they shape the architecture — you cannot bolt a consent check onto an
  agent that never exposes when it acted.
- **What good looks like when nothing goes wrong.** Correct, grounded, relevant, appropriately
  short. Numeric bars; mostly informational.
- **What we can't measure yet, stated explicitly.** Writing down "we have no multi-turn cases" is
  worth doing — but documenting a gap is not covering it, and it is very easy to mistake the note
  for protection for months.

Then the design constraint: if retrieval is something the model may or may not do, groundedness
becomes unmeasurable on exactly the runs you most want to inspect. So retrieval becomes a fixed
step, not an optional tool. Instrumentation isn't a chore before evaluation; it *is* the substrate.

**Weak answer**
> "Once we have a working prototype, we'll collect outputs, build a test set, and start measuring
> quality so we can iterate."

Puts evaluation downstream of a system that has already made the choices evaluation should have
influenced — and by then the cheap fixes (make retrieval always run, emit a signal when a write
happens) are expensive.

**If they push**
*"Isn't that over-engineering for a prototype?"* The prototype can skip the harness, not the
definition. Three thresholds cost an hour to write and end the "it feels better" argument two
months later when there's no baseline.

---

## Q4 — "The customer wants one number for a dashboard. What do you give them?"

**The issue**
A reasonable executive request that, taken literally, destroys the signal — an aggregate over a
mixed dataset averages the safety-critical slice into invisibility.

**What they're checking**
- Will you let a summary hide the thing that matters?
- Can you give an executive something honest *and* usable?

**Strong answer**
One number, and a refusal to let it be the only one. A system slightly wrong everywhere and a
system perfect except that it leaks account data on adversarial prompts produce the same headline.

What I'd put on the dashboard:

- **A release verdict** — pass/fail against the blocking gates — rather than an average. It
  answers what they're really asking ("can we ship?") and can't be improved by strength elsewhere.
- **Beneath it, the slices:** by question category, by whether a tool was involved, by attack
  class, by turn position. That's where the actionable signal lives.
- **Separately, "not measured".** An unmeasured dimension and a failed one must never look alike.
  Reporting a gap as zero makes a healthy system look broken; hiding it makes a blind spot look
  like coverage.

Framing for the customer: the headline tells you *whether* to look, the slices tell you *where*.

**Weak answer**
> "I'd give them an overall quality score — a weighted average across our metrics."

Weighted averages are the worst of both worlds: a safety failure gets diluted by good conciseness,
and nobody can say what a move from 0.86 to 0.84 means or what to do about it. It also invites
the team to optimise the composite, which is the number least connected to any real decision.

**If they push**
*"They'll ignore the slices."* Then make the verdict the only thing on the front page and put the
slices one click away. The goal isn't to force them to read everything; it's to ensure the number
they *do* read cannot be green while something critical is red.

---

# Part 2 — Decomposing *what* to measure

## Q5 — "A RAG assistant gives a wrong answer. How do you find out which part is broken?"

**The issue**
Three distinct failures look identical from outside — the answer is wrong either way — and each
has a completely different fix. Treating the system as one blob means fixing the wrong stage.

**What they're checking**
- Can you localise a failure in a pipeline?
- Do you know that a grounded answer can still be wrong?

**Strong answer**
Split the evaluation the way the pipeline splits:

| Where it broke | Question | What you'd see |
|---|---|---|
| Retrieval | Did we fetch the right material at all? | The answer's supporting facts aren't in the retrieved context |
| Generation, ungrounded | Given correct context, did the model invent? | The claim isn't supported by anything retrieved |
| Generation, grounded but wrong | Was the source itself wrong or stale? | The answer faithfully reflects a document that shouldn't be trusted |

So: something that judges the *context* the agent had, something that judges the *answer against
that context*, and something that judges the answer against a known-correct one. The third needs
ground truth and doesn't scale; the first two don't and do.

The diagnostic value is the point. High retrieval quality with low groundedness means the
retriever is fine and the generation is inventing. Low retrieval quality means prompt tuning is
wasted effort. The third row is the one people miss: an answer can be perfectly grounded and still
wrong because the knowledge base is out of date — no grounding metric catches that, and the fix is
a freshness policy, not a model change.

**Weak answer**
> "I'd look at the end-to-end accuracy metric and iterate on the prompt until it improves."

End-to-end accuracy tells you *that* it's broken, never *where*. Teams that measure only this
spend weeks tuning prompts against a retrieval bug, and the improvements they do get are usually
the model learning to paper over bad context.

**If they push**
*"Which would you build first?"* Groundedness — it needs no ground truth, so it's cheap, and for a
retrieval system an ungrounded answer is the most likely real failure.

---

## Q6 — "Same question, but it's an agent with tools, not just RAG. What changes?"

**The issue**
Agent evaluation has layers RAG evaluation doesn't, and passing every lower layer tells you
nothing about the top one.

**What they're checking**
- Do you know the mechanics → process → outcome ladder?
- Do you reach for end-state verification, or trust the model's own account of what it did?

**Strong answer**
RAG asks "was the answer right?". An agent asks "did it do the right thing, the right way?", and
that separates into a ladder:

1. **Tool selection** — the right tool? With one tool this question doesn't exist. With two it
   does, and calling the *wrong* tool is worse than calling none: it returns data that's real,
   irrelevant and confidently presented.
2. **Arguments** — right tool, wrong parameters. Invisible to selection checks.
3. **Trajectory** — was the sequence sound? Redundant calls, wasted steps, no recovery after an
   error. Two agents reach the same answer in two steps and in nine.
4. **Task completion** — forget mechanics: did the user get what they asked for? Every call can be
   individually correct while a stated constraint — a budget, a deadline — is silently dropped.

You can pass every level below and fail the top one, which is why task completion is a separate
concern rather than a restatement of tool correctness.

The strongest signal when available: **verify the end state in the system of record** — was the
ticket actually created, with the right fields? A judge reads text and can be fooled by a
confident sentence that misrepresents what happened. The database cannot.

**Weak answer**
> "I'd add tool-correctness checks on top of the RAG metrics — did it call the tools we expected."

Covers exactly one rung. It passes an agent that called the right tool with wrong arguments,
took nine steps to do a two-step job, and dropped the user's budget constraint — all while the
dashboard reads green.

**If they push**
*"Isn't end-state verification expensive to build?"* It's the cheapest reliable signal you have
if the system of record is already queryable. And it's the only one an eloquent wrong answer
can't defeat.

---

## Q7 — "Which of these do you actually implement first, given two weeks?"

**The issue**
Everything above is worth measuring and there isn't time for all of it. The answer reveals
whether you prioritise by consequence or by what's intellectually interesting.

**What they're checking**
- Prioritisation under a real constraint.
- Whether you know which checks are free.

**Strong answer**
Order by consequence, then by cost:

- **First, the non-negotiables — deterministic where possible.** Did it disclose another
  customer's data? Did it take a write action? These end projects, and many are checkable in plain
  code: no model call, no cost, instant, same verdict every time. Anything code can check should
  never be checked by a judge.
- **Second, one grounding check.** For any retrieval system this is the most likely real failure,
  it needs no ground truth, and it transfers to production later unchanged.
- **Third, a small hand-built set with expected answers**, core happy path only. This is the
  expensive one — someone writes and maintains the labels.
- **Not yet:** trajectory quality, tone, conciseness. Real, but informational, and the first
  things I'd cut for time.

What I would not do is build a suite that measures ten things shallowly. Two gates people trust
beat ten numbers nobody looks at.

**Weak answer**
> "I'd get broad coverage first — a metric for each dimension — then deepen the ones that look
> weak."

Spreads a fixed budget so thin that no single check is trustworthy, and produces a dashboard where
everything is amber. It also front-loads the expensive labelled work before anyone has agreed what
the bar is.

**If they push**
*"What if the customer insists on tone and conciseness?"* They can have them — as informational
metrics that don't block. The distinction between measured and blocking is the negotiating room.

---

## Q8 — "Retrieval scores are excellent but users still complain. What's your hypothesis?"

**The issue**
A green metric and an unhappy user are both facts. The interesting question is which of several
explanations is cheapest to rule out.

**What they're checking**
- Do you treat a green metric as proof or as a claim to check?
- Can you enumerate causes and order them by cost to eliminate?

**Strong answer**
Several possibilities, ranked by how cheaply I can test them:

- **The metric measures the wrong population.** Retrieval is scored on a curated set built from
  questions we imagined; users ask different ones. Hand-written datasets contain what the author
  thought of, and that gap is invisible from inside the dataset.
- **Retrieval is right, the answer isn't.** Fetching the correct document and answering a
  different question is entirely possible — which is why relevance-to-query is a separate check.
- **The document is correct and obsolete.** Grounding says the answer matches the source; nothing
  says the source is current.
- **The complaint isn't about correctness at all.** Too long, wrong tone, no citation, three
  clarifying questions before an answer. All real product failures, none visible to an accuracy
  metric.

The action is the same in every case: stop arguing from the dashboard and read the traces of the
complaining users' actual sessions. Whatever is wrong is visible there, and it tells you which
metric is *missing* rather than which is broken.

**Weak answer**
> "The retrieval metric is probably fine — it's likely a generation problem, so I'd focus on
> prompt engineering."

Picks a conclusion before looking. It's also the most expensive guess to be wrong about: prompt
iteration is slow, and if the real cause is an unrepresentative eval set, no amount of it helps.

**If they push**
*"How many traces would you read?"* Ten to twenty from the complaining segment, read properly. The
answer is almost never in the aggregate and almost always in the third or fourth trace.

---

## Q9 — "How would you evaluate an agent whose job is to decide *not* to answer?"

**The issue**
The correct behaviour is a refusal, an escalation or a clarifying question. There is no correct
*content*, so the usual "compare against the expected answer" shape doesn't apply — and forcing it
is actively dangerous.

**What they're checking**
- Can you evaluate the absence of an action?
- Do you see the trap where the eval rewards the leak?

**Strong answer**
The case doesn't get a gold answer; it gets a rule: must decline, must not state any account
details, must offer a human.

This distinction matters more than it sounds. Force those cases into a gold-answer format and you
end up asserting that a refusal contains particular facts — and the only way to make the case pass
is for the agent to reveal the data you were protecting. The eval doesn't just miss the leak, it
rewards it.

Two more things I'd insist on:

- **Absence is a behaviour worth scoring.** An agent that correctly makes no tool call produces no
  tool activity — which looks exactly like an agent whose instrumentation is broken. Distinguish
  the two deliberately, or a silent failure hides inside a passing metric.
- **Over-refusal is the other failure.** An agent that declines everything scores perfectly on
  safety and is useless. Both directions belong in the dataset, or you optimise into the useless
  corner.

**Weak answer**
> "I'd add the refusal cases to the test set with the expected response — something like 'I'm
> sorry, I can't share that information.'"

Pins a single wording as correct, so a perfectly good refusal phrased differently scores as a
failure — and the team tunes the agent toward one canned sentence. Do this on a data-protection
case and the only way to make the row pass is to leak.

**If they push**
*"How do you stop it becoming too cautious?"* Put near-miss cases in the set — questions that
*sound* sensitive but are fine to answer. Refusing those is a failure, and scoring it makes the
trade-off visible instead of one-directional.

---

# Part 3 — Ground truth and datasets

## Q10 — "Where does your evaluation data come from on day one, and how does that change by month three?"

**The issue**
On day one there is no traffic, so the set is imagined. By month three there is traffic, and the
imagined set is the weakest part of the system — but switching to traffic introduces its own trap.

**What they're checking**
- Do you know dataset strategy has a lifecycle?
- Do you know what trace mining does and doesn't give you for free?

**Strong answer**
**Day one it's hand-written**, because nothing else exists — built from the customer's own
categories, their top ticket types, the cases their support leads argue about, rather than from
imagination. Its weakness is structural and worth saying out loud: it contains what we thought of.

**By month three the real traffic is the asset.** Production traces give you the *distribution* —
which questions actually arrive, in what proportion, with what messiness. That's the expensive
half to guess and the free half to collect.

The caveat: mining gives you **inputs, not labels**. What people asked is free; what the right
answer was still needs a human.

And the trap to name before they do: **never use the agent's own outputs as expected answers.** It
passes by construction and freezes today's bugs as the definition of correct.

**Weak answer**
> "We'd log production traffic and build the eval set from real user queries — that way it's
> representative."

Half right, and the missing half is the expensive one. It implies labelling is solved by logging,
when logging only solves the input side. Teams that plan this way discover in month four that
nobody budgeted for the labels and quietly start using model outputs as ground truth.

**If they push**
*"How do you choose which traces to promote?"* Not at random — random sampling reproduces the head
of the distribution you already cover. Target novelty: inputs unlike anything in the current set,
sessions where the agent hedged or the user rephrased. And select by a quality bar rather than a
fixed count, so a quiet week yields fewer rows instead of duplicates.

---

## Q11 — "Your eval set and production traffic have diverged. How do you keep both honest?"

**The issue**
The two datasets have opposite requirements — one must never change, the other must always change
— and most teams run a single set that satisfies neither.

**What they're checking**
- Do you understand that comparison validity and freshness are in direct conflict?
- Is there a loop from production discovery back to permanent coverage?

**Strong answer**
Two datasets, two policies:

- **The curated regression set must not drift.** Its entire value is that a score from March and
  one from June are comparable. Change it and every historical comparison is void — a changed
  dataset invalidates a comparison as surely as a changed scorer set does. It changes only through
  a deliberate, announced update, and then you re-baseline rather than compare across the boundary.
- **The mined set must stay fresh.** Its value is reflecting what users do *now*. Refreshed
  continuously, used to *find* problems, never to gate releases.

The bridge is a rule, and it's the one I'd emphasise: **every production failure gets promoted into
the gated set.** Online discovers; offline prevents recurrence. A finding not carried into a
permanent test only helps you once.

**Weak answer**
> "I'd continuously refresh the eval set from production so it always reflects current traffic."

Sounds like good hygiene and quietly destroys your ability to detect regressions. If the set
changes between runs, a score drop could be a worse agent or a harder dataset, and you can never
tell which. This is how teams end up unable to answer "did last week's change help?"

**If they push**
*"When would you update the regression set?"* When the product changes scope, or when coverage
gaps show up repeatedly in production. And I'd run both versions side by side once to record the
offset, so historical numbers stay interpretable.

---

## Q12 — "How big does the evaluation set need to be?"

**The issue**
The question invites a round number. The honest answer depends on the smallest difference you need
to be able to detect, which nobody has stated yet.

**What they're checking**
- Do you reason backwards from the decision, or reach for "a few hundred"?
- Do you know composition matters more than count?

**Strong answer**
Not a number I'd guess. It's set by the smallest difference you need to *detect*.

If the question is "did this prompt change make things worse?" and you need to catch a couple of
percentage points, a small set can't resolve that — the difference sits inside the run-to-run
wobble. If you only need to catch catastrophic regressions, a few dozen well-chosen cases suffice.

Two corollaries:

- **Composition beats size.** Fifty cases spanning every category and attack class are worth more
  than five hundred variations on the same easy question. You're buying coverage of the *decision
  space*.
- **The noise floor sets the resolution.** Model-judged metrics wobble between identical runs;
  below that wobble a real change and the judge changing its mind are indistinguishable. A bigger
  set narrows that, never removes it.

For a first production system: enough curated cases to cover every category and every
must-never-happen class, then grow from traffic where it turns out thin.

**Weak answer**
> "Usually a few hundred examples is a good rule of thumb — enough for the metrics to be stable."

A number with no derivation. It may be ten times more than needed for a go/no-go gate, or far too
few to resolve the regression you actually care about, and the candidate has no way to tell which
because the size wasn't tied to any decision.

**If they push**
*"Give me a starting point anyway."* Enough to cover every category and every must-never-happen
class with more than one phrasing — in practice that lands somewhere in the dozens, and it grows
from real traffic rather than from a target.

---

## Q13 — "Who actually writes the labels, and how do you get their time?"

**The issue**
Expert attention is the binding constraint on most eval programmes — not tooling, not metrics.
Plans that assume unlimited labelling quietly die in month three.

**What they're checking**
- Have you run this in a real organisation?
- Do you spend scarce expert time where it's irreplaceable?

**Strong answer**
This is the constraint that actually kills eval programmes. What works:

- **Spend expert time where it's irreplaceable.** Experts adjudicate ambiguous and high-stakes
  cases, not confirm that easy ones are easy. Anything code can check shouldn't reach a human.
- **Ask for judgements, not documents.** "Rate these twenty answers, one line of reasoning each"
  is a 40-minute task. "Write us an evaluation rubric" is a project that never starts.
- **Make the reasons the artefact.** Ratings calibrate the system; the written reasons become the
  standard, and can align an automated judge so the expert doesn't rate the next thousand.
- **Show the return.** Bring back the failures their labels caught. Nothing sustains expert
  participation like seeing their standard block a bad release.

And record **who** produced each label — expert, contractor or script. When that data later
calibrates a judge, provenance is the difference between a defensible standard and an unexamined
one.

**Weak answer**
> "We'd have the domain experts label a few thousand examples up front, then we're set."

Names a quantity nobody has agreed to supply, front-loads the most expensive activity before the
rubric is stable, and treats labelling as one-off when it's continuous — labels go stale as the
product changes.

**If they push**
*"They'll give you two hours a month, total."* Then it goes entirely on contested cases, and I'd
use those judgements to calibrate a judge that handles the volume. Two hours of adjudication on
the hard cases is worth more than twenty on easy ones.

---

# Part 4 — Judges, and who validates them

## Q14 — "You're using an LLM to grade another LLM. Why should anyone believe the number?"

**The issue**
Every score in the system rests on an instrument nobody has calibrated. This is the single most
common naivety in eval work.

**What they're checking**
- Do you treat a judge as an instrument or as an oracle?
- Can you predict the awkward conversation calibration causes?

**Strong answer**
They shouldn't, until it's been checked. A judge is a model with a rubric and inherits every
weakness of the thing it judges — it can be persuaded by fluent, confident, wrong text; it drifts
with wording; it disagrees with itself between runs.

So treat it as a measuring instrument requiring calibration:

- **Check it against people.** Domain experts rate a sample the judge scored; compare where they
  disagree and why.
- **Measure agreement, not average score.** A judge that rates everything highly produces a lovely
  average and is worthless. The question is whether it agrees with a human on the *same case*.
- **Expect the score to fall after calibration, and read that correctly.** A drop doesn't mean the
  agent got worse — it means the measurement stopped flattering. Much easier to say in advance
  than to explain afterwards.

Strongest where no deterministic check exists: open-ended text quality. Weakest on anything a rule
could decide, and on anything the judge is also being optimised against.

**Weak answer**
> "We use a strong frontier model as the judge, so accuracy is generally high — and we can spot
> check a sample if there are concerns."

"Strong model therefore trustworthy" is the assumption in question, and "spot check if concerns
arise" means the judge is trusted until someone complains. It also never mentions agreement, so
a uniformly generous judge would pass this candidate's process untouched.

**If they push**
*"How many human ratings do you need to calibrate?"* Fewer than people expect, if they're spent on
contested cases rather than spread evenly — agreement measured on an easy, skewed sample flatters
everyone.

---

## Q15 — "Your judge and your domain expert disagree on 20% of cases. What do you do?"

**The issue**
A disagreement rate is not a verdict. Whether 20% is alarming depends entirely on *which* 20%, and
the cause is as likely to be your rubric as the model.

**What they're checking**
- Can you debug a measurement instead of discarding it?
- Do you check whether the humans agree with each other first?

**Strong answer**
First, look at *which* 20%. Disagreement scattered across the range is a different problem from
disagreement concentrated near a threshold — the latter is usually borderline cases and matters
far less.

Then separate three causes:

1. **The rubric is vague.** Most common. The judge is applying a reasonable reading of an ambiguous
   instruction. Fix the wording, not the model.
2. **The experts disagree with each other.** Check this before blaming the judge. If two experts
   don't agree, no judge can be right, and you've found an unresolved policy question that belongs
   to the product owner.
3. **The judge is genuinely weak here.** Then a stronger judge, or a deterministic check that
   removes the judgement entirely.

The improvement path: feed the expert ratings *and their reasons* back in to calibrate, then
re-measure agreement. The valuable by-product isn't the tuned judge — it's the distilled rubric,
your experts' tacit standard finally written down.

One caution I'd volunteer: agreement measured on a skewed set flatters. If 90% of cases are
obviously fine, two raters agree most of the time by luck. Judge the judge on the contested cases.

**Weak answer**
> "80% agreement is fairly low, so I'd switch to a stronger judge model and re-run."

Jumps to the most expensive remedy without diagnosing, and it's the one least likely to help: if
the rubric is ambiguous, a better model applies the ambiguous rubric more consistently and still
disagrees with your expert.

**If they push**
*"The experts turn out to disagree with each other 15% of the time."* Then 20% judge disagreement
is close to the human ceiling, and the work isn't judge tuning — it's getting a policy decision on
the contested class.

---

## Q16 — "When would you *not* use an LLM judge?"

**The issue**
Judges are the default reach for anything subjective, and three of the four situations where they
are the wrong tool look exactly like situations where they're the right one.

**What they're checking**
- Cost discipline.
- Whether you spot the circularity when a judge is also an optimisation target.

**Strong answer**
Four cases:

- **When code can decide it.** Was a forbidden identifier disclosed? Was a write action taken? Was
  the tool called? Deterministic, free, instant and — most importantly — *reproducible*, so when
  the number moves you know the behaviour moved.
- **When the judge is also the optimisation target.** If a prompt is being tuned against a judge,
  that judge can no longer certify the result — it is by definition the most overfit number
  available. Certify against a strictly larger set of checks.
- **When you need ground truth and don't have it.** A judge can say whether an answer is supported
  by the retrieved text. It cannot say whether that text is true.
- **At high volume on every request.** Each judged metric is an extra model call per case. Five
  metrics across a day's traffic is a serious bill — often more than serving the traffic cost.

The rule: judges are for questions that genuinely need judgement — quality, tone, whether a
paraphrase leaked something. Everything else is code.

**Weak answer**
> "LLM judges are good for most subjective metrics — I'd use them wherever we don't have a
> reference answer."

Correct as far as it goes and expensive in practice. It sends a judge at things a regex decides
better, misses the circularity problem entirely, and has no cost model, which is how eval bills
end up larger than inference bills.

**If they push**
*"Deterministic checks seem brittle."* They are narrow, not brittle — they catch the blatant case
every time and the clever paraphrase never. The judge is the reverse. Run both; they're
complements, not alternatives.

---

## Q17 — "The judge scores 0.9 and the customer says it's terrible. Who's wrong?"

**The issue**
Two facts in conflict, a stakeholder losing confidence, and a strong temptation to defend the
dashboard. Usually neither party is wrong and the metric is answering a different question.

**What they're checking**
- Composure and diagnostic order.
- Whether you go to traces or argue from aggregates.

**Strong answer**
Probably neither, and I'd resist picking a side before looking. Usual explanations, in the order I
check them:

- **The metric doesn't cover what they care about.** They're reacting to latency, tone, or three
  clarifying questions before an answer. Invisible to correctness.
- **The aggregate is hiding their slice.** They're in the 10%. If their use case is a category
  that fails consistently, the mean is accurate overall and irrelevant to them.
- **The judge is uncalibrated and generous.** Entirely possible if nobody checked it against a
  human.
- **They're right and the dataset is unrepresentative.** The set was built from questions we
  invented; theirs aren't in it.

The move is the same regardless: get three specific examples they consider bad, run them, read the
traces. Either the metric scores them badly — the aggregate was hiding a slice — or it scores them
well, and you've found the dimension nobody was measuring. Both are progress; arguing from the
dashboard is not.

**Weak answer**
> "I'd explain that the metrics show the system is performing well and ask them for specifics."

The order is backwards. Leading with a defence of the number tells the customer you trust your
instrument more than their experience, and you'll spend the rest of the engagement fighting the
dashboard instead of using it.

**If they push**
*"They give you three examples and the judge scores all three at 0.9."* Then the judge is wrong or
the rubric is missing a dimension they care about — and those three examples are now the seed of
the calibration set.

---

# Part 5 — Offline → online

## Q18 — "What can you measure in production that you can't measure offline, and vice versa?"

**The issue**
The difference isn't deployment, it's ground truth — and that single fact partitions the entire
scorer suite in a way most people discover the hard way.

**What they're checking**
- Do you understand the structural asymmetry?
- Do you have a loop between the two, or just two isolated systems?

**Strong answer**
The asymmetry is ground truth. Production traffic has none — nobody wrote the correct answer for a
question asked thirty seconds ago, and nobody ever will.

| Transfers to production | Offline only |
|---|---|
| Groundedness, relevance, safety, policy-adherence rules | Anything comparing against a known-correct answer |
| Any deterministic check over input and output | Anything comparing against expected tool calls |

A scorer needing expected answers works perfectly in CI and, pointed at live traffic, scores
nothing at all — quietly, which is worse than failing loudly.

The complementary roles: **offline catches what your dataset contains; online exists to find what
it didn't.** Offline is total coverage of a narrow fixed world with a hard pass/fail bar. Online is
partial coverage of the real world with no bar, only a trend. The loop between them is mandatory:
every production discovery becomes a permanent offline test, or it only helps you once.

**Weak answer**
> "Offline is for pre-release testing and online is for monitoring quality in production — same
> metrics, different environment."

"Same metrics" is the error. Half the suite silently returns nothing against live traffic, and
because it fails quietly, the dashboard shows a metric that simply stopped having data rather
than an alarm.

**If they push**
*"So what do you actually alert on?"* Reference-free signals and deterministic rules only — and
only at thresholds the sampled volume can resolve.

---

## Q19 — "You can't afford to judge every production request. How do you decide what to sample?"

**The issue**
"Sample 5%" is usually a number chosen for affordability, not for detection power — which produces
monitoring that cannot detect anything anyone would act on.

**What they're checking**
- Is the rate derived from a decision or picked?
- Do you know that some checks shouldn't be sampled at all?

**Strong answer**
Two decisions, and the first is the one people get wrong by treating everything uniformly.

**Don't sample the free checks.** Deterministic rules cost nothing — run them on 100% of traffic.
Sampling a free check creates blind spots for no saving. Sampling applies only to model-judged
metrics.

**Derive the rate from the decision.** Start from the smallest regression you must detect, work
out how many scored requests resolve a change that size, divide by daily traffic. That gives a
rate you can defend. Picking 5% because it sounds affordable may leave you unable to detect
anything actionable — the worst outcome, because it looks like monitoring.

**The corollary people miss:** a sampled rate is an estimate with error bars. If the alert
threshold is tighter than the sample can resolve, it fires on noise, and within a month people
ignore it. Set the alert at something the sample can distinguish and catch smaller movements
offline, where coverage is total.

**Weak answer**
> "I'd sample 5–10% of production traffic — enough for a representative signal without blowing the
> budget."

Reasonable-sounding and undefended. It samples the free checks along with the expensive ones, and
it never connects the rate to the size of regression the team needs to catch — so nobody can say
whether the monitoring would notice the thing they're most afraid of.

**If they push**
*"Traffic is low — a few hundred a day."* Then judged online monitoring is a weak trend signal at
best, and I'd say so. At that volume the detection work belongs offline, and online is for
deterministic rules and error rates.

---

## Q20 — "What does production monitoring for an agent look like beyond a quality score?"

**The issue**
Quality scores are the least sensitive thing on the dashboard. Behavioural and operational signals
move first, and one whole class of failure is invisible by construction.

**What they're checking**
- Breadth: do you see a trace as an operational artefact, not just an eval input?
- Do you check that the monitor is actually running?

**Strong answer**
Four things, only one of which is a quality score:

- **Quality signals on sampled traffic** — groundedness, relevance, policy adherence — as a trend,
  not a gate.
- **Behavioural distributions.** What fraction of requests call a tool, and is it drifting? A
  silent jump after a prompt change is a real signal long before quality moves.
- **Operational shape per step.** Because steps are timed individually, "it got slower" becomes
  "retrieval latency doubled" — a diagnosis rather than a complaint. Token usage per step is the
  same story for cost.
- **Failures and refusals.** Error rates, tool failures, how often the agent declines. A rising
  refusal rate is a quality regression that most quality metrics score as a pass.

The one most commonly missed: a monitor configured but never actually switched on looks exactly
like a monitor reporting no problems. Verifying the pipeline is *running* belongs on the launch
checklist, not in the assumption.

**Weak answer**
> "We'd track our quality metrics over time and alert if they drop, plus standard latency and
> error-rate dashboards."

Two separate dashboards that never meet. It misses behavioural drift entirely, can't turn "slower"
into a per-step diagnosis, and treats a rising refusal rate as healthy because refusals are safe.

**If they push**
*"How would you catch a prompt change that made the agent chattier?"* Response-length distribution
and tool-call rate, both free and both deterministic. Quality judges would likely score it fine.

---

## Q21 — "A metric dropped two points this week. Walk me through what you do."

**The issue**
A small movement in a noisy measurement, with organisational pressure to react. Reacting to noise
trains the team to ignore alerts, which costs more than the drop.

**What they're checking**
- Can you resist reacting before establishing the move is real?
- Do you separate causes systematically?

**Strong answer**
First question: **can this sample even resolve two points?** If daily scored volume is small and
the metric is model-judged, two points may be entirely within the noise. Paging someone teaches
the team to ignore the alert.

If it's real, separate three things that could have changed:

1. **Us.** A prompt, a model version, a retrieval config, a tool. Check the deployment timeline
   first — cheapest to confirm or eliminate.
2. **Them.** Traffic mix shifted: new segment, product launch, seasonality. The agent is the same;
   the questions are harder. Slice by category and see whether the drop is uniform or concentrated.
3. **The measurement.** A judge model upgraded underneath you, or the scored population changed.
   Rare, infuriating when missed — the system never moved at all.

Then reproduce it offline, where the comparison is controlled and paired. Confirm, fix, and leave
those traces behind as permanent test cases.

**Weak answer**
> "I'd investigate the recent changes, roll back the most likely culprit, and see if the metric
> recovers."

Assumes the cause is a deployment and treats rollback as a diagnostic. If the real cause was a
traffic shift, you've reverted a good change, the metric doesn't recover, and you've now got two
unknowns instead of one.

**If they push**
*"The business wants an answer today."* Then say what's known: whether the move exceeds the noise
floor, whether it's uniform or concentrated, and what's been eliminated. That's a real update. A
guessed root cause is not.

---

# Part 6 — Gating, regressions and rollback

## Q22 — "How do you decide whether a new prompt version is safe to ship?"

**The issue**
A threshold alone is not a gate. It permits a system to degrade release by release without any
single release ever failing.

**What they're checking**
- Do you know both conditions and why each alone is insufficient?
- Do you separate registering a version from serving it?

**Strong answer**
Two conditions, both must hold:

1. **Absolute.** Every blocking dimension clears its bar.
2. **No regression.** No blocking metric has fallen meaningfully below the version currently
   serving traffic.

Each alone fails differently. Threshold-only permits slow erosion: a score sliding 0.98 → 0.91
still clears a 0.90 bar, and three "passing" releases later you're on the floor with no single
release to blame. Regression-only lets a candidate that improved on a bad baseline ship while
still being bad.

Two supporting details:

- **"Meaningfully" is defined per metric type.** A deterministic check has no noise, so any
  movement is real. A judged metric wobbles on its own, so a tolerance below that wobble blocks
  good releases for no reason — and a gate people learn to override is worse than no gate.
- **Registering a version is not deploying it.** Keep those separate with evaluation in the gap.
  Rollback is then moving a pointer back, not an emergency revert-and-redeploy, and the rejected
  candidate stays as evidence of what was tried.

**Weak answer**
> "If it beats the current version on our metrics and clears the quality thresholds, we ship it."

This is actually close — but "beats on our metrics" glosses the hard part. Beats by how much? On
which metrics, and what about the ones it lost on? Without a per-metric-type tolerance the team
argues about noise every release, and eventually stops arguing and just ships.

**If they push**
*"It improved on five metrics and dropped on one."* Depends entirely on whether the one is
blocking and whether the drop exceeds its tolerance. An improvement elsewhere never buys down a
blocking regression — that's what "blocking" means.

---

## Q23 — "An automated prompt-optimisation tool produced a version that scores higher. Ship it?"

**The issue**
The score being cited is the objective that was maximised. It is the least informative number in
the system, and the setup is circular unless something outside the loop certifies the result.

**What they're checking**
- Do you recognise an overfit number?
- Do you know that an uncalibrated judge makes automated optimisation actively harmful?

**Strong answer**
Not on that evidence. The optimiser maximised a specific objective, so a high score against it is
the thing being maximised, not evidence of quality.

Before shipping I'd require:

- **Evaluation against a strictly larger set of checks than it optimised against.** The extra
  checks reveal the overfitting: a prompt tuned for correctness may have become longer, more
  confident, and quietly worse at declining.
- **The same release gate as a human-written prompt.** No exemption for provenance.
- **A read of the prompt itself.** Machine-written prompts drift toward instructions that game the
  judge rather than serve the user — visible on inspection, invisible in the score.

And the prerequisite, which is the real answer: **if the judge driving optimisation was never
calibrated against humans, the whole exercise is harmful rather than merely unreliable.** You've
automated the pursuit of an unvalidated standard, at speed. Aligning the judge comes before
automating anything against it.

**Weak answer**
> "If it scores higher on our eval suite, that's what the suite is for — I'd ship it and monitor."

Treats the optimisation target and the acceptance criterion as the same thing, which removes the
only check that could have caught the overfitting. "Monitor afterwards" doesn't rescue it: the
failure modes introduced here — over-confidence, reduced refusal — are exactly the ones production
monitoring scores as passes.

**If they push**
*"What if there's no time to build a larger check set?"* Then read the prompt and test it on the
adversarial cases specifically. Those are where a correctness-optimised prompt degrades first.

---

## Q24 — "How do you keep a green dashboard from being wrong?"

**The issue**
Every failure in this class produces the same visual result as health. Green means "nothing
reported", and the gap between that and "nothing wrong" is where incidents live.

**What they're checking**
- Have you been burned by silent failures?
- Do you test the alarm, or trust it?

**Strong answer**
By assuming green means "nothing reported" and checking the difference deliberately. The false
greens all look identical to health:

- **A metric measured but not gated.** Adding a scorer does not add a gate. Most dashboards have
  at least one metric faithfully computed, visibly reported, and blocking nothing — a regression
  in it ships.
- **A check that never ran.** A monitor configured but not started; a scorer erroring on every row
  and dropping out of the results. Absence of a number reads as absence of a problem.
- **A metric name that doesn't exist.** A gate looking up a mistyped name gets nothing, which
  renders as zero or as a pass depending on the plumbing.
- **A dimension nobody wrote a check for.** The most common, and the only fix is periodically
  asking what isn't on the board.

Countermeasures: assert that each gate matched a metric the run actually produced, and report
unmatched gates as **not measured** in their own section — never as zero, never silently. And test
the alarm: deliberately ship something that should fail and confirm the gate stops it. An untested
gate is a belief.

**Weak answer**
> "We'd have good test coverage of the eval pipeline and review the dashboard regularly in
> standup."

Unit tests confirm the pipeline computes what it was told to; they can't tell you a whole
dimension is missing or that a gate was never wired to anything. And reviewing a green dashboard
is exactly the activity that these failures survive.

**If they push**
*"How often would you test the gates?"* Every time one is added or its threshold changes, plus a
periodic deliberate failure — the same logic as a fire drill.

---

## Q25 — "Something got through. How do you run the post-mortem?"

**The issue**
The instinct is to fix the instance. The valuable output is a class of cases and a new gate — and
an honest answer about whether this had been happening unnoticed.

**What they're checking**
- Do failures improve the system or just get patched?
- Will you ask the uncomfortable question about prior undetected occurrences?

**Strong answer**
The fix is the smaller half. The questions that matter:

- **Which check should have caught this, and why didn't it?** Usually: the dimension was never
  measured; it was measured but not blocking; or it was blocking and the dataset contained nothing
  resembling this case.
- **Was it measurable in principle?** Some failures are only visible across turns, or only in the
  end state of a real system. If the instrumentation couldn't express the failure, the fix is
  instrumentation, not another rule.
- **What's the class, not the instance?** Patching the exact input that leaked is theatre. The
  useful output is a class with several phrasings, added permanently to the gated set.

Then the loop closes: incident → test → gate → blocked next time. A post-mortem ending in a code
change and no new test has converted an outage into nothing.

I'd also ask the uncomfortable one: **had this been happening silently before we noticed?** If the
answer is "we can't tell", that's the finding — retention or slicing wasn't good enough to answer
a basic question about your own system.

**Weak answer**
> "We'd root-cause it, fix the prompt, and add the failing example to the regression set."

The last clause is right and too narrow. Adding the one string that failed protects against that
string; the next phrasing of the same attack passes. And it never asks whether the failure was
detectable at all, so a systemic instrumentation gap survives the post-mortem intact.

**If they push**
*"The fix is a one-line prompt change — is a post-mortem proportionate?"* The size of the fix says
nothing about the size of the gap. A one-line fix for something that reached a customer means the
detection failed, and that's what's being reviewed.

---

# Part 7 — Multi-turn, tools and agency

## Q26 — "Your per-turn quality is 95%. The customer says conversations fall apart. Both true?"

**The issue**
A healthy per-step number and a failing product, with compounding as the explanation. The metric
looks best precisely where the product is worst.

**What they're checking**
- Do you see that turns compound?
- Do you evaluate at the level the user experiences?

**Strong answer**
Yes, both true, and compounding is the reason. If each turn must go right for the conversation to
succeed, a 95% per-turn rate is roughly 77% over five turns and under 60% over ten.

And that's the *optimistic* model. It assumes turns fail independently, when in reality a bad turn
poisons the context for every turn after it. Real conversation-level rates run below what
compounding predicts, not at it.

Two consequences for the design:

- **Multi-turn systems need conversation-level gates**, not just turn-level ones. A conversation is
  a unit of success; a turn is not.
- **Any "95% per-step" claim is close to meaningless** until you multiply by typical conversation
  depth. It's the single best argument for evaluating where the user actually lives.

I'd also track **where** conversations first break. Failures on turn one point at basic competence;
failures on later turns point at context handling. Different fixes, and an aggregate can't tell
them apart.

**Weak answer**
> "95% is strong — the complaints are probably about a specific hard category, so I'd slice the
> metric by topic."

Slicing is a good instinct aimed at the wrong axis. The problem isn't that some turns are harder,
it's that the measurement unit is wrong: even if every category sits at 95%, five-turn
conversations still fail a quarter of the time.

**If they push**
*"What's the conversation-level metric?"* Whether the conversation achieved what the user came
for, plus the things only visible across turns — context retained, consent respected, no drift.

---

## Q27 — "What kind of failure can only be seen across turns?"

**The issue**
Some failures have no single-turn representation at all — the individual reply is exemplary, and
what makes it wrong happened in a different turn.

**What they're checking**
- Can you name a failure invisible to every single-turn check?
- Do you know that instruction-gated actions must be verified, not assumed?

**Strong answer**
The clearest is acting without consent. The agent says *"I've opened a ticket for you"* on turn
one, when nobody asked. Evaluate the final reply alone and it's helpful, on-topic, grounded, safe
and reports a completed action — every single-turn check passes it. What makes it wrong is that no
agreement preceded it, and agreement lives *between* turns.

Others in the same family:

- **Context loss.** Re-asking for an account number given two turns ago. Perfectly reasonable in
  isolation.
- **Ignoring a refusal.** The customer says "no, don't do that", and it happens anyway. The refusal
  is in turn two; the consequence is in the execution record.
- **Drift.** Each turn individually fine, the conversation ends somewhere it shouldn't.

Two design implications:

- **Gate write actions in the instructions, then verify by evaluation.** Most agent write actions
  are governed by a prompt, not by the API refusing — which makes obedience something evaluation
  must test rather than something the code guarantees.
- **Three outcomes, not two:** complied, violated, and *stalled* — the customer agreed and nothing
  happened. Not dangerous, but they asked and didn't get it, and it needs a different fix.

**Weak answer**
> "Multi-turn failures are mostly about memory — the agent forgetting earlier context — so I'd add
> a context-retention check."

Names the most benign member of the family and stops. Context loss is annoying; acting without
consent is a business risk, and no retention check detects it.

**If they push**
*"How do you evaluate consent if the tool has no consent check?"* By relating what the agent did
to what the customer said before it — the sequence is the evidence. Which is only possible if the
execution record shows which turn the action happened on.

---

## Q28 — "How do you evaluate whether an agent took an efficient path, not just a correct one?"

**The issue**
Two agents reach the same right answer, one in two steps and one in nine. Outcome evaluation
scores them identically, and the difference is real cost, latency and risk.

**What they're checking**
- Can you evaluate process, not only outcome?
- Do you know when trajectory work is over-engineering?

**Strong answer**
The path is visible in the execution record, so checks operate on the sequence rather than the
final text: redundant repeated calls, steps contributing nothing, whether it recovered after a
failure or gave up, whether the order made sense.

What I'd measure, in priority order:

1. **Recovery.** Did a failed tool call lead to a sensible alternative or to a confident
   fabrication? The one with real user impact.
2. **Redundancy.** The same call repeated with the same arguments is pure cost and latency.
3. **Ordering.** Acting before gathering, or an order producing wrong results.

I'd be honest about the trade-off: strict path-matching against a gold trajectory is usually the
wrong tool, because many valid paths reach a correct outcome and enforcing one makes the eval
brittle and expensive to maintain. Assert *properties* of the path rather than prescribe the path.

**When it earns its cost:** when steps are expensive, slow, or have side effects. For a two-step
read-only agent, outcome evaluation is enough and trajectory work is over-engineering.

**Weak answer**
> "I'd define the expected sequence of tool calls for each test case and score how closely the
> agent's actual sequence matches it."

Encodes one correct path when several exist, so genuinely good runs fail. It also becomes a
maintenance burden — every legitimate change to the agent's approach means rewriting gold
trajectories — and teams respond by loosening it until it measures nothing.

**If they push**
*"Give me one trajectory check you'd always include."* Recovery after a failed tool call. A polite
failure the agent skates past produces the most dangerous output in the system: specific,
plausible, and about the customer's own data.

---

## Q29 — "The agent has five tools. What new evaluation risks does that create?"

**The issue**
An existing check quietly stops meaning what it meant. Nothing breaks, nothing turns red, and the
suite now certifies the failure.

**What they're checking**
- Do you know that scorers have a scope of validity a system can outgrow?
- Do you treat eval-suite maintenance as an obligation?

**Strong answer**
The headline risk is that an existing metric silently changes meaning. A check asking "was a tool
called when one was expected?" was correct for a one-tool agent. With five tools it passes an agent
that calls the billing lookup for a network outage question — a tool *was* called, one *was*
expected. The check now certifies the failure.

On adding tools I'd re-examine:

- **Selection, not just usage.** Which tool, not whether any.
- **The wrong-tool failure mode specifically.** It returns data that's genuine, irrelevant and
  confidently presented — far more convincing to a user, and to a judge, than a missing answer.
- **Arguments.** More tools means more parameter surface; right-tool-wrong-arguments is invisible
  to selection checks.
- **Interactions.** Tools called in the wrong order, or one whose output poisons the next.

The general lesson: **when an agent gains a capability, audit which existing scorers still mean
what they meant.** Skipping that is how a suite becomes decorative — every check green, none still
measuring what its name says.

**Weak answer**
> "More tools means more combinations to test, so I'd expand the test set to cover each tool and
> the common pairings."

Treats it as a coverage problem only. Expanding cases doesn't help if the scorer scoring them has
become wrong — you'd be adding rows evaluated by a check that now passes the exact failure you're
worried about.

**If they push**
*"How would you have caught the stale scorer?"* A case where the wrong tool is called deliberately.
If both the old and new checks pass it, the old one is no longer measuring anything.

---

# Part 8 — Adversarial, safety and governance

## Q30 — "How do you build an adversarial test set that's worth having?"

**The issue**
A flat list of jailbreak strings passes, everyone relaxes, and nothing has been learned — you know
those strings fail, not that the surface is covered.

**What they're checking**
- Do you design by attack surface or collect examples?
- Do you know that injection can arrive through content, not just from the user?

**Strong answer**
Enumerate the *classes* of attack the design exposes, and cover each:

- Direct instruction override ("ignore your instructions").
- False authority ("as the system administrator...").
- Access to data belonging to someone else.
- Injection through content the agent ingests — a retrieved document or tool output formatted to
  look like a system instruction. Frequently missed, because the attacker isn't the user.
- Requests to act beyond the agent's remit.

Then **several phrasings per class**, so one lucky string doesn't stand in for the surface.
Coverage is measured over classes and results read per class — the aggregate is exactly the wrong
view here, because one class at zero is the whole story and a mean hides it.

Each case asserts a boundary — must not disclose, must not claim to have acted — rather than a gold
answer. And I'd state the limit honestly: this measures the surfaces we thought of. It's a floor,
not a guarantee, and it sits alongside red-teaming rather than replacing it.

**Weak answer**
> "I'd pull a set of known jailbreak prompts and prompt-injection examples and add them as test
> cases."

Borrowed strings test someone else's threat model. They also miss the surface specific to *this*
system — retrieved content carrying instructions, cross-account data access — and when they all
pass, the team concludes it's safe, which is the worst possible outcome of a passing test.

**If they push**
*"How do you know when you have enough classes?"* You don't, which is why coverage is reported as
classes covered rather than as a pass rate, and why it's paired with red-teaming by people who
didn't design the system.

---

## Q31 — "Regulated industry — legal asks what evidence you have that the system is safe. What do you show them?"

**The issue**
Engineering-grade evidence and audit-grade evidence differ. What convinces a team that a system
works is not what demonstrates to a reviewer that it was governed.

**What they're checking**
- Is your eval output auditable?
- Do you recognise the trace store as a security surface in its own right?

**Strong answer**
Four things, and the fourth is the one engineers forget:

1. **The written standard** — what the system must never do, who approved it, when.
2. **The gate results per release** — which checks blocked, which passed, what decision followed.
   The value is that criteria were fixed *before* the results existed, which separates a standard
   from a rationalisation.
3. **The record of what the system actually did** — retained execution traces, so a specific
   interaction can be reconstructed months later.
4. **The known gaps, stated.** What isn't covered and why. "We don't evaluate X, here's why,
   here's the compensating control" is far stronger than silence — silence is indistinguishable
   from not having considered it.

One point that cuts the other way: **a trace store is itself a security surface.** It captures
whatever flowed through the system, including customer data. Log what the checks need and redact
what they don't — the boundary is "needed for scoring", not "everything that happened to pass
through". That's usually the first question a serious reviewer asks.

**Weak answer**
> "I'd show them our evaluation results and the safety metrics — we have high scores on the safety
> suite and full test coverage."

Shows outputs without provenance. A reviewer's question isn't "what did you score?" but "who
decided that was the bar, when, and can you show me what the system did on 14 March?" Scores
without the standard, the approval and the retained record are unauditable.

**If they push**
*"They want to see the failures too."* Good — show them. A record that includes blocked releases
is far more credible than one where everything always passed.

---

## Q32 — "The customer wants to launch next week and evaluation isn't ready. What do you say?"

**The issue**
A real deadline against incomplete assurance. Blocking reads as process-worship; waving it through
reads as negligence. The answer is neither.

**What they're checking**
- Pragmatism versus process-worship.
- Can you make a risk explicit rather than absorb it silently?

**Strong answer**
I wouldn't block on a complete harness. I'd insist on the minimum that makes the launch reversible
and its failures visible:

- **The must-never-happen checks**, even if crude and deterministic. About consequence, not polish.
- **Full tracing from the first request.** Non-negotiable and cheap. Without it the launch produces
  no evidence and every later question is unanswerable.
- **A rollback that works** — tested once before launch, not a plan, an actual exercise.
- **A narrowed blast radius.** One segment, one category, internal users first. Scoping exposure
  buys more safety than any metric.

Then name the risk plainly: what we can't currently detect, and how we'd find out. "We have no way
to tell if it's giving wrong advice about X; we'll be reading traces manually for the first week"
is a legitimate position, honestly stated.

What I wouldn't do is claim the launch is safe because a number looked fine. And if they overrule a
must-never-happen gap, that's their call — but it gets written down.

**Weak answer**
> "I'd push back — launching without evaluation is too risky, and we should delay until the suite
> is ready."

Offers the customer one option, which they'll reject, and then the launch happens without you.
It's also not the real trade-off: tracing plus a narrow rollout plus a working rollback buys most
of the safety in days, and refusing to engage with that forfeits the influence you had.

**If they push**
*"They're launching to everyone regardless."* Then tracing and rollback matter more, not less — and
the manual trace review for week one becomes a staffed commitment, not a good intention.

---

# Part 9 — Cost, ownership and rollout

## Q33 — "What does evaluation cost, and how do you keep it from getting out of hand?"

**The issue**
Judged evaluation is a recurring per-change cost that routinely exceeds what people expect, and
the second cost — maintaining labels — is almost never budgeted at all.

**What they're checking**
- Have you run this at scale or only read about it?
- Do you know the cheapest lever?

**Strong answer**
It's recurring, not one-off. Every judged check is at least one model call per case per metric — a
suite of five across a few hundred cases is thousands of calls per run, and runs happen on every
change.

Controls, in order of effect:

- **Push work down the cost ladder.** If a rule can decide it, a judge should never see it.
  Deterministic checks are free and reproducible. Biggest lever, and free.
- **Split the suite by purpose.** A cheap fast set on every change; the expensive full set before a
  release decision. Not every commit needs the full judgement.
- **Cheaper judge for informational metrics**, strong judge for blocking gates.
- **Sample online, never offline.** Offline coverage should be total.
- **Smoke-test before the full run.** A typo in a rubric is cheaper to find on three cases than on
  five hundred.

The second cost, larger and never budgeted: **maintaining ground truth.** Labels go stale as the
product changes, and someone has to own that.

**Weak answer**
> "It's mostly API costs for the judge calls — manageable, and it scales with how often we run the
> suite."

True and incurious. No lever is named, the deterministic-vs-judged split — the one that actually
controls the bill — never comes up, and the labelling cost is absent entirely, which is the line
item that stops eval programmes.

**If they push**
*"Give me the one change with the biggest saving."* Move everything rule-decidable out of the
judge. In most suites that's a third to a half of the checks, and it makes those checks
reproducible as a bonus.

---

## Q34 — "Who owns evaluation — the engineers, the domain experts, or a separate team?"

**The issue**
Ownership determines what gets measured. Put it in the wrong place and you get quality that's
convenient to measure, or a gate that delivery routes around.

**What they're checking**
- Organisational realism.
- Do you see the failure mode of a separate eval team?

**Strong answer**
Split by what each group is uniquely able to do:

- **Domain experts own the standard.** What counts as a good answer is a business judgement, not an
  engineering one. If engineers define quality, you get quality that's convenient to measure.
- **Engineers own the mechanism** — instrumentation, harness, gates, pipeline — and the obligation
  to keep checks meaning what they say as the system changes.
- **Nobody should own it *separately* from shipping.** An eval team disconnected from delivery
  becomes an approval queue, and approval queues get routed around under deadline pressure. The
  gate belongs in the release path, not in a meeting.

The failure mode I'd name: evaluation only the person who built it understands. When they move on,
the suite keeps running and slowly stops being trusted, because nobody can say what a failing check
means. Write down what each gate protects and why the bar is where it is — that document is what
makes the suite survivable.

**Weak answer**
> "Ideally a dedicated evaluation team owns it, so there's independence from the people building
> the system."

Independence sounds like rigour and produces a queue. The reviewing team lacks the context to judge
borderline cases, delivery teams treat the gate as an obstacle, and the first hard deadline
establishes the precedent for going around it.

**If they push**
*"So no independence at all?"* Independence in the *standard* — experts outside the build team
define it — and integration in the *mechanism*. That gets you the check without the queue.

---

## Q35 — "Six months in, how do you know the evaluation system itself is still working?"

**The issue**
The suite is a claim about the system, and claims expire. A suite can keep running, keep reporting
green, and have stopped measuring anything real months earlier.

**What they're checking**
- Do you think of the eval suite as something that also decays?
- Would you notice a suite that had become decorative?

**Strong answer**
Signals I'd watch:

- **Does it ever fail?** A suite that hasn't blocked anything in months is either protecting a
  perfect system or measuring nothing. The second is more likely — prove it either way by putting a
  known-bad candidate through.
- **Do failures get overridden?** A rising override rate means the gates no longer match what the
  team believes, usually a mis-set threshold or a check that has outlived its validity. Overrides
  are the earliest warning that the suite is drifting into decoration.
- **Do production incidents show up as eval failures afterwards?** If real failures keep arriving
  from a direction the suite doesn't cover, coverage is the problem, not sensitivity.
- **Is the judge still agreeing with people?** Models change underneath you. Periodic re-checking
  is calibration, not ceremony.
- **Has the system outgrown its checks?** New tools, channels, segments — each can silently
  invalidate an existing metric.

One line: **an evaluation suite is a claim about the system, and claims expire.** Re-testing it on a
schedule is the difference between a safety net and a decorative one.

**Weak answer**
> "As long as the suite runs in CI and the metrics stay stable, it's working — and we'd add new
> tests as we find new failure modes."

"Metrics stay stable" is exactly what a suite that has stopped measuring anything looks like.
Stability is being read as health when it's equally consistent with a broken scorer, an unstarted
monitor, or a gate wired to nothing.

**If they push**
*"What would you schedule?"* A deliberate known-bad candidate through the full gate each quarter,
and a judge-versus-human re-check on the contested cases. Both are cheap; both catch decay nothing
else catches.

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
