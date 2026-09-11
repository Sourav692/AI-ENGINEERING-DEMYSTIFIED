# A Small Team of Agents — and How to Tell If It Works

A deliberately tiny end-to-end demo. Four files of real code, each showing one idea:

| Idea | File |
|---|---|
| Several agents working as a team | `app/agents.py` |
| Measuring whether they did well | `app/evaluation.py` + `app/dataset.py` |
| Putting it behind a service | `app/api.py` |
| Giving it a face | `app/streamlit_app.py` |

The task the agents perform is intentionally dull — tips and totals. The point is the
shape of the system, not what it computes.

---

## 1. The team

One **supervisor** and two **specialists**.

```
                 ┌──────────────┐
        ┌───────▶│  supervisor  │────────▶ done
        │        └──────┬───────┘
        │               │ picks one
        │      ┌────────┴────────┐
        │      ▼                 ▼
        │  calculator         writer
        └──────┴─────────────────┘
              hands control back
```

The supervisor reads the task, picks who works next, and gets control back as soon as
that specialist is finished. It keeps going until it decides there is nothing left to do.

Three things are worth noticing:

**The specialists never talk to each other.** They only read and write one shared
dictionary. `calculator` has no idea `writer` exists. You can add a third specialist
without touching either of them.

**Nothing is wired in advance.** There are no fixed connections between the supervisor and
the specialists. Each node *returns* the name of whoever should go next, decided while it
runs. That is what makes the path different for different tasks:

```
"What is 15% of 80?"                    supervisor → calculator → supervisor → writer → supervisor
"Rewrite this as a friendly sentence"   supervisor → writer → supervisor
```

**Something has to stop it.** A supervisor that keeps choosing specialists loops forever.
This is the most common way the pattern fails, so there are two guards: never pick someone
who has already worked, and stop after six turns regardless. Both are in `supervisor()`.

---

## 2. Measuring it

Running an agent tells you it produced *something*. It does not tell you whether that
something was any good. So `dataset.py` writes down, in advance, what a good outcome looks
like for each example, and `evaluation.py` scores against it.

Four scores, of two different kinds:

| Score | Kind | Asks |
|---|---|---|
| `routing` | rule | Did the right specialists get involved? |
| `content` | rule | Does the answer contain the number it needs to? |
| `efficiency` | rule | How many hand-offs did it take? |
| `quality` | judged | Does it read well? (a second model gives an opinion) |

The distinction matters more than any individual score. **Rules** cost nothing, run
instantly, and give the same answer every time. **Judgements** cost money, are slow, and
will not give you the identical number twice — but they can assess things no rule can.

### Why you need both — an actual result from this demo

Running the suite as written produces:

```
numbers-only       routing=0.0  content=1.0  efficiency=1.0  quality=1.0
words-only         routing=1.0  content=1.0  efficiency=1.0  quality=1.0
needs-both         routing=1.0  content=0.0  efficiency=1.0  quality=1.0
needs-both-again   routing=1.0  content=1.0  efficiency=1.0  quality=1.0

average            routing=0.75 content=0.75 efficiency=1.0  quality=1.0
```

Look at the `needs-both` row. The task was an $80 bill with a 15% tip. The team answered:

> "No problem, your total comes out to $112 with the tip!"

The correct answer is $92. **The judge gave that answer a perfect score.** It reads
beautifully, so the model rated it 5 out of 5. The one-line rule checking for "92" caught
it instantly, for free.

That is the lesson. A judge tells you whether an answer *sounds* right. Use cheap rules
for anything you can state precisely, and save the judge for the part that genuinely needs
taste.

The `routing=0.0` row is the other kind of finding: asked a pure arithmetic question, the
supervisor sent it to the writer as well. Harmless here, but it is a wasted call on every
such request — the sort of thing nobody notices without measuring.

---

## 3. Behind a service

`api.py` puts three endpoints in front of all of it:

```
GET  /health      is it up
POST /run         run one task    → answer, path taken, turns
POST /evaluate    run every case  → per-case scores, averages
```

This is the step people skip. Once the agents are reachable over HTTP, the front end has
no idea they are agents, and anything else — a script, a scheduled job, another service —
can use them without importing a line of Python.

Note that `/evaluate` retries when the model provider pushes back. An evaluation fires far
more requests than normal use, so rate limits show up there first.

---

## 4. A face

`streamlit_app.py` has two tabs, mirroring the two ideas: **watch it work** shows the path
the team took for one task, and **measure it** runs the whole suite and shows the scorecard.

It holds no logic at all — it only calls the API. That separation is deliberate: you can
replace this UI entirely without touching the agents.

---

## Running it

Everything is already covered by the repo's environment:

```bash
uv pip install -e ".[fullstack,apps]"
```

Then, from this folder, in two terminals:

```bash
# terminal 1 — the service
uvicorn app.api:api --reload

# terminal 2 — the UI
streamlit run app/streamlit_app.py
```

The UI is at `http://localhost:8501`, the API docs at `http://localhost:8000/docs`.

To skip the UI entirely:

```bash
curl -X POST localhost:8000/run -H "Content-Type: application/json" \
     -d '{"task": "What is 15% of 80?"}'

curl -X POST localhost:8000/evaluate
```

The model comes from the repo's shared `helpers.get_llm()`, so whichever provider is
configured on your machine is the one that runs.

---

## Where to take it

- **Add a specialist.** Write one function, add one node. The supervisor prompt is the only
  other thing that changes — nothing else in the file knows the difference.
- **Add a test case.** One entry in `dataset.py`. Every score applies to it automatically.
- **Make a specialist a real agent.** Each one here is a single model call. Swap in
  `create_agent()` with tools and the rest of the system is unaffected.
- **Track scores over time.** Right now the scorecard vanishes when you close the tab.
  Saving each run is what turns evaluation into a safety net against getting worse.
