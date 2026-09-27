# Forward Deployed website redesign plan

## Goal

Evolve the existing Next.js learning site into a professional, minimalist editorial experience that is easier to understand, navigate, read, and practise on every screen size.

This is a targeted redesign. Preserve the working content pipeline, URLs, progress data, worksheets, answer-key behavior, search, export, print, and theme support. Improve the interface around them.

## Audit basis

- Live site reviewed: `https://forward-deployed-sigma.vercel.app`
- All 117 public URLs were inventoried and checked against the live deployment: 80 Next.js routes and 37 standalone Last-Day Prep HTML pages.
- Desktop and 390 px mobile views were reviewed across every distinct layout family, including worksheet, behavioral practice, one-tab/four-tab/five-tab reading pages, the guide, the Last-Day Prep hub, concise modules, memory cards, and the trigger sheet.
- Local Next.js 16, React 19, and Tailwind 4 source reviewed under `site/`.
- Existing product specification reviewed at `site/specs/2026-09-17-forward-deployed-site-design.md`.
- Detailed findings: [audit.md](audit.md)
- Route inventory, validation evidence, and audit limits: [full-route-audit.md](full-route-audit.md)
- Content architecture and self-containedness findings: [content-audit.md](content-audit.md)
- Recommended names for navigation, sections, tracks, tabs, and revision topics: [naming-audit.md](naming-audit.md)

## Design direction

**Professional editorial learning system:** warm neutral surfaces, restrained ink-indigo accent, strong typographic hierarchy, clear reading widths, flat document structure, and quiet interaction feedback.

Recommended type system:

- UI and body: Geist Sans or another characterful neutral sans.
- Editorial display and selected article headings: Newsreader.
- Code, counters, shortcuts, and metadata: Geist Mono or SF Mono.

Recommended palette direction:

- Light canvas: warm off-white rather than blue-white.
- Text: charcoal rather than pure black.
- Accent: a quieter, less saturated ink-indigo.
- Surfaces: two neutral levels with borders doing most of the separation.
- Dark mode: charcoal with the same accent identity, stronger body-text contrast than the current theme.

## Product principles

1. Lead users to a next action within one screen.
2. Separate practice, reading, and last-day revision as clear modes.
3. Make long-form content feel like a publication, not an application dashboard.
4. Use cards only when a container communicates a real grouping or action.
5. Keep one primary action per page region.
6. Preserve all existing route paths and browser-storage keys.
7. Mobile receives complete navigation and controls, not reduced functionality.
8. Accessibility, loading, empty, error, and offline-safe states are part of the design.

## Workstreams and order

| Order | Plan | Priority | Depends on |
| --- | --- | --- | --- |
| 1 | [Foundation, theme, and typography](01-foundation-theme-typography/plan.md) | P0 | None |
| 2 | [Navigation and information architecture](02-navigation-information-architecture/plan.md) | P0 | Plan 01 tokens |
| 3 | [Homepage and content discovery](03-homepage-content-discovery/plan.md) | P0 | Plans 01-02 |
| 4 | [Reading and tutorial experience](04-reading-tutorial-experience/plan.md) | P0 | Plans 01-02 |
| 5 | [Worksheet and practice experience](05-worksheet-practice-experience/plan.md) | P1 | Plans 01-02 |
| 6 | [Responsive, accessibility, and states](06-responsive-accessibility-states/plan.md) | P0, continuous | Plans 01-05 |
| 7 | [SEO, performance, and trust](07-seo-performance-trust/plan.md) | P1 | Stable page structure |
| 8 | [Content architecture and editorial quality](09-content-architecture-editorial-quality/plan.md) | P0 | Plans 02-05 |
| 9 | [Validation and rollout](08-validation-rollout/plan.md) | P0 before release | All plans |

## Suggested release slices

1. **Foundation release:** tokens, fonts, header/mobile navigation, active states, and shared page shell.
2. **Discovery release:** homepage and module-library restructuring.
3. **Learning release:** long-form reading and worksheet improvements.
4. **Editorial release:** learning-path map, content-mode labels, cross-links, behavioral personalization, source freshness, and canonical case-study structure.
5. **Quality release:** responsive/accessibility fixes, system states, metadata, performance, and final validation.

## Success measures

- A new visitor can distinguish Practice, Case Studies, and Last-Day Prep without opening the guide.
- Every primary destination is reachable from the mobile header.
- Long-form article body text stays between 60 and 72 characters per line.
- Mobile tabs and worksheet actions remain discoverable at 320 px without clipped labels.
- WCAG AA contrast and visible keyboard focus pass in both themes.
- No existing URL or `fd:v1:*` localStorage key changes.
- No regression in content parsing, progress restoration, answer-key reveals, search, export, or print.
- Every content family states who it is for, what prior knowledge it assumes, what the user will be able to do, and where to continue.
- Every public behavioral answer is either generalized for public use or clearly marked as a private personalization template.
- Lighthouse targets: Accessibility 95+, Best Practices 95+, SEO 95+, and no material Core Web Vitals regression.

## Scope boundary

This plan does not migrate frameworks, add accounts, replace the markdown pipeline, rewrite source tutorials, or deploy changes. It creates the design and implementation roadmap only.
