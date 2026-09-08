# A Day in the Life — Senior Forward Deployed Engineer (Databricks)

### Purpose: interview-ready articulation of how the role actually splits across technical build, customer-facing delivery, and team/leadership work — grounded in the AIA Group engagement pattern, generalizable to any FDE conversation.

> **How to use this doc:** not a script to read verbatim — a reference to pull specific lines from when asked "walk me through a typical day/week" or "how do you split your time." Pick the 3-4 lines that fit the question actually asked.

---

## The one-line framing

*"A Senior FDE's day rarely splits cleanly into 'coding day' vs. 'customer day' — most days touch all three: enough hands-on build to keep technical credibility with the team I'm guiding, enough direct customer time to keep the solution anchored to a real business outcome, and enough team-facing time that the people around me aren't blocked on me to move."*

---

## The three lenses (weighted, not sequential)

| Lens | Roughly how it shows up daily | What it's actually for |
|---|---|---|
| **Technical build** | Architecture decisions, hands-on code/review, debugging production issues, evaluating retrieval/agent strategies | Staying credible enough to make calls the team will trust, and to catch problems before a customer does |
| **Customer-facing** | Stakeholder discovery, requirement translation, demo/readouts, escalation handling, expectation-setting on scope and timeline | Making sure what gets built is what the business actually needs — not what the spec said six weeks ago |
| **Leadership / guiding the team** | Unblocking engineers, reviewing designs before they're built (not after), calibrating scope with delivery leads, mentoring on customer communication | Making the team's output better and faster than any one person's individual throughput |

---

## Morning — orientation and unblocking (leadership-heavy)

*"I start by finding out who's blocked, not what I'm building. A five-to-fifteen-minute team sync — sometimes just async — surfaces the one decision that, if I don't make it in the next hour, costs someone their whole day. That's usually an ambiguous requirement, an access/permissions issue on the platform, or a design question that's really a scoping question in disguise."*

**Pointers this demonstrates:**
- Prioritizes removing team friction over personal output first thing — a senior IC habit, not a manager title.
- Treats "blocked engineer" as the highest-leverage problem to solve before touching own tickets.
- Recognizes that a lot of "technical" questions from junior engineers are actually unclear scope — and coaches them to see that distinction themselves over time.

---

## Mid-morning — deep technical work (technical-heavy)

*"This is where I do the work only I should be doing — the architecture decision with real trade-offs, the piece of the pipeline that's genuinely hard, or reviewing a design before code gets written rather than after. On the AIA engagement, this looked like designing the two-layer access-control pattern — a fast metadata pre-filter at the vector-search layer, and a live re-verification against Unity Catalog right before generation — because getting that boundary wrong doesn't fail loud, it fails silent."*

**Pointers this demonstrates:**
- Chooses to protect deep-work time for the highest-blast-radius decisions, not routine tickets — delegates the rest deliberately.
- Reviews design *before* implementation, which is a leadership signal (catching cost-of-change early) as much as a technical one.
- Frames technical depth in terms of risk (silent failure) rather than just novelty — shows judgment, not just skill.

---

## Midday — customer / stakeholder time (customer-facing-heavy)

*"This is discovery, demo, or escalation — never a fixed slot, always whatever the account actually needs that day. Early in an engagement it's sitting with the people who'll actually use the system — claims managers, analysts, actuaries — and separately with compliance and security, because those two conversations surface completely different requirements and you need both before you write a single access rule. Later in the engagement it's a readout, or a hard conversation about what's realistically in scope for this sprint versus next."*

**Pointers this demonstrates:**
- Runs discovery as two separate conversations (users vs. governance stakeholders) rather than one generic requirements meeting — shows structured customer engagement, not ad hoc.
- Deliberately narrows first-build scope (e.g., two business units, one market) to prove a model before expanding — protects the customer relationship by shipping something trustworthy first.
- Owns hard scope conversations directly rather than routing them through a delivery lead — a mark of a senior-enough FDE that the customer trusts them with expectation-setting.

---

## Afternoon — build, review, and team calibration (mixed)

*"Afternoons are usually a mix: my own build time on whatever I scoped for myself that morning, plus reviewing what the team produced that day — not just for correctness, but for whether it matches what the customer actually asked for, which isn't always the same as what the ticket says. If someone's design has drifted from the customer's real intent, that's a conversation I'd rather have today than after it ships."*

**Pointers this demonstrates:**
- Distinguishes "is this code correct" from "does this solve the customer's actual problem" when reviewing — a customer-outcome lens applied to team output, not just a code-quality lens.
- Catches scope/intent drift early through frequent, lightweight review rather than end-of-sprint surprises.
- Balances own build output against team-enablement time rather than treating them as competing priorities.

---

## Late afternoon / evening — testing, honesty, and closing the loop

*"Before I call anything done, I want to know how it fails, not just that it works. On AIA, my own testing harness caught three real issues before the customer ever would have — including a case where I initially thought the system had leaked access, and it turned out my own test data was stale. Reporting that transparently, including the false alarm, mattered more to the trust I built with that customer than a clean track record would have."*

**Pointers this demonstrates:**
- Treats rigorous self-testing as a leadership behavior — modeling the standard for the team, not just personal diligence.
- Chooses transparency about failures/false-positives over presenting a spotless narrative — signals maturity and builds durable customer trust.
- Closes the day by validating outcomes against the customer's actual success bar (e.g., zero-leak gate agreed with compliance beforehand), not just internal Definition of Done.

---

## How the three lenses reinforce each other (the actual point)

*"None of these are really separable. My technical credibility is what lets the team trust my scoping calls without re-litigating them. My direct customer relationships are what let me make fast, confident trade-off decisions without waiting on a chain of approvals. And the team's growth is what lets me stay hands-on where it matters most instead of being a bottleneck everywhere. Pull any one of the three out and the other two get slower."*

**Pointers this demonstrates (the senior-vs-mid-level tell):**
- Explicitly frames the three responsibilities as interdependent rather than three separate job descriptions stapled together — this is the line that differentiates "senior" from "does three jobs."
- Positions technical depth as an enabler of *speed of trust* (with both the team and the customer), not just personal capability.
- Shows self-awareness about being a potential bottleneck, and structures the day specifically to avoid becoming one.

---

## Quick-reference: pointers on "guiding internal teams" (if asked directly)

- Unblocks before building — treats team velocity as the first problem of the day, ahead of personal tickets.
- Reviews designs *before* code is written, not after, to keep the cost of a wrong turn cheap.
- Distinguishes ambiguous-requirement problems from technical problems when coaching engineers, and coaches toward the underlying skill (spotting the ambiguity) rather than just resolving the instance.
- Runs review with a customer-intent lens, not just a correctness lens — catches drift between "what the ticket says" and "what the customer meant."
- Models rigorous self-testing and transparent reporting of failures (including false alarms) as the team standard, rather than mandating it top-down.
- Owns hard scope/timeline conversations with the customer directly, shielding the team from ambiguity while keeping them informed of the real constraint.
- Scopes deliberately narrow initial builds to prove a model before scaling it across the team's future work — protects both the team's confidence and the customer's trust.

---

## Closing line (if asked "so what actually makes you a *senior* FDE, not just an FDE")

*"It's less about doing harder individual work and more about being the person whose judgment the team can borrow — on scope, on what 'done' means for this customer, on when to go deep versus when to ship the simpler thing. That only works if I stay technical enough to be trusted, customer-connected enough to know what actually matters, and available enough that I'm not the bottleneck."*
