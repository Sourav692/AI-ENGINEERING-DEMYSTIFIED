# Enterprise Chatbot Platform - Answer Key

This answer key is designed for interview preparation. It shows what a strong GenAI FDE candidate should ask, design, evaluate, secure, and communicate before moving from demo to production.

## Strong discovery questions
- Is model sourcing a commercial API, self-hosted, or hybrid by data classification? That decides weeks of orchestration versus quarters of GPU fleet.
- Does grounding start with general chat or company systems, and which three systems come first?
- How long are conversations retained, who may read another employee's history, and under what legal process?
- Can any employee publish an assistant, or is publishing governed by review?
- Is corporate SSO the sole identity source, and do residency or works-council rules constrain usage telemetry?
- What specifically rules out licensing a vendor's enterprise tier, since that is the build-versus-buy crux?
- What is the measured consumer-AI egress baseline today, and is it already in the proxy logs?
- What time-to-first-token do employees get from the free tool they already have on their phones?

## Strong functional requirements
- Support the core workflow: an employee asks a question, the platform grounds it in systems they personally may read, and streams a cited answer under policy.
- Establish identity at the session and re-evaluate authorization on every turn, not once at login.
- Filter retrieval by the caller's live permissions at query time, so a chunk they cannot open never becomes evidence.
- Let departments publish assistants whose effective scope is the assistant's scope intersected with the viewer's own permissions.
- Classify input before dispatch and scan streamed output, blocking or redacting with the decision recorded.
- Record an append-only audit of every turn, including administrative reads of employee conversations.

## Strong non-functional requirements
- Latency: time-to-first-token is the adoption SLO — p95 under 1.0s and p99 under 2.0s, because a four-second spinner feels broken.
- Availability: about 576,000 turns a day, 40 turns per second at a 2.5x morning peak, and roughly 800 concurrent streams.
- Security: every isolation layer fails closed, because failing open in this system means leaking.
- Compliance: retention is a named policy class with legal hold, and audit completeness must be 100% of turns served.
- Reliability: never lose the user's typed message; degrade to a smaller labeled model rather than returning an error page.
- Cost: conversation history grows quadratically, so pin the head, summarize the middle, and lay out a cacheable stable prefix from day one.

## Architecture explanation
- The coherence rule comes before any box: identity is established at the session, re-evaluated per turn, and nothing enters the context window without passing policy and being audited.
- A gateway validates the SSO token and shapes traffic; the conversation service owns conversation state and authorizes the caller on every turn.
- The context assembler is the design center, where permissions, cost, safety, and quality all intersect — it builds context from the asking human's identity, never the client's claims.
- Retrieval and connectors fetch candidates filtered by the caller's live permissions, and an unavailable ACL resolver drops the chunk rather than widening access.
- Policy and DLP classify the input before dispatch and scan streamed output with a sliding window that overlaps, so a pattern straddling a boundary cannot slip through.
- A model router chooses provider, deployment, and model by data class, cost, and health, with classification outranking cost; provider adapters normalize vendors and own retries.
- A streaming relay holds long-lived connections and handles mid-stream aborts, cancelling the upstream stream when a client disconnects so nobody pays for unread tokens.
- An assistant registry governs definitions and scopes, usage and quota meter tokens, and an append-only audit pipeline records every turn including admin reads.

## Data model / integration assumptions
- Conversation(id, workspace_id, owner_id, assistant_id, retention_class, legal_hold); Message(id, conversation_id, parent_id, role, content_ref, citations, token_count, model_id, status); Assistant(id, author_id, instructions, tool_bindings, data_scopes, visibility, version, review_state); Attachment(id, uploader_id, scan_status, extract_ref); AuditEvent(event_id, actor_id, action, resource_ref, decision, reason).
- Assume Message is a tree, not a list, since `parent_id` is what makes regeneration and branching work.
- Assume `status` distinguishes complete, blocked, failed, and partial, because a stream dying at 80% is none of the first three.
- Assume `retention_class` is a named policy rather than a raw number, so legal can answer which policy applied years later.
- Assume `scan_status` gates entry to the context window, and a failed scan means the attachment is untrusted rather than merely unavailable.

## Red-team risks
- over-scoped assistant laundering access, stale ACLs after revocation, prompt injection via documents, silent head truncation, runaway scripted accounts
- The permission laundromat: one privileged author publishes an assistant company-wide, so its data scope must intersect with each viewer's own permissions.
- Stale ACLs after a revocation, where a cached permission outlives the access change and surfaces a document the employee can no longer open.
- Indirect prompt injection inside an uploaded or retrieved document, which must carry no authority over tool calls or policy.
- Silent system-prompt truncation, where naive drop-from-front removes the head on long conversations and invisibly changes the assistant's behavior.
- Audit pipeline failure, which must fail the turn rather than proceed unrecorded, since backfill is impossible by design.

## Rollout plan
- Week 0-1: baseline consumer-AI egress from proxy logs and agree the two bars — governance and adoption — as one joint target.
- Week 1-2: ship general chat with SSO, quotas, retention classes, and audit before any grounding exists.
- Week 2-3: add grounding on the first corpus, proving query-time permission filtering with a contract test on titles and snippets.
- Week 3-4: hold the gate until permission-boundary violations are zero and citation click-through shows grounding is actually trusted.
- Week 5: add attachments with malware scanning and text extraction, gating context entry on scan status.
- Week 6-8: add assistant publishing under review, asserting scope intersection with the viewer on every turn.
- After pilot: expand corpora only while egress falls, weekly active rises, and audit completeness stays at 100%.

## Evaluation plan
| Metric | What it proves | Strong threshold | Dataset / method |
|---|---|---|---|
| Consumer-AI egress volume | The risk the project was funded to remove is actually shrinking | Down about 80% over two quarters | Network proxy logs against the pre-launch baseline |
| Weekly active over eligible | Adoption is the safety outcome, not a vanity metric | At or above 50% of eligible employees | Product telemetry by department |
| Permission-boundary violations | The isolation layers hold under real use | Zero; any occurrence is an incident, not a trend | Contract tests plus production audit review |
| Audit completeness | Every turn is defensible to legal | 100% of turns served are recorded | Turns recorded divided by turns served |
| p95 time-to-first-token | The platform feels competitive with the free tool | Under 1.0 second, p99 under 2.0 | Streaming telemetry at the relay |
| Policy block rate with false-positive rate | Safety is not driving employees back to consumer tools | Read as a pair, never separately | Block logs with sampled human review |

## Weak answer
I would build a React frontend, a vector database, and an LLM gateway so employees can chat with company data. This is weak because it describes a product without naming its purpose — it never mentions the shadow-AI egress that funded the project, and never filters retrieval by the asking employee's permissions.

## Average answer
I would put a chat UI over a commercial model behind SSO, add retrieval over internal documents with permission filtering, log conversations, and set retention policies. This is better, but still incomplete because it authorizes once at session start rather than per turn, has no scope-intersection rule for shared assistants, and treats adoption as a nice-to-have rather than the safety outcome.

## Strong answer
I would frame the goal as moving AI usage out of ungoverned consumer tools into a governed platform without losing the usefulness that drove people there. That sets two bars in tension: nothing leaves our boundary except under an agreement we control, and time-to-first-token stays close to what employees get free. The coherence rule is that identity is set at the session, re-evaluated every turn, and nothing enters the context window without passing policy and being audited. Permissions derive from the asking human — an assistant's effective scope is its own scope intersected with the viewer's. Every layer fails closed, because failing open here means leaking. Success is displaced shadow-AI traffic plus weekly active use.

## Interviewer scorecard
| Area | 1 - Weak | 3 - Average | 5 - Strong |
|---|---|---|---|
| Problem framing | "Build a ChatGPT clone" | Names governance and internal data | Egress risk as the driver; governance and adoption as one joint, testable target |
| Requirements | Lists chat features | Adds SSO and retention | Aggressive exclusions, TTFT as the adoption SLO, quotas as control surfaces |
| Architecture | UI plus vector DB plus LLM | Retrieval with permission filter | Coherence rule stated first; assembler as design center; router, relay, audit, registry |
| Data/integration | Mentions chat history | Names conversations and messages | Message tree, named retention class, scan-gated attachments, append-only audit of admin reads |
| Evaluation | "People like it" | Tracks usage and latency | Egress displacement, weekly active, zero boundary violations, block and false-positive paired |
| Safety/security | "It is behind SSO" | Adds ACL filtering | Seven layers each failing closed; scope intersection; overlap-window output scanning |
| Rollout | Launch to all 40,000 | Pilot then expand | Grounding, then attachments, then assistants — one new risk class per phase with measured gates |
| Communication | Technical only | Clear but generic | Tells the board, department, and on-call stories from the same telemetry |

## Final 2-minute spoken answer
I would not start with the model. The ask is "build us our own ChatGPT" for 40,000 employees, but the real driver is in the egress report: 6,400 staff are already pasting company data into consumer AI tools. So the business result is moving AI usage out of ungoverned tools into a governed platform without losing what made the consumer tools attractive. That gives two bars that stay in tension — nothing leaves our boundary except under an agreement we control, and time-to-first-token stays close to what they get free on their phones. It also gives an unusually good success metric, because the baseline is already instrumented: reduce measured consumer-AI egress by 80% in two quarters while reaching 50% weekly active use. You cannot hit that by locking down and you cannot hit it by shipping ungoverned. Architecturally, the coherence rule comes before any diagram: identity is established at the session, re-evaluated per turn, and nothing enters the context window without passing policy and being recorded in audit. The context assembler is the design center, where permissions, cost, safety and quality intersect, and permissions always derive from the asking human — so a published assistant's effective scope is its own scope intersected with the viewer's, which is what stops one privileged author laundering access to everyone. Retrieval resolves ACLs at query time and drops a chunk if the resolver is unavailable. Every layer fails closed, because failing open here means leaking. I would ship general chat first, then grounding, then attachments, then assistants — one new risk class per phase.
