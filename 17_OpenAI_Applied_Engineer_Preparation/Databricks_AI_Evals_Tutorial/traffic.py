"""
Simulated production traffic for TelcoAssist
============================================

Built in Phase 4, reused by Phase 6 for continuous production monitoring.

Why simulate traffic at all
---------------------------
Phases 2 and 3 evaluate against a dataset somebody *wrote*. That dataset can only contain
questions its author thought of, which makes it structurally blind to whatever real users
do that the author didn't anticipate. Phase 4 is about mining real traffic instead — but a
tutorial has no real users, so this module stands in for them.

What makes it a useful stand-in is the shape, not the content:

**It is heavily skewed.** A handful of questions account for most volume, and a long tail
of rare ones accounts for the rest. Real support traffic looks like this, and it is the
entire reason random sampling is a poor way to build an evaluation set: sample randomly and
you draw the head of the distribution, which is precisely the part you already had covered.

**The tail contains things the curated dataset never tested**, deliberately:

- questions the knowledge base genuinely cannot answer (family plans, pausing service,
  5G) — these test *abstention*, which `eval_dataset.py` has no row for at all
- a non-English question
- typo-laden and telegraphic phrasing
- a rambling multi-part question
- a billing dispute, which is an escalation path the curated set only probes adversarially

Those are the cases worth discovering, and none of them would appear in a dataset written
by the person who built the agent.
"""

import random

# ============================================================================
# TRAFFIC MIX
# ============================================================================
# (query, customer_id, weight, note)
#
# `weight` is relative frequency. The four highest-weighted entries are questions the
# curated dataset already covers -- that overlap is realistic and is what makes random
# sampling look productive while teaching you nothing new.

TRAFFIC_MIX = [
    # ---- head of the distribution: common, and already covered by the curated set ----
    ("What data plans do you offer for a single line?", None, 18, "covered"),
    ("Why is my bill higher this month than last month?", None, 15, "covered"),
    ("How much do I owe?", "CUST-1001", 12, "covered"),
    ("When do you charge a late fee?", None, 9, "covered"),
    ("How much does international roaming cost?", None, 7, "covered"),
    ("When can I upgrade my phone?", None, 6, "covered"),

    # ---- mid: paraphrases of covered questions, phrased as real users phrase them ----
    ("why is my bill so high???", "CUST-1003", 5, "paraphrase"),
    ("wat plans u hav for one line", None, 4, "typos"),
    ("my phone says SOS only what do i do", None, 4, "paraphrase"),
    ("whats the diff between throttling and being suspended", None, 3, "paraphrase"),

    # ---- tail: NOT covered by the knowledge base -- these test abstention ----
    ("Do you offer family plans for four lines?", None, 3, "out-of-scope"),
    ("Can I pause my service for three months while I'm travelling abroad?", None, 2, "out-of-scope"),
    ("Is 5G included in the Essential plan or is it extra?", None, 2, "out-of-scope"),
    ("Do you have a student discount?", None, 2, "out-of-scope"),

    # ---- tail: other shapes the curated set never exercises ----
    ("¿Cuánto cuesta el roaming internacional?", None, 2, "non-english"),
    ("I was charged twice for the same month, I want that money back today.", "CUST-1001", 2, "dispute"),
    (
        "hi so i moved apartments last month and since then my signal has been terrible, "
        "also i think my bill went up but im not sure, and my wife's phone is fine on the "
        "same plan which is weird, can you figure out whats going on",
        "CUST-1002", 2, "rambling-multipart",
    ),
    ("cancel", "CUST-1003", 1, "telegraphic"),
]

# Questions whose answers the knowledge base genuinely does not contain. The correct
# behaviour is to say so and offer a human -- never to guess. Tracked explicitly because
# Phase 4 uses it to show that mined traffic exposed an untested behaviour.
OUT_OF_SCOPE_NOTES = {"out-of-scope"}


def simulate_traffic(n=30, seed=7):
    """Draw `n` requests according to the weights above.

    Returns a list of `(query, customer_id, note)` tuples. Deterministic for a given seed
    so a tutorial run is reproducible.
    """
    rng = random.Random(seed)
    population = [(q, cid, note) for q, cid, _, note in TRAFFIC_MIX]
    weights = [w for _, _, w, _ in TRAFFIC_MIX]
    return rng.choices(population, weights=weights, k=n)


def traffic_profile():
    """Summarise the mix by note, as share of total weight.

    Useful for making the skew visible before sampling from it: if 'covered' is ~70% of
    volume, a random sample of traces will be ~70% questions you already test.
    """
    total = sum(w for _, _, w, _ in TRAFFIC_MIX)
    by_note = {}
    for _, _, weight, note in TRAFFIC_MIX:
        by_note[note] = by_note.get(note, 0) + weight
    return {note: weight / total for note, weight in sorted(by_note.items(), key=lambda kv: -kv[1])}
