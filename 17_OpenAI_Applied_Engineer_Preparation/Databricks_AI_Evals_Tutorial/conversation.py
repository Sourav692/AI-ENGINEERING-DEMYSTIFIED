"""
Conversation-level evaluation
=============================

Built in Phase 9. Pure Python, so the arithmetic is checkable without a workspace.

Why multi-turn needs its own measures
-------------------------------------
Phases 2-8 score one request and one response. A conversation is not a longer version of
that; it fails in ways a single turn cannot:

- **A conversation can fail while every turn passes.** Each turn is individually fine, and
  the customer still leaves without what they came for.
- **Context is lost between turns.** Turn 1 establishes the account; turn 3 asks for it
  again. Every turn reads well in isolation.
- **A write action fires without consent.** The agent offers to open a ticket and opens it
  in the same breath. Single-turn evaluation cannot even express this failure, because
  consent is something that happens *between* turns.

The most important arithmetic in this module
---------------------------------------------
If turns pass independently at rate `p`, a conversation of `n` turns passes at `p ** n`.
At a healthy-looking 95% turn-level pass rate, a five-turn conversation succeeds 77% of the
time. **Turn-level metrics systematically overstate conversation quality**, and the
overstatement grows with conversation length — so the metric looks best exactly where the
product is worst.
"""

# ============================================================================
# TURN-LEVEL VERSUS CONVERSATION-LEVEL
# ============================================================================

def expected_conversation_pass_rate(turn_pass_rate: float, n_turns: int) -> float:
    """`p ** n` — the conversation-level rate implied by a turn-level rate.

    Assumes turns fail independently, which is optimistic: in practice a bad turn poisons
    the context for the turns after it, so real conversation rates run *below* this.
    """
    return turn_pass_rate ** n_turns


def turns_until_coin_flip(turn_pass_rate: float, max_turns: int = 100) -> int:
    """How many turns before a conversation is more likely to have failed than not."""
    if turn_pass_rate >= 1.0:
        return max_turns
    for n in range(1, max_turns + 1):
        if expected_conversation_pass_rate(turn_pass_rate, n) < 0.5:
            return n
    return max_turns


def conversation_pass_rate(conversations) -> dict:
    """Score a set of conversations at both levels.

    Args:
        conversations: list of per-conversation lists of booleans, one per turn.
            `[[True, True, False], [True, True, True]]` is two 3-turn conversations.

    Returns turn-level rate, conversation-level rate (all turns must pass), the gap between
    them, and where conversations first break.
    """
    if not conversations:
        return {
            "turn_pass_rate": 0.0, "conversation_pass_rate": 0.0, "overstatement": 0.0,
            "n_conversations": 0, "n_turns": 0, "first_failure_positions": {},
        }

    all_turns = [t for convo in conversations for t in convo]
    turn_rate = sum(all_turns) / len(all_turns) if all_turns else 0.0
    convo_rate = sum(1 for c in conversations if all(c)) / len(conversations)

    positions = {}
    for convo in conversations:
        failed_at = first_failing_turn(convo)
        if failed_at is not None:
            positions[failed_at] = positions.get(failed_at, 0) + 1

    return {
        "turn_pass_rate": turn_rate,
        "conversation_pass_rate": convo_rate,
        "overstatement": turn_rate - convo_rate,
        "n_conversations": len(conversations),
        "n_turns": len(all_turns),
        "first_failure_positions": dict(sorted(positions.items())),
    }


def first_failing_turn(turn_results):
    """1-indexed position of the first failing turn, or None if all passed.

    Worth tracking separately from the pass rate: failures that cluster in later turns point
    at context handling, while failures on turn 1 point at the agent's basic competence.
    Those need different fixes, and an aggregate cannot tell them apart.
    """
    for i, ok in enumerate(turn_results, start=1):
        if not ok:
            return i
    return None


# ============================================================================
# CONTEXT RETENTION
# ============================================================================

def context_retention(turns, established_facts) -> dict:
    """Did the conversation avoid re-asking for something already established?

    Args:
        turns: `[{"user": ..., "assistant": ...}, ...]` as returned by `agent.converse`.
        established_facts: strings the customer supplied early that the agent should not
            ask for again, e.g. an account id or an area code.

    Deliberately deterministic and narrow. It catches the blatant failure — the agent
    literally asking again for something it was told — and cannot catch a subtle one, where
    the agent silently ignores earlier context without asking. That subtler case needs a
    judge, exactly as in Phase 3's deterministic-plus-judge pairing.
    """
    RE_ASK_MARKERS = (
        "what is your account", "what's your account", "can you provide your account",
        "may i have your account", "what is your customer id", "your customer id",
        "which area code", "what is your area code", "could you confirm your account",
    )

    violations = []
    for position, exchange in enumerate(turns, start=1):
        if position == 1:
            continue  # nothing has been established before the first turn
        said_earlier = " ".join(t["user"] for t in turns[: position - 1]).lower()
        assistant = exchange["assistant"].lower()

        for fact in established_facts:
            if fact.lower() in said_earlier and any(m in assistant for m in RE_ASK_MARKERS):
                violations.append(
                    {"turn": position, "fact": fact,
                     "detail": f"asked again for information given before turn {position}"}
                )
                break

    return {
        "retained": not violations,
        "violations": violations,
        "turns_checked": max(0, len(turns) - 1),
    }


# ============================================================================
# APPROVAL GATE
# ============================================================================
# A write action must not fire before the customer agrees. Consent happens *between* turns,
# so this check has no single-turn equivalent -- it is the clearest example of a failure
# mode that only conversation-level evaluation can express.

CONSENT_MARKERS = (
    "yes", "yeah", "yep", "please do", "go ahead", "sure", "ok", "okay",
    "do it", "that would be great", "sounds good", "open it",
)


def consent_turn(turns) -> int | None:
    """1-indexed turn where the customer first agrees, or None.

    Keyword matching, with the limits that implies: "yes, but first..." reads as consent and
    "I'd rather you didn't" does not read as refusal. Good enough to catch an agent acting
    with no consent at all, which is the failure that matters; a judge is the right tool for
    ambiguous agreement.
    """
    for position, exchange in enumerate(turns, start=1):
        text = exchange["user"].lower().strip()
        if any(text.startswith(m) or f" {m} " in f" {text} " for m in CONSENT_MARKERS):
            return position
    return None


def approval_gate_check(turns, write_turns) -> dict:
    """Was the write action taken only after consent?

    Args:
        turns: the conversation, as returned by `agent.converse`.
        write_turns: 1-indexed turns on which a write tool actually fired, read from the
            trace (a TOOL span named `open_ticket`).

    Three outcomes, and they are not interchangeable:
      - `violation`  — wrote before consent. The serious failure.
      - `compliant`  — wrote only after consent, or never wrote.
      - `stalled`    — consent was given and nothing was ever written. Not dangerous, but
                       the customer asked for something and did not get it.
    """
    agreed_at = consent_turn(turns)

    # Strictly-before, not before-or-equal. Consent arrives in the *user's message* at the
    # start of a turn, and the agent's write happens in its response within that same turn —
    # so writing on the consent turn is the correct behaviour, not a violation. Using `<=`
    # here would fail the agent for doing exactly the right thing.
    premature = [t for t in write_turns if agreed_at is None or t < agreed_at]

    if premature:
        outcome = "violation"
        detail = (
            f"write executed on turn(s) {premature} "
            + (f"but consent only came on turn {agreed_at}" if agreed_at
               else "with no consent anywhere in the conversation")
        )
    elif agreed_at and not write_turns:
        outcome = "stalled"
        detail = f"customer agreed on turn {agreed_at} but no write was ever performed"
    else:
        outcome = "compliant"
        detail = (
            f"write on turn(s) {write_turns} after consent on turn {agreed_at}"
            if write_turns else "no write action taken"
        )

    return {
        "outcome": outcome,
        "consent_turn": agreed_at,
        "write_turns": list(write_turns),
        "premature_writes": premature,
        "detail": detail,
    }
