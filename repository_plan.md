# Repository Split Plan

**Status:** proposal, awaiting execution approval
**Author:** drafted 2026-09-19
**Current state:** one repo, 3,182 tracked files, 607 notebooks, 436 MB tracked content, 510 MB `.git`, 115 commits (2026-08-16 → 2026-09-19)

---

## 1. Decision summary

| Decision | Choice | Rationale |
|---|---|---|
| Split axis | **5 content repos by artifact type** | Each repo gets one purpose and one audience. Splitting by learning stage would cut the roadmap's sequencing in half; splitting by domain would need 11 repos and break cross-phase links in 6 places. |
| Visibility | **All repos private initially** | 15/16/17 and `tutorials/` contain purchased vendor material. Start private, flip individual repos public after a licence audit. |
| History | **`git filter-repo` per repo** | 115 commits — extraction takes seconds and each repo lands with real, attributable history. |
| Shared code | **`helpers` published to PyPI** | `from helpers import get_llm` keeps working across 69 files in 9 phase folders without vendoring or submodules. |

### One deviation from the option you picked, flagged

You chose the 5-repo layout where `helpers/` lives inside the roadmap repo, *and* chose to publish it to PyPI. Those pull against each other: a release-tagged package inside a 120 MB content repo means every `v0.2.1` tag sits in the same history as notebook edits, and CI has to path-filter every push to decide whether to publish.

**Recommendation: a 6th, tiny repo — `ai-engineering-helpers`.** ~2 files, its own release cadence, its own CI. If you'd rather hold at five, the fallback is a `packages/helpers/` subdirectory in the roadmap repo with a tag-triggered publish workflow — it works, it's just noisier. Everything below assumes the 6-repo shape; §9 lists what changes if you overrule it.

### What splitting does and does not fix

Be clear-eyed about this, because it changes what "done" looks like.

**It does fix:** licence exposure (purchased material can never be accidentally pushed public), clone time for someone who only wants the curriculum, CI scoping, and the cognitive load of a 24-entry root listing.

**It does not fix your actual weight.** 436 MB tracked is ~90% binary assets — a 15 MB medical textbook PDF, a 14 MB pptx, arXiv papers, course slide exports. After the split, the *sum* is unchanged; it's just distributed. §7 handles that separately, and it is the higher-leverage change of the two. The 997 MB in `03_LangGraph_Fundamentals` and 929 MB in `site/` are an untracked `.venv` and `node_modules` — already ignored, not part of any of this.

### The rule the split must not break

This repo's cardinal organizing rule is **one topic, one phase** — it was reintroduced-duplication that forced the last restructure. The split below is safe against that rule because it cuts along *artifact type*, never through a topic:

- No topic is split across two repos. RAG stays whole in the roadmap repo (Phase 4 + Phase 8); agents stay whole (Phase 5 + 7).
- `13_Projects` is not a topic — it is the *application* of many topics, which is why it's a clean cut.
- Interview prep is not a topic either; it's a different artifact class (drills, cram sheets, scorecards) derived from the same topics.

---

## 2. Target topology

| # | Repo | Visibility | Size | Contents | Changes |
|---|---|---|---|---|---|
| 1 | `ai-engineering-roadmap` | private → public later | ~120 MB | Phases 00–12, the learning path | weekly |
| 2 | `ai-engineering-projects` | private → public later | ~70 MB | Phase 13 + standalone full-stack apps | per project |
| 3 | `ai-engineering-interview-prep` | **private, permanently** | ~55 MB | Phases 14–17, `tutorials/` | daily while prepping |
| 4 | `ai-engineering-site` | private → public later | ~2 MB | `site/` (Next.js/Vercel) + `docs/` | per deploy |
| 5 | `claude-ai-toolkit` | private → public later | ~0.5 MB | Generic Claude Code skills + plugins | rarely |
| 6 | `ai-engineering-helpers` | public (needs to be, for PyPI) | ~50 KB | The LLM/embedding factory package | rarely |

Naming is deliberate: four `ai-engineering-*` siblings read as one family in a repo list; `claude-ai-toolkit` is named off-family because it is tool-domain, not content-domain, and is the one most likely to be useful to strangers.

---

## 3. Path-by-path migration map

Every current top-level entry has exactly one destination. Nothing is orphaned.

| Current path | → Repo | Destination path | Note |
|---|---|---|---|
| `00_Theory_and_Foundations/` | roadmap | `00_Theory_and_Foundations/` | |
| `01_LangChain_Fundamentals/` | roadmap | `01_LangChain_Fundamentals/` | |
| `02. Prompt_and_Context_Engineering/` | roadmap | `02_Prompt_and_Context_Engineering/` | **rename** — drop the `". "`, it breaks shell globs and URLs |
| `03_LangGraph_Fundamentals/` | roadmap | same | drop the untracked `.venv` |
| `04_Retrieval_and_RAG/` | roadmap | same | incl. `shared_data/` |
| `05_AI_Agent_Fundamentals/` | roadmap | same | |
| `06_Agent_SDKs_First_Party/` | roadmap | same | scaffold only |
| `07_Advanced_Agentic_Systems/` | roadmap | same | incl. Deep Agents + its `CLAUDE.md` |
| `08_Advanced_RAG/` | roadmap | same | `building-adaptive-rag/` and `mcp_a2a_agentic_rag/` **stay here**, not in projects — they were deliberately placed RAG-first |
| `09_Agent_Protocols/` | roadmap | same | |
| `10_Alternative_Agent_Frameworks/` | roadmap | same | largest phase, 101 MB |
| `11_Claude_Code_and_AI_Coding_Tools/` | roadmap | same | scaffold only |
| `12_Production_and_Observability/` | roadmap | same | |
| `13_Projects/` | **projects** | `projects/<name>/` | flatten the numeric prefix; each project is top-level |
| `14_AI_Engineering_Handbook/` | **prep** | `handbook/` | |
| `15_FDE_Related_Preparation/` | **prep** | `fde/` | purchased material |
| `16_AI_Engineer_Interview_Preparation/` | **prep** | `ai-engineer/` | purchased material |
| `17_OpenAI_Applied_Engineer_Preparation/` | **prep** | `openai-applied/` | |
| `tutorials/` | **prep** | `playbooks/` | Cost & Latency cram sheets + drills |
| `site/` | **site** | `/` (repo root) | fixes the Vercel root-directory problem |
| `docs/` | **site** | `legacy-docs/` | static HTML microsite; fold into `site/` later |
| `helpers/` | **helpers** | `src/ai_engineering_helpers/` | published to PyPI |
| `archive/` | roadmap | `archive/` | frozen; never reorganized |
| `plugins/` | **toolkit** + roadmap | see §6.3 | `langchain-v1-migration` is roadmap-specific |
| `.claude/skills/` | **split** | see §6.3 | 11 skills, 3 destinations |
| `CLAUDE.md` | all | rewritten per repo | each repo needs its own |
| `NOTEBOOK_INDEX.md` | roadmap | same | curriculum ground truth |
| `RAG_CURRICULUM.md`, `THEORY_DOCS_INDEX.md` | roadmap | `docs/` | |
| `MCP_SERVERS.md`, `Reference_Links.md` | roadmap | `docs/` | |
| `README.md` | all | rewritten per repo | |
| `pyproject.toml`, `requirements*.txt` | roadmap + projects | per-repo, re-resolved | see §6.1 |
| `databricks.yml` | roadmap | same | |
| `LICENSE` | all | copied | check it permits the prep repo's contents |
| `tutorial_chapters.excalidraw` | prep | `playbooks/` | |
| `__builtins__.pyi` | — | **delete** | stray artifact, no references |

---

## 4. Repo 1 — `ai-engineering-roadmap`

**Purpose:** the 13-phase learning path. One topic per phase, framework variants as sibling tracks inside the phase that owns the topic.
**Audience:** you, and eventually anyone following the path.

```
ai-engineering-roadmap/
├── .github/workflows/
│   ├── lint.yml                 # ruff check . on push
│   └── notebook-hygiene.yml     # fail if any .ipynb carries outputs
├── .claude/
│   ├── skills/
│   │   ├── ai-roadmap-organizer/
│   │   ├── learning-tracker/
│   │   ├── notebook-folder-cleanup/
│   │   └── notebook-folder-cleanup-planner/
│   └── settings.json
├── plugins/langchain-v1-migration/
├── 00_Theory_and_Foundations/ … 12_Production_and_Observability/
├── 13_Projects/README.md        # STUB → points at the projects repo
├── archive/
├── docs/
│   ├── NOTEBOOK_INDEX.md        # ground truth for what exists
│   ├── RAG_CURRICULUM.md
│   ├── THEORY_DOCS_INDEX.md
│   ├── MCP_SERVERS.md
│   └── Reference_Links.md
├── scripts/fetch_shared_data.py # re-downloads arXiv PDFs instead of storing them
├── .gitignore  .pre-commit-config.yaml  CLAUDE.md  README.md  LICENSE
├── pyproject.toml               # depends on ai-engineering-helpers
├── requirements.txt  requirements.lock.txt
└── databricks.yml
```

**Notes**
- The `13_Projects/README.md` stub matters: the roadmap's last phase is capstones, and a learner who reaches Phase 12 needs a signpost, not a missing folder.
- `pyproject.toml` keeps the eleven extras (`providers`, `protocols`, `frameworks`, `retrieval`, `hf`, `databricks`, `eval`, `data`, `apps`, `dev`) minus `fullstack`, which follows the projects out.
- `pre-commit` + `nbstripout` must come across intact — committed notebook outputs have leaked absolute filesystem paths here before.
- `[tool.ruff] extend-exclude` currently hardcodes five JS frontend paths; **four of the five leave with the projects repo.** Prune it to the one that stays (`07_Advanced_Agentic_Systems/.../app/frontend`).

---

## 5. Repo 2 — `ai-engineering-projects`

**Purpose:** 12 standalone, runnable applications. Each is independently clonable, buildable and demoable — this is the repo a hiring manager is pointed at.
**Audience:** you, reviewers, interviewers.

```
ai-engineering-projects/
├── .github/workflows/ci.yml     # matrix over projects that declare a test target
├── projects/
│   ├── langgraph-fullstack-capstone/    # FastAPI + Angular + Postgres + tests
│   ├── langchain-microservices-capstone/
│   ├── rag-systems/                      # 7 applied RAG notebooks
│   ├── shopunow-agentic-rag/
│   ├── ai-powered-customer-support/
│   ├── candidate-interview-evaluation/
│   ├── medical-chatbot/
│   ├── pipecat-quickstart/
│   ├── realtime-source-code-analyzer/
│   ├── realtime-voice-rag-agent/
│   ├── holiday-management-agent/
│   └── resume-genie/
├── docs/PROJECT_INDEX.md        # one row per project: stack, status, run command, demo link
├── CLAUDE.md  README.md  LICENSE  .gitignore
└── (no root pyproject — each project owns its deps)
```

**The rule that makes this repo professional:** every directory under `projects/` must contain a `README.md` with *Problem → Architecture → Stack → Run → Demo*, a dependency manifest, and a `.env.example`. A project that can't be run from its own README in under five minutes is a liability in an interview, not an asset.

**Per-project dependencies, deliberately.** These apps have genuinely conflicting pins — CrewAI hard-pins `chromadb<1.2` and cannot share an environment with `langchain-chroma` 1.1. A root-level lock here would be a lie. One venv per project.

---

## 6. Repo 3 — `ai-engineering-interview-prep` *(private, permanently)*

**Purpose:** interview preparation material and everything derived from purchased sources.
**Audience:** you alone.

```
ai-engineering-interview-prep/
├── handbook/            # was 14_AI_Engineering_Handbook
├── fde/                 # was 15_FDE_Related_Preparation  ⚠ purchased
├── ai-engineer/         # was 16_AI_Engineer_Interview_Preparation  ⚠ purchased
├── openai-applied/      # was 17_OpenAI_Applied_Engineer_Preparation
├── playbooks/           # was tutorials/ — Cost & Latency cram sheets, drills  ⚠ derived
├── .claude/skills/
│   ├── fde-case-study-worksheet-v3/
│   ├── fde-tutorial-interview-format/
│   ├── interview-book-tutorial-builder/
│   └── notebook-interview-tutorial/
├── LICENSING.md         # ← non-negotiable, see below
├── CLAUDE.md  README.md  .gitignore
```

**`LICENSING.md` is required, not optional.** This repo contains third-party commercial material — the "Premium GenAI FDE Interview System", vendor course exports, Medium article PDFs. The file records, per directory: the source, whether it was purchased, and the redistribution terms. It exists so that "can I make this public?" is answerable in thirty seconds, six months from now, without re-deriving provenance from filenames.

**Hard guard against accidental publication.** Add a pre-push hook that refuses to push if `git remote get-url --push origin` resolves to a public repo. The cost of the mistake is asymmetric.

---

## 7. Repo 4 — `ai-engineering-site`

**Purpose:** the public-facing FDE interview-prep website (Next.js, Vercel) and the older static tutorial microsite.

```
ai-engineering-site/
├── src/  public/  scripts/  content/     # site/ contents promoted to root
├── legacy-docs/                          # was docs/ — static HTML chapters
├── .github/workflows/build.yml
├── next.config.ts  package.json  tsconfig.json  .gitignore  README.md  CLAUDE.md
```

**This split fixes a live bug.** Git-push deploys currently fail because the Vercel project's root directory is `.` while the app lives in `site/`; only CLI deploys from inside `site/` work. Promoting `site/` to the repo root makes root `.` correct and restores push-to-deploy. **Action required after the split:** reconnect the Vercel project to the new repo and reset root directory to `.`.

`site/content/` must stay committed — the build reads from it.

---

## 8. Repo 5 — `claude-ai-toolkit`

**Purpose:** reusable Claude Code tooling that is not specific to any one content repo. The most plausibly useful-to-others repo you own.

```
claude-ai-toolkit/
├── skills/
│   ├── format-notebook/
│   ├── git-smart-commit/
│   └── virtual-env-setup/
├── plugins/                    # future home for generic plugins
├── .claude-plugin/marketplace.json
├── README.md                   # install instructions per skill
└── LICENSE
```

### 8.3 How the 11 skills and 1 plugin divide

This is the fiddliest part of the split, so it's enumerated rather than left to judgement:

| Skill | → | Why |
|---|---|---|
| `ai-roadmap-organizer` | roadmap | Encodes the 13-phase rule; meaningless elsewhere |
| `learning-tracker` | roadmap | Tracks progress through *this* curriculum |
| `notebook-folder-cleanup` | roadmap | Operates on the phase folders |
| `notebook-folder-cleanup-planner` | roadmap | Paired with the above |
| `fde-case-study-worksheet-v3` | prep | Reads `15_FDE.../Version_2/` |
| `fde-tutorial-interview-format` | prep | FDE chapter series |
| `interview-book-tutorial-builder` | prep | Sourced from a specific book |
| `notebook-interview-tutorial` | prep | Produces interview prep from notebooks |
| `format-notebook` | **toolkit** | Generic notebook formatting |
| `git-smart-commit` | **toolkit** | Generic — any Python/ML repo |
| `virtual-env-setup` | **toolkit** | Generic uv/venv setup |
| `plugins/langchain-v1-migration` | roadmap | Its five skills reference repo-relative script paths |

`notebook-interview-tutorial` reads notebooks (roadmap) and writes prep material (prep). It goes to **prep** — its output is the deliverable, and pointing it at a sibling clone is trivial. Note this in its SKILL.md.

---

## 9. Repo 6 — `ai-engineering-helpers`

```
ai-engineering-helpers/
├── src/ai_engineering_helpers/
│   ├── __init__.py          # exports get_llm, get_embeddings
│   ├── llm.py  embeddings.py  platform.py
├── tests/test_factory.py
├── .github/workflows/publish.yml   # tag v* → build → PyPI via trusted publishing
├── pyproject.toml  README.md  LICENSE
```

**Import compatibility is the whole point.** 69 files across 9 phase folders do `from helpers import get_llm`. Keep that working by shipping a `helpers` shim module alongside the real package, so `from helpers import get_llm` resolves after `pip install ai-engineering-helpers` without editing a single notebook.

Preserve the documented behaviour exactly: keyword-only args; platform-aware defaults (Windows → Groq `openai/gpt-oss-120b` for LLM + OpenAI `text-embedding-3-small` for embeddings; macOS → Databricks `databricks-claude-opus-4-6` / `databricks-gte-large-en`); and `get_databricks_llm`'s own standalone default of `databricks-gpt-5-2`, which is distinct from the macOS override applied by `get_llm()`. That distinction is a real trap — encode it in a test.

**Verify the PyPI name is free** before committing to it; fall back to a namespaced variant if taken.

*If you overrule the 6th repo:* put this at `packages/helpers/` in the roadmap repo, add `paths: ['packages/helpers/**']` to the publish workflow trigger, and use `v-helpers-*` tags so package releases don't collide with content tags.

---

## 10. Cross-cutting concerns

### 10.1 Binary assets — the change worth making regardless

Do this **during** the split, while you're rewriting history anyway. It is cheaper now than ever again.

| Class | Examples | Action |
|---|---|---|
| Re-downloadable papers | `04_.../shared_data/*.pdf` (attention, GPT-3, RAG, ViT, ResNet), `08_.../research_papers/*.pdf` | **Drop from git.** Ship `scripts/fetch_shared_data.py` with the arXiv IDs. ~45 MB saved. |
| Purchased course exports | Beautiful.ai slide PDFs, vendor PDFs | Keep — private repos, and they're not re-downloadable. |
| Project datasets | `Medical_book.pdf` (15 MB) | Keep, but **Git LFS** in the projects repo. |
| Presentations | `ShopUNow_...pptx` (14 MB) | LFS. |
| Oversized images | `substack_image.png` (10.5 MB) | Compress in place — it's a screenshot. |

Be aware of the LFS quota: GitHub gives 1 GB storage / 1 GB monthly bandwidth free per account. Only the projects repo should use it, and only for files >5 MB.

### 10.2 Cross-repo navigation — the real cost of splitting

Today, `NOTEBOOK_INDEX.md` can link anything to anything. After the split it can't. Mitigations, in order of value:

1. **Sibling-clone convention.** Document that all repos are cloned as siblings under `~/Github_Repos/`, so `../ai-engineering-projects/...` resolves for a human and for Claude Code.
2. **A `## Related repositories` block** in every README and every `CLAUDE.md`, listing the other five with one line each.
3. **Keep `NOTEBOOK_INDEX.md` authoritative for the roadmap only**, and add `PROJECT_INDEX.md` (projects) and `PREP_INDEX.md` (prep) as peers.
4. *(Optional)* an umbrella `ai-engineering-demystified` repo with the six as git submodules. Gives one `git clone --recursive` entry point. Adds submodule-pointer maintenance — only worth it if you want a single canonical clone.

### 10.3 The stale `CLAUDE.md` problem

The current `CLAUDE.md` documents a 13-phase repo. On disk there are **18 numbered phases (00–17)** plus `tutorials/` and `site/` — phases 14–17 and several tracks postdate it. **Do not copy it into six repos as-is; you'd propagate the drift six times.** Each repo gets a freshly written `CLAUDE.md` covering only its own contents, and the roadmap's copy gets reconciled against `NOTEBOOK_INDEX.md` as part of the migration.

### 10.4 Dependencies after the split

| Repo | Strategy |
|---|---|
| roadmap | One `pyproject.toml`, ten extras, `requirements.txt` pinned mirror + `requirements.lock.txt`. Depends on `ai-engineering-helpers`. |
| projects | No root manifest. One venv per project, each with its own manifest. |
| prep | Minimal — `jupyter`, `pypdf`. Mostly markdown and HTML. |
| site | `package.json` only. |
| toolkit | None. |
| helpers | `pyproject.toml` with the provider SDKs as optional extras. |

Re-resolve the roadmap lock after the split — dropping `fullstack` removes a chunk of the transitive tree.

---

## 11. Migration runbook

Run in order. Each step is independently verifiable; stop and check before continuing.

### Step 0 — Safety net
```bash
cd ~/Github_Repos
git -C AI-ENGINEERING-DEMYSTIFIED status          # must be clean
cp -R AI-ENGINEERING-DEMYSTIFIED AI-ENG-BACKUP-$(date +%Y%m%d)   # untracked files too
brew install git-filter-repo                      # or: uv tool install git-filter-repo
```
Keep the backup until every new repo has been pushed **and** verified. Do not skip it — `filter-repo` rewrites history irreversibly.

### Step 1 — Create the six empty private repos
```bash
for r in roadmap projects interview-prep site helpers; do
  gh repo create "ai-engineering-$r" --private --description "..." ; done
gh repo create claude-ai-toolkit --private
```

### Step 2 — Extract each repo with its history
Repeat this block per repo, changing only the `--path` list:
```bash
git clone --no-local AI-ENGINEERING-DEMYSTIFIED /tmp/split-roadmap
cd /tmp/split-roadmap
git filter-repo \
  --path 00_Theory_and_Foundations --path 01_LangChain_Fundamentals \
  --path "02. Prompt_and_Context_Engineering" --path 03_LangGraph_Fundamentals \
  --path 04_Retrieval_and_RAG --path 05_AI_Agent_Fundamentals \
  --path 06_Agent_SDKs_First_Party --path 07_Advanced_Agentic_Systems \
  --path 08_Advanced_RAG --path 09_Agent_Protocols \
  --path 10_Alternative_Agent_Frameworks --path 11_Claude_Code_and_AI_Coding_Tools \
  --path 12_Production_and_Observability --path archive \
  --path NOTEBOOK_INDEX.md --path RAG_CURRICULUM.md --path THEORY_DOCS_INDEX.md \
  --path pyproject.toml --path requirements.txt --path requirements.lock.txt \
  --path databricks.yml --path LICENSE \
  --path-rename "02. Prompt_and_Context_Engineering:02_Prompt_and_Context_Engineering"
```
`--path-rename` performs the folder renames from §3 *across all history*, so old commits stay navigable at the new path. Use it for the prep repo's four renames and the projects flattening too.

`--invert-paths` is the tool for dropping the re-downloadable PDFs in the same pass.

### Step 3 — Per-repo setup
For each extracted repo: write `README.md` and `CLAUDE.md`, add `.gitignore`, `.pre-commit-config.yaml` and CI, move the skills per §8.3, then `git remote add origin` and push.

### Step 4 — `helpers` first, everything else after
Publish `ai-engineering-helpers` to PyPI (or TestPyPI first) **before** the roadmap repo's lockfile is regenerated, so the dependency resolves.

### Step 5 — Verify before decommissioning
- [ ] `git log --oneline | wc -l` in each repo — non-zero, plausible
- [ ] Open three notebooks per repo — relative data paths still resolve
- [ ] `pip install ai-engineering-helpers && python -c "from helpers import get_llm"` in a clean venv
- [ ] `ruff check .` passes in roadmap
- [ ] `pre-commit run --all-files` strips outputs as expected
- [ ] One project builds end to end (`docker compose up` on the LangGraph capstone)
- [ ] Site builds and deploys from a git push with root directory `.`
- [ ] No file from `fde/`, `ai-engineer/` or `playbooks/` appears in any public repo: `git log --all --name-only | grep -iE "fde|premium"` in each public repo returns nothing
- [ ] File count reconciles: sum across six repos ≈ 3,182 minus deliberate drops

### Step 6 — Decommission
Rename this repo to `AI-ENGINEERING-DEMYSTIFIED-archive`, archive it on GitHub (read-only), and leave a `README.md` pointing at the six successors. **Do not delete it** — it is the provenance record for every filter-repo extraction.

---

## 12. What breaks, and the fix

| Breaks | Where | Fix |
|---|---|---|
| `from helpers import get_llm` | 69 files, 9 phase folders | PyPI package + `helpers` shim module — no notebook edits |
| `pyproject.toml` ruff excludes | 4 of 5 JS paths leave | Prune the list in the roadmap repo |
| Plugin marketplace path | `.claude-plugin/marketplace.json` → `plugins/langchain-v1-migration` | Both move to roadmap together; path unchanged |
| Cross-phase relative links | 7 found, incl. `../../12_Production_and_Observability/...` | 5 stay intra-repo; 2 point into prep — rewrite as repo-relative notes |
| `04_.../shared_data/` relative paths | Already fragile pre-split (`../../data/` style, never re-verified) | Fix during the move, or leave known-broken and document it — don't silently half-fix |
| Vercel deploy | Project root `.` vs app in `site/` | Promoting `site/` to root fixes it; reconnect the project |
| `learning-tracker` state | Local gitignored checklist | Migrates with the roadmap repo; verify it survives |
| Deep Agents `app/` | Has thrown "device busy" on 3 prior restructures | Expect it. Drain contents one level at a time, then remove the shell |
| `.env` at root | Used by every phase | Each repo needs its own; write `.env.example` per repo |

---

## 13. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Purchased material reaches a public repo | **High** | All repos start private; `LICENSING.md`; pre-push hook; Step 5 grep check |
| `filter-repo` run with a wrong path list | High | Always operate on `/tmp` clones, never the original; backup from Step 0 |
| Split stalls half-done, content in two places | Medium | Execute in one sitting; don't push to old and new concurrently |
| Notebook data paths break silently | Medium | Spot-check three notebooks per repo before decommissioning |
| Six `CLAUDE.md` files drift apart | Medium | Each covers only its own repo — smaller surface drifts less than one 18-phase file already has |
| PyPI name unavailable | Low | Check first; namespaced fallback |

---

## 14. Sequencing

Don't do this in one night. The split is reversible until Step 6.

| Wave | Do | Why first |
|---|---|---|
| 1 | `ai-engineering-helpers` → PyPI | Everything else depends on it |
| 2 | `claude-ai-toolkit` | Smallest, lowest risk — proves the filter-repo procedure on something you can afford to redo |
| 3 | `ai-engineering-site` | Self-contained; fixes the live deploy bug |
| 4 | `ai-engineering-interview-prep` | Highest licence risk — get it out of the shared repo early |
| 5 | `ai-engineering-projects` | Needs per-project READMEs and LFS setup — the most actual work |
| 6 | `ai-engineering-roadmap` | Largest; benefits from every lesson learned above |
| 7 | Archive the original | Only after Step 5 passes for all six |

---

## 15. Open questions

1. **PyPI name** — is `ai-engineering-helpers` free? Check before Wave 1.
2. **Does `LICENSE` cover the prep repo?** A permissive licence on a repo containing purchased vendor PDFs is a contradiction. The prep repo likely wants *no* licence file plus an explicit "all rights reserved, third-party material included" note.
3. **Umbrella submodule repo** — yes or no (§10.2 item 4)?
4. **`docs/` microsite** — fold into the Next.js site as routes, or keep as static `legacy-docs/`?
5. **`14_AI_Engineering_Handbook`** — it's your own writing. Does it belong in the private prep repo, or is it a public portfolio piece in its own right?
