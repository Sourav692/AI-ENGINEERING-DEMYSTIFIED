---
id: T-011
title: Rewrite PipelinePromptTemplate section (class removed from ecosystem)
type: migration
status: done
review: approved
review_rounds: 1
wave: 4
effort: M
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.2_Prompt_Templates.ipynb]
rules: [IMP-prompts]
depends_on: []
output: 02_Inputs_Outputs_Prompts/2.2_Prompt_Templates.ipynb
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Rewrite PipelinePromptTemplate section (class removed from ecosystem)** — `done` · review: ✓ approved · round 1

## Objective

Cell 20 teaches composable prompts without PipelinePromptTemplate, which no longer exists in langchain_core, langchain_classic, or anywhere in site-packages. Needs a conceptual replacement (PromptTemplate composition / ChatPromptTemplate assembly), not an import repoint.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/2.2_Prompt_Templates.ipynb`

Findings this task closes: `IMP-prompts`

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for `IMP-prompts`
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified
- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: APPLIED. PEDAGOGY DECISION (overrule freely): replaced PipelinePromptTemplate with the `+` operator on PromptTemplate, with .partial() shown for the pre-filled-component case. Rationale: `+` preserves the one property that made the old class worth teaching - it computes the UNION of the components' input_variables automatically, which is exactly what pipeline_prompt.input_variables demonstrated. Verified all four candidate approaches against .venv before choosing: `+` composition, .partial(), nested .format(), and ChatPromptTemplate concatenation all work; the alternatives make composition manual and lose the lesson. SCOPE WAS WIDER THAN THE TASK SAID: the task named cell 20, but a guard assertion caught that cells 22 and 25 also referenced the class - cell 22 said its serialization 'is not yet fully supported' (now: a composed prompt IS an ordinary PromptTemplate and serializes fine, unlike the old class), and cell 25's key-takeaway list still advertised it. Fixing only cell 20 would have left the notebook contradicting itself twice. SELF-CAUGHT DEFECT: I over-escaped the JSON example value as '{{ "sentiment": ... }}'. Argument VALUES are not re-parsed by str.format, so that rendered literal double braces. Confirmed with a direct test, then fixed to single braces in both places. VERIFIED BY EXECUTION (template construction only, no API call): cells 20 and 21 run end to end; input_variables union is the exact expected 6-name set; .partial() correctly drops the 5 filled names leaving ['input']; the JSON example renders with single braces. Scanner: IMP-prompts 0, and 2.2 no longer appears in the findings at all.

- 2026-09-05: review r1: APPROVED, all six gates. The reviewer RULED ON THE PEDAGOGY CHOICE and backed `+`: it pulled the archived langchain-core 0.3.29 source and confirmed PipelinePromptTemplate's get_input_variables computed union(components) minus slot names - exactly what `+` gives free - and that the old cell's final template was pure in-order concatenation, so `+` reproduces it with no lost capability. It rejected the alternatives I asked about: ChatPromptTemplate would teach a message-list model in a section whose neighbours are all string templates (belongs in 2.3), and an LCEL pattern answers how to RUN a prompt, not how to BUILD one, breaking one-concept-per-notebook. It also confirmed .partial() earns its place rather than padding. Independently verified: a whole-environment grep found ZERO files containing PipelinePromptTemplate anywhere in site-packages, upgrading my namespace-scoped check; and it round-tripped a composed prompt through save/load in both YAML and JSON, confirming cell 22's new claim, while the old class's _prompt_type was a bare raise ValueError so it genuinely could not serialize. 5 nits; 3 APPLIED: cell 19 now states the ONE capability `+` loses (named-slot placement) with the loop form the class's own deprecation notice recommended; cell 20's example_prompt renamed to example_component_prompt because it shadowed cell 14's binding and would make a re-run of cell 15 fail with a confusing KeyError; cell 21's .partial() demo used sentiment 'mixed', outside the positive/neutral/negative taxonomy its own intro defines. Re-executed cells 20-21 after: union correct, partial correct, no double braces. 2 nits boarded as follow-ups rather than absorbed.
