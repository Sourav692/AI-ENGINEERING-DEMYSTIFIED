# Current website audit

## What already works

- The content model supports worksheets and long-form case studies without duplicating content logic.
- Search, local progress, reveal-on-demand answers, export, print, theme switching, and reduced-motion behavior are meaningful product features.
- The site uses semantic landmarks, a skip link, visible focus styles, descriptive control labels, and static generation.
- The existing page width is controlled, and long-form pages already have a desktop table of contents.
- The design uses a single accent and consistent tokens across light and dark themes.

## Highest-impact issues

### Information architecture

- The top navigation disappears below the `sm` breakpoint with no mobile replacement. Search and theme remain, but Modules, Last-Day Prep, and How to use are unavailable from the header.
- The homepage mixes three different systems: a 15-module roadmap, a 33-case-study library, and an 18-module last-day course. Their relationship is not explained clearly.
- Twelve planned modules occupy most of the homepage, while the available practice paths receive less hierarchy.
- Header links do not expose a current-page state.
- “Modules” is too broad for a site that also has Case Studies and Last-Day Prep.

### Visual system

- Inter, indigo, rounded-xl cards, pill badges, and repeated border-plus-surface containers create a familiar SaaS template rather than a distinctive editorial learning identity.
- Many regions use the same card treatment, so featured content, navigation, progress, and planned content compete at similar visual weight.
- Small uppercase metadata appears frequently and weakens hierarchy when repeated.
- Dark mode is polished but body and metadata contrast feels subdued in long reading sessions.
- Light mode is closer to the desired editorial direction but still feels cool and application-like.

### Homepage and discovery

- The hero explains the product accurately but uses a long paragraph before users see the available learning modes.
- The FDE Case Studies and Last-Day Prep promos are visually identical, so neither establishes a distinct purpose.
- “3 of 15 modules available” can read as an unfinished product even though the site has extensive usable content elsewhere.
- The live and planned module cards form one long grid. Planned items add browsing cost without enabling an action.

### Reading experience

- Long-form article text and the desktop table of contents are small for sustained reading.
- Article headings rely on uppercase metadata styling rather than an editorial heading scale.
- The mobile document tabs overflow horizontally; “Full Pack” can be partially clipped without a strong scroll affordance.
- The five-tab Enterprise Chatbot variant is more severe: at 375 px, “Tutorial V1” begins outside the initial view and “Tutorial V1 (Uncondensed)” is fully off-screen.
- The desktop TOC disappears on mobile instead of becoming a compact disclosure or jump menu.
- Long documents need stronger section rhythm, current-section feedback, and a clearer return/continue path.
- Previous/next navigation follows the global scenario registry, so the first behavioral exercise links backward into a different practice module.

### Standalone Last-Day Prep pages

- The 37 generated HTML pages are visually and structurally separate from the Next.js site shell.
- None provides a direct route back to the Last-Day Prep hub or the main site navigation.
- None has a keyboard skip link. The 18 memory cards also have no local navigation landmark.
- Their theme follows only `prefers-color-scheme`; it does not share the manual theme choice used by the main site.
- The generated pages load a separate font and color system, which makes the transition from the hub feel like a different product.
- Heading permalink controls contribute extra accessible content to headings and need screen-reader review.

### Worksheet experience

- The sticky mobile toolbar fits progress, status, timer, reveal, export, print, and reset into a tight two-row area.
- Secondary and destructive actions have similar prominence to high-frequency practice actions.
- Breadcrumbs and scenario metadata consume substantial vertical space on mobile.
- Section navigation is entirely linear; long worksheets lack a compact overview of answered and unanswered sections.

### Responsive and accessibility

- There is no mobile site menu.
- Several controls and metadata labels use text below comfortable mobile reading size.
- Horizontal tab overflow and dense toolbar actions need explicit keyboard, touch, and overflow testing.
- There are no route-level `loading.tsx`, `error.tsx`, or custom `not-found.tsx` experiences.
- Active navigation states and `aria-current` are absent.
- Standalone Last-Day Prep pages need the same keyboard, focus, landmark, contrast, and responsive acceptance criteria as app routes.

### Trust, SEO, and finish

- Metadata has basic Open Graph fields but no canonical base, share image, Twitter metadata, sitemap, robots configuration, or structured learning data.
- The footer communicates local-only storage well, but source attribution, privacy explanation, and core navigation are scattered.
- The default Vercel subdomain is functional but a custom domain would improve trust when the product is ready.

## Constraints to preserve

- Do not change existing URLs.
- Do not rename `fd:v1:*` localStorage keys.
- Do not replace the markdown sync and parser architecture.
- Do not remove search, export, print, theme, or progress features.
- Treat `site/content/` as generated content and keep source markdown canonical.
- Use the installed Next.js 16 and Tailwind 4 patterns, consulting local Next.js documentation before implementation.
