# Standard Repository Layout

Every repository should use the same predictable shape, omitting empty directories.

```text
ai-engineering-demystified-NN-topic-name/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── .gitignore
├── .env.example
├── .pre-commit-config.yaml
├── pyproject.toml
├── uv.lock
├── docs/
│   ├── learning-path.md
│   ├── prerequisites.md
│   ├── setup.md
│   ├── curriculum-map.md
│   ├── content-inventory.csv
│   └── data-sources.md
├── modules/
│   ├── 01_topic/
│   │   ├── README.md
│   │   ├── notebooks/
│   │   ├── exercises/
│   │   └── assets/
│   └── 02_topic/
├── src/
│   └── ai_engineering_demystified_<nn>/
├── tests/
├── scripts/
│   ├── check_notebooks.py
│   ├── check_links.py
│   └── smoke_test.py
├── data/
│   ├── README.md
│   └── sample/
└── solutions/
    └── README.md
```

## README contract

Each README should contain, in this order:

1. Repository number and title.
2. One-sentence scope statement.
3. “You are here” learning-path strip with Previous and Next links.
4. Prerequisites stated as knowledge, not cross-repo imports.
5. Learning outcomes.
6. Ordered module table.
7. Setup and a verified quick start.
8. Required environment variables.
9. What is deliberately out of scope, naming the later owner.
10. License and source acknowledgements.

## Self-contained checklist

Each repository must have:

- one supported Python version;
- pinned direct and transitive dependencies (`pyproject.toml` plus `uv.lock`);
- `.env.example` containing names only, never secrets;
- local helpers under `src/` rather than a shared cross-repository package;
- local sample data small enough to clone, or a reproducible download script with checksums;
- notebooks using paths relative to the repository root;
- at least one offline smoke test that does not require paid API keys;
- optional live tests marked separately;
- no references such as `../other-repo`, an absolute workstation path, or the old monorepo root;
- no committed `.venv`, caches, generated Databricks bundle state, telemetry, or temporary agent output.

## Numbering inside a repository

Use two-digit ordering consistently:

```text
modules/01_intro/
modules/02_core_mechanics/
modules/03_guided_lab/
modules/04_assessment/
```

Notebook filenames should also be ordered within the module. Repository sequence numbers never replace module numbers; both communicate a different level of order.

## Dependency policy

- Keep framework extras local to the repository that uses them.
- Do not maintain one global `requirements.txt` for all repositories.
- Use dependency groups such as `dev`, `notebooks`, `databricks`, or `app` when a repository has optional surfaces.
- A framework upgrade should be independently testable in its owning repository.
- Databricks examples may include `databricks.yml`, but only in repositories that contain deployable Databricks assets.

## Projects repository variation

Repository 14 contains all 18 independent applications, arranged in three ordered groups. Use this variation:

```text
projects/
├── 01_foundational_projects/
│   ├── README.md
│   ├── 01_project_name/
│   │   ├── README.md
│   │   ├── pyproject.toml
│   │   ├── .env.example
│   │   ├── src/
│   │   └── tests/
│   └── 02_project_name/
├── 02_retrieval_agent_projects/
│   ├── README.md
│   └── 01_project_name/
└── 03_enterprise_realtime_capstones/
    ├── README.md
    └── 01_project_name/
```

Every project remains independently installable. The repository root contains navigation and aggregate checks, not a single environment that pretends all applications share compatible dependencies.
