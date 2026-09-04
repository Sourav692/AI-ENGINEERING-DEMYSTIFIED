# A Day in the Life of a Senior FDE

> **Level** 🔴 The FDE Role · **Module** 10 · **Doc** 1 of 7 · **Time** ~20 min
> **Prerequisites:** Module 00 doc 2
> **Source material:** `4. FDE_Related_Preparation/Senior_FDE_Day_to_Day.md`

## Why this matters

*"Walk me through a typical day"* and *"how do you split your time"* are asked to find out whether you understand that a senior forward-deployed engineer's job is three jobs that reinforce each other — or whether you think it is coding with occasional meetings. This document is the day as the source material describes it, grounded in a real insurance engagement and generalisable to any FDE conversation. Do not read it as a script; pull the three or four lines that fit the question actually asked.

## The one-line framing

> *"A Senior FDE's day rarely splits cleanly into 'coding day' vs 'customer day' — most days touch all three: enough hands-on build to keep technical credibility with the team I'm guiding, enough direct customer time to keep the solution anchored to a real business outcome, and enough team-facing time that the people around me aren't blocked on me to move."*

## The three lenses — weighted, not sequential

| Lens | How it shows up daily | What it is actually for |
|---|---|---|
| **Technical build** | Architecture decisions, hands-on code and review, debugging production issues, evaluating retrieval and agent strategies | Staying credible enough to make calls the team will trust, and to catch problems before a customer does |
| **Customer-facing** | Discovery, requirement translation, demos and readouts, escalation handling, expectation-setting on scope and timeline | Making sure what gets built is what the business actually needs — not what the spec said six weeks ago |
| **Guiding the team** | Unblocking engineers, reviewing designs before they are built, calibrating scope with delivery leads, mentoring on customer communication | Making the team's output better and faster than any one person's throughput |

## The day

### Morning — orientation and unblocking (leadership-heavy)

> *"I start by finding out who's blocked, not what I'm building. A five-to-fifteen-minute team sync — sometimes just async — surfaces the one decision that, if I don't make it in the next hour, costs someone their whole day. That's usually an ambiguous requirement, an access or permissions issue on the platform, or a design question that's really a scoping question in disguise."*

What it demonstrates: removing team friction comes before personal output — a senior-IC habit, not a manager title. A blocked engineer is the highest-leverage problem of the day. And many "technical" questions from junior engineers are unclear scope in disguise; the coaching is toward seeing that distinction themselves.

### Mid-morning — deep technical work (technical-heavy)

> *"This is where I do the work only I should be doing — the architecture decision with real trade-offs, the piece of the pipeline that's genuinely hard, or reviewing a design before code gets written rather than after. On the engagement, this looked like designing the two-layer access-control pattern — a fast metadata pre-filter at the vector-search layer, and a live re-verification against the governance catalogue right before generation — because getting that boundary wrong doesn't fail loud, it fails silent."*

What it demonstrates: protecting deep-work time for the highest-blast-radius decisions and delegating the rest deliberately; reviewing design *before* implementation, which is a leadership signal as much as a technical one; framing depth in terms of risk (silent failure) rather than novelty. The two-layer pattern is Module 04 and Module 08 doc 3 — here as the thing a senior person spends their protected hours on.

### Midday — customer and stakeholder time (customer-facing-heavy)

> *"This is discovery, demo or escalation — never a fixed slot, always whatever the account actually needs that day. Early in an engagement it's sitting with the people who'll actually use the system — claims managers, analysts, actuaries — and separately with compliance and security, because those two conversations surface completely different requirements and you need both before you write a single access rule. Later it's a readout, or a hard conversation about what's realistically in scope for this sprint versus next."*

What it demonstrates: discovery as **two separate conversations** — users and governance stakeholders — rather than one generic requirements meeting; deliberately narrowing first-build scope (two business units, one market) to prove a model before expanding; owning hard scope conversations directly rather than routing them through a delivery lead.

### Afternoon — build, review and team calibration (mixed)

> *"Afternoons are usually a mix: my own build time on whatever I scoped for myself that morning, plus reviewing what the team produced that day — not just for correctness, but for whether it matches what the customer actually asked for, which isn't always the same as what the ticket says. If someone's design has drifted from the customer's real intent, that's a conversation I'd rather have today than after it ships."*

What it demonstrates: distinguishing *is this code correct* from *does this solve the customer's actual problem* when reviewing; catching intent drift through frequent lightweight review rather than end-of-sprint surprises; balancing own output against team enablement rather than treating them as competing.

### Late afternoon — testing, honesty and closing the loop

> *"Before I call anything done, I want to know how it fails, not just that it works. On the engagement, my own testing harness caught three real issues before the customer ever would have — including a case where I initially thought the system had leaked access, and it turned out my own test data was stale. Reporting that transparently, including the false alarm, mattered more to the trust I built with that customer than a clean track record would have."*

What it demonstrates: rigorous self-testing as a leadership behaviour — modelling the standard, not mandating it; transparency about failures and false positives over a spotless narrative; closing the day against the customer's *actual* success bar (a zero-leak gate agreed with compliance beforehand), not just an internal definition of done. Module 04 doc 7's false-alarm story, told as a trust-building moment.

## Why the three lenses are one job

> *"None of these are really separable. My technical credibility is what lets the team trust my scoping calls without re-litigating them. My direct customer relationships are what let me make fast, confident trade-off decisions without waiting on a chain of approvals. And the team's growth is what lets me stay hands-on where it matters most instead of being a bottleneck everywhere. Pull any one of the three out and the other two get slower."*

This is the senior-vs-mid-level tell: framing the three responsibilities as interdependent rather than three job descriptions stapled together; positioning technical depth as an enabler of *speed of trust* with team and customer alike; self-awareness about being a potential bottleneck, and structuring the day to avoid becoming one.

## If asked directly about guiding internal teams

- Unblocks before building — team velocity is the first problem of the day.
- Reviews designs *before* code is written, so a wrong turn is cheap.
- Distinguishes ambiguous-requirement problems from technical problems when coaching, and coaches toward spotting the ambiguity rather than resolving the instance.
- Reviews with a customer-intent lens, not just a correctness lens.
- Models rigorous self-testing and transparent reporting of failures, including false alarms, as the team standard.
- Owns hard scope and timeline conversations with the customer directly, shielding the team from ambiguity while keeping them informed of the real constraint.
- Scopes deliberately narrow initial builds to prove a model before scaling.

## The closing line

If asked *"what actually makes you a senior FDE, not just an FDE?"*:

> *"It's less about doing harder individual work and more about being the person whose judgment the team can borrow — on scope, on what 'done' means for this customer, on when to go deep versus when to ship the simpler thing. That only works if I stay technical enough to be trusted, customer-connected enough to know what actually matters, and available enough that I'm not the bottleneck."*

## Checkpoint

- Name the three lenses and the sentence that explains why they are interdependent.
- Why is discovery two conversations rather than one?
- What is the difference between reviewing for correctness and reviewing for customer intent?
- Why does the false-alarm story build more trust than a clean record?
- Deliver the closing line without notes.

**Next →** [End-to-End AI Delivery in Six Stages](02_End_To_End_AI_Delivery_Six_Stages.md)
