# Migration Plan

The split should be performed as a controlled content migration, not sixteen simultaneous folder copies.

## Phase 0 — Freeze and inventory

1. Finish or shelve unrelated work in the monorepo.
2. Tag the source state, for example `pre-multirepo-split-2026-09`.
3. Generate a complete file inventory including size, hash, notebook title, imports, relative data paths, and current Git status.
4. Create `docs/content-inventory.csv` for every destination using the boundary rules.
5. Mark every source item as `move`, `rewrite`, `split`, `support-asset`, `legacy-only`, or `delete-generated`.
6. Scan for secrets before copying any history or file.

**Exit criterion:** every tracked source file has exactly one destination or an explicit legacy-only reason.

## Phase 1 — Create the repository template

Create one template containing the standard README contract, Python tooling, notebook/link checks, pre-commit hooks, issue templates, and CI. Instantiate all repositories from the same template, then customize dependencies per repository.

Do not create a shared runtime package. Template files may be copied; execution must remain local to each repository.

**Exit criterion:** an empty generated repository passes formatting, lint, tests, link checks, and notebook structure checks.

## Phase 2 — Resolve boundary violations in the source map

Before extraction, decide each mixed-content case:

1. LangChain agents/memory/LangSmith currently inside fundamentals.
2. LangGraph ReAct/tool-use and agentic-RAG routing examples currently inside fundamentals.
3. Agent fundamentals containing multi-agent and advanced harness content.
4. Foundational RAG containing agentic RAG.
5. Advanced RAG anthologies that repeat foundational RAG and evaluation.
6. Alternative-framework applications that are actually standalone products.
7. Production lessons embedded inside projects.

Prefer moving the whole lesson when its learning objective is clear. Rewrite only when one notebook genuinely teaches two owner concepts.

**Exit criterion:** no earlier destination contains primary content owned by a later destination.

## Phase 3 — Extract repositories 01-05

Extract foundations through standard RAG first. These establish the conventions and reveal broken paths early.

For each repository:

1. Use `git filter-repo` (or an equivalent history-preserving method) with explicit source paths.
2. Normalize the destination layout without changing notebook semantics unnecessarily.
3. Copy only required helpers/assets.
4. Create a repository-specific `pyproject.toml`, lockfile, and `.env.example`.
5. Repair relative paths.
6. Run notebook static checks, offline smoke tests, and selected live tests.
7. Add Previous/Next links and explicit out-of-scope statements.

**Exit criterion:** a clean clone of each repository works without the monorepo or sibling repositories.

## Phase 4 — Extract repositories 06-13

Repeat the same process for agents through production. Do not begin by copying entire phase folders: apply the relocation decisions from Phase 2.

Important verification:

- repository 06 contains only single-agent fundamentals;
- repository 07 focuses on SDK-specific fundamentals;
- repository 08 owns memory and multi-agent systems;
- repository 09 contains only advanced/agentic RAG;
- repository 10 owns protocol composition;
- repository 11 applies prior patterns through other frameworks;
- repository 12 focuses on coding tools;
- repository 13 owns all cross-cutting production concerns.

## Phase 5 — Extract all projects into repository 14

Move each project into the appropriate numbered group as an independent subproject with its own setup and tests. Standardize only navigation and quality gates at the repository root.

For each application:

1. remove embedded secrets, caches, generated output, and obsolete lockfiles;
2. verify its own environment rather than forcing a repository-wide dependency union;
3. add an architecture summary and prerequisite links;
4. add one offline test or deterministic demo;
5. mark external services and expected cost clearly;
6. verify Docker, Databricks, frontend, and deployment instructions where present.

If any project grows into a maintained product, later promote it to its own repository without changing the 01-14 curriculum sequence. Use a product name rather than inserting a new course number.

## Phase 6 — Navigation and redirects

1. Publish the ordered table in the GitHub organization/profile README.
2. Add Previous/Next links to every repository.
3. Replace the monorepo README with a migration notice and the 14-repository table.
4. Keep the monorepo read-only for at least one release cycle.
5. Add a path-redirect table from every old top-level path to its new repository.
6. Update external documentation and bookmarks where practical.

## Phase 7 — Final verification

Run these checks for every repository from a clean clone:

- install succeeds using documented commands;
- no dependency on a sibling repository or old monorepo path;
- no secrets or local environment files;
- all notebook data paths resolve;
- all internal links resolve;
- offline smoke tests pass;
- representative notebooks execute when credentials are available;
- repository boundary audit passes;
- Previous/Next navigation is correct;
- license and third-party attribution are present.

Compare the final destination inventories with the frozen source inventory. The count need not match when generated files and deliberate legacy material are excluded, but every difference must have a recorded reason.

## Suggested rollout order

Pilot with repositories 03, 04, and 05. They expose the hardest boundaries and the largest path/dependency issues without requiring the full project migration. Once their template and checks are stable, migrate 01-02, then 06-13, then the grouped projects repository 14.

## Rollback strategy

The source monorepo remains tagged and read-only. New repositories are additive until verification completes. Do not delete source content or rewrite the monorepo's default branch during extraction. Archive the monorepo only after all inventory rows are reconciled and links have been published.
