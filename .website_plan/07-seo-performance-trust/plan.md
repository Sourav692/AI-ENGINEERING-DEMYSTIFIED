# Plan 07: SEO, performance, and trust

## Outcome

Make the site credible when shared, discoverable for interview-prep searches, and fast despite large content libraries and Mermaid diagrams.

## Recommendations

- Add a metadata base, canonical URLs, Twitter cards, and a designed social image.
- Generate sitemap and robots configuration for public pages while avoiding unhelpful duplicate HTML artifact indexing if needed.
- Add `BreadcrumbList`, `Course`, and `LearningResource` structured data where accurate.
- Strengthen per-module and per-case metadata with concrete descriptions.
- Lazy-load heavy Mermaid/runtime work and keep search indexing off the critical path.
- Add a clear source/attribution route and a short privacy/storage explanation.
- Consider a custom domain after design validation; keep deployment out of the redesign implementation until approval.

## Primary files

- `site/src/app/layout.tsx`
- Route metadata functions
- New `sitemap.ts`, `robots.ts`, and social-image route/assets
- `site/src/components/Diagram.tsx`
- `site/src/components/SearchDialog.tsx`

## Acceptance criteria

- Every indexable route has a unique title, description, canonical URL, and share preview.
- Sitemap includes intended public routes only.
- Structured data matches visible content and passes validation.
- Initial page load does not eagerly execute Mermaid or download unnecessary search data.
- Privacy/storage behavior and content attribution are easy to find.

