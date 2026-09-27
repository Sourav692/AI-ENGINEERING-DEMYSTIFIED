# Plan 06: Responsive, accessibility, and system states

## Outcome

Ensure the redesign works as a complete product from 320 px through large desktop, with keyboard, screen-reader, reduced-motion, high-zoom, and failure-state coverage.

## Focus areas

- Mobile navigation and discoverable horizontal overflow.
- Minimum readable sizes and 44 px touch targets.
- Logical focus order, focus trapping for dialogs/menus, Escape behavior, and focus restoration.
- `aria-current`, tab semantics, disclosure semantics, live regions, and descriptive control names.
- Route-level loading, error, and not-found experiences.
- Empty search, no progress, blocked storage, diagram failure, and missing-content states.
- 200% and 400% zoom, long titles, and large text.

## Primary files

- `site/src/app/layout.tsx`
- New `loading.tsx`, `error.tsx`, and `not-found.tsx` files
- Interactive components under `site/src/components/`
- `site/src/app/globals.css`

## Acceptance criteria

- Complete keyboard navigation without traps or lost focus.
- WCAG 2.2 AA target for contrast, focus visibility, semantics, and target size.
- No horizontal page overflow at 320 px; intentional table/tab overflow is labelled and usable.
- Every asynchronous or fallible surface has loading, empty, and error behavior.
- Reduced-motion preference disables nonessential movement.

