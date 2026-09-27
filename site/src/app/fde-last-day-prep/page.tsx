import Link from 'next/link'
import type { Metadata } from 'next'
import { pageRef } from '@/lib/content'
import {
  LAST_DAY,
  LAST_DAY_GUIDES,
  REVIEW_DOCS,
  REVIEWS,
  REVISION_META,
  TRIGGER_SHEET,
  reviewHref,
  reviewLabel,
} from '@/lib/editorial'
import { BeforeYouStart, MetaStrip } from '@/components/PageIntro'

/**
 * The eighteen reviews and the trigger sheet are static HTML, served as-is from
 * `public/fde-last-day-prep/` (their own CSS, fonts and — for the trigger sheet —
 * client-side search). `scripts/last-day.mjs` renames and cross-links them at sync time.
 * The Roadmap and Rapid Revision Guide are markdown, rendered by the app at
 * `/fde-last-day-prep/[guide]`. All names come from `src/lib/editorial.ts`.
 */

const BLURB =
  `Eighteen condensed reviews, a searchable trigger-to-concept reference, an orientation ` +
  `roadmap and a final rehearsal guide — for the days before an FDE interview, once the ` +
  `concepts are already familiar.`

export const metadata: Metadata = {
  title: LAST_DAY.title,
  description: BLURB,
}

export default async function LastDayReviewPage() {
  // Resolved here so each review card can name the practice to learn from first.
  const firstPractice = await Promise.all(REVIEWS.map((r) => pageRef(r.learnFirst[0])))

  return (
    <div className="py-14 sm:py-20">
      <section className="max-w-2xl">
        <p className="mb-3 text-[0.8125rem] font-semibold uppercase tracking-[0.1em] text-accent">
          {LAST_DAY.eyebrow}
        </p>
        <h1 className="text-[2.25rem] font-bold leading-[1.15] tracking-[-0.022em] sm:text-[2.75rem]">
          {LAST_DAY.title}
        </h1>
        <p className="mt-5 text-[1.0625rem] leading-relaxed text-muted">{BLURB}</p>
        <div className="mt-4">
          <MetaStrip meta={REVISION_META} minutes={null} />
        </div>
        <BeforeYouStart meta={REVISION_META} />
      </section>

      <section className="mt-12 grid gap-4 sm:grid-cols-2">
        {LAST_DAY_GUIDES.map((g) => (
          <Link
            key={g.id}
            href={`${LAST_DAY.href}/${g.id}`}
            className="group flex flex-col rounded-xl border border-accent/30 bg-accent-soft/40 p-5 transition-colors hover:border-accent"
          >
            <span className="text-[0.8125rem] font-semibold uppercase tracking-[0.1em] text-accent">
              {g.eyebrow}
            </span>
            <h2 className="mt-1 text-[1.25rem] font-semibold tracking-[-0.014em] group-hover:text-accent">
              {g.title}
            </h2>
            <p className="mt-1.5 flex-1 text-[0.9375rem] leading-relaxed text-muted">{g.blurb}</p>
            <span className="mt-4 text-[0.9375rem] font-semibold text-accent">Open →</span>
          </Link>
        ))}
      </section>

      <section className="mt-4">
        <a
          href={`${LAST_DAY.href}/${TRIGGER_SHEET.dir}/${TRIGGER_SHEET.file}`}
          className="group flex flex-col gap-4 rounded-xl border border-border bg-surface p-5 transition-colors hover:border-border-strong sm:flex-row sm:items-center"
        >
          <div className="flex-1">
            <span className="text-[0.8125rem] font-semibold uppercase tracking-[0.1em] text-subtle">
              Searchable quick reference
            </span>
            <h2 className="mt-1 text-[1.25rem] font-semibold tracking-[-0.014em] group-hover:text-accent">
              {TRIGGER_SHEET.title}
            </h2>
            <p className="mt-1.5 text-[0.9375rem] leading-relaxed text-muted">{TRIGGER_SHEET.blurb}</p>
          </div>
          <span className="shrink-0 text-[0.9375rem] font-semibold text-accent">Open the reference →</span>
        </a>
      </section>

      <section className="mt-14">
        <div className="mb-5 flex items-baseline justify-between gap-4">
          <h2 className="text-[1.375rem] font-semibold tracking-[-0.014em]">The {REVIEWS.length} reviews</h2>
          <Link href="/learning-map" className="text-[0.8125rem] font-medium text-accent hover:text-accent-hover">
            How they map to practice and case studies →
          </Link>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {REVIEWS.map((r, i) => {
            const practice = firstPractice[i]
            return (
              <div
                key={r.dir}
                className="flex flex-col rounded-xl border border-border bg-surface p-5 shadow-[var(--shadow)] transition-colors hover:border-border-strong"
              >
                <span className="mb-2 text-[0.75rem] font-bold tabular-nums tracking-wide text-accent">
                  {reviewLabel(r.number)}
                </span>
                <h3 className="text-[1.0625rem] font-semibold">{r.title}</h3>
                <p className="mt-1.5 flex-1 text-[0.875rem] leading-relaxed text-muted">{r.blurb}</p>
                {practice && (
                  <p className="mt-3 text-[0.8125rem] text-subtle">
                    New to this? Learn first:{' '}
                    <Link href={`/modules/${practice.moduleId}/${practice.trackId}/${practice.slug}`} className="font-medium text-accent hover:text-accent-hover">
                      {practice.title}
                    </Link>
                  </p>
                )}
                {/* Plain anchors: the reviews are static HTML files, not app routes. */}
                <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-border pt-4 text-[0.875rem] font-semibold">
                  <a href={reviewHref(r, 'concise')} className="text-accent transition-colors hover:text-accent-hover">
                    {REVIEW_DOCS.concise.label} →
                  </a>
                  <a href={reviewHref(r, 'card')} className="text-accent transition-colors hover:text-accent-hover">
                    {REVIEW_DOCS.card.label} →
                  </a>
                </div>
              </div>
            )
          })}
        </div>
      </section>
    </div>
  )
}
