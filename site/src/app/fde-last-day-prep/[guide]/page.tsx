import Link from 'next/link'
import { notFound } from 'next/navigation'
import type { Metadata } from 'next'
import { getLastDayGuide } from '@/lib/content'
import {
  FINAL_REHEARSAL_META,
  LAST_DAY,
  LAST_DAY_GUIDES,
  ORIENTATION_META,
  REVIEWS,
  reviewHref,
  reviewLabel,
} from '@/lib/editorial'
import { BeforeYouStart, MetaStrip } from '@/components/PageIntro'
import { ReadingPanel } from '@/components/CaseStudyView'

/**
 * The Roadmap (orientation) and the Rapid Revision Guide (final rehearsal): markdown
 * from `06_Interview_Prep/Last_Day_Prep/`, synced to `content/last-day/` by
 * `scripts/last-day.mjs` and rendered with the same reading panel as the case studies.
 */

type Params = { guide: string }

export const dynamicParams = false

export function generateStaticParams() {
  return LAST_DAY_GUIDES.map((g) => ({ guide: g.id }))
}

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { guide } = await params
  const loaded = await getLastDayGuide(guide)
  return loaded ? { title: `${loaded.guide.title} · ${LAST_DAY.title}`, description: loaded.guide.blurb } : {}
}

export default async function LastDayGuidePage({ params }: { params: Promise<Params> }) {
  const { guide } = await params
  const loaded = await getLastDayGuide(guide)
  if (!loaded) notFound()
  const meta = guide === 'roadmap' ? ORIENTATION_META : FINAL_REHEARSAL_META
  const other = LAST_DAY_GUIDES.find((g) => g.id !== guide)!

  return (
    <div className="py-10">
      <nav aria-label="Breadcrumb" className="no-print mb-6 flex flex-wrap items-center gap-1.5 text-[0.8125rem] text-subtle">
        <Link href={LAST_DAY.href} className="transition-colors hover:text-text">
          {LAST_DAY.title}
        </Link>
        <span aria-hidden>/</span>
        <span className="text-muted">{loaded.guide.eyebrow}</span>
      </nav>

      <header className="mb-10 max-w-3xl">
        <h1 className="text-[2rem] font-bold leading-[1.2] tracking-[-0.02em]">{loaded.guide.title}</h1>
        <p className="mt-3 text-[1rem] leading-relaxed text-muted">{loaded.guide.blurb}</p>
        <div className="mt-3">
          <MetaStrip meta={meta} minutes={loaded.minutes} />
        </div>
        <BeforeYouStart meta={meta} />
      </header>

      <ReadingPanel doc={loaded.doc} drawDiagrams />

      <section className="no-print mt-14 rounded-xl border border-border bg-surface p-5">
        <h2 className="text-[1.0625rem] font-semibold">Where next</h2>
        <p className="mt-1 text-[0.875rem] leading-relaxed text-muted">
          {guide === 'roadmap'
            ? 'Work through the reviews in order, starting with the first. Finish with the Rapid Revision Guide.'
            : 'Anything that did not come back quickly points to the review to reopen.'}
        </p>
        <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-[0.875rem] font-semibold">
          {guide === 'roadmap' && (
            <a href={reviewHref(REVIEWS[0])} className="text-accent hover:text-accent-hover">
              {reviewLabel(1)} · {REVIEWS[0].title} →
            </a>
          )}
          <Link href={`${LAST_DAY.href}/${other.id}`} className="text-accent hover:text-accent-hover">
            {other.title} →
          </Link>
          <Link href={LAST_DAY.href} className="text-accent hover:text-accent-hover">
            All {REVIEWS.length} reviews →
          </Link>
        </div>
      </section>
    </div>
  )
}
