---
id: T-005
title: Rewrite summarization off load_summarize_chain
type: migration
status: done
review: approved
review_rounds: 2
wave: 4
effort: L
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/8.0_Summarization_Essentials.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/8.1_Text_Summarization.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/app.py]
rules: [CHN-loaders, CHN-llmchain]
depends_on: [T-002]
output: 05_Summarization/ (8.0, 8.1, app.py)
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Rewrite summarization off load_summarize_chain** — `done` · review: ✓ approved · round 2

## Objective

Summarization taught with LCEL and an explicit map-reduce, not legacy chain loaders.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/8.0_Summarization_Essentials.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/8.1_Text_Summarization.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/05_Summarization/app.py`

Findings this task closes: `CHN-loaders`, `CHN-llmchain`

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [ ] Scanner re-run over the target reports no remaining findings for `CHN-loaders`, `CHN-llmchain`
- [ ] Notebook narrative (markdown cells) matches the new code
- [ ] Every code cell parses (`static_check.py`) and every 1.x API used is verified
- [ ] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: From T-013 review r1 (nit): clearing 8.1 cell 15's outputs removed the only place in the notebook showing the verbatim LangChainDeprecationWarning text for LLMChain and Chain.run - exactly the string a learner would paste into a search box. When this task rewrites that cell to 'prompt | llm', quote BOTH deprecation strings verbatim in the accompanying markdown so the searchable text survives the output clear. Also in scope for this task: 8.1 cell 9 'response = llm(chat_message)' raises TypeError on 1.x (BaseChatModel.__call__ removed) - use llm.invoke(...).

- 2026-09-05: SCOPE ADDITION: 8.1 cell 12 also has 'from langchain import PromptTemplate' (IMP-toplevel), which raises ImportError on 1.x. Caught by a scanner rule added during this task's prep - the fourth blind spot found this session. 8.1's copy is in T-005 scope; 3.0's copy is boarded separately as T-015.

- 2026-09-05: APPLIED. 8.0 (13->12 cells): getpass+os.environ shim -> load_dotenv with an assert (the os.environ cell was deleted as dead once .env loads); unused load_summarize_chain import dropped; OpenAI(gpt-3.5-turbo-instruct) -> ChatOpenAI(gpt-4o-mini) [JUDGEMENT CALL, flagged: the legacy /completions model is retired and every sibling notebook uses chat models - overrule if you want the completions API taught]; LLMChain + per-chunk .run() loop -> 'prompt | llm | StrOutputParser()' + .batch(), which also makes the map step concurrent; chain.invoke(bare string) -> .invoke({'text': ...}) since LCEL does not accept the bare string LLMChain tolerated. 8.1 (34 cells, unchanged): llm(chat_message) -> llm.invoke() with the TypeError quoted; 'from langchain import PromptTemplate' -> langchain_core; LLMChain+.run() -> LCEL WITH BOTH LangChainDeprecationWarning strings reinstated verbatim in comments (T-013's output-clearing had removed the only copy - the searchable text a learner would paste into Google); load_summarize_chain('stuff') -> LCEL over joined docs; ('map_reduce') -> explicit map .batch() + reduce, so the strategy is visible rather than packaged; ('refine') -> an explicit sequential loop with a note on why refine cannot be batched. app.py: same stuff->LCEL swap, parses clean. RESULT: CHN-loaders 7->0, IMP-chains 5->0, MOD-direct-call 1->0, IMP-toplevel 1->0; 05_Summarization/ no longer appears in the scan at all. METHOD: scripted with 13 guard assertions asserting each target index still contains its expected marker - one guard fired during the dry run and caught a real off-by-one after a cell deletion that would have overwritten a markdown cell.

- 2026-09-05: review r1: CHANGES_REQUESTED, 3 blockers + 3 nits, ALL FIXED. B1: 8.1 c15 used StrOutputParser before its import in c19 - a genuine NameError on a clean top-to-bottom run, introduced by my own rewrite (the LLMChain line it replaced needed no such import). Added the import to c12 and dropped the now-duplicate one from c19; re-verified with an AST pass over both notebooks that resolves names cell-by-cell - zero forward references. B2: the 'searchable' deprecation strings I reinstated were MISQUOTED three ways - 'removed in 1.0' (actually 2.0.0), a Sphinx ':meth:' wrapper that only appears in rendered docs and never at runtime, and 'langchain' where the runtime says 'langchain-classic'. A misquoted searchable string is worse than none since it matches nothing. Replaced with text CAPTURED by actually triggering both warnings against the installed packages. B3: 8.0 c9 was labelled REDUCE STEP but re-summarized the raw input_text and ignored the `summaries` list entirely - teaching map-reduce wrong in the notebook whose stated lesson is map-reduce. Now a real reduce over ' '.join(summaries), with the single-pass 'stuff' baseline kept as documented contrast. NITS: my import cell added an unused RecursiveCharacterTextSplitter (ruff F401) in the very cell whose comment criticises unused imports - fixed by actually USING it, which also fixed the second nit: CharacterTextSplitter splits on blank lines and input_text has none, so chunks was a single element and Runnable.batch short-circuits at len==1, meaning the concurrency the comment advertised never happened. app.py continuation re-indented. REVIEWER RULED the gpt-3.5-turbo-instruct -> gpt-4o-mini swap IN SCOPE and said do not revert: the completions model is retired, so leaving it would ship a 'rewritten' notebook that fails at the API.

- 2026-09-05: review r2: APPROVED - all six gates. Reviewer INDEPENDENTLY reproduced both deprecation warnings against the installed packages and confirmed the notebook quotes them character-for-character, and empirically verified the splitter fix: input_text is 630 chars, RecursiveCharacterTextSplitter(100,20) -> 11 chunks vs CharacterTextSplitter -> 1, so .batch() really parallelizes now and the cell-4 comment is true. AST name-resolution over both notebooks: zero forward references, including pre-existing ones. 4 nits raised; 3 APPLIED: 8.0 c9 now reuses final_summary so the reduce visibly consumes the map output; 8.1 c16 heading retitled off StuffDocumentChain (a class the section no longer uses); 8.1 c19 comment-only cell deleted and folded into the stuff cell with a proper banner (34 -> 33 cells). While folding I duplicated the '# Was:' header and caught it on read-back - cleaned. 1 nit ACCEPTED as unavoidable: two E501 long lines in c15, which are the verbatim deprecation strings and must stay exact to be searchable.
