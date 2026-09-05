# Deprecation map — non-LangChain libraries

**LangChain / LangGraph migrations are NOT here.** They belong to
`.claude/skills/langchain-v1-migration-audit/` — run its scanner and use its
`references/v0-to-v1-rewrite-map.md`. Duplicating those rules here would let the two
drift apart.

This file covers the rest of the stack. **Always verify against the version actually
pinned in `requirements.txt` before rewriting** — this repo pins deliberately, and 18 pins
are held below latest for documented upstream reasons. A "fix" that assumes a newer version
than the lockfile is a regression, not a migration.

Check first:

```bash
grep -iE "^(pandas|numpy|scikit-learn|torch|tensorflow|crewai|autogen|pyautogen)" requirements.txt
```

---

## pandas (2.x)

| Deprecated / removed | Replacement |
| --- | --- |
| `df.append(other)` | **removed in 2.0** → `pd.concat([df, other], ignore_index=True)` |
| `df.applymap(f)` | `df.map(f)` (2.1; `applymap` deprecated) |
| `Series.append` | `pd.concat` |
| `df.ix[...]` | `.loc` / `.iloc` (long gone) |
| `pd.util.testing` | `pd.testing` |
| `inplace=True` | assign the result instead — chained `inplace` is being wound down |
| `df.iteritems()` | `df.items()` |
| `pd.read_csv(..., error_bad_lines=)` | `on_bad_lines="skip"` / `"warn"` |
| `.astype(str)` on object cols for text | consider `dtype="string"` (pyarrow-backed) |
| `pd.set_option("mode.use_inf_as_na")` | removed in 3.0 — handle infs explicitly |

## NumPy (2.x)

| Deprecated / removed | Replacement |
| --- | --- |
| `np.float`, `np.int`, `np.bool`, `np.object`, `np.str` | builtins: `float`, `int`, `bool`, `object`, `str` |
| `np.float_`, `np.complex_` | `np.float64`, `np.complex128` |
| `np.NaN`, `np.Inf` | `np.nan`, `np.inf` (capitalized aliases removed in 2.0) |
| `np.in1d` | `np.isin` |
| `np.product`, `np.cumproduct`, `np.alltrue`, `np.sometrue` | `np.prod`, `np.cumprod`, `np.all`, `np.any` |
| `np.round_` | `np.round` |
| `np.msort` | `np.sort(a, axis=0)` |
| ragged `np.array([...])` without `dtype=object` | pass `dtype=object` explicitly |

## scikit-learn (1.x)

| Deprecated / removed | Replacement |
| --- | --- |
| `from sklearn.externals import joblib` | `import joblib` |
| `normalize=` on linear models | removed 1.2 → `StandardScaler` in a `Pipeline` |
| `n_features_` | `n_features_in_` |
| `sklearn.metrics.SCORERS` | `sklearn.metrics.get_scorer_names()` |
| `base_estimator=` | `estimator=` |
| `OneHotEncoder(sparse=)` | `sparse_output=` |
| `.get_feature_names()` | `.get_feature_names_out()` |
| `sklearn.datasets.load_boston` | removed — use `fetch_california_housing` |

## PyTorch (2.x)

| Deprecated / removed | Replacement |
| --- | --- |
| `Variable(x)` | tensors track grad natively; drop `Variable` |
| `tensor.data` | `tensor.detach()` |
| `torch.load(path)` | pass `weights_only=True` unless you must unpickle objects |
| `.cuda()` / `.cpu()` scattered | one `device = torch.device(...)` + `.to(device)` |
| `torch.nn.functional.sigmoid` | `torch.sigmoid` |
| manual AMP scaling | `torch.autocast` |

## TensorFlow / Keras (2.x → 3)

| Deprecated / removed | Replacement |
| --- | --- |
| `tf.Session`, `tf.placeholder`, `tf.global_variables_initializer` | TF1 graph API — rewrite eagerly, or `tf.compat.v1` as a stopgap |
| `keras.utils.multi_gpu_model` | `tf.distribute` strategies |
| `model.fit_generator` | `model.fit` accepts generators |
| `lr=` | `learning_rate=` |
| `.h5` saving | `.keras` format (Keras 3 default) |

## CrewAI (1.x)

Note: `requirements.txt` **excludes CrewAI on purpose** — it hard-pins `chromadb<1.2`
while `langchain-chroma` 1.1 needs `>=1.3.5`. It installs from its own per-folder
`requirements.txt` in a separate venv. Migrate its notebooks against **that** pin, not the
root one.

| Older pattern | Current |
| --- | --- |
| `from crewai import Agent, Task, Crew` | unchanged, but `llm=` now takes a model string or LLM object |
| tools from `langchain.tools` passed directly | `crewai_tools`, or wrap with `@tool` |
| `Crew(process="sequential")` | `Process.sequential` enum |
| `Crew(...).kickoff()` returning a string | returns a `CrewOutput`; read `.raw` |

## AutoGen (v0.4+ restructure — the big one)

AutoGen split the monolithic `pyautogen` package. Imports change wholesale:

| v0.2 (`pyautogen`) | v0.4+ |
| --- | --- |
| `from autogen import AssistantAgent` | `from autogen_agentchat.agents import AssistantAgent` |
| `from autogen import UserProxyAgent` | `from autogen_agentchat.agents import UserProxyAgent` |
| `from autogen import GroupChat, GroupChatManager` | `from autogen_agentchat.teams import RoundRobinGroupChat`, `SelectorGroupChat` |
| `config_list` / `llm_config` dicts | `from autogen_ext.models.openai import OpenAIChatCompletionClient` |
| `initiate_chat(...)` | `await team.run(task=...)` / `run_stream(...)` — **async** |

This is a rewrite, not a find/replace: v0.4 is async-first, so cells gain `await` and
notebooks rely on the running event loop. Treat an AutoGen notebook as `effort: L` and
check which major version its folder's `requirements.txt` pins before touching it.

---

## Rules for applying any of this

1. **Verify the pin first.** If the repo pins the old version deliberately, the notebook is
   correct as written — record it and move on.
2. **One library per commit/task**, so a regression is bisectable.
3. **Don't modernize style beyond deprecation.** Rewriting working `.loc` chains into
   something you prefer is scope creep and makes review harder.
4. **Update the narrative too.** A markdown cell explaining `df.append` next to
   `pd.concat` code is worse than either alone.
5. **If a replacement changes results** (e.g. `normalize=` → `StandardScaler` shifts
   coefficients), say so in the notebook rather than silently changing outputs a learner
   may have memorized.
