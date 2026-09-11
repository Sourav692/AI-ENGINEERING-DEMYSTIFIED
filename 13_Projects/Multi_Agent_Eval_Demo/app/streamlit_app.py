"""
The front end.

Two tabs mirroring the two ideas in this project: watch the team work, then
measure how well it works. It talks to the API over HTTP and holds no logic
of its own -- that separation is the point.
"""

import os

import requests
import streamlit as st

API = os.environ.get("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Multi-Agent Demo", page_icon="🤝", layout="wide")
st.title("🤝 A small team of agents")

# --- Is the API reachable? -------------------------------------------------
try:
    requests.get(f"{API}/health", timeout=3).raise_for_status()
except Exception:
    st.error(f"Cannot reach the API at {API}. Start it first:\n\n"
             "`uvicorn app.api:api --reload`")
    st.stop()

run_tab, eval_tab = st.tabs(["Watch it work", "Measure it"])


# ---------------------------------------------------------------------------
# Tab 1 -- run one task
# ---------------------------------------------------------------------------
with run_tab:
    st.caption(
        "A supervisor reads the task and picks who works next. Each specialist "
        "does one narrow job and hands control back. The supervisor decides "
        "when there is nothing left to do."
    )

    task = st.text_input(
        "Give the team something to do",
        value="A $80 bill with a 15% tip. Tell the customer the total in one friendly sentence.",
    )

    if st.button("Run", type="primary"):
        with st.spinner("The team is working..."):
            result = requests.post(f"{API}/run", json={"task": task}, timeout=120).json()

        st.subheader("Answer")
        st.success(result["answer"])

        left, right = st.columns(2)
        with left:
            st.subheader("Who did what, in order")
            for i, name in enumerate(result["trajectory"], 1):
                st.write(f"{i}. **{name}**")
            st.metric("Supervisor decisions", result["turns"])
        with right:
            st.subheader("What each one produced")
            for note in result["notes"]:
                st.write(f"- {note}")


# ---------------------------------------------------------------------------
# Tab 2 -- evaluate
# ---------------------------------------------------------------------------
with eval_tab:
    st.caption(
        "The same team, run against a fixed set of examples with the expected "
        "outcome written down in advance. Three of the scores are plain rules; "
        "**quality** is a second model giving an opinion."
    )

    if st.button("Run the evaluation", type="primary"):
        with st.spinner("Running every case..."):
            report = requests.post(f"{API}/evaluate", timeout=600).json()

        summary = report["summary"]
        st.subheader(f"Averages across {summary['cases']} cases")

        cols = st.columns(4)
        labels = {
            "routing": "Right specialists",
            "content": "Said the right thing",
            "efficiency": "Few hand-offs",
            "quality": "Reads well (judged)",
        }
        for col, key in zip(cols, ["routing", "content", "efficiency", "quality"]):
            col.metric(labels[key], summary[key] if summary[key] is not None else "-")

        st.subheader("Case by case")
        st.dataframe(
            [
                {
                    "case": r["id"],
                    "answer": r["answer"],
                    "path": r["trajectory"],
                    **{labels[k]: r[k] for k in labels},
                }
                for r in report["rows"]
            ],
            use_container_width=True,
            hide_index=True,
        )

        weak = [r["id"] for r in report["rows"] if (r["routing"] or 0) < 1]
        if weak:
            st.warning(f"Wrong specialists picked for: {', '.join(weak)}")
