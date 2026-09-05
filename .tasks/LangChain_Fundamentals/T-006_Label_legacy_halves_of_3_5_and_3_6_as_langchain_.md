---
id: T-006
title: Label legacy halves of 3.5 and 3.6 as langchain-classic
type: migration
status: done
review: approved
review_rounds: 4
wave: 4
effort: M
disposition: repoint
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.5_Chain_Migrations.ipynb, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.6_Chain_Migration_Advanced.ipynb]
rules: [CHN-llmchain, CHN-retrieval]
depends_on: [T-002]
output: -
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Label legacy halves of 3.5 and 3.6 as langchain-classic** — `done` · review: ✓ approved · round 4

## Objective

The before/after lessons still run, with the before side clearly marked legacy.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.5_Chain_Migrations.ipynb`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/03_LCEL/3.6_Chain_Migration_Advanced.ipynb`

Findings this task closes: `CHN-llmchain`, `CHN-retrieval`

## Steps

- [ ] (fill in — one checkable action each)

## Acceptance criteria

- [x] ~~Scanner reports no remaining `CHN-llmchain` / `CHN-retrieval` findings~~ —
      **unsatisfiable as written, and correctly so.** This task's disposition is
      `repoint`, not `rewrite`: the legacy halves are the lesson and are kept on
      purpose, so the scanner still reports 4 `CHN-*` findings in 3.5 and 2 in 3.6
      and always will. The plan says the same at
      `.plan/LangChain_Fundamentals_langchain_v1_plan.md:54`. The stock criterion
      was boilerplate that does not fit a `repoint` task. Replaced by:
- [x] Every `CHN-*` finding that survives is one the notebook deliberately teaches,
      and is labelled as legacy where a learner meets it
- [x] Notebook narrative (markdown cells) matches the new code
- [x] Every code cell parses (`static_check.py` → `ok: true`, 0 syntax errors on both)
      and every 1.x API claim is verified against installed source
- [x] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

_(append findings, blockers, decisions as you work — this is the audit trail)_

- 2026-09-05: 3.5: replaced the four bare section headings ('### Legacy Chains', '### LCEL', '### Legacy RAG', '### LCEL') with labelled versions explaining that LLMChain/RetrievalQA/hub are RETIRED and live in langchain-classic, that they are shown deliberately as the 'before' half, and that LCEL is not deprecated. 3.6: inserted two markdown cells (16 -> 18 cells) - one labelling the ConversationalRetrievalChain section as legacy, one marking where the LCEL rewrite begins; it previously had almost no narrative at all. SELF-CHECK CAUGHT ONE MORE: 3.5 cell 10 sits under the 'LCEL - the 1.x way' heading but imports 'from langchain_classic import hub'. A learner would read that as a contradiction. Cell 9 now explains it: the CHAIN is fully LCEL, only the prompt hub moved to classic, and inlining the prompt with ChatPromptTemplate drops the dependency (and the network call).

- 2026-09-05: review r2: 2 BLOCKERS, both fixed. (1) My hub explanation was WRONG in the direction I asked the reviewer to check. I said hub.pull 'still goes through langchain-classic', implying it is the supported 1.x route. Verified myself against .venv: langchain_classic/hub.py decorates BOTH pull and push with @deprecated(since=1.0.6, removal=2.0.0, 'Use the LangSmith SDK instead') and each body is a 2-line delegation to langsmith.Client.pull_prompt/push_prompt. langsmith==0.12.1 is already pinned. Cell 9 now says plainly that the hub.pull line is NOT the 1.x way, gives Client().pull_prompt() as the native path, keeps inlining as the offline option, and surfaces hub.pull's own docstring warning that hub manifests are untrusted executable config. Cell 6 amended from 'moved with it' to 'reduced to a deprecated shim'. (2) 3.6's 'LCEL rewrite begins here' marker sat at index 8, three cells AFTER the rewrite actually starts - cells 5-7 build rephrase_chain in pure LCEL, so they were stranded under the Legacy heading and the marker's own text was falsified by the code above it. Moved to index 5, immediately after the legacy cell; 18 cells preserved. NITS fixed: legacy labels now name BOTH deprecations (retired class AND chain(...) vs chain.invoke(...)); 3.5 cell 5 reuses the bound llm instead of constructing a second inline ChatOpenAI. Formatting nit boarded as T-016.

- 2026-09-05: review r3: blockers 1+3 confirmed fixed; blocker 2's FIX introduced a NEW error. I replaced a wrong hub claim with another wrong one: Client().pull_prompt('rlm/rag-prompt') raises ValueError on the pinned langsmith 0.12.1 - _validate_public_prompt_pull (client.py:464) rejects any owner != '-' unless dangerously_pull_public_prompt=True. Verified myself. WORSE than the reviewer stated: langchain_classic/hub.py:117 delegates WITHOUT that flag, so the LEGACY cell 8 fails too, not just the LCEL cell 10 - both halves of the RAG lesson were unrunnable, falsifying T-006's core objective. FIXED by inlining the rag-prompt in cells 8 and 10 (three lines, no network, no trust decision), demoting hub.pull and the LangSmith SDK route to documented comments in cell 9 with the correct dangerously_pull_public_prompt=True, and rewriting cell 6 to say hub.pull RAISES rather than merely warns. Nits fixed: 3.5 c7 duplicate llm binding dropped; 3.6 c7/c10 ChatOpenAI(temperature=0) given model='gpt-4o-mini' (was silently falling back to the legacy gpt-3.5-turbo default). SELF-CAUGHT after applying: my cell 8 rewrite had switched to .invoke(), contradicting cell 6's promise of TWO deprecation warnings - restored the legacy qa_chain(...) call style so the 'before' half actually demonstrates the before behaviour. T-006 HAS NOW HIT THE 3-ROUND REVIEW CAP.

- 2026-09-05: DEFERRED BY USER at the 3-round review cap. State on disk: all round-1/2/3 fixes ARE applied to 3.5 and 3.6 (legacy labels naming both deprecations, marker repositioned to index 5, hub.pull inlined in cells 8 and 10 so both halves run, cell 9 documenting the three prompt options, duplicate llm bindings removed, 3.6 ChatOpenAI given an explicit model). Those edits were verified against .venv source, but they carry NO review approval - the last self-assessment on this task was wrong twice in a row, so treat the labelling text as unverified. Deliberately NOT closed as done and NOT force-closed: the review gate is doing its job. To resume: run notebook-review round 4 on 3.5/3.6, or accept and close with --force (which stamps the bypass in this log).

- 2026-09-05: ⚠️ closed with --force, bypassing review (review was 'changes-requested')

- 2026-09-05: CLOSED ON EXPLICIT USER APPROVAL 2026-09-05 ('Approve 006'). To be precise about what this does and does not mean: notebook-review NEVER approved this task - its last verdict was CHANGES_REQUESTED at round 3, and the --force stamp below records that. The user is the authority on their own teaching material and has accepted it; the review gate has not. WHAT IS ON DISK, all verified but unapproved: 3.5 and 3.6 carry legacy labels naming BOTH deprecations (the retired class and the retired chain(...) call style); 3.6's 'LCEL rewrite begins here' marker sits at index 5 where the rewrite actually starts; 3.5 cells 8 and 10 inline the rag-prompt because hub.pull RAISES ValueError on the pinned langsmith rather than merely warning; cell 9 documents the three prompt options with the correct dangerously_pull_public_prompt=True on the LangSmith route; duplicate llm bindings dropped; 3.6's ChatOpenAI calls given an explicit model. Round 3's open finding was that my round-2 FIX for the hub explanation introduced a NEW wrong claim, which I then corrected - but that correction was never independently checked. Treat the hub/prompt narrative in 3.5 cells 6 and 9 as the least verified text in this folder. T-016 later formatted both notebooks and confirmed these label cells survived intact.

- 2026-09-05: REVIEW ROUND 4 — **APPROVED**, no blockers. Run at user request to
  retire the force-close, by a FRESH reviewer with no context on the three prior
  rounds (the T-020 reviewer was deliberately not reused). Static analysis only;
  no cell executed.

  The unreviewed part of round 3 — the hub/prompt narrative and the inlining of
  both RAG halves — was checked sentence by sentence against `.venv` source and
  holds up. Independently confirmed: `hub.pull` is `@deprecated(since="1.0.6",
  removal="2.0.0")` and its two-line body delegates WITHOUT
  `dangerously_pull_public_prompt`; `pull_prompt_commit` calls
  `_validate_public_prompt_pull` as its first statement, before any network call,
  so `rlm/rag-prompt` raises rather than fetching; cell 6's fenced quote is a
  verbatim truncation of the real message, not a paraphrase; cell 9's option 2 has
  the right keyword-only parameter name and shape; `hub.pull`'s real docstring does
  carry the "Hub manifests are untrusted input" danger block; `langsmith==0.12.1`
  is pinned in requirements.txt:87 and pyproject.toml:29. Also confirmed: both RAG
  halves inline the prompt with no live `hub` import anywhere; 3.5 cell 8 still
  uses the legacy `qa_chain("...")` call style, so cell 6's promise of a call-style
  warning is honest; 3.6's LCEL marker at cell 5 is truthfully placed and its
  "nothing below imports langchain-classic" claim holds; all three 3.6
  `ChatOpenAI` calls carry an explicit `model=`; exactly one `llm` binding per
  notebook.

  FIXED BEFORE CLOSE — 3 of 5 nits, all factual errors in teaching text, which is
  the defect class that cost this task its first three rounds:
   1. "emits **two** deprecation warnings" undercounted, in 3.5 c6 and 3.6 c3.
      Verified the reviewer's reasoning myself rather than taking it on trust:
      `RetrievalQA.from_llm` constructs `LLMChain(` and `StuffDocumentsChain(`
      internally (both carry `__deprecated__`) and `BaseRetrievalQA._call` runs
      `self.combine_documents_chain.run(...)`, and `Chain.run.__deprecated__` is
      "Use invoke instead." So a learner sees more than two. Both cells now say
      **at least two** and name why. NOTE 3.5 c2's "two, not one" for plain
      `LLMChain` is correct and was left alone — nothing deprecated runs inside
      `LLMChain._call`.
   2. 3.6 c1 claimed cells 7, 11 and 16 construct clients inline "because they need
      temperature=0". Cell 16 sets no temperature. Reworded to "want deterministic
      output" rather than adding a parameter the lesson did not ask for.
   3. 3.6 c7's banner described cell 8's content, not its own. Retitled.

  NOT FIXED, deliberately: the blueprint sections (`Why this changed`, `Common
  errors`, `Key takeaways`) are absent by those names. These are pre-existing
  course notebooks under a `repoint` disposition, not blueprint-generated
  explainers; the reviewer recorded this without failing on it and I agree.

  Post-fix: `static_check.py` → `ok: true`, 0 syntax errors on both; diff is 11
  insertions / 7 deletions with no reserialization damage; cell counts unchanged
  (3.5: 12, 3.6: 21); the legacy `qa_chain(...)` call style re-verified as intact
  after my edits.

  T-006 now carries a genuine review approval. The earlier `--force` stamp above
  stands as the historical record of how it was closed the first time; it is no
  longer the basis for the close.
