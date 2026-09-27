import Link from 'next/link'
import {
  MODES,
  SOURCE_STATUS_LABELS,
  reviewHref,
  reviewLabel,
  type EditorialMeta,
  type Review,
} from '@/lib/editorial'
import { qualifiedTitle, scenarioHref, type ScenarioRef } from '@/lib/scenario'

/**
 * The editorial contract, rendered: every page says near its top what it is, who it is
 * for, what it assumes, what the reader will be able to do, and how to use it — and at
 * its foot, where to go next. The values come from `src/lib/editorial.ts`, so a page
 * cannot state one audience here and another in search or metadata.
 */

export function MetaStrip({
  meta,
  minutes,
  extra,
}: {
  meta: EditorialMeta
  minutes: number | null
  extra?: React.ReactNode
}) {
  const time = minutes ?? meta.minutes
  return (
    <div className="flex flex-wrap items-center gap-x-2.5 gap-y-1 text-[0.8125rem] text-subtle">
      <span className="font-semibold text-accent">{MODES[meta.mode].label}</span>
      <Dot />
      <span>{meta.difficulty}</span>
      {time !== null && (
        <>
          <Dot />
          <span>{meta.mode === 'practice' || meta.mode === 'behavioural' ? `About ${time} min` : `${time} min read`}</span>
        </>
      )}
      {extra}
    </div>
  )
}

function Dot() {
  return <span aria-hidden>·</span>
}

export function BeforeYouStart({ meta, children }: { meta: EditorialMeta; children?: React.ReactNode }) {
  return (
    <section
      aria-label="Before you start"
      className="no-print mt-5 grid gap-x-8 gap-y-3 border-l-2 border-accent/40 pl-4 text-[0.875rem] leading-relaxed sm:grid-cols-2"
    >
      <Fact term="For">{meta.audience}</Fact>
      <Fact term="Assumes">
        <List items={meta.prerequisites} />
      </Fact>
      <Fact term="You will be able to">
        <List items={meta.outcomes} />
      </Fact>
      <Fact term="How to use it">{meta.howToUse}</Fact>
      {children}
      <p className="text-[0.75rem] text-subtle sm:col-span-2">
        {SOURCE_STATUS_LABELS[meta.sourceStatus]}
        {meta.lastReviewed ? ` · Key facts checked against official sources on ${formatDate(meta.lastReviewed)}` : ''}
      </p>
    </section>
  )
}

/** "2026-09-27" -> "27 Sep 2026". Parsed by hand so the server and browser agree. */
function formatDate(iso: string): string {
  const [y, m, d] = iso.split('-').map(Number)
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return `${d} ${months[m - 1]} ${y}`
}

export function Fact({ term, children }: { term: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="text-[0.6875rem] font-semibold uppercase tracking-[0.08em] text-subtle">{term}</div>
      <div className="mt-0.5 text-muted">{children}</div>
    </div>
  )
}

function List({ items }: { items: string[] }) {
  if (items.length === 1) return <>{items[0]}</>
  return (
    <ul className="list-disc space-y-0.5 pl-4 marker:text-subtle">
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  )
}

/**
 * The foot of a page: the reviews that cover its concepts, its counterpart in the
 * other format, and the next page in its track.
 */
export function WhereNext({
  reviews,
  counterpart,
  next,
  intro,
}: {
  reviews: Review[]
  counterpart: ScenarioRef | null
  next: ScenarioRef | null
  intro?: string
}) {
  if (!reviews.length && !counterpart && !next) return null
  return (
    <section aria-labelledby="where-next" className="no-print mt-14 rounded-xl border border-border bg-surface p-5">
      <h2 id="where-next" className="text-[1.0625rem] font-semibold">
        Where next
      </h2>
      {intro && <p className="mt-1 text-[0.875rem] leading-relaxed text-muted">{intro}</p>}
      <dl className="mt-4 grid gap-4 text-[0.875rem] sm:grid-cols-3">
        {counterpart && (
          <div>
            <dt className="text-[0.6875rem] font-semibold uppercase tracking-[0.08em] text-subtle">
              {counterpart.reading ? 'See it as a case study' : 'Practise it yourself'}
            </dt>
            <dd className="mt-1">
              <Link href={scenarioHref(counterpart)} className="font-medium text-accent hover:text-accent-hover">
                {counterpart.title}
              </Link>
            </dd>
          </div>
        )}
        {reviews.length > 0 && (
          <div>
            <dt className="text-[0.6875rem] font-semibold uppercase tracking-[0.08em] text-subtle">
              Revise the concepts
            </dt>
            <dd className="mt-1 space-y-1">
              {reviews.map((r) => (
                <div key={r.number}>
                  {/* Plain anchors: these are static HTML pages, not app routes. */}
                  <a href={reviewHref(r)} className="font-medium text-accent hover:text-accent-hover">
                    {reviewLabel(r.number)} · {r.title}
                  </a>
                </div>
              ))}
            </dd>
          </div>
        )}
        {next && (
          <div>
            <dt className="text-[0.6875rem] font-semibold uppercase tracking-[0.08em] text-subtle">
              Next in {next.trackTitle}
            </dt>
            <dd className="mt-1">
              <Link href={scenarioHref(next)} className="font-medium text-accent hover:text-accent-hover">
                {qualifiedTitle(next)}
              </Link>
            </dd>
          </div>
        )}
      </dl>
    </section>
  )
}
