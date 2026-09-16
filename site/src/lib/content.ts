import 'server-only'

import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { cache } from 'react'
import { parseDocument, type Section } from './parse'
import { ANSWER_KEY_MAP, CLOSING_SECTION_KEY } from './mapping'
import { scenarioHref } from './scenario'
import type {
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
    if (index === -1) return null
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
      answerKey: (ANSWER_KEY_MAP[section.key] ?? [])
        .map((key) => keyByKey.get(key))
        .filter((s): s is Section => Boolean(s)),
    }))

    return {
      ref,
      title: worksheet.title.replace(/\s*[-–—]\s*Case Study Worksheet\s*$/i, ''),
      sections,
      closing: keyByKey.get(CLOSING_SECTION_KEY) ?? null,
      answerKeyDocument: answerKey,
      prev: index > 0 ? all[index - 1] : null,
      next: index < all.length - 1 ? all[index + 1] : null,
    }
  },
)

/** Build-time search index. Section-level so results land on a specific heading. */
export const getSearchIndex = cache(async (): Promise<SearchEntry[]> => {
  const all = await getAllScenarios()
  const entries: SearchEntry[] = []

  for (const ref of all) {
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
