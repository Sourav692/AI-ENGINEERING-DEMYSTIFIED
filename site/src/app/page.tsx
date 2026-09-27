import Link from 'next/link'
import { getAllScenarios } from '@/lib/content'
import { MODULES, SITE, getModule } from '@/lib/registry'
import {
  LAST_DAY,
  LAST_DAY_GUIDES,
  MODES,
  REVIEWS,
  ROADMAP_COVERAGE,
  ROADMAP_PHASES,
  reviewLabel,
} from '@/lib/editorial'
import { ModuleProgress } from '@/components/Progress'

const PRACTICE_MODULES = [
  { id: '01-customer-discovery-and-decomposition', mode: 'practice' },
  { id: '14-behavioural-and-leadership-round', mode: 'behavioural' },
] as const
const CASE_STUDIES = '15-fde-case-studies'

export default async function HomePage() {
  const scenarios = await getAllScenarios()
  const scenariosIn = (moduleId: string) => scenarios.filter((s) => s.moduleId === moduleId)
  const caseStudies = getModule(CASE_STUDIES)!
  const live = MODULES.filter((m) => m.status === 'live').length

  return (
    <div className="py-14 sm:py-20">
      <section className="max-w-2xl">
        <p className="mb-3 text-[0.8125rem] font-semibold uppercase tracking-[0.1em] text-accent">
          {SITE.tagline}
        </p>
        <h1 className="text-[2.25rem] font-bold leading-[1.15] tracking-[-0.022em] sm:text-[2.75rem]">
          Practise the interview, one customer problem at a time.
        </h1>
        <p className="mt-5 text-[1.0625rem] leading-relaxed text-muted">
          A Forward Deployed Engineer interview is not a quiz. You are handed a vague
          customer problem and judged on how you turn it into users, requirements, an
          architecture, an evaluation plan and a rollout. Practise that here, read how
          complete systems answer it, and review it all before the day.
        </p>
        <div className="mt-7 flex flex-wrap gap-3">
          <Link
            href={`/modules/${PRACTICE_MODULES[0].id}`}
            className="rounded-md bg-accent px-4 py-2.5 text-[0.9375rem] font-semibold text-white transition-colors hover:bg-accent-hover"
          >
            Start practising
          </Link>
          <Link
            href="/learning-map"
            className="rounded-md border border-border bg-surface px-4 py-2.5 text-[0.9375rem] font-semibold transition-colors hover:border-border-strong"
          >
            See how it fits together
          </Link>
        </div>
      </section>

      <section id="practice" className="mt-16 scroll-mt-20">
        <ModeHeading mode="practice" title="Practice">
          Worksheets you fill in, then check against a model answer and score yourself.
          Your answers stay in this browser.
        </ModeHeading>
        <div className="grid gap-4">
          {PRACTICE_MODULES.map(({ id, mode }) => {
            const m = getModule(id)!
            const refs = scenariosIn(id)
            return (
              // Not a link itself: the progress block holds its own "continue" link, and
              // an anchor inside an anchor is invalid HTML.
              <div
                key={id}
                className="flex flex-col rounded-xl border border-border bg-surface p-5 shadow-[var(--shadow)] transition-colors hover:border-border-strong"
              >
                <span className="mb-1.5 text-[0.75rem] font-semibold uppercase tracking-[0.08em] text-subtle">
                  {MODES[mode].label}
                </span>
                <h3 className="text-[1.125rem] font-semibold">
                  <Link href={`/modules/${id}`} className="transition-colors hover:text-accent">
                    {m.title}
                  </Link>
                </h3>
                <p className="mt-1.5 text-[0.875rem] leading-relaxed text-muted">{m.blurb}</p>
                <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-3 border-t border-border pt-4">
                  <ModuleProgress scenarios={refs} />
                  <Link
                    href={`/modules/${id}`}
                    className="text-[0.875rem] font-semibold text-accent transition-colors hover:text-accent-hover"
                  >
                    All {refs.length} →
                  </Link>
                </div>
              </div>
            )
          })}
        </div>
      </section>

      <section className="mt-14">
        <ModeHeading mode="case-study" title="Case Studies">
          Complete system designs to read at several depths — the answer you would give,
          the detail behind it, and the sources.
        </ModeHeading>
        <div className="flex flex-col rounded-xl border border-border bg-surface p-5 shadow-[var(--shadow)]">
          <h3 className="text-[1.125rem] font-semibold">
            <Link href={`/modules/${CASE_STUDIES}`} className="transition-colors hover:text-accent">
              {caseStudies.title}
            </Link>
          </h3>
          <p className="mt-1.5 text-[0.875rem] leading-relaxed text-muted">{caseStudies.blurb}</p>
          <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-3 border-t border-border pt-4">
            <ModuleProgress scenarios={scenariosIn(CASE_STUDIES)} />
            <Link
              href={`/modules/${CASE_STUDIES}`}
              className="text-[0.875rem] font-semibold text-accent transition-colors hover:text-accent-hover"
            >
              All {scenariosIn(CASE_STUDIES).length} case studies →
            </Link>
          </div>
        </div>
      </section>

      <section className="mt-14">
        <ModeHeading mode="revision" title={LAST_DAY.title}>
          {MODES.revision.summary} Start with the roadmap, finish with the rapid guide.
        </ModeHeading>
        <div className="flex flex-col rounded-xl border border-border bg-surface p-5 shadow-[var(--shadow)]">
          <h3 className="text-[1.125rem] font-semibold">
            <Link href={LAST_DAY.href} className="transition-colors hover:text-accent">
              {REVIEWS.length} reviews, a quick reference and two guides
            </Link>
          </h3>
          <p className="mt-1.5 text-[0.875rem] leading-relaxed text-muted">
            Each review has an Interview Review and a One-Page Recall Card, and links back
            to the practice and case studies to learn from if a concept is new.
          </p>
          <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 border-t border-border pt-4 text-[0.875rem] font-semibold">
            {LAST_DAY_GUIDES.map((g) => (
              <Link key={g.id} href={`${LAST_DAY.href}/${g.id}`} className="text-accent hover:text-accent-hover">
                {g.title} →
              </Link>
            ))}
            <Link href={LAST_DAY.href} className="text-accent hover:text-accent-hover">
              All {REVIEWS.length} reviews →
            </Link>
          </div>
        </div>
      </section>

      <section className="mt-20">
        <div className="mb-2 flex items-baseline justify-between gap-4">
          <h2 className="text-[1.375rem] font-semibold tracking-[-0.014em]">
            The 15-part curriculum roadmap
          </h2>
          <span className="text-[0.8125rem] text-subtle">
            {live} of {MODULES.length} available
          </span>
        </div>
        <p className="mb-6 max-w-2xl text-[0.9375rem] leading-relaxed text-muted">
          The full plan for this site, grouped by phase. Planned parts are not blank: where
          the reviews already cover their ground, it says which. The{' '}
          <Link href="/learning-map" className="text-accent underline underline-offset-2">
            learning map
          </Link>{' '}
          explains how the roadmap, the reviews and the case studies relate.
        </p>
        <div className="space-y-8">
          {ROADMAP_PHASES.map((phase) => (
            <div key={phase.title}>
              <h3 className="text-[1rem] font-semibold">{phase.title}</h3>
              <p className="text-[0.8125rem] text-subtle">{phase.blurb}</p>
              <ul className="mt-3 grid gap-3 sm:grid-cols-2">
                {phase.modules.map((n) => {
                  const m = MODULES.find((x) => x.number === n)!
                  const coverage = ROADMAP_COVERAGE[n] ?? []
                  return (
                    <li
                      key={m.id}
                      className={`rounded-xl border p-4 ${m.status === 'live' ? 'border-accent/30 bg-surface' : 'border-border bg-surface-2/50'}`}
                    >
                      <div className="mb-1 flex items-center gap-2 text-[0.6875rem] font-semibold uppercase tracking-wide">
                        <span className="tabular-nums text-subtle">Part {String(m.number).padStart(2, '0')}</span>
                        {m.status === 'live' ? (
                          <span className="rounded-full bg-success-soft px-2 py-0.5 text-success">Available</span>
                        ) : (
                          <span className="text-subtle">Planned</span>
                        )}
                      </div>
                      <div className="text-[0.9375rem] font-semibold">
                        {m.status === 'live' ? (
                          <Link href={`/modules/${m.id}`} className="hover:text-accent">
                            {m.title}
                          </Link>
                        ) : (
                          <span className="text-muted">{m.title}</span>
                        )}
                      </div>
                      <p className="mt-1 text-[0.8125rem] leading-relaxed text-subtle">{m.blurb}</p>
                      {m.status !== 'live' && coverage.length > 0 && (
                        <p className="mt-2 text-[0.75rem] text-muted">
                          Covered for revision today in{' '}
                          {coverage.map((c) => reviewLabel(c)).join(', ')}.
                        </p>
                      )}
                    </li>
                  )
                })}
              </ul>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

function ModeHeading({
  mode,
  title,
  children,
}: {
  mode: keyof typeof MODES
  title: string
  children: React.ReactNode
}) {
  return (
    <div className="mb-5 max-w-2xl">
      <h2 className="text-[1.375rem] font-semibold tracking-[-0.014em]" data-mode={mode}>
        {title}
      </h2>
      <p className="mt-1 text-[0.9375rem] leading-relaxed text-muted">{children}</p>
    </div>
  )
}
