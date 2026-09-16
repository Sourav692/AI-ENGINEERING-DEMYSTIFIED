# Embraces Adversity - Answer Key

Spoken answers - 3 grounded, 1 needing your input. Deliver them in your own cadence; the wording is a script, not a recitation.

## 1. The hardest professional challenge you've faced

**GROUNDED — AIA live architecture failure.** Alternative if you'd rather: Barclays (~700M events/day cross-region migration, 70% runtime cut) — `[FILL: the bottleneck, the hardest call, the go-live friction]`.

*"The hardest was AIA: weeks into an 8-to-9-week engagement with Asia's largest listed life insurer, my first architecture broke down in real testing. Not subtly — the single agent with 20-plus tools was picking the wrong tool and losing accuracy under context bloat. I had a sponsor expecting an MVP, a data team watching whether the 'AI person' actually knew what they were doing, and no slack in the calendar.*

*I told the sponsor directly: version one doesn't work, here's the specific mechanism, here's the fix and what it costs. Then I re-architected live into the Supervisor pattern, kept every existing tool and asset so the pivot was reversible, and added tracing so we'd know fast if the second design failed too. Later the same failure mode reappeared one level up, and I pivoted again into the Deep Agent pattern.*

*What it changed: the relationship with the sponsor moved from 'vendor with a plan' to 'engineer who tells us the truth mid-flight.' `[FILL: one concrete sign — e.g., they brought me into the next scoping conversation directly].` And it gave me a pattern I've used on every agentic engagement since: specialize early, keep each agent's context small, and don't depend on Beta features for the core path."*

## 2. Adversity that strengthened trust

**GROUNDED — the transparent pivot + the reported false alarm**

*"The same AIA failure is the example. The moment the first architecture broke, the easy move was to quietly patch it and keep the demo narrative intact. I did the opposite: I put the failure in front of the team and the sponsor with the trace data, named the mechanism, and proposed the pivot.*

*Two things happened. The team stopped hedging their own findings — once the senior person on the engagement had said 'my design was wrong, here's the evidence,' `[FILL: e.g., engineers started flagging their own drift in daily review instead of at demo time]`. And the customer's compliance and security stakeholders, who had every reason to be skeptical of an AI system over health disclosures, saw that when something went wrong they'd hear about it from me first. That's what made the later false-alarm report land as a trust builder instead of a crisis.*

*Adversity erodes trust when it's discovered. It strengthens trust when it's disclosed."*

## 3. Push through or change course

**GROUNDED — AIA pivot logic**

*"At AIA, when the single agent broke mid-engagement, 'push through' meant prompt-tuning a design with a structural flaw; 'change course' meant re-architecting with a shrinking window. The deciding question was: is the failure a tuning problem or a mechanism problem? Tracing showed it was mechanism — tool selection degrades with twenty-plus schemas in context — and no amount of prompt work fixes that. So I changed course, but bounded it: same tools, same data, new orchestration on top.*

*The second time — when the Supervisor itself started re-approaching the same bloat — I changed course earlier, before it broke, because I recognised the mechanism.*

*The rule: push through when the problem is tuning and the structure is sound; change course when the structure is the problem — and make the change as small as the mechanism allows."*

## 4. Receiving harsh or unexpected criticism

**NEEDS YOUR INPUT.** Suggested spine, with your existing stance (evidence over ego, the retrieval benchmark, the false alarm):

*"`[FILL: who, what they said, context].` My first move was to check whether it was true before deciding how I felt about it — `[FILL: what you looked at]`. `[It was right / partly right / wrong]`, and `[FILL: what you changed or how you responded]`. I'd rather be corrected early than be confidently wrong in front of a customer — it's the same reason I benchmark my own preferences and report my own false alarms."*
