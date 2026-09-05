# Task board — LangChain_Fundamentals

**Source plan(s):** `.plan/LangChain_Fundamentals_langchain_v1_plan.md`
**Updated:** 2026-09-05

**Progress:** `████████████░░░░░░░░░░░░` 7/14

| Status | Count |
| --- | --- |
| `todo` | 4 |
| `in-review` | 3 |
| `done` | 7 |

## Wave 0

| | ID | Task | Type | Effort | Disp. | Review | Blocked by | Output |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [x] | [`T-001`](T-001_Add_langchain_classic_to_dependency_files.md) | Install already-pinned langchain-classic + text-splitters into .venv | prereq | S | n/a | — | — | - |

## Wave 1

| | ID | Task | Type | Effort | Disp. | Review | Blocked by | Output |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [x] | [`T-002`](T-002_Repoint_legacy_chain_imports_to_langchain_classi.md) | Repoint legacy chain imports to langchain-classic | migration | M | repoint | ✓ approved | — | - |
| [x] | [`T-003`](T-003_Fix_moved_core_imports_schema_text_splitter_llms.md) | Fix moved core imports (schema, text_splitter, llms, parsers) | migration | S | rewrite | ✓ approved | — | - |
| [x] | [`T-004`](T-004_Drop_stale_langchain_0_3_x_pip_pins.md) | Drop stale langchain 0.3.x pip pins | migration | S | rewrite | ✓ approved | — | - |
| [x] | [`T-009`](T-009_Fix_langchain_prompts_imports_scanner_blind_spot.md) | Fix langchain.prompts imports (scanner blind spot) | migration | S | rewrite | ✓ approved | — | - |
| [x] | [`T-010`](T-010_Assign_orphaned_IMP_chains_hits_in_3_1_LCEL_Intr.md) | Assign orphaned IMP-chains hits in 3.1_LCEL_Introduction | migration | S | repoint | ✓ approved | — | - |
| [?] | [`T-012`](T-012_Strip_stale_non_langchain_pip_pins_in_1_1_and_1_.md) | Strip stale non-langchain pip pins in 1.1 and 1.3 | migration | S | rewrite | ✗ changes requested | — | - |

## Wave 4

| | ID | Task | Type | Effort | Disp. | Review | Blocked by | Output |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [ ] | [`T-005`](T-005_Rewrite_summarization_off_load_summarize_chain.md) | Rewrite summarization off load_summarize_chain | migration | L | rewrite | ⏳ pending | — | - |
| [?] | [`T-006`](T-006_Label_legacy_halves_of_3_5_and_3_6_as_langchain_.md) | Label legacy halves of 3.5 and 3.6 as langchain-classic | migration | M | repoint | ⏳ pending | — | - |
| [ ] | [`T-011`](T-011_Rewrite_PipelinePromptTemplate_section_class_rem.md) | Rewrite PipelinePromptTemplate section (class removed from ecosystem) | migration | M | rewrite | ⏳ pending | — | - |

## Wave 5

| | ID | Task | Type | Effort | Disp. | Review | Blocked by | Output |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [x] | [`T-007`](T-007_Explainer_the_package_split_and_where_imports_mo.md) | Explainer: the package split and where imports moved | explainer | M | rewrite | ✓ approved | — | 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/01_Getting_Started/1.8_Package_Split_and_Imports_LangChain_v1.ipynb |
| [ ] | [`T-008`](T-008_Explainer_document_combining_chains_to_LCEL.md) | Explainer: document-combining chains to LCEL | explainer | M | rewrite | ⏳ pending | T-005 | 05_Summarization/8.2_Doc_Chains_to_LCEL_LangChain_v1.ipynb |
| [?] | [`T-013`](T-013_Sweep_personal_absolute_paths_from_notebook_outp.md) | Sweep personal absolute paths from notebook outputs | migration | S | rewrite | ⏳ pending | — | - |
| [ ] | [`T-014`](T-014_Clear_saved_outputs_folder_wide_add_nbstripout_h.md) | Clear saved outputs folder-wide + add nbstripout hook | migration | M | rewrite | ⏳ pending | T-005, T-011 | - |

---

Regenerate with `python .claude/skills/plan-to-tasks/scripts/tasks.py index .tasks/LangChain_Fundamentals` — do not hand-edit this file; edit the task files' frontmatter instead.
