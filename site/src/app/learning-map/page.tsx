import Link from 'next/link'
import type { Metadata } from 'next'
import { pageRef } from '@/lib/content'
import { MODULES } from '@/lib/registry'
import {
  LAST_DAY,
  LAST_DAY_GUIDES,
  MODES,
  REVIEWS,
  ROADMAP_COVERAGE,
  reviewHref,
  reviewLabel,
  type ContentMode,
} from '@/lib/editorial'
import { scenarioHref, type ScenarioRef } from '@/lib/scenario'

export const metadata: Metadata = {
  title: 'Learning map',
  description:
    'How practice, case studies and the last-day review fit together, what each numbering ' +
    'system means, and which material covers each of the eighteen review topics.',
}

const LOOP: { mode: ContentMode; title: string; href: string; when: string }[] = [
  { mode: 'orientation', title: LAST_DAY_GUIDES[0].title, href: `${LAST_DAY.href}/roadmap`, when: 'First, once' },
  { mode: 'practice', title: 'Practice', href: '/#practice', when: 'To learn a skill by doing it' },
  { mode: 'case-study', title: 'Case Studies', href: '/modules/15-fde-case-studies', when: 'To see the skill in a complete system' },
  { mode: 'revision', title: LAST_DAY.title, href: LAST_DAY.href, when: 'The days before the interview' },
]

const NUMBERING = [
  {
    label: 'Part 01–15',
    name: 'Curriculum roadmap',
    body: 'The full plan for this site. Three parts are available today — Customer Discovery (Part 01), Behavioural and Leadership Practice (Part 14) and Case Studies (Part 15); the rest are planned.',
  },
  {
    label: 'Review 01–18',
    name: 'Last-Day Review',
    body: 'A separate, complete sequence of condensed topics, in the order an interview answer flows. Reviews are not roadmap parts: several reviews usually cover one part.',
  },
  {
    label: 'G01–G20, #4–#100',
    name: 'Case numbers',
    body: 'G-numbers are the twenty grouped case studies; #-numbers come from the wider case index, which is why they have gaps. Neither implies an order to read in.',
  },
  {
    label: 'Scenario 01–12',
    name: 'Practice order',
    body: 'Practice scenarios are numbered within their track, easiest first.',
  },
]

export default async function LearningMapPage() {
  const resolve = async (refs: string[]) =>
    (await Promise.all(refs.map(pageRef))).filter((r): r is ScenarioRef => r !== null)
  const rows = await Promise.all(
    REVIEWS.map(async (r) => ({
      review: r,
      learnFirst: await resolve(r.learnFirst),
      goDeeper: await resolve(r.goDeeper),
      parts: Object.entries(ROADMAP_COVERAGE)
        .filter(([, reviews]) => reviews.includes(r.number))
        .map(([n]) => MODULES.find((m) => m.number === Number(n))!),
    })),
  )

  return (
    <div className="py-12">
      <header className="max-w-2xl">
        <p className="mb-3 text-[0.8125rem] font-semibold uppercase tracking-[0.1em] text-accent">
          {MODES.orientation.label}
        </p>
        <h1 className="text-[2rem] font-bold leading-tight tracking-[-0.02em]">Learning map</h1>
        <p className="mt-4 text-[1.0625rem] leading-relaxed text-muted">
          The site has four kinds of material, three numbering systems, and one loop for
          using them. This page shows how they relate, and which practice and case studies
          stand behind each review topic.
        </p>
      </header>

      <section className="mt-12">
        <h2 className="text-[1.25rem] font-semibold tracking-[-0.014em]">The learning loop</h2>
        <ol className="mt-4 grid gap-3 sm:grid-cols-4">
          {LOOP.map((step, i) => (
            <li key={step.mode} className="rounded-xl border border-border bg-surface p-4">
              <div className="text-[0.75rem] font-bold tabular-nums text-accent">Step {i + 1}</div>
              <Link href={step.href} className="mt-1 block text-[0.9375rem] font-semibold hover:text-accent">
                {step.title}
              </Link>
              <p className="mt-1 text-[0.8125rem] leading-relaxed text-muted">{MODES[step.mode].summary}</p>
              <p className="mt-2 text-[0.75rem] text-subtle">{step.when}</p>
            </li>
          ))}
        </ol>
        <p className="mt-4 max-w-2xl text-[0.875rem] leading-relaxed text-muted">
          Behavioural practice sits beside this loop rather than inside it: it is a template
          for your own stories, and only you can complete it.
        </p>
      </section>

      <section className="mt-14">
        <h2 className="text-[1.25rem] font-semibold tracking-[-0.014em]">Three numbering systems</h2>
        <dl className="mt-4 grid gap-3 sm:grid-cols-2">
          {NUMBERING.map((n) => (
            <div key={n.label} className="rounded-xl border border-border bg-surface p-4">
              <dt>
                <span className="font-mono text-[0.8125rem] font-semibold text-accent">{n.label}</span>
                <span className="ml-2 text-[0.9375rem] font-semibold">{n.name}</span>
              </dt>
              <dd className="mt-1 text-[0.875rem] leading-relaxed text-muted">{n.body}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="mt-14">
        <h2 className="text-[1.25rem] font-semibold tracking-[-0.014em]">Coverage by review topic</h2>
        <p className="mt-2 max-w-2xl text-[0.9375rem] leading-relaxed text-muted">
          For each review: the practice to learn the concept from, the case studies that
          show it in a complete system, and the roadmap part it belongs to.
        </p>
        <div className="mt-5 divide-y divide-border overflow-hidden rounded-xl border border-border bg-surface">
          <div
            aria-hidden
            className="hidden gap-6 bg-surface-2/60 px-4 py-2 text-[0.6875rem] font-semibold uppercase tracking-[0.08em] text-subtle lg:grid lg:grid-cols-[16rem_1fr_1fr_12rem]"
          >
            <span>Review</span>
            <span>Learn first</span>
            <span>Go deeper</span>
            <span>Roadmap</span>
          </div>
          {rows.map(({ review: r, learnFirst, goDeeper, parts }) => (
            <div key={r.number} className="grid gap-3 p-4 text-[0.875rem] lg:grid-cols-[16rem_1fr_1fr_12rem] lg:gap-6">
              <div>
                <a href={reviewHref(r)} className="font-semibold hover:text-accent">
                  <span className="mr-1.5 tabular-nums text-accent">{reviewLabel(r.number)}</span>
                  {r.title}
                </a>
              </div>
              <LinkList label="Learn first" refs={learnFirst} />
              <LinkList label="Go deeper" refs={goDeeper} />
              <div>
                <div className="text-[0.6875rem] font-semibold uppercase tracking-[0.08em] text-subtle lg:hidden">
                  Roadmap
                </div>
                <div className="text-muted">
                  {parts.map((m) => `Part ${String(m.number).padStart(2, '0')} · ${m.title}`).join('; ') || '—'}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

function LinkList({ label, refs }: { label: string; refs: ScenarioRef[] }) {
  return (
    <div>
      <div className="text-[0.6875rem] font-semibold uppercase tracking-[0.08em] text-subtle lg:hidden">{label}</div>
      <ul className="space-y-0.5">
        {refs.map((ref) => (
          <li key={`${ref.trackId}/${ref.slug}`}>
            <Link href={scenarioHref(ref)} className="text-accent hover:text-accent-hover">
              {ref.reading && ref.tag ? `${ref.tag} ` : ''}
              {ref.title}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
