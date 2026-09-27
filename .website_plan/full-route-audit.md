# Full-route audit

## Scope

Audit date: 2026-09-27  
Deployment: `https://forward-deployed-sigma.vercel.app`

The public inventory contains 117 unique URLs:

| Family | Count | Coverage |
| --- | ---: | --- |
| Shared pages: home, guide, Last-Day Prep hub | 3 | HTTP and structural checks; desktop/mobile visual review |
| Module landing pages | 3 | HTTP and structural checks; representative visual review |
| Worksheet and behavioral practice pages | 41 | HTTP and parser checks; both distinct practice layouts visually reviewed |
| Case-study reading pages | 33 | HTTP and parser checks; one-, two-, four-, and five-tab variants reviewed |
| Concise interview modules | 18 | HTTP and static-HTML checks; representative mobile/desktop review |
| One-page memory cards | 18 | HTTP and static-HTML checks; representative mobile/print-oriented review |
| Trigger-to-concept sheet | 1 | HTTP, static-HTML, and mobile visual review |
| **Total** | **117** | |

The audit treats repeated content instances differently from layout variants. Every URL received automated availability and source-structure checks. Every distinct interactive or visual layout received manual visual review. It would be misleading to describe all 117 pages as individually reviewed pixel by pixel.

## Validation results

- All 117 deployed URLs returned HTTP 200 on 2026-09-27.
- `npm run check:content` passed for every worksheet, answer key, and case study.
- The content check parsed 149 Mermaid diagrams successfully.
- `next build --webpack` completed successfully, including TypeScript checks and static generation.
- All 37 standalone HTML files contain a document title, language, viewport metadata, an `h1`, and a `main` landmark.
- The default Turbopack build could not complete in the audit environment because its CSS processing worker attempted to bind a local port and received `Operation not permitted`. The webpack production build establishes that the application and generated routes compile successfully; this environment-specific Turbopack behavior should still be rechecked in normal CI.

## Cross-page findings added to the plan

### Standalone prep pages are an isolated experience

All 37 standalone pages omit the shared application header and a route back to the Last-Day Prep hub. They use their own Plus Jakarta Sans/JetBrains Mono theme and follow system color preference, while the main app uses its own tokens and manual theme state. This breaks continuity immediately after a user leaves the hub.

None of the 37 pages has a skip link. Nineteen pages have a contents navigation landmark; the 18 memory cards do not. The print-focused memory cards still need a small screen-reader and on-screen navigation strategy that disappears cleanly in print.

### Five-tab mobile navigation hides choices

On the five-document Enterprise Chatbot page at a 375 px CSS viewport, the tab row extends to approximately 616 px. The fourth tab starts beyond the initial content edge and the fifth tab is entirely outside the first view. Horizontal scrolling prevents global page overflow, but there is no strong affordance telling users that more documents exist.

### Previous/next can cross learning contexts

The first behavioral hiring-manager exercise links backward to “Enterprise Chatbot Platform,” which belongs to the preceding practice module. The registry order is technically consistent, but the interface does not explain this context switch. Navigation scope needs a product decision and consistent labels.

### Shared mobile navigation remains incomplete

The Next.js header still hides its primary destinations on small screens. Search and theme controls remain visible, but users cannot reach Practice, Last-Day Prep, or Guide from the header. This remains the highest-priority shared-shell fix.

## Review matrix for implementation

Use these representatives for visual regression while still checking the generated route inventory for availability:

| Variant | Representative |
| --- | --- |
| Homepage | `/` |
| Guide | `/guide` |
| Module landing | `/modules/15-fde-case-studies` |
| Worksheet | `/modules/01-customer-discovery-and-decomposition/core/internal-knowledge-assistant` |
| Behavioral practice | `/modules/14-behavioural-and-leadership-round/hiring-manager/ambiguity-and-discovery` |
| Four-tab case study | `/modules/15-fde-case-studies/knowledge-retrieval/enterprise-knowledge-assistant` |
| Five-tab case study | `/modules/15-fde-case-studies/standalone-designs/enterprise-chatbot-platform` |
| Two-tab case study | `/modules/15-fde-case-studies/standalone-designs/recruiting-platform` |
| One-tab case study | `/modules/15-fde-case-studies/standalone-designs/personal-assistant-with-memory` |
| Last-Day Prep hub | `/fde-last-day-prep` |
| Concise module | `/fde-last-day-prep/module-18-end-to-end-fde-interview-execution/concise-interview-module.html` |
| Memory card | `/fde-last-day-prep/module-18-end-to-end-fde-interview-execution/one-page-memory-card.html` |
| Trigger sheet | `/fde-last-day-prep/trigger-to-concept-cheat-sheet/trigger-to-concept-cheat-sheet.html` |

## Required recheck after implementation

1. Regenerate the inventory from `site/content/manifest.json` and `site/public/fde-last-day-prep`.
2. Require HTTP 200 for every preview URL.
3. Run content parsing, lint, TypeScript, and a production build.
4. Run visual regression on every representative above in both themes at 320, 390, 768, 1024, and 1440 px where applicable.
5. Keyboard-test the shared header, mobile menu, search, worksheet toolbar, tab variants, local contents navigation, and standalone-page return route.
6. Verify print output for worksheets, all case-study document variants, concise modules, memory cards, and the trigger sheet.
