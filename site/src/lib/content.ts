import 'server-only'

import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { cache } from 'react'
import { parseDocument, type Section } from './parse'
import { parseReading, readingText, toPlainText } from './reading'
import { ANSWER_KEY_MAP, CLOSING_SECTION_KEY } from './mapping'
import { READING_TABS, scenarioHref } from './scenario'
import type {
  CaseStudy,
  Manifest,
  Scenario,
  ScenarioRef,
  ScenarioSection,
  SearchEntry,
  TrackMeta,
} from './scenario'

/**
 * Reads the synced content at build time.
 *
 * `server-only` is imported for its side effect: it turns an accidental client
 * import of this module into a clear error at the import site, instead of a
 * bundler failure about `node:fs` appearing in a browser chunk.
 */

const CONTENT_DIR = join(process.cwd(), 'content')

export const getManifest = cache(async (): Promise<Manifest> => {
  try {
    return JSON.parse(await readFile(join(CONTENT_DIR, 'manifest.json'), 'utf8'))
  } catch {
    throw new Error(
      'content/manifest.json is missing. Run `npm run sync` before building.',
    )
  }
})

export async function getTracks(moduleId: string): Promise<TrackMeta[]> {
  const manifest = await getManifest()
  return manifest.modules.find((m) => m.id === moduleId)?.tracks ?? []
}

/** Flat, ordered list across all tracks — drives prev/next, search and progress. */
export const getAllScenarios = cache(async (): Promise<ScenarioRef[]> => {
  const manifest = await getManifest()
  return manifest.modules.flatMap((module) =>
    module.tracks.flatMap((track) =>
      track.scenarios.map((scenario) => ({
        moduleId: module.id,
        trackId: track.id,
        trackTitle: track.title,
        slug: scenario.slug,
        title: scenario.title,
        order: scenario.order,
        tag: scenario.tag,
        reading: module.kind === 'reading',
      })),
    ),
  )
})

export const getScenario = cache(
  async (
    moduleId: string,
    trackId: string,
    slug: string,
  ): Promise<Scenario | null> => {
    const all = await getAllScenarios()
    const index = all.findIndex(
      (s) => s.moduleId === moduleId && s.trackId === trackId && s.slug === slug,
    )
    if (index === -1 || all[index].reading) return null
    const ref = all[index]

    const base = join(CONTENT_DIR, 'modules', moduleId, trackId)
    const [worksheetRaw, answerKeyRaw] = await Promise.all([
      readFile(join(base, 'worksheets', `${slug}.md`), 'utf8'),
      readFile(join(base, 'answer-keys', `${slug}.md`), 'utf8'),
    ])

    const worksheet = parseDocument(worksheetRaw)
    const answerKey = parseDocument(answerKeyRaw)
    const keyByKey = new Map(answerKey.sections.map((s) => [s.key, s]))

    const sections: ScenarioSection[] = worksheet.sections.map((section) => ({
      ...section,
      // Falling back to the section's own key pairs a worksheet section with an
      // answer-key section of the same name. Module 01's two documents have
      // deliberately different shapes, so it declares its pairings in ANSWER_KEY_MAP
      // and the fallback only ever resolves to nothing there. Tracks whose two
      // documents share a heading structure — the behavioural ones, where each
      // question is one section in both files — need no entry at all.
      answerKey: (ANSWER_KEY_MAP[section.key] ?? [section.key])
        .map((key) => keyByKey.get(key))
        .filter((s): s is Section => Boolean(s)),
    }))

    return {
      ref,
      title: worksheet.title.replace(
        /\s*[-–—]\s*(Case Study|Practice) Worksheet\s*$/i,
        '',
      ),
      intro: worksheet.intro,
      sections,
      closing: keyByKey.get(CLOSING_SECTION_KEY) ?? null,
      answerKeyDocument: answerKey,
      prev: index > 0 ? all[index - 1] : null,
      next: index < all.length - 1 ? all[index + 1] : null,
    }
  },
)

const SEARCH_TEXT_CAP = 500

/**
 * A reading page: one group's four documents, each parsed for display. prev/next stay
 * inside the module, so the last case study does not lead into a worksheet.
 */
export const getCaseStudy = cache(
  async (moduleId: string, trackId: string, slug: string): Promise<CaseStudy | null> => {
    const siblings = (await getAllScenarios()).filter((s) => s.moduleId === moduleId)
    const index = siblings.findIndex((s) => s.trackId === trackId && s.slug === slug)
    if (index === -1 || !siblings[index].reading) return null
    const ref = siblings[index]

    const base = join(CONTENT_DIR, 'modules', moduleId, trackId, slug)
    const docs = await Promise.all(
      READING_TABS.map(async (tab) => ({
        tab: tab.id,
        label: tab.label,
        doc: parseReading(await readFile(join(base, `${tab.id}.md`), 'utf8'), tab.id),
      })),
    )

    return {
      ref,
      title: ref.title,
      docs,
      prev: index > 0 ? siblings[index - 1] : null,
      next: index < siblings.length - 1 ? siblings[index + 1] : null,
    }
  },
)

/** Build-time search index. Section-level so results land on a specific heading. */
export const getSearchIndex = cache(async (): Promise<SearchEntry[]> => {
  const all = await getAllScenarios()
  const entries: SearchEntry[] = []

  for (const ref of all) {
    if (ref.reading) {
      const study = await getCaseStudy(ref.moduleId, ref.trackId, ref.slug)
      if (!study) continue
      const href = scenarioHref(ref)
      for (const { label, doc } of study.docs) {
        for (const section of doc.sections) {
          if (!section.title) continue
          entries.push({
            title: `${ref.tag} · ${study.title}`,
            section: toPlainText(section.title),
            kind: label,
            href: `${href}#${section.id}`,
            // Capped: the index ships to every page, and these guides are long. The
            // opening of a section carries its claim, which is what a search hits.
            text: `${toPlainText(section.title)} ${readingText(section)}`.slice(0, SEARCH_TEXT_CAP),
          })
        }
      }
      continue
    }
    const scenario = await getScenario(ref.moduleId, ref.trackId, ref.slug)
    if (!scenario) continue
    const href = scenarioHref(ref)

    for (const section of scenario.sections) {
      entries.push({
        title: scenario.title,
        section: section.title,
        kind: 'worksheet',
        href: `${href}#section-${section.index}`,
        text: plainText(section),
      })
    }
    for (const section of scenario.answerKeyDocument.sections) {
      entries.push({
        title: scenario.title,
        section: section.title,
        kind: 'answer key',
        href: `${href}#section-${section.index}`,
        text: plainText(section),
      })
    }
  }

  return entries
})

function plainText(section: Section): string {
  const parts: string[] = [section.title]
  for (const block of section.blocks) {
    if (block.kind === 'prose') parts.push(stripHtml(block.html))
    if (block.kind === 'subheading') parts.push(block.text)
    if (block.kind === 'list') {
      for (const item of block.items) {
        if (item.kind === 'text') parts.push(stripHtml(item.html))
        if (item.kind === 'field') parts.push(item.label)
      }
    }
    if (block.kind === 'table') {
      parts.push(block.headers.join(' '))
      for (const row of block.rows) {
        for (const cell of row) if (cell.text) parts.push(stripHtml(cell.text))
      }
    }
    if (block.kind === 'scorecard') {
      for (const row of block.rows) {
        parts.push(row.area, ...row.levels.map((l) => l.label))
      }
    }
  }
  return parts.join(' ').replace(/\s+/g, ' ').trim()
}

function stripHtml(html: string): string {
  return html.replace(/<[^>]*>/g, ' ')
}
