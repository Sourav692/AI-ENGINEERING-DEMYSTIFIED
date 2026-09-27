# Plan 05: Worksheet and practice experience

## Outcome

Reduce control density and make the core attempt, compare, score, and continue loop obvious without weakening advanced actions such as timer, export, print, and reset.

## Recommendations

- Split the toolbar into high-frequency practice state and secondary utilities.
- Keep completion and status visible. Move timer, export, print, and reset into a clearly labelled overflow menu on narrow screens.
- Keep “Reveal all keys” visibly separate from section-by-section reveals and explain its consequence.
- Add a compact section navigator that shows answered, unanswered, and revealed state.
- Reduce breadcrumb height on mobile and bring the first prompt into view sooner.
- Preserve autosave wording and local-only storage reassurance.
- Keep destructive reset visually and spatially separate from normal actions.

## Primary files

- `site/src/components/ScenarioToolbar.tsx`
- `site/src/components/ScenarioView.tsx`
- `site/src/components/AnswerKeyReveal.tsx`
- `site/src/components/Blocks.tsx`
- `site/src/components/AutoTextarea.tsx`

## Acceptance criteria

- The mobile toolbar works at 320 px without wrapped or clipped action labels.
- Attempt, reveal, self-score, and continue are visually dominant over utilities.
- Reset requires a clear confirmation and cannot be triggered accidentally.
- Saved/not-saving status remains available to assistive technology.
- Existing answer restoration and exports produce the same content as before.

