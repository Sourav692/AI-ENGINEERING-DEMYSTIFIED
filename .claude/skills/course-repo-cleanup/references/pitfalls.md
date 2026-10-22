# Pitfalls and how to avoid them

Collected from full cleanups of `ai-engineering-demystified-06-agent-fundamentals` (14 modules, ≈85 notebooks) and `ai-engineering-demystified-08-advanced-agent-systems` (10 modules, 58 → 53 notebooks; modules 06–10 done without executing anything). Read the section for the step you are on.

## Contents
1. Demos that run but prove nothing
2. LLM judges, gates and loops
3. Consolidation and references
4. Running notebooks
5. Providers, credentials and cost
6. LangChain / LangGraph specifics
7. Git, PRs and shared working trees
8. Security: model-written SQL, queries and code
9. When the user runs the notebooks (no-execution mode)

## 1. Demos that run but prove nothing
"Ran clean" is necessary, not sufficient. The most common defect found was a notebook that
executes without error while its output contradicts (or fails to show) what the prose claims.
- **Read every printed output** after a run and check it against the notebook's claims.
- **Make the example produce the failure being taught.** A reflection demo whose first draft is already optimal, a verification demo whose baseline has no errors, a problem the model has memorised (wolf/goat/cabbage) — none of them can show the technique helping. Pick inputs the model actually gets wrong, graded in code.
- **Pick demo inputs by sampling** (~10–20 runs with the exact notebook prompt): a question's difficulty for a model is not stable, and one lucky run is not a demo.
- **"A beats B" claims need ground truth in code** — a known list, brute force, hidden tests — measured over a few samples, not an LLM score or narrative. When the measured result is weaker than the prose, change the prose.
- **Timing and ordering claims need measurement**: print wall time; verify ordering with a timed stub graph. (LangGraph reducers keep `Send` order; `stream_mode="updates"` shows finish order.)
- **"The expected name is in the answer" is too weak** — an answer listing six candidates passes. Require it to be the first known entity mentioned, or parse the answer.
- **Agents answering "latest"/"recent" questions need today's date** in the system prompt, or they search for stale periods.
- **Check the scoring and ground truth themselves**: substring scoring against a one-letter answer is always true; an off-by-one expected answer silently flips accuracy.
- **Remove hint comments** (`# BUG:`) from anything an agent reads, or the agent fixes bugs without using its tools.
- **Early stops can trivialise a demo**: adding a stop condition to a loop may make it end after round 1 with a lenient model; tighten the critic so the loop is still visible.
- **Steps the model may skip need a design that holds**: an "or say 'not available'" escape clause lets an agent skip its tool — force the first step (`bind_tools(..., tool_choice=<name>)`) or move the step into a graph node, and give the prompt one concrete example call.
- **Call-count claims are measurable**: pass a counter (`BaseCallbackHandler.on_chat_model_start`) via `callbacks=[counter]` and print expected (shown as arithmetic) vs measured with a code-computed ✅.
- **Entity pickers drift to an inferred entity**; "use the entity the question names explicitly" took one from 2/8 to 8/8.
- **Memory-tier demos (MemGPT style) need an explicit core-memory policy** in the prompt and tool docstring, or the model puts everything in core memory and archival recall is never exercised.

## 2. LLM judges, gates and loops
- **Verify both outcomes** of every gate/router/vote/judge over several samples before the full run. Keyword gates on LLM text leak.
- **Judges: one field per criterion**, code-checkable criteria (length, format, counts) checked in code, verdict computed in code. Better still: have the judge *copy the evidence* (or `none`) and let code decide — yes/no questions get answered from the task text, not the answer.
- **Numeric hints anchor small models** ("2 sections, or 5+" → always 5). Describe what drives the number; forbid padding sections.
- **Retry/regenerate loops need temperature > 0**; many factories default to 0, making every retry identical.
- **Refine loops pass the previous draft *and* the feedback** (feedback alone makes the generator start over), and **cap iterations in state**, enforced by the router.
- **In LangGraph**, an LLM gate is a node that writes its verdict to state plus a pure routing function — never an LLM call inside the conditional-edge function.
- **Make the swappable part an argument** of the graph builder (worker, reviewer, evaluator) so a stub can prove edge cases (caps, anti-patterns, failure paths) with zero LLM calls.
- **Scripted fake models** prove agent graphs with zero API calls: subclass `GenericFakeChatModel` with `bind_tools` returning `self`; one shared message iterator serves every agent in call order.
- **Hand-rolled JSON/text tool loops must feed wrong-shaped replies back** ("Unrecognised step …", `ERROR:` observations): gpt-4o-mini answers `{"action": "<tool>", …}`, and a loop that ignores unknown shapes ends silently at max steps while the notebook "runs clean".
- **Structured output via tool schemas**: use strict mode (`bind_tools(..., strict=True)` or the provider's equivalent) or small models drop required fields.
- **Cap judge output** (`max_tokens`); retry only length-limit errors, re-raise the rest.
- **Search/planning environments apply moves in code** — never trust LLM arithmetic for state transitions.
- **"No data" must not look like "safe"**: return `None` and escalate.

## 3. Consolidation and references
- **Headings mislead** — read the code; graph edges decide what a notebook teaches. Two notebooks that differ by one edge (`tools → END` vs `tools → agent`) are a valid pair; three with the same loop are not.
- **Cross-module duplicates count too**: deleting a notebook fully covered in another module is valid; record `deleted: covered by <file>` in any source→target inventory.
- **A redundant notebook can fill a gap** the module promises but never shows, instead of being deleted.
- **Build scripts must be re-runnable**: restore the source notebook from `HEAD` before each rebuild, or the second run reads its own output. `git mv` first, then write rebuilt content over the moved file, so history follows.
- **Exact-count replacements** when editing notebook JSON: assert the number of matches — guessed counts are often wrong.
- **Stale-reference search covers every tracked text file** (`git ls-files`), including CSV inventories and docs that *describe behaviour* ("the agent never runs code", "measured results") — not only file names. Old numbering schemes ("Notebook 6.2") sit next to file names in docs.
- **CSV inventories**: edit only through a CSV library (quoting!); hand-written rows with commas break the column count. Keep the file's line endings (`csv.writer` writes `\r\n` by default; never switch the terminator) or the diff covers the whole file.
- **Merging notebooks**: nbformat ≥ 4.5 cells carry ids, so a merge duplicates them — give duplicates fresh ids (`nbformat.corpus.words.generate_corpus_id()`); 4.4 notebooks have none (`c.pop("id", None)`). `nbformat.v4.new_notebook(cells=…)` silently rewrites duplicates — check plain cell lists.
- **Renumbering**: map bare numbers ("notebook 04's") in one combined regex pass — sequential passes map some twice. Audits and briefs keep the old numbers; give later workers an old → new map.
- **Link-only fixes in notebooks you aren't rebuilding**: edit the working-copy JSON — rebuilding from `git show BASE:` wipes their local outputs.
- **Never drop an existing guard** (a regex filter, a refusal check) during a rewrite without a replacement at least as strict.
- **`uv remove` leaves the dependency's inline `# comment`** dangling in `pyproject.toml`; diff it after every `uv add/remove`.
- **`%%writefile` must be a cell's first line** — the banner comment goes after it.
- **Scan every source notebook for hard-coded secrets** (`api_key = "…"`, tokens in URLs) during inventory. Remove them *and* report them for rotation — they stay in git history.
- **Read, then write, in separate statements**: `open(p, "w").write(f(open(p).read()))` truncates the file before reading it. Never redirect a script's output into a file the script also writes.
- **Scripts that patch other build scripts double-escape** (`\\n` becomes a real newline inside notebook code) — run the notebook right after every patch.
- **Exercises copied from solved notebooks** need TODO stubs plus check cells that report "not done yet", so the exercise runs clean unfinished.
- **Unused provider imports** hint at an intended demo — build it as an optional section or remove the import.

## 4. Running notebooks
- **Working directory** is the notebook's folder; load `.env` with `load_dotenv(find_dotenv(usecwd=True))`.
- **Rate limits spill over**: image-heavy notebooks can exhaust tokens-per-minute and fail the *next* notebook; run heavy ones last, and wrap calls in a 429-aware retry.
- **Bare display objects hide network calls**: a graph/agent as a cell's last line renders through an external diagram service; print nodes/edges instead (keep an explicit diagram only where the picture is the lesson).
- **Thread pools**: `with ThreadPoolExecutor()` waits for slow threads even after `result(timeout=…)` gives up — use `shutdown(wait=False, cancel_futures=True)`; give every HTTP fetch its own timeout.
- **Interactive `input()`** can't run unattended: use the framework's interrupt/resume (e.g. LangGraph `interrupt()` + `Command(resume=…)`) with a scripted reviewer by default and the interactive path behind a flag. Side effects must happen before the interrupting node — it re-runs on resume.
- **Checkpointed state**: plain dicts, not rich objects (serialization warnings/blocks).
- **Streaming**: delta streams aren't reduced; request both updates and values when you need the final state.
- **Web UIs (Streamlit etc.)**: test headlessly (e.g. `streamlit.testing.v1.AppTest`) with a temporary dependency overlay (`uv run --with streamlit`) instead of syncing optional groups into the shared env.
- **Read-only data demos**: open databases read-only in code (e.g. SQLite `file:X.db?mode=ro&uri=true`) so an agent's "no writes" rule holds, and show the unchanged row count. For model-written SQL this is not enough — see §8.
- **`warnings.filterwarnings("once")` does not dedupe across Jupyter cells**; to show one category on purpose (e.g. `LangChainDeprecationWarning` in a legacy notebook) use `"default"` after the global `"ignore"`.
- **SQLite in WAL mode** (`SqliteSaver`) leaves `*.db-wal` / `*.db-shm` beside the notebook even after its context closes — git-ignore them and check `git status` after runs.
- **Files a notebook creates at run time** (a SQLite db built from a script, written modules, images) must be declared wherever the repo's path checks expect them (e.g. `scripts/path_allowlist.txt`), especially when they're git-ignored: the check passes on your machine because the file is left over from a run, and fails on a fresh clone and in CI. Run the repo's checks from a clean checkout (`git clone`/`git worktree add`, or `git clean -xdn` to see what's untracked) before calling a module done.
- **PDF text** can come out one word per line — normalize whitespace before any quote/evidence check.
- **Scrapers and public APIs**: set a descriptive User-Agent (e.g. `wikipedia.set_user_agent`) — shared defaults get rate-limited (a `JSONDecodeError` is often a 429 in disguise).

## 5. Providers, credentials and cost
- **Check every credential first** (`scripts/check_credentials.py`). A 401 may mean the wrong *provider*, not a bad key — the same variable name is used by different services.
- **Global tracing switches** in `.env` (e.g. `LANGSMITH_TRACING=true`) send every call to a tracing service; an exceeded quota floods output with 429s. Run bulk executions with tracing disabled in the environment (`load_dotenv` doesn't override variables already set) and never make tracing a requirement.
- **Factories with defaults**: pass the model explicitly. OpenAI-compatible routers need provider-prefixed ids (`openai/gpt-4o-mini`).
- **Probe optional SDKs with one live call per provider** before rewriting tools around them: vendors remove APIs (login endpoints) and data providers can quietly return nothing.
- **Model ids get retired** — list models before keeping an id in an optional demo.
- **Optional providers** run only when their key works (try/except + a printed "skipped" line); the default path uses the standard model.
- **Shrink before you skip**: expose the multiplying factors (sections × queries × results) as named settings, cap the plan in code and assert the real count. Tag `skip-execution` only what can't be shrunk (e.g. image generation).
- **Verify API support with the cheapest call** that exercises it (a hosted tool attached on a turn where it shouldn't fire).
- **Writer prompts**: "Reply with the output only" — conversational preambles inflate word counts and fake length problems.
- **Swapping an unavailable provider** (no AWS for Bedrock, rejected key): ask the user for a provider that works here, then swap the optional demo to it — update the objectives, prerequisites, Part text, summary, module README, root README key table and `.env.example` together, and drop keys nobody uses any more.
- **Databricks Foundation Model APIs through `aied_helpers.get_databricks_llm`** (OpenAI-compatible AI Gateway): use the Unity Catalog name (`system.ai.<model>`) — old `databricks-<model>` endpoint names can return 403 "no longer available". List endpoints first. Reasoning models (e.g. Qwen 3.5) return content as a list with a reasoning block, which breaks `with_structured_output` (json_schema mode), and `method="function_calling"` sends `parallel_tool_calls`, which the gateway rejects (400). What works: `llm.bind_tools([Schema], tool_choice="Schema") | PydanticToolsParser(tools=[Schema], first_tool_only=True)`; forced `tool_choice` works as-is.
- **Tracing quota**: a closed/ignored tracing quota is fine as long as bulk runs keep tracing off; the key itself may still be valid (check with one call). Org billing endpoints need an org-scoped admin key — not needed for the cleanup.
- **Optional extras install fewer providers than the docs list**: check `uv.lock` before trusting a provider list (an OpenBB extra lacked `cboe`/`finviz`/`tmx`, so those calls had always failed).
- **An optional dependency that isn't installed** can still be checked: read its tagged source (`gh api repos/<owner>/<repo>/contents/<path>?ref=v<locked version>`).
- **Unreachable services** (a cloud DB that resets TLS from this network, no Docker for Postgres): keep a skip-when-unusable path (catch the connect error, print why), verify generated queries offline by sampling, file a gap.

## 6. LangChain / LangGraph specifics (1.x)
- `ToolNode` can't be invoked outside a graph (needs a runtime config) — demo it in a one-node graph. Its default error handling only catches bad arguments; exceptions raised inside tools crash the run unless `handle_tool_errors=True`.
- `create_agent` + middleware: `stream_mode="values"` can emit the same message twice — print by message id. `ModelCallLimitMiddleware(run_limit=…)` caps one run (`thread_limit` spans a conversation) and appends its own final message.
- TypedDict→JSON-schema conversion fails on `NotRequired[...]`; use `Annotated[T | None, None, "description"]`.
- ReAct demos about one tool call per turn need `parallel_tool_calls=False`.
- 0.x agent APIs (`AgentExecutor`, `hub`, chains) live in `langchain_classic`.
- **Deprecation audits**: import each symbol with `-W always` *and* grep the installed source for `warn_deprecated` / `@deprecated` — some classes warn only in `__init__` (`RunnableWithMessageHistory`), so docstring probes miss them. `create_react_agent` → `langchain.agents.create_agent(system_prompt=…)`; `MemorySaver` is an alias of `InMemorySaver`.
- **A compiled subgraph used as a node hands back its whole final state** and the parent re-applies its reducers: shared `add_messages` keys merge by id (safe), a shared `operator.add` counter or log double-counts. Keep counters in parent-only or subgraph-only keys (subclass the shared TypedDict).
- **Joins**: separate edges into a join run it once per superstep in which a predecessor finished — twice with unequal branches; a list edge `add_edge(["a", "b"], "join")` or `add_node(..., defer=True)` runs it once. Prove scheduling with stub nodes and `graph.stream(x, stream_mode=["debug", "values"])` (task events carry the superstep). Annotate stub params `state: dict` — a TypedDict hint can raise "Channel already exists with a different type".
- **Handoffs by hand**: a tool returning `Command(goto=<agent>, graph=Command.PARENT, update={"messages": state["messages"] + [tool_message], "active_agent": <agent>})` (as in `langgraph_swarm/handoff.py`), START routed on `active_agent`, plus a checkpointer. Update keys must exist in the parent schema. Command-returning tools can be called directly with a tool-call dict (`{"type": "tool_call", "id", "name", "args": {…, "state": {…}}}`) to show the `Command` without a model.
- **Typed hand-offs between agents**: `create_agent(..., response_format=ToolStrategy(Schema))`; the result is in `structured_response`. A bare schema picks ProviderStrategy, which sets `strict=True` on every tool for OpenAI, third-party tools included.
- **`create_agent` runs tools in worker threads**: SQLite connections need `check_same_thread=False`.
- **Stores**: `store.search()` returns 10 items unless given `limit=` — pass it whenever code counts or prunes. `SqliteStore` ignores `omit_expired` (expired items come back until `sweep_ttl()`); TTL behaviour is backend-specific. Reach the store through `ToolRuntime` / `Runtime[Context]`, not a global user id.

## 7. Git, PRs and shared working trees
- **Stage explicit paths only**; other people or sessions may have uncommitted work.
- **Committing your edit to a file that also carries someone else's uncommitted edits**: stage `HEAD` + only your edits (`git hash-object -w` + `git update-index --cacheinfo`) and apply the same edit to the working copy.
- **A switch/pull blocked by someone else's edit**: stash only that path, switch and pull, pop.
- **Committed outputs**: outputs ship with the notebooks, so the last run before a commit is what learners see. Run with the scripted runner (fresh kernel, tracing off), read the outputs, then stage. Output-only re-runs change every LLM answer — re-commit a notebook's outputs only when you deliberately re-ran it. An nbstripout **git filter** cannot keep outputs reliably (`--install` ignores `--keep-output`; the flags live in unshared `.git/config`) — use the pre-commit hook with `--keep-output --keep-count`.
- **Secret scans on outputs need anchored patterns**: `sk-` also appears inside URLs (`…/elon-musk-backs-…`); anchor with `(?<![\w-])`. A real key in an output means: clear it, rotate the key.
- **Checks that read the staged copy** see your fix only after `git add`.
- **The tracker is local** (`.tracker/` in `.gitignore`): PR bodies carry the plan summary, run table and blocker/gap list. Still store repo-relative paths in reports — they get pasted into PRs.
- **Never commit while a notebook run is in progress**: pre-commit stashes unstaged changes during the commit; a runner that reads a notebook in that window executes the committed version and writes it back, silently reverting your edits. If it happens: `git diff` shows only outputs vs HEAD → re-apply the edit and re-run.
- **Right after a push**, a PR can report "not mergeable"/"UNSTABLE" while checks (including third-party reviewers) compute — inspect `mergeStateStatus`/`statusCheckRollup` and retry. `gh pr merge --delete-branch` also switches locally; if that switch is blocked the remote branch survives — check `git branch -a`. Some repos auto-delete merged branches.
- **Leftover same-name remote branches** from an earlier cleanup: check `git merge-base --is-ancestor origin/<branch> origin/main` before pushing — if it is an ancestor, a plain push fast-forwards it.
- **Repos that strip outputs with an nbstripout git filter**: a branch switch (including `gh pr merge --delete-branch`) overwrites local notebook outputs — copy them aside first and restore after; phantom diffs that block a pull clear with `git -c filter.nbstripout.clean=cat pull --ff-only`.
- **Background security reviews** of pushed commits: treat each finding as a review comment — verify it, fix it on the PR branch (through the worker that owns the branch, if one is running) before merging, and note the fix in the PR body.
- **Auto-mode classifiers** may block `gh pr merge` until the user says "merge" in chat, and block `uv run python -` even for inspect-only imports — read signatures by grepping `.venv/lib/python3.X/site-packages/<pkg>`.
- **Lint you can trust**: repo ruff configs often exclude `*.ipynb` (and lesson `*.py`) — dump code cells to a scratch `.py` and run `ruff check --isolated`. In zsh, a glob with no matches (`rm -f dir/*.py`) aborts an `&&` chain; print the file count before trusting "All checks passed".
- **Delegation**: subagents can't write report `.md` files — have them return text and let the lead write the tracker. Split an oversized module into two sequential PRs (shared code and fixes first, merges and renumbering second).

## 8. Security: model-written SQL, queries and code
- **Model-written SQL on SQLite**: `mode=ro` + `PRAGMA query_only = ON` stop writes, but not `ATTACH DATABASE '<path>'` (reads any SQLite file on the machine) or `PRAGMA query_only = OFF`. Also install `conn.set_authorizer` allowing only `SQLITE_SELECT`/`READ`/`FUNCTION`/`RECURSIVE` (after the PRAGMA, which it would refuse), and show DELETE, `ATTACH ':memory:'` and the PRAGMA refused through the agent's own tool.
- **Read-only is not private**: when a tool promises a column stays hidden (other guests' names), return `SQLITE_IGNORE` for `SQLITE_READ` on that (table, column) — it reads as NULL in SELECT, WHERE, subqueries, CTEs and functions, and `SELECT *` still works. Prove it with a code-computed ✅.
- **Writes go through parameterised tools** (bound parameters, validated inputs, check and insert in one `BEGIN IMMEDIATE` transaction), never model-written INSERTs. An agent that must not write gets a toolset without the write tool, not a prompt rule.
- **Model-written Cypher**: a Neo4j READ access mode is a routing hint, not enforcement — gate with `EXPLAIN` and `summary.query_type == "r"`, and use a read-only DB role in production.
- **Model-written code**: a child process (`sys.executable -I`, empty `env`, closed stdin, temp cwd, `timeout=`) stops hangs and keeps keys out, but it is NOT a sandbox — say so in the prose. Token denylists are bypassable (generator-frame attribute paths pass a `__` filter). Real isolation is a container or a hosted sandbox.
- **Prompt injection → code execution**: an agent that runs code must not read untrusted text (web or news results). Hand it typed data only (`ToolStrategy(Schema)` with numeric fields and pattern-constrained short labels) plus the user's own request, and show in a zero-LLM cell that an instruction-like label fails validation.

## 9. When the user runs the notebooks (no-execution mode)
- **No notebook runs, probe scripts or LLM/API calls** — static checks, offline tests and reading docs or installed source are fine. A stdlib-only check of a guard on a throwaway in-memory database is not lesson code; say when you ran one.
- **Verify by reading**: trace each changed cell's data flow; check every API name and signature against the installed source or current docs.
- **Make each claim print a code-computed ✅** the user's run will show; prefer zero-LLM proofs (stubs, scripted fake models, direct tool calls) so the mechanism is proven even when the model misbehaves.
- **The PR body carries the run**: "⚠️ Not executed — run before merging", a verification checklist (notebook | cell | must show), and a risks list of model-dependent outcomes you could not prove.
- **Tracker**: "Run result" = `not run (user)`; gaps stay open until the user's run confirms them.
