# Plan 03: Homepage and content discovery

## Outcome

Turn the homepage from a roadmap-heavy module dashboard into a clear entry point that helps a visitor choose the right learning mode and resume useful work.

## Proposed hierarchy

1. Compact promise and one primary action: “Start practising.”
2. Three distinct learning paths: Practice, Case Studies, Last-Day Prep.
3. “Continue where you left off” when local progress exists; otherwise show recommended starting points.
4. Available curriculum grouped by mode.
5. Upcoming curriculum as secondary roadmap content.
6. Short explanation of the practice loop and local-only storage.

## Visual approach

- Keep the hero left aligned and editorial, with shorter support copy.
- Replace the two identical promotional cards with differentiated rows or an asymmetric grid based on purpose.
- Use one featured action, text links for secondary actions, and fewer boxed regions.
- Show progress as supporting information rather than a dashboard motif.
- Use meaningful labels such as “Practice,” “Read,” and “Revise” rather than “New” or generic status decoration.

## Primary files

- `site/src/app/page.tsx`
- `site/src/components/Progress.tsx`
- `site/src/lib/registry.ts`

## Acceptance criteria

- A first-time visitor can describe the three modes after scanning the first viewport.
- At least one useful action is available without scrolling at 390 x 844.
- Live content appears before planned content.
- Returning users see a clear continuation action derived from existing local progress.
- The homepage remains useful when localStorage is unavailable.

