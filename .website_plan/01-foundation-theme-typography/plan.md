# Plan 01: Foundation, theme, and typography

## Outcome

Create a restrained editorial design system that supports application controls, fillable worksheets, and long-form technical reading without making every surface look like a SaaS card.

## Direction

- Replace Inter with Geist Sans for UI/body and introduce Newsreader only for high-level editorial headings and selected quotations.
- Keep monospace for code, counters, keyboard shortcuts, and compact technical metadata.
- Move from cool blue-white and saturated indigo toward warm paper neutrals and a quieter ink-indigo accent.
- Preserve light and dark themes. Make light the visual reference and dark a full reading theme with stronger text contrast.
- Define typography, spacing, radius, border, focus, shadow, and motion tokens in one place.
- Use flat sections and whitespace by default. Reserve containers for interactive groups, progress, and calls to action.

## Primary files

- `site/src/app/globals.css`
- `site/src/app/layout.tsx`
- Shared component class names under `site/src/components/`

## Acceptance criteria

- The type hierarchy distinguishes display, page title, section title, body, metadata, and code.
- Article text is at least 1rem on mobile and approximately 1.0625-1.125rem on desktop.
- Main reading paragraphs stay between 60 and 72 characters per line.
- One accent family is used across both themes.
- Shadows are rare, tinted, and limited to floating overlays such as search.
- Both themes meet WCAG AA contrast.
- No content, URL, interaction, or storage behavior changes.

