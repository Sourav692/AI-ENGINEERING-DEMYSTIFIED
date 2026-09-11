"""
The test set.

An evaluation is only as good as the examples you check against. Each case
says what to ask and what a good outcome looks like -- written down in advance,
so scoring is not a matter of opinion after the fact.
"""

from dataclasses import dataclass, field


@dataclass
class Case:
    id: str
    task: str
    expect_agents: set[str] = field(default_factory=set)  # who should have worked
    expect_text: list[str] = field(default_factory=list)  # what the answer should mention


CASES = [
    Case(
        id="numbers-only",
        task="What is 15% of 80?",
        expect_agents={"calculator"},
        expect_text=["12"],
    ),
    Case(
        id="words-only",
        task="Rewrite this as one friendly sentence: order delayed, arrives Friday.",
        expect_agents={"writer"},
        expect_text=["Friday"],
    ),
    Case(
        id="needs-both",
        task="A $80 bill with a 15% tip. Tell the customer the total in one friendly sentence.",
        expect_agents={"calculator", "writer"},
        expect_text=["92"],
    ),
    Case(
        id="needs-both-again",
        task="We shipped 3 boxes of 12 items. Tell the customer how many items in one friendly sentence.",
        expect_agents={"calculator", "writer"},
        expect_text=["36"],
    ),
]
