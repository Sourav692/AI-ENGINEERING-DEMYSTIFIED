/**
 * Runs the parser over every synced worksheet and answer key and asserts the
 * structural invariants the UI depends on. Run with `npm run check:content`.
 *
 * This exists because the fillable regions are inferred from emptiness rather than
 * declared, so a formatting change in a source file can silently turn an input into
 * static text. That would look fine and be wrong.
 *
 * Tracks are read from the manifest rather than listed here, so a new track is
 * checked from the moment it syncs. What differs per track is the *shape* expected,
 * which `EXPECTATIONS` declares: case-study worksheets are a fixed 11-section
 * scaffold ending in a scorecard, while the behavioural ones are one section per
 * interview question and carry no scorecard at all.
 */

import { readFile, readdir } from 'node:fs/promises'
import { join, resolve } from 'node:path'
import { parseDocument } from '../src/lib/parse.ts'
import type { Block } from '../src/lib/parse.ts'
import { ANSWER_KEY_MAP } from '../src/lib/mapping.ts'
import { parseReading } from '../src/lib/reading.ts'
import {
  FAMILY_META,
  LAST_DAY_GUIDES,
  RELATED_CASE,
  REQUIRED_META_FIELDS,
  REVIEW_DOCS,
  REVIEWS,
  TABS,
  TRACKS,
  TRIGGER_SHEET,
} from '../src/lib/editorial.ts'
import { existsSync } from 'node:fs'
import { GLOSSARY, NOT_ACRONYMS } from '../src/lib/glossary.ts'

const CONTENT = resolve(import.meta.dirname, '..', 'content')

type Expectation = {
  /** Exact section count, or a minimum when the shape varies by document. */
  sections: { exact: number } | { min: number }
  scorecards: number
  minFillable: number
  minKeySections: number
  /**
   * Whether every worksheet section must resolve to an answer-key section. True for
   * tracks that pair by identity — a worksheet question with no answer renders as a
   * dead reveal, which is the failure this catches.
   */
  requirePairing: boolean
}

const CASE_STUDY: Expectation = {
  sections: { exact: 11 },
  scorecards: 1,
  minFillable: 20,
  minKeySections: 10,
  requirePairing: false,
}

const BEHAVIOURAL: Expectation = {
  sections: { min: 3 },
  scorecards: 0,
  minFillable: 8,
  minKeySections: 3,
  requirePairing: true,
}

const EXPECTATIONS: Record<string, Expectation> = {
  core: CASE_STUDY,
  'system-design': CASE_STUDY,
  'hiring-manager': BEHAVIOURAL,
  'leadership-principles': BEHAVIOURAL,
}

type Counts = {
  inputs: number
  fields: number
  editableCells: number
  scorecards: number
  growableTables: number
  diagrams: number
  /**
   * Fences that reached the prose path instead of becoming a `diagram` or `code`
   * block. That was a real regression: a mermaid fence rendered as its own source
   * text on the live site, which looks like broken content rather than a bug.
   */
  leakedFences: number
}

function emptyCounts(): Counts {
  return {
    inputs: 0,
    fields: 0,
    editableCells: 0,
    scorecards: 0,
    growableTables: 0,
    diagrams: 0,
    leakedFences: 0,
  }
}

function count(blocks: Block[], counts: Counts): void {
  for (const b of blocks) {
    if (b.kind === 'diagram') counts.diagrams++
    if (b.kind === 'prose' && /language-mermaid|&#96;&#96;&#96;|```/.test(b.html)) {
      counts.leakedFences++
    }
    if (b.kind === 'list') {
      for (const item of b.items) {
        if (item.kind === 'input') counts.inputs++
        if (item.kind === 'field') counts.fields++
      }
    }
    if (b.kind === 'table') {
      for (const row of b.rows) {
        for (const cell of row) if (cell.editable) counts.editableCells++
      }
      if (b.growable) counts.growableTables++
    }
    if (b.kind === 'scorecard') counts.scorecards++
  }
}

const failures: string[] = []
const rows: string[] = []
let diagramTotal = 0

const manifest = JSON.parse(await readFile(join(CONTENT, 'manifest.json'), 'utf8'))

/**
 * Reading modules (FDE Case Studies) have no blanks to find. What can go wrong there is
 * different: a tab file missing, a mermaid fence printed as source, or a link still
 * pointing into the repo, which is a dead link on the site. The sync step rewrites
 * every repo link, so one surviving here means that rewrite missed a case.
 */
async function checkReading(mod: {
  id: string
  tracks: { id: string; scenarios: { slug: string; tabs?: { id: string }[] }[] }[]
}) {
  for (const track of mod.tracks) {
    for (const { slug, tabs = [] } of track.scenarios) {
      if (tabs.length === 0) failures.push(`${track.id}/${slug}: no tabs in the manifest`)
      let sections = 0
      let diagrams = 0
      for (const tab of tabs) {
        const label = `${track.id}/${slug}/${tab.id}`
        const raw = await readFile(join(CONTENT, 'modules', mod.id, track.id, slug, `${tab.id}.md`), 'utf8').catch(() => null)
        if (raw === null) {
          failures.push(`${label}: missing tab document`)
          continue
        }
        const doc = parseReading(raw, tab.id)
        if (!doc.title) failures.push(`${label}: no # title`)
        const titled = doc.sections.filter((x) => x.title).length
        if (titled === 0) failures.push(`${label}: no ## sections — the tab would have no contents list`)
        sections += titled
        for (const section of doc.sections) {
          for (const chunk of section.chunks) {
            if (chunk.kind === 'diagram') {
              diagrams++
              continue
            }
            if (/language-mermaid/.test(chunk.html)) {
              failures.push(`${label}: a mermaid fence rendered as prose in "${section.title ?? 'intro'}"`)
            }
            for (const [, href] of chunk.html.matchAll(/href="([^"]*)"/g)) {
              if (!/^(https?:|mailto:|#|\/)/.test(href)) {
                failures.push(`${label}: link still points into the repo: ${href}`)
              }
            }
          }
        }
      }
      diagramTotal += diagrams
      rows.push(`  ${`${track.id}/${slug}`.padEnd(52)} ${String(sections).padStart(3)} sec  ${diagrams} diagram(s)  (${tabs.length} tab${tabs.length === 1 ? '' : 's'})`)
    }
  }
}

for (const mod of manifest.modules) {
  if (mod.kind === 'reading') {
    await checkReading(mod)
    continue
  }
  for (const track of mod.tracks) {
    const expect = EXPECTATIONS[track.id]
    if (!expect) {
      failures.push(
        `${track.id}: no expectation declared in check-parse.ts — add one so the ` +
          `track is actually checked rather than silently skipped`,
      )
      continue
    }

    const trackDir = join(CONTENT, 'modules', mod.id, track.id)
    const worksheetDir = join(trackDir, 'worksheets')
    const keyDir = join(trackDir, 'answer-keys')
    const files = (await readdir(worksheetDir)).filter((f) => f.endsWith('.md')).sort()

    for (const file of files) {
      const slug = file.replace(/\.md$/, '')
      const label = `${track.id}/${slug}`
      const doc = parseDocument(await readFile(join(worksheetDir, file), 'utf8'))
      const counts = emptyCounts()
      count(doc.intro, counts)
      for (const section of doc.sections) count(section.blocks, counts)

      if (counts.leakedFences > 0) {
        failures.push(
          `${label}: ${counts.leakedFences} fenced block(s) rendered as prose — ` +
            `a code or mermaid fence is not being parsed as its own block`,
        )
      }

      const total =
        counts.inputs + counts.fields + counts.editableCells + counts.scorecards

      if ('exact' in expect.sections) {
        if (doc.sections.length !== expect.sections.exact) {
          failures.push(
            `${label}: expected ${expect.sections.exact} sections, got ${doc.sections.length}`,
          )
        }
      } else if (doc.sections.length < expect.sections.min) {
        failures.push(
          `${label}: expected at least ${expect.sections.min} sections, got ${doc.sections.length}`,
        )
      }
      if (counts.scorecards !== expect.scorecards) {
        failures.push(
          `${label}: expected ${expect.scorecards} scorecard(s), got ${counts.scorecards}`,
        )
      }
      if (total < expect.minFillable) {
        failures.push(`${label}: only ${total} fillable regions — suspiciously few`)
      }
      if (!doc.title) failures.push(`${label}: no title`)

      // The reveal under each worksheet section is populated by key lookup. A section
      // that resolves to nothing renders an empty reveal, which reads as missing
      // content rather than as a bug.
      if (expect.requirePairing) {
        const keyDoc = parseDocument(
          await readFile(join(keyDir, file), 'utf8').catch(() => ''),
        )
        const keyKeys = new Set(keyDoc.sections.map((s) => s.key))
        for (const section of doc.sections) {
          const targets = ANSWER_KEY_MAP[section.key] ?? [section.key]
          if (!targets.some((k) => keyKeys.has(k))) {
            failures.push(
              `${label}: worksheet section "${section.title}" ` +
                `(key ${section.key}) has no matching answer-key section`,
            )
          }
        }
      }

      rows.push(
        `  ${label.padEnd(52)} ` +
          `${String(doc.sections.length).padStart(2)} sec  ` +
          `${String(counts.editableCells).padStart(3)} cells  ` +
          `${String(counts.inputs).padStart(2)} bullets  ` +
          `${String(counts.fields).padStart(2)} fields  ` +
          `${counts.growableTables} growable`,
      )
    }

    for (const file of (await readdir(keyDir)).filter((f) => f.endsWith('.md'))) {
      const doc = parseDocument(await readFile(join(keyDir, file), 'utf8'))
      const counts = emptyCounts()
      count(doc.intro, counts)
      for (const section of doc.sections) count(section.blocks, counts)
      if (counts.leakedFences > 0) {
        failures.push(
          `${track.id}/answer-keys/${file}: ${counts.leakedFences} fenced block(s) ` +
            `rendered as prose instead of a diagram or code block`,
        )
      }
      if (counts.diagrams > 0) diagramTotal += counts.diagrams
      // Answer keys are reference text. Anything editable in one means the parser is
      // treating authored content as a blank.
      if (counts.inputs + counts.editableCells > 0) {
        failures.push(
          `${track.id}/answer-keys/${file}: ${counts.inputs + counts.editableCells} ` +
            `unexpected editable regions in an answer key`,
        )
      }
      if (doc.sections.length < expect.minKeySections) {
        failures.push(
          `${track.id}/answer-keys/${file}: only ${doc.sections.length} sections`,
        )
      }
    }
  }
}

// ------------------------------------------------------------------ editorial contract
//
// Every published page must be able to say what it is, who it is for, what it assumes
// and teaches, how to use it, and where to go next. Those answers live in
// src/lib/editorial.ts; these checks make a missing one a build failure rather than a
// page that silently renders without it.

const SITE_ROOT = resolve(import.meta.dirname, '..')
const pages = new Set<string>()
const routes = new Set<string>(['/', '/guide', '/learning-map', '/glossary', '/fde-last-day-prep'])
for (const g of LAST_DAY_GUIDES) routes.add(`/fde-last-day-prep/${g.id}`)
const tabsByPage = new Map<string, string[]>()

for (const mod of manifest.modules) {
  routes.add(`/modules/${mod.id}`)
  for (const track of mod.tracks) {
    if (!TRACKS[track.id]) failures.push(`${track.id}: no display name in TRACKS`)
    else if (track.title !== TRACKS[track.id].title) {
      failures.push(`${track.id}: manifest title "${track.title}" has drifted from TRACKS — re-run npm run sync`)
    }
    const meta = FAMILY_META[track.id]
    if (!meta) {
      failures.push(`${track.id}: no FAMILY_META entry, so its pages have no audience, prerequisites or outcomes`)
    } else {
      for (const field of REQUIRED_META_FIELDS) {
        const value = meta[field]
        if (value === undefined || value === '' || (Array.isArray(value) && value.length === 0)) {
          failures.push(`${track.id}: required metadata "${field}" is empty`)
        }
      }
    }
    for (const s of track.scenarios) {
      const key = `${track.id}/${s.slug}`
      pages.add(key)
      routes.add(`/modules/${mod.id}/${key}`)
      tabsByPage.set(`/modules/${mod.id}/${key}`, (s.tabs ?? []).map((t: { id: string }) => t.id))
      for (const tab of s.tabs ?? []) {
        if (!TABS[tab.id]) failures.push(`${key}: tab "${tab.id}" has no label or purpose in TABS`)
        else if (tab.label !== TABS[tab.id].label) failures.push(`${key}: tab label "${tab.label}" has drifted from TABS`)
      }
    }
  }
}

// Every cross-link names a page that exists, and every practice or case page is reachable
// from at least one review — a page no review points to is missing from the learning map.
const cited = new Set<string>()
for (const r of REVIEWS) {
  for (const ref of [...r.learnFirst, ...r.goDeeper]) {
    cited.add(ref)
    if (!pages.has(ref)) failures.push(`Review ${r.number}: links to "${ref}", which is not a published page`)
  }
}
for (const [practice, study] of Object.entries(RELATED_CASE)) {
  for (const ref of [practice, study]) {
    if (!pages.has(ref)) failures.push(`RELATED_CASE: "${ref}" is not a published page`)
  }
}
for (const mod of manifest.modules) {
  for (const track of mod.tracks) {
    if (FAMILY_META[track.id]?.personalisation) continue
    for (const s of track.scenarios) {
      const key = `${track.id}/${s.slug}`
      if (!cited.has(key)) failures.push(`${key}: not linked from any review in REVIEWS, so it is missing from the learning map`)
    }
  }
}

/** A site-internal href resolves to a route, a tab of a route, or a public file. */
function resolvesInternally(href: string): boolean {
  const [path, hash = ''] = href.split('#')
  if (path.endsWith('.html')) return existsSync(join(SITE_ROOT, 'public', decodeURIComponent(path)))
  const clean = path.replace(/\/$/, '') || '/'
  if (!routes.has(clean)) return false
  const tabs = tabsByPage.get(clean)
  // A hash on a reading page must open one of its tabs (or a section within one).
  if (tabs?.length && hash) return tabs.some((t) => hash === t || hash.startsWith(`${t}-`))
  return true
}

// Case-sensitive on purpose: "the agent's todo list" is prose; "TODO" is an author's note.
const PLACEHOLDER = /\[FILL\b|\bTODO\b|\bTBD\b|\bXXX\b|[Ll]orem ipsum/
let linksChecked = 0

async function checkDocument(label: string, raw: string, allowPlaceholders: boolean) {
  if (!allowPlaceholders && PLACEHOLDER.test(raw)) {
    failures.push(`${label}: unresolved placeholder (${raw.match(PLACEHOLDER)![0]}) on a public page`)
  }
  for (const [, href] of raw.matchAll(/\]\((\/[^)\s]*)\)/g)) {
    linksChecked++
    if (!resolvesInternally(href)) failures.push(`${label}: broken internal link ${href}`)
  }
}

for (const mod of manifest.modules) {
  for (const track of mod.tracks) {
    const personal = Boolean(FAMILY_META[track.id]?.personalisation)
    for (const s of track.scenarios) {
      const base = join(CONTENT, 'modules', mod.id, track.id)
      const files =
        mod.kind === 'reading'
          ? (s.tabs ?? []).map((t: { id: string }) => join(base, s.slug, `${t.id}.md`))
          : [join(base, 'worksheets', `${s.slug}.md`), join(base, 'answer-keys', `${s.slug}.md`)]
      for (const file of files) {
        const raw = await readFile(file, 'utf8').catch(() => null)
        if (raw !== null) await checkDocument(`${track.id}/${s.slug}`, raw, personal)
      }
    }
  }
}
for (const g of LAST_DAY_GUIDES) {
  const raw = await readFile(join(CONTENT, 'last-day', `${g.id}.md`), 'utf8').catch(() => null)
  if (raw === null) failures.push(`last-day/${g.id}.md: missing — run npm run sync`)
  else await checkDocument(`last-day/${g.id}`, raw, false)
}

// The static reviews: every internal link, including the ones sync added, must resolve.
const staticFiles = [
  ...REVIEWS.flatMap((r) => Object.values(REVIEW_DOCS).map((d) => `/fde-last-day-prep/${r.dir}/${d.file}`)),
  `/fde-last-day-prep/${TRIGGER_SHEET.dir}/${TRIGGER_SHEET.file}`,
]
for (const path of staticFiles) {
  const raw = await readFile(join(SITE_ROOT, 'public', path), 'utf8').catch(() => null)
  if (raw === null) {
    failures.push(`${path}: missing from public/`)
    continue
  }
  if (/\bModule\s+\d+\b/.test(raw.replace(/<[^>]+>/g, ' ').replace(/id="[^"]*"/g, ''))) {
    failures.push(`${path}: still says "Module N" — the Last-Day sequence is Review 01–18`)
  }
  for (const [, href] of raw.matchAll(/href="(\/[^"]*)"/g)) {
    linksChecked++
    if (!resolvesInternally(href)) failures.push(`${path}: broken internal link ${href}`)
  }
  for (const [, href] of raw.matchAll(/href="((?!https?:|#|\/|mailto:)[^"]+)"/g)) {
    linksChecked++
    const target = join(SITE_ROOT, 'public', path, '..', href.split('#')[0])
    if (!existsSync(target)) failures.push(`${path}: broken relative link ${href}`)
  }
}

// Acronyms: anything in capitals that shows up on three or more pages must either be in
// the glossary or be listed as not-an-acronym. A new term then gets a plain definition
// the day it spreads, instead of the reader having to guess.
const defined = new Set(GLOSSARY.map((g) => g.term))
const acronymPages = new Map<string, Set<string>>()
// A capitalised token that also appears as an ordinary lower-case word ("MODEL", "CACHE")
// is emphasis, not an acronym.
const lowerWords = new Set<string>()
const scanFiles: string[] = []
for (const mod of manifest.modules) {
  for (const track of mod.tracks) {
    for (const s of track.scenarios) {
      const base = join(CONTENT, 'modules', mod.id, track.id)
      if (mod.kind === 'reading') for (const t of s.tabs ?? []) scanFiles.push(join(base, s.slug, `${t.id}.md`))
      else scanFiles.push(join(base, 'worksheets', `${s.slug}.md`), join(base, 'answer-keys', `${s.slug}.md`))
    }
  }
}
for (const g of LAST_DAY_GUIDES) scanFiles.push(join(CONTENT, 'last-day', `${g.id}.md`))
for (const path of staticFiles) scanFiles.push(join(SITE_ROOT, 'public', path))
for (const file of scanFiles) {
  const raw = await readFile(file, 'utf8').catch(() => '')
  const text = raw
    .replace(/<(script|style)[\s\S]*?<\/\1>/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/```[\s\S]*?```/g, ' ')
  for (const [word] of text.matchAll(/\b[a-z]{4,}\b/g)) lowerWords.add(word)
  for (const [token] of text.matchAll(/\b[A-Z][A-Z0-9]{1,6}\b/g)) {
    if (defined.has(token) || NOT_ACRONYMS.has(token) || /^(G\d{2}|[A-Z]\d{1,3}|LLM\d{2})$/.test(token)) continue
    if (!acronymPages.has(token)) acronymPages.set(token, new Set())
    acronymPages.get(token)!.add(file)
  }
}
for (const [token, files] of acronymPages) {
  if (files.size >= 3 && !lowerWords.has(token.toLowerCase())) {
    failures.push(`acronym ${token} appears on ${files.size} pages but is not in the glossary (src/lib/glossary.ts) or NOT_ACRONYMS`)
  }
}

rows.push(`\n  editorial: ${pages.size} pages with metadata, ${cited.size} cited by reviews, ${linksChecked} internal links resolved`)

console.log(rows.join('\n'))
console.log(`\n  ${diagramTotal} mermaid diagram(s) parsed across answer keys and case studies`)

if (failures.length) {
  console.error(`\n${failures.length} problem(s):`)
  for (const f of failures) console.error(`  ✗ ${f}`)
  process.exit(1)
}
console.log(`\n✓ all worksheets, answer keys and case studies parse cleanly`)
