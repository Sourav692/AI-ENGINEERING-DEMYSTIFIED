# Plan 02: Navigation and information architecture

## Outcome

Make the site's three learning modes immediately understandable and reachable from desktop and mobile: practise worksheets, read case studies, and revise with Last-Day Prep.

## Proposed global navigation

- **Practice**: worksheet modules and progress.
- **Case studies**: long-form interview guides.
- **Last-Day Prep**: condensed revision modules and trigger cheat sheet.
- **Guide**: how the learning loop works.
- Search and theme remain utilities on the right.

On mobile, use a compact menu button that opens an inline or popover menu with the same destinations, current-page state, and search entry. Do not hide primary destinations.

## Structural recommendations

- Explain the relationship between the 15-product-roadmap modules and 18 revision modules once, in plain language.
- Show live material before planned material.
- Collapse planned modules under an “Upcoming curriculum” disclosure or separate roadmap section.
- Add `aria-current="page"` to the active global and local navigation item.
- Keep breadcrumbs concise on mobile and fully descriptive on desktop.
- Preserve every existing route.

## Primary files

- `site/src/app/layout.tsx`
- `site/src/lib/registry.ts`
- Route pages under `site/src/app/`
- New shared navigation component if needed

## Acceptance criteria

- All four primary destinations are reachable from a 320 px viewport.
- Desktop and mobile use the same labels and information hierarchy.
- The active global section is visible and exposed to assistive technology.
- Search remains available from every route.
- Navigation fits one line on desktop and has 44 px touch targets on mobile.
- Existing deep links and breadcrumbs continue to work.

