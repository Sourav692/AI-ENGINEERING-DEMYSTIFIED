# Content Boundary Rules

These rules are the acceptance criteria for the split.

## 1. One primary owner per concept

Every concept is introduced and explained in exactly one repository. Framework-specific implementations may appear later, but they must link back to the owner and avoid reteaching the theory.

Examples:

- Tool calling and the agent loop are introduced in repository 06, not repository 03 or 04.
- Multi-agent orchestration is introduced in repository 08, not repository 06 or 07.
- Corrective, adaptive, self, graph, and other agentic RAG patterns are introduced in repository 09, not repository 05.
- Tracing, cost controls, deployment, security, and production testing are introduced in repository 13, not in framework-fundamentals repositories.

## 2. Earlier repositories cannot preview later topics

An earlier README may say what comes next, but its lessons, labs, and required exercises cannot explain or implement the later topic.

Allowed:

> Repository 05 ends with a standard retrieval pipeline and links to repository 09 for agentic RAG.

Not allowed:

> Repository 05 contains a “simple agentic RAG” notebook as an optional bonus.

## 3. Later repositories may recap, but not duplicate

A later repository may include a short prerequisite check or a compact recap limited to what is necessary for the new lesson. Use links and a five-to-ten-minute refresher, not a copied notebook.

## 4. Knowledge dependency is allowed; code dependency is not

Repository `NN` may state that `NN-1` is a prerequisite. It may not import helpers, datasets, editable packages, notebooks, Git submodules, or environment files from another course repository.

Each repository must work after this test:

```bash
git clone <only-this-repository>
cd <repository>
cp .env.example .env
uv sync
uv run pytest
uv run jupyter lab
```

Commands may vary for JavaScript or app-heavy repositories, but the single-clone rule does not.

## 5. Support assets may be duplicated; teaching content may not

Small datasets, helper modules, diagrams, and fixtures can be copied when two repositories need them. The copied asset must include provenance and a content hash in `THIRD_PARTY_NOTICES.md` or `docs/data-sources.md`.

Do not duplicate explanatory notebooks or chapters to achieve self-containment.

## 6. Examples cannot silently broaden scope

Classify an item by the concept it teaches, not by the framework imported or its current folder.

- A LangGraph notebook whose learning objective is ReAct belongs to agent fundamentals.
- A routing notebook whose main example is agentic RAG belongs to advanced RAG unless it can be rewritten with a neutral routing example.
- A CrewAI application belongs to alternative frameworks when it teaches CrewAI; a polished deployable CrewAI product belongs to a project repository.
- A notebook about LangSmith belongs to production and observability even if it currently sits in LangChain fundamentals.

## 7. The projects repository applies previous concepts

Repository 14 may combine earlier topics because its purpose is integration, not first instruction. Every project README must list prerequisites and point to the owning concept repositories.

## 8. Boundary audit required before release

For every repository, maintain `docs/content-inventory.csv` with these columns:

```text
path,learning_objective,primary_concept,owner_repo,status,notes
```

Release is blocked when an item in an earlier repository has an `owner_repo` with a higher sequence number.
