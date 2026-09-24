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
  /** Reading pages only: the page's tabs, in display order. */
  tabs?: ReadingTab[]
  /** Reading pages only: `track/slug` of the same case's interactive worksheet in Module 01. */
  practice?: string
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
  tabs?: ReadingTab[]
  practice?: string
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
 * One tab of a reading page. Tabs vary per page — the grouped case studies have four,
 * a standalone case can have one to five — so the list comes from the manifest, written
 * by `scripts/case-studies.mjs`, which also writes one `<id>.md` per tab.
 */
export type ReadingTab = { id: string; label: string }

export type CaseStudy = {
  ref: ScenarioRef
  title: string
  docs: { tab: string; label: string; doc: ReadingDocument }[]
  prev: ScenarioRef | null
  next: ScenarioRef | null
}
