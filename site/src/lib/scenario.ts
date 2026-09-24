import type { Block, Section, ParsedDocument } from './parse'
import type { ReadingDocument } from './reading'

/**
 * Types and helpers shared by server and client code.
 *
 * These deliberately live apart from `content.ts`, which reads the filesystem. A
 * client component importing a *value* from that module would pull `node:fs` into
 * the browser bundle and fail the build, so anything both sides need belongs here.
 */

export type ScenarioMeta = {
  slug: string
  order: number
  title: string
  /** Short label shown instead of the order number, e.g. `G01` in FDE Case Studies. */
  tag?: string
}

export type TrackMeta = {
  id: string
  title: string
  blurb: string
  scenarios: ScenarioMeta[]
}

export type Manifest = {
  generatedAt: string
  /** `kind: 'reading'` marks a module of reading pages rather than worksheets. */
  modules: { id: string; kind?: 'reading'; tracks: TrackMeta[] }[]
}

export type ScenarioRef = {
  moduleId: string
  trackId: string
  trackTitle: string
  slug: string
  title: string
  order: number
  tag?: string
  /** True for reading pages (FDE Case Studies): read-only, tabbed, progress by tab. */
  reading?: boolean
}

export type ScenarioSection = Section & {
  /** Answer-key sections that correspond to this worksheet section, if any. */
  answerKey: Section[]
}

export type Scenario = {
  ref: ScenarioRef
  title: string
  /** Worksheet content above the first `## ` heading, shown as a lead-in. Empty for
   *  the case-study worksheets, whose first line is already a numbered section. */
  intro: Block[]
  sections: ScenarioSection[]
  /** The "Final 2-minute spoken answer" section, shown as the closing card. */
  closing: Section | null
  /** Every answer-key section, for readers who want the document whole. */
  answerKeyDocument: ParsedDocument
  prev: ScenarioRef | null
  next: ScenarioRef | null
}

export type SearchEntry = {
  title: string
  section: string
  /** 'worksheet' | 'answer key' for worksheets; the tab label for reading pages. */
  kind: string
  href: string
  text: string
}

export function scenarioHref(ref: {
  moduleId: string
  trackId: string
  slug: string
}): string {
  return `/modules/${ref.moduleId}/${ref.trackId}/${ref.slug}`
}

/**
 * The tabs of a reading page, in display order; the first opens by default.
 * Must match `DOC_TABS` in `scripts/case-studies.mjs`, which writes one file per id.
 */
export const READING_TABS = [
  { id: 'main', label: 'Main' },
  { id: 'deep-dive', label: 'Deep Dive' },
  { id: 'cheat-sheet', label: 'Cheat Sheet' },
  { id: 'full-pack', label: 'Full Pack' },
] as const

export type ReadingTabId = (typeof READING_TABS)[number]['id']

export type CaseStudy = {
  ref: ScenarioRef
  title: string
  docs: { tab: ReadingTabId; label: string; doc: ReadingDocument }[]
  prev: ScenarioRef | null
  next: ScenarioRef | null
}
