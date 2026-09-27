/**
 * Syncs the Last-Day Review collection from `06_Interview_Prep/Last_Day_Prep/`.
 *
 * Two outputs, because the collection has two shapes:
 *
 *  - The Roadmap and the Rapid Revision Guide are markdown. They are copied into
 *    `content/last-day/` and rendered by the app's reading pipeline, so they get the
 *    site's theme, contents list and search like every other reading page.
 *
 *  - The eighteen reviews and the trigger sheet are finished HTML documents with their
 *    own styles and scripts. They are copied into `public/fde-last-day-prep/` as-is,
 *    except for a small set of edits made here rather than in the sources:
 *      · visible names follow `REVIEWS` in src/lib/editorial.ts ("Module 5 — RAG &
 *        Enterprise Data" becomes "Review 05 — Retrieval-Augmented Generation and
 *        Enterprise Data"), so the 18-part review never reads as a second set of
 *        "modules" beside the 15-part roadmap;
 *      · every "Module N" reference becomes a link to that review;
 *      · a bar at the top links back to the hub, to the neighbouring reviews, and to
 *        the practice worksheets and case studies to learn from first or go deeper.
 *
 * Paths, file names and anchors are untouched, so existing links keep working. Every
 * edit that must happen is asserted: a source whose heading changed shape fails the
 * sync instead of shipping half-renamed.
 */

import { existsSync } from 'node:fs'
import { cp, mkdir, readdir, readFile, rm, writeFile } from 'node:fs/promises'
import { join } from 'node:path'
import {
  LAST_DAY,
  LAST_DAY_GUIDES,
  REVIEW_DOCS,
  REVIEWS,
  TRIGGER_SHEET,
  reviewLabel,
} from '../src/lib/editorial.ts'

const byNumber = new Map(REVIEWS.map((r) => [r.number, r]))

function review(n) {
  const r = byNumber.get(Number(n))
  if (!r) throw new Error(`Last-Day source refers to Module ${n}, which has no entry in REVIEWS`)
  return r
}

const hrefOf = (r, doc = 'concise') => `${LAST_DAY.href}/${r.dir}/${REVIEW_DOCS[doc].file}`

const escapeHtml = (text) =>
  text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

// ------------------------------------------------------------------ markdown guides

/**
 * The guides use `#` for their top-level sections; the reading pipeline treats the
 * first `#` as the title and splits sections at `##`. So everything after the title
 * moves down one level. Fenced blocks are copied through untouched apart from the
 * Module → Review rename, which keeps the text diagrams consistent with the headings.
 */
function transformGuide(markdown) {
  const out = []
  let inFence = false
  let seenTitle = false
  for (const line of markdown.split('\n')) {
    if (/^\s*(```|~~~)/.test(line)) {
      inFence = !inFence
      out.push(line)
      continue
    }
    if (inFence) {
      out.push(line.replace(/Module\s+(\d+)\s+—/g, (_, n) => `${reviewLabel(Number(n))} —`))
      continue
    }
    const heading = line.match(/^(#{1,5})\s+(.*)$/)
    if (heading) {
      if (!seenTitle && heading[1] === '#') {
        seenTitle = true
        out.push(line)
        continue
      }
      const level = '#'.repeat(heading[1].length + 1)
      const mod = heading[2].match(/^Module\s+(\d+)\s+—\s+.*$/)
      if (mod) {
        const r = review(mod[1])
        out.push(`${level} ${reviewLabel(r.number)} — ${r.title}`, '')
        out.push(`*[Open ${reviewLabel(r.number)} →](${hrefOf(r)})*`)
        continue
      }
      out.push(`${level} ${heading[2]}`)
      continue
    }
    out.push(
      line.replace(/\bModule\s+(\d+)\b/g, (_, n) => `[${reviewLabel(Number(n))}](${hrefOf(review(n))})`),
    )
  }
  return out.join('\n')
}

// ------------------------------------------------------------------ static HTML

/**
 * Applies `fn` to text between tags only — never to attributes, and never inside
 * <script>, <style> or an existing <a>, where adding a link would nest anchors.
 */
function mapText(html, fn) {
  let depthA = 0
  let raw = null
  return html.replace(/(<[^>]+>)|([^<]+)/g, (whole, tag, text) => {
    if (tag) {
      const name = tag.match(/^<\/?\s*([a-zA-Z0-9]+)/)?.[1]?.toLowerCase()
      const closing = tag.startsWith('</')
      if (name === 'script' || name === 'style') raw = closing ? null : name
      if (name === 'a') depthA += closing ? -1 : 1
      return tag
    }
    if (raw) return text
    return fn(text, depthA > 0)
  })
}

function replaceRequired(html, from, to, what) {
  if (!html.includes(from)) throw new Error(`${what}: expected to find ${JSON.stringify(from)}`)
  return html.split(from).join(to)
}

const linkReviews = (html) =>
  mapText(html, (text, insideLink) =>
    text.replace(/\bModule\s+(\d+)\b/g, (_, n) => {
      const r = review(n)
      return insideLink ? reviewLabel(r.number) : `<a href="${hrefOf(r)}">${reviewLabel(r.number)}</a>`
    }),
  )

const SITEBAR_CSS = `
<style>
  .fd-sitebar { font: 500 0.8125rem/1.5 var(--sans, system-ui, sans-serif); color: var(--text-2, #555);
    background: var(--surface, #fff); border-bottom: 1px solid var(--border-strong, #ddd);
    padding: 0.625rem 1rem; display: grid; gap: 0.25rem; }
  .fd-sitebar .fd-row { display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.25rem 0.875rem;
    max-width: 72rem; margin: 0 auto; width: 100%; }
  .fd-sitebar a { color: var(--primary, #2952cc); text-decoration: none; font-weight: 600; }
  .fd-sitebar a:hover { text-decoration: underline; }
  .fd-sitebar .fd-label { font-weight: 700; color: var(--text, #111); }
  .fd-sitebar .fd-mode { font-size: 0.75rem; }
  .fd-sitebar .fd-pn { margin-left: auto; display: flex; gap: 0.875rem; }
  @media print { .fd-sitebar { display: none; } }
</style>`

function sitebar({ label, mode, prev, next, rows = [] }) {
  const link = (href, text) => `<a href="${href}">${escapeHtml(text)}</a>`
  const pn = [prev && link(prev.href, `← ${prev.text}`), next && link(next.href, `${next.text} →`)]
    .filter(Boolean)
    .join('')
  return (
    `<div class="fd-sitebar" role="navigation" aria-label="Last-Day Review">` +
    `<div class="fd-row">${link(LAST_DAY.href, `← ${LAST_DAY.title}`)}` +
    `<span class="fd-label">${escapeHtml(label)}</span>` +
    `<span class="fd-mode">${escapeHtml(mode)}</span>` +
    (pn ? `<span class="fd-pn">${pn}</span>` : '') +
    `</div>` +
    rows
      .filter((r) => r.links.length)
      .map(
        (r) =>
          `<div class="fd-row"><span class="fd-label">${escapeHtml(r.label)}</span>` +
          r.links.map((l) => link(l.href, l.title)).join(' · ') +
          `</div>`,
      )
      .join('') +
    `</div>`
  )
}

function injectSitebar(html, bar, what) {
  if (!/<body[^>]*>/.test(html)) throw new Error(`${what}: no <body> tag`)
  return html
    .replace('</head>', `${SITEBAR_CSS}\n</head>`)
    .replace(/<body([^>]*)>/, `<body$1>${bar}`)
}

async function transformReview(html, r, doc, oldTitle, pages) {
  const what = `${r.dir}/${REVIEW_DOCS[doc].file}`
  const oldHeading = `Module ${r.number} — ${escapeHtml(oldTitle)}`
  const newHeading = `${reviewLabel(r.number)} — ${escapeHtml(r.title)}`
  const n = String(r.number).padStart(2, '0')

  html = replaceRequired(html, oldHeading, newHeading, what)
  // The heading anchors' aria-labels escape the title a second time (`&amp;amp;`).
  html = html.split(`Module ${r.number} — ${escapeHtml(escapeHtml(oldTitle))}`).join(newHeading)
  html = html.replace(`<span class="doc-id">MOD·${n}</span>`, `<span class="doc-id">REV·${n}</span>`)

  if (doc === 'concise') {
    html = replaceRequired(html, '— Concise Interview Module</title>', `— ${REVIEW_DOCS.concise.label} · Forward Deployed</title>`, what)
    html = replaceRequired(html, 'Concise Interview Module — FDE Discovery Protocol', `${REVIEW_DOCS.concise.label} — ${LAST_DAY.title}`, what)
    html = replaceRequired(html, '>Memory card →</a>', '>Recall card →</a>', what)
    html = html.split('CONCISE INTERVIEW MODULE').join(REVIEW_DOCS.concise.label)
  } else {
    html = replaceRequired(html, '— One-Page Memory Card</title>', `— ${REVIEW_DOCS.card.label} · Forward Deployed</title>`, what)
    html = replaceRequired(html, 'One-Page Memory Card — FDE Discovery Protocol', `${REVIEW_DOCS.card.label} — ${LAST_DAY.title}`, what)
    html = replaceRequired(html, '>← Concise module</a>', '>← Interview review</a>', what)
    html = html
      .split(`ONE-PAGE MEMORY CARD — ${escapeHtml(oldTitle)}`)
      .join(`${REVIEW_DOCS.card.label} — ${escapeHtml(r.title)}`)
  }
  html = html.replace(/(<meta name="description" content=")[^"]*"/, `$1${escapeHtml(`${reviewLabel(r.number)} — ${r.title}: ${r.blurb}`)}"`)
  html = linkReviews(html)

  const prev = byNumber.get(r.number - 1)
  const next = byNumber.get(r.number + 1)
  const resolve = (refs) =>
    refs.map((ref) => {
      const page = pages.get(ref)
      if (!page) throw new Error(`${what}: REVIEWS links to "${ref}", which is not a published page`)
      return page
    })
  const bar = sitebar({
    label: `${reviewLabel(r.number)} of ${REVIEWS.length}`,
    mode: 'Revision — assumes you have already studied this topic',
    prev: prev && { href: hrefOf(prev, doc), text: reviewLabel(prev.number) },
    next: next && { href: hrefOf(next, doc), text: reviewLabel(next.number) },
    rows:
      doc === 'concise'
        ? [
            { label: 'New to this? Learn first:', links: resolve(r.learnFirst) },
            { label: 'Go deeper:', links: resolve(r.goDeeper) },
          ]
        : [],
  })
  return injectSitebar(html, bar, what)
}

function transformTriggerSheet(html) {
  const what = TRIGGER_SHEET.file
  const oldTitle = 'FDE Interview - Trigger → Concept Cheat Sheet'
  html = replaceRequired(html, `<title>${oldTitle}</title>`, `<title>${TRIGGER_SHEET.title} · Forward Deployed</title>`, what)
  html = replaceRequired(html, `>${oldTitle}<a class="anchor"`, `>${TRIGGER_SHEET.title}<a class="anchor"`, what)
  html = html.split(`Link to ${oldTitle}`).join(`Link to ${TRIGGER_SHEET.title}`)
  html = html.replace('questions, or modules"', 'questions, or reviews"')
  html = html.replace(/mapping common prompts to concepts, questions, and modules/, 'mapping common prompts to concepts, questions, and reviews')

  // Section headings: "Modules 1-3" -> "Reviews 01–03", "Module 4" -> "Review 04" —
  // in the text and in the heading anchors' aria-labels.
  const rename = (text) =>
    text
      .replace(/\bModules\s+(\d+)\s*[-–]\s*(\d+)\b/g, (_, a, b) => `Reviews ${String(a).padStart(2, '0')}–${String(b).padStart(2, '0')}`)
      .replace(/\bModule\s+(\d+)\b/g, (_, n) => reviewLabel(Number(n)))
  html = mapText(html, rename).replace(/aria-label="([^"]*)"/g, (_, v) => `aria-label="${rename(v)}"`)

  // The last column of every trigger table names the review(s) covering the row.
  let tables = 0
  html = html.replace(/<table>[\s\S]*?<\/table>/g, (table) => {
    if (!table.includes('<th>Module</th>')) return table
    tables++
    return table
      .replace('<th>Module</th>', '<th>Review</th>')
      .replace(/<td>([\d,\s]+)<\/td>(\s*<\/tr>)/g, (_, nums, end) => {
        const links = nums
          .split(',')
          .map((n) => n.trim())
          .filter(Boolean)
          .map((n) => {
            const r = review(n)
            return `<a href="${hrefOf(r)}" title="${escapeHtml(r.title)}">${String(r.number).padStart(2, '0')}</a>`
          })
        return `<td>${links.join(', ')}</td>${end}`
      })
  })
  if (tables === 0) throw new Error(`${what}: found no trigger tables with a Module column`)

  return injectSitebar(
    html,
    sitebar({ label: TRIGGER_SHEET.title, mode: 'Revision — searchable index of all eighteen reviews' }),
    what,
  )
}

// ------------------------------------------------------------------ entry point

/**
 * `pages` maps `track/slug` to `{ title, href }` for every published page, so the
 * learn-first and go-deeper links are checked against what actually exists.
 */
export async function syncLastDay({ repoRoot, siteDir, outDir, pages }) {
  const root = join(repoRoot, '06_Interview_Prep', 'Last_Day_Prep')
  if (!existsSync(root)) throw new Error(`Last-Day sources not found at ${root}`)

  // Markdown guides -> content/last-day/
  const guideDir = join(outDir, 'last-day')
  await mkdir(guideDir, { recursive: true })
  for (const guide of LAST_DAY_GUIDES) {
    const markdown = await readFile(join(root, guide.source), 'utf8')
    await writeFile(join(guideDir, `${guide.id}.md`), transformGuide(markdown))
  }

  // Static HTML -> public/fde-last-day-prep/
  const htmlSource = join(root, 'html')
  const htmlOut = join(siteDir, 'public', 'fde-last-day-prep')
  const dirs = (await readdir(htmlSource, { withFileTypes: true })).filter((e) => e.isDirectory()).map((e) => e.name)
  const expected = [...REVIEWS.map((r) => r.dir), TRIGGER_SHEET.dir]
  const unknown = dirs.filter((d) => !expected.includes(d))
  const missing = expected.filter((d) => !dirs.includes(d))
  if (unknown.length || missing.length) {
    throw new Error(
      `Last-Day html folders do not match REVIEWS (unknown: ${unknown.join(', ') || '—'}; missing: ${missing.join(', ') || '—'})`,
    )
  }

  await rm(htmlOut, { recursive: true, force: true })
  await cp(htmlSource, htmlOut, { recursive: true })

  for (const r of REVIEWS) {
    const source = await readFile(join(root, `${r.dir}.md`), 'utf8')
    const heading = source.split('\n')[0].match(/^#\s+Module\s+\d+\s+—\s+(.+)$/)
    if (!heading) throw new Error(`${r.dir}.md: first line is not "# Module N — Title"`)
    for (const doc of Object.keys(REVIEW_DOCS)) {
      const file = join(htmlOut, r.dir, REVIEW_DOCS[doc].file)
      await writeFile(file, await transformReview(await readFile(file, 'utf8'), r, doc, heading[1].trim(), pages))
    }
  }
  const sheet = join(htmlOut, TRIGGER_SHEET.dir, TRIGGER_SHEET.file)
  await writeFile(sheet, transformTriggerSheet(await readFile(sheet, 'utf8')))

  return { guides: LAST_DAY_GUIDES.length, reviews: REVIEWS.length }
}
