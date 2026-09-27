import Link from 'next/link'
import { notFound } from 'next/navigation'
import type { Metadata } from 'next'
import { getStoryBank, getTracks } from '@/lib/content'
import { STORY_BANK, STORY_BANK_META } from '@/lib/editorial'
import { getModule } from '@/lib/registry'
import { BeforeYouStart, MetaStrip } from '@/components/PageIntro'
import { ReadingPanel } from '@/components/CaseStudyView'

/**
 * The behavioural Story Bank (CONTENT-15): markdown from
 * `06_Interview_Prep/FDE/Behavioral_and_Leadership/story_bank.md`, synced to
 * `content/behavioural/` and rendered with the same reading panel as the case studies.
 * It lives under the behavioural module, beside its two tracks; the static `story-bank`
 * segment takes precedence over the `[track]` route.
 */

type Params = { module: string }

export const dynamicParams = false

export function generateStaticParams() {
  return [{ module: STORY_BANK.moduleId }]
}

export const metadata: Metadata = { title: STORY_BANK.title, description: STORY_BANK.blurb }

export default async function StoryBankPage({ params }: { params: Promise<Params> }) {
  const { module: moduleId } = await params
  const mod = getModule(moduleId)
  const bank = await getStoryBank()
  if (moduleId !== STORY_BANK.moduleId || !mod || !bank) notFound()
  const tracks = await getTracks(moduleId)

  return (
    <div className="py-10">
      <nav aria-label="Breadcrumb" className="no-print mb-6 flex flex-wrap items-center gap-1.5 text-[0.8125rem] text-subtle">
        <Link href={`/modules/${moduleId}`} className="transition-colors hover:text-text">
          {mod.title}
        </Link>
        <span aria-hidden>/</span>
        <span className="text-muted">{STORY_BANK.title}</span>
      </nav>

      <header className="mb-10 max-w-3xl">
        <h1 className="text-[2rem] font-bold leading-[1.2] tracking-[-0.02em]">{STORY_BANK.title}</h1>
        <p className="mt-3 text-[1rem] leading-relaxed text-muted">{STORY_BANK.blurb}</p>
        <div className="mt-3">
          <MetaStrip meta={STORY_BANK_META} minutes={bank.minutes} />
        </div>
        <BeforeYouStart meta={STORY_BANK_META} />
      </header>

      <ReadingPanel doc={bank.doc} drawDiagrams />

      <section className="no-print mt-14 rounded-xl border border-border bg-surface p-5">
        <h2 className="text-[1.0625rem] font-semibold">Where next</h2>
        <p className="mt-1 text-[0.875rem] leading-relaxed text-muted">
          Take a worksheet question, pick a story from its &ldquo;Stories that fit&rdquo; line and say it
          out loud in two minutes.
        </p>
        <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-[0.875rem] font-semibold">
          {tracks.map((track) => (
            <Link
              key={track.id}
              href={`/modules/${moduleId}#${track.id}`}
              className="text-accent hover:text-accent-hover"
            >
              {track.title} →
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
