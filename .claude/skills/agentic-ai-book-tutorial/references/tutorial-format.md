# Tutorial Format Reference

This is the fixed structure and visual system every tutorial (chapter, part, or
single-concept) must follow, so the whole set reads as one coherent series.

## Module structure (repeats for every concept)

Each concept in the source unit becomes one module, in this fixed order:

1. **Title** — the concept's own name from the book, not a reworded version.
2. **One-liner** — a single bolded sentence: what it is, in plain words.
3. **Why it exists** — 1-3 sentences: the problem it solves, grounded in a
   small concrete scenario (the book's own case study/example if it has one
   for this concept, otherwise one small invented illustration, clearly
   informal in tone — "picture a..."). Skip only if the one-liner already
   makes it obvious and no example is needed.
4. **Diagram** — exactly one, sized to the content (see "Choosing a diagram").
5. **Key points** — 2-5 short bullets: the parts of the concept a reader must
   retain. Numbers, named states/types, and trade-offs live here, not in prose.
6. *(conditional)* **🎯 OpenAI Interview Pointer** — 1-2 sentences.
7. *(conditional)* **🔍 Deep Dive** — collapsed by default in HTML, a clearly
   marked blockquote in Markdown. Only per the trigger rule in SKILL.md.

A chapter/part tutorial opens with a 2-4 sentence framing (why this
chapter/part exists, one line on how it connects to neighboring chapters) and
closes with a **Cheat Sheet** — one row per concept, one line each: what it is
+ the single fact most worth remembering. Where the unit is a whole Part, the
Interview Drill (if the book has one for that Part) becomes its own final
module: each of the 5 questions gets a one-line prompt + a one-line "what a
strong answer covers" summary — not a full worked answer, since the book's own
worked answers are the deep-dive material, not something to reproduce
verbatim.

## Choosing a diagram

Pick the diagram type that actually matches the concept's shape — never
default to the same flowchart for everything:

| Content shape | Diagram type | Example from the book |
|---|---|---|
| Steps in sequence / a loop | `flowchart` (Mermaid) or `sequenceDiagram` | bounded control loop, seven-step design method |
| Components and who talks to whom | `flowchart` with subgraphs | six-component reference architecture, tool gateway |
| A decision tree / branching logic | `flowchart` with diamond decision nodes | escalation router, degradation ladder |
| A spectrum / slider / tiered scale | a simple HTML/CSS bar or Mermaid left-to-right flowchart | autonomy slider, agency spectrum, evaluation pyramid |
| A comparison of options | a small table, or a 2-column Mermaid/HTML side-by-side | four coordination topologies, three hybrid edge topologies |
| A formula or arithmetic relationship | rendered as a boxed equation + one worked micro-example, no diagram needed if a table conveys it better | readiness/expected-return formula, Little's law |
| A taxonomy / family of things | a Mermaid `flowchart` tree or a grouped table | 30 design patterns in 6 families, four memory tiers |
| A timeline / lifecycle | `sequenceDiagram` or a horizontal Mermaid flowchart | A2A task lifecycle, model lifecycle on edge hardware |

If a single diagram would need to cram in more than ~7 nodes to represent one
concept faithfully, that's a signal the concept should be split into two
modules rather than one overloaded diagram.

## Markdown structure

- Filename: `chXX_kebab_title.md` / `partX_kebab_title.md` / `concept_kebab_title.md`
- Real headers: `#` for the unit title, `##` per concept module, `###` for
  Key Points / Deep Dive if needed (usually just bold labels + bullets suffice
  under a `##`).
- Every diagram as a fenced ` ```mermaid ` block.
- Callouts as blockquotes with bolded emoji labels:
  - `> **🎯 OpenAI Interview Pointer**`
  - `> **🔍 Deep Dive**`
- Cheat Sheet as a real Markdown table, two columns: Concept | One line that matters most.
- No filler transitions between modules ("Now let's look at...") — a `##`
  header is transition enough.

## HTML structure and design system

Self-contained single file: inline `<style>`, Mermaid.js from
`https://cdnjs.cloudflare.com` as the only external dependency. Mirrors the
Markdown module order exactly.

### Layout

- A masthead: unit title, one-line framing, a pill-style quick-nav row
  linking to each module's anchor.
- Each concept as its own card: title bar → one-liner → why-it-exists (if
  present) → diagram → key points list → optional pointer callout → optional
  collapsed deep dive.
- `<details><summary>🔍 Deep Dive</summary>...</details>` for deep dives —
  collapsed by default, native disclosure widget, no JS needed.
- OpenAI Interview Pointer as a visually distinct callout box (accent border +
  icon), never blended into the card body.
- Cheat Sheet as a compact two-column grid/table near the end, visually
  distinct (dark or accent-colored section) so it's the thing a reader
  screenshots.
- Interview Drill module (Part-level tutorials only): 5 small cards, one per
  drill question, each with the question and a 1-2 line "what a strong answer
  covers" summary.

### Palette and type — reuse exactly across every tutorial in the set

A clean, technical, high-contrast palette distinct from prose-heavy book
design — this is a study tool, not a novel, so it should feel scannable and
modern:

```css
:root {
  --bg: #0F1419;            /* page background, dark technical feel */
  --bg-raised: #161C24;     /* card background */
  --ink: #E8EDF3;           /* body text on dark */
  --ink-soft: #A8B3C2;
  --ink-faint: #6B7686;
  --rule: #2A323D;
  --accent: #5B8DEF;        /* primary accent - links, module titles */
  --accent-bg: #16223B;
  --accent-border: #2E4A80;
  --openai-teal: #10A37F;   /* OpenAI Interview Pointer callout only */
  --openai-teal-bg: #0D2B24;
  --openai-teal-border: #1C5C4A;
  --amber: #E0A72E;         /* Deep Dive marker */
  --amber-bg: #2B2412;
  --green: #4CAF7D;         /* key points check marks */
  --code-bg: #06090C;
  --code-fg: #D8E2EC;
}
```

- **Display/headers:** "Space Grotesk" or system sans fallback — clean,
  geometric, technical.
- **Body:** Inter.
- **Code/labels:** JetBrains Mono.
- Load via `@import url(...)` from Google Fonts.
- Mermaid init: `theme: 'base'` with `themeVariables` mapped to the palette
  above (`background: '#161C24'`, `primaryColor: '#16223B'`,
  `primaryBorderColor: '#2E4A80'`, `lineColor: '#5B8DEF'`, `textColor: '#E8EDF3'`)
  so diagrams look native to the page, not like a default Mermaid render.
- The **OpenAI Interview Pointer** callout always uses `--openai-teal` (a
  distinct color from everything else) so it's instantly scannable when
  flipping through for last-minute review — the entire point of this callout
  is to be spottable at a glance.
- Responsive to mobile (the user primarily reads on a phone-width screen —
  single column, generous tap targets, cards never wider than viewport,
  diagrams scale via Mermaid's `useMaxWidth`), visible focus states, respects
  `prefers-reduced-motion`. No login, no external API calls, no tracking.

### Verification before presenting

```bash
grep -c '<div' file.html   # compare against
grep -c '</div>' file.html # — must match
```

Confirm every concept from Step 1's research list appears as its own
`<article class="concept">` (HTML) / `##` (Markdown) — cross-check against the
book's chapter contents so nothing was silently dropped, and confirm nothing
was padded past what the density rule allows.
