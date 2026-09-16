import type { Block, Section, ParsedDocument } from './parse'

/**
 * Types and helpers shared by server and client code.
 *
 * These deliberately live apart from `content.ts`, which reads the filesystem. A
 * client component importing a *value* from that module would pull `node:fs` into
 * the browser bundle and fail the build, so anything both sides need belongs here.
 */

export type ScenarioMeta = { slug: string; order: number; title: string }

export type TrackMeta = {
  id: string
  title: string
  blurb: string
  scenarios: ScenarioMeta[]
}

export type Manifest = {
  generatedAt: string
  modules: { id: string; tracks: TrackMeta[] }[]
}

export type ScenarioRef = {
  moduleId: string
  trackId: string
  trackTitle: string
  slug: string
  title: string
  order: number
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
  kind: 'worksheet' | 'answer key'
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
