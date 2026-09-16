import Link from 'next/link'
import type { Metadata } from 'next'
import { MODULES, SITE } from '@/lib/registry'
import { ClearAllButton } from '@/components/ClearAllButton'

export const metadata: Metadata = {
  title: 'How to use this site',
  description:
    'The practice loop behind Forward Deployed: attempt a section, compare with the ' +
    'answer key, score yourself honestly, and repeat until the moves are automatic.',
}

const STEPS = [
  {
    n: 1,
    title: 'Read the prompt and resist the urge to design',
    body: 'Section 1 is deliberately vague, the way a real customer conversation is. The first instinct of most candidates is to reach for a vector database. The first instinct of a strong candidate is to ask what breaks today and who pays for it.',
  },
  {
    n: 2,
    title: 'Fill in the blanks before you reveal anything',
    body: 'Sections 3 through 6 are empty because writing a wrong answer and seeing why it is wrong teaches more than reading a right one. Type badly, type fast, type something. An empty worksheet compared against a perfect key teaches nothing.',
  },
  {
    n: 3,
    title: 'Reveal one section at a time',
    body: 'Each section has its own “Compare with the answer key”. Open it only after you have attempted that section. The keys are not the only correct answer — they show the ground a strong answer covers, and the shape of the reasoning behind it.',
  },
  {
    n: 4,
    title: 'Score yourself against the rubric, honestly',
    body: 'Section 11 is the interviewer’s scorecard. A 3 means “reasonable components” and most first attempts land there. The value is in seeing which row is consistently lowest across several scenarios — that is the one to work on.',
  },
  {
    n: 5,
    title: 'Rehearse the closing answer out loud',
    body: 'Every answer key ends with a two-minute spoken summary. Say yours out loud before revealing theirs. Being right and being unable to say it in two minutes reads, from the other side of the table, as not being right.',
  },
]

export default function GuidePage() {
  const live = MODULES.filter((m) => m.status === 'live').length

  return (
    <div className="py-12">
      <header className="max-w-2xl">
        <h1 className="text-[2rem] font-bold leading-tight tracking-[-0.02em]">
          How to use this site
        </h1>
        <p className="mt-4 text-[1.0625rem] leading-relaxed text-muted">
          {SITE.name} is a practice system, not a reading list. Every case study is a
          worksheet you fill in and an answer key you check yourself against. The loop
          below is the whole method.
        </p>
      </header>

      <section className="mt-12 max-w-2xl space-y-8">
        {STEPS.map((step) => (
          <div key={step.n} className="flex gap-4">
            <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent-soft text-[0.8125rem] font-bold text-accent">
              {step.n}
            </span>
            <div>
              <h2 className="text-[1.0625rem] font-semibold">{step.title}</h2>
              <p className="mt-1.5 leading-relaxed text-muted">{step.body}</p>
            </div>
          </div>
        ))}
      </section>

      <section className="mt-14 max-w-2xl">
        <h2 className="text-[1.25rem] font-semibold tracking-[-0.014em]">
          What an FDE interview actually tests
        </h2>
        <p className="mt-3 leading-relaxed text-muted">
          Across every scenario here, the same five things are being assessed — they are
          the rows of the scorecard, and they are worth knowing by name:
        </p>
        <dl className="mt-5 space-y-3">
          {[
            ['Problem framing', 'Do you find the dangerous constraint before you design, or do you jump to tools?'],
            ['Architecture', 'Are your components specific, bounded and observable, or is it a generic diagram?'],
            ['Evaluation', 'Can you say how you would know it works — with datasets, thresholds and owners?'],
            ['Production thinking', 'Do you plan for failure, rollback, cost and drills, or does the story end at the demo?'],
            ['Communication', 'Can an executive and an engineer both take what they need from the same answer?'],
          ].map(([term, desc]) => (
            <div key={term} className="rounded-lg border border-border bg-surface p-4">
              <dt className="text-[0.9375rem] font-semibold">{term}</dt>
              <dd className="mt-1 text-[0.9375rem] leading-relaxed text-muted">{desc}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="mt-14 max-w-2xl">
        <h2 className="text-[1.25rem] font-semibold tracking-[-0.014em]">Your answers</h2>
        <p className="mt-3 leading-relaxed text-muted">
          Everything you type is stored in this browser and nowhere else. There is no
          account and no server — nothing you write is sent anywhere or visible to anyone
          else. That also means answers do not follow you to another device or browser,
          and clearing your browsing data clears them. Use <strong>Export</strong> on any
          scenario to download your answers as markdown before that matters.
        </p>
        <p className="mt-3 leading-relaxed text-muted">
          If your browser blocks local storage — a private window, or site data turned off
          — the worksheets still work, but nothing is kept between visits. The toolbar
          says <em>Not saving</em> when that happens.
        </p>
        <div className="mt-5">
          <ClearAllButton />
        </div>
      </section>

      <section className="mt-14 max-w-2xl border-t border-border pt-8">
        <h2 className="text-[1.25rem] font-semibold tracking-[-0.014em]">
          Sources and attribution
        </h2>
        <p className="mt-3 leading-relaxed text-muted">
          The System Design Scenarios track is derived from{' '}
          <em>The Forward Deployed Engineer System Design Interview</em>; the worksheets
          and answer keys here are condensed practice material built from those
          scenarios, not a reproduction of the book. If the scenarios are useful to you,
          the book is worth reading in full. The final scenario in that track, the
          enterprise chatbot platform, is a custom addition and is not from the book.
        </p>
        <p className="mt-3 leading-relaxed text-muted">
          The Core Scenarios track is original material written for this system.
        </p>
      </section>

      <section className="mt-14 max-w-2xl border-t border-border pt-8">
        <h2 className="text-[1.25rem] font-semibold tracking-[-0.014em]">What’s next</h2>
        <p className="mt-3 leading-relaxed text-muted">
          {live} of {MODULES.length} modules are available today. The rest of the path is
          listed on the{' '}
          <Link href="/" className="text-accent underline underline-offset-2">
            modules page
          </Link>
          {' '}so you can see where the preparation goes from here.
        </p>
      </section>
    </div>
  )
}
