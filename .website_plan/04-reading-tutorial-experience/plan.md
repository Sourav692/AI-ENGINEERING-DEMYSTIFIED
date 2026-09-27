# Plan 04: Reading and tutorial experience

## Outcome

Make case studies and tutorials comfortable for sustained reading, easy to scan, and easy to resume on both desktop and mobile.

## Recommendations

- Use an editorial article shell with a 60-72 character reading column and separate wide lanes for tables, diagrams, and code.
- Increase body size and contrast; use Newsreader selectively for article display headings while keeping technical body copy in Geist Sans.
- Strengthen h2-h4 scale, spacing, and hierarchy. Reduce reliance on uppercase metadata headings.
- Keep the desktop table of contents, add current-section feedback, and turn it into a mobile “On this page” disclosure.
- Make document tabs sticky below the site header. On mobile, show overflow affordance and keep the active tab fully visible.
- Add explicit previous/next document actions and a clear return to the case-study index.
- Keep reading progress lightweight and secondary.

## Primary files

- `site/src/components/CaseStudyView.tsx`
- `site/src/app/globals.css`
- `site/src/app/modules/[module]/[track]/[scenario]/page.tsx`
- Markdown rendering components in `site/src/components/Blocks.tsx`

## Acceptance criteria

- Article body is readable without zoom at 320 px.
- No document-tab label is clipped or unreachable.
- Mobile users can open section navigation without returning to the top.
- Tables and diagrams retain horizontal scrolling without shrinking text.
- Heading anchors land below sticky site and tab navigation.
- Print output remains clean and complete.

