import type { Metadata } from 'next'
import { GLOSSARY, glossaryAnchor, type GlossaryGroup } from '@/lib/glossary'

export const metadata: Metadata = {
  title: 'Glossary',
  description:
    'Every acronym and term the site uses, in plain spoken words — and, for the big ones, ' +
    'the line you would actually say in an interview.',
}

const GROUPS: GlossaryGroup[] = [
  'Interview and delivery',
  'Models and AI',
  'Retrieval and data',
  'Agents and tools',
  'Security and compliance',
  'Reliability and operations',
  'Performance and cost',
  'Business and domain',
]

export default function GlossaryPage() {
  return (
    <div className="py-12">
      <header className="max-w-2xl">
        <h1 className="text-[2rem] font-bold leading-tight tracking-[-0.02em]">Glossary</h1>
        <p className="mt-4 text-[1.0625rem] leading-relaxed text-muted">
          Every acronym and term the site leans on, said the simple way. Where a term comes
          up a lot in interviews, there is a line you can actually say out loud. Acronyms are
          also spelled out the first time they appear on each page.
        </p>
      </header>

      <nav aria-label="Glossary sections" className="no-print mt-8 flex flex-wrap gap-2">
        {GROUPS.map((g) => (
          <a
            key={g}
            href={`#${glossaryAnchor(g)}`}
            className="rounded-full border border-border px-3 py-1 text-[0.8125rem] text-muted transition-colors hover:border-border-strong hover:text-text"
          >
            {g}
          </a>
        ))}
      </nav>

      <div className="mt-10 space-y-12">
        {GROUPS.map((group) => {
          const entries = GLOSSARY.filter((e) => e.group === group).sort((a, b) =>
            a.term.localeCompare(b.term, 'en', { sensitivity: 'base' }),
          )
          return (
            <section key={group} id={glossaryAnchor(group)} className="scroll-mt-20">
              <h2 className="text-[1.25rem] font-semibold tracking-[-0.014em]">{group}</h2>
              <dl className="mt-4 divide-y divide-border rounded-xl border border-border bg-surface">
                {entries.map((e) => (
                  <div key={e.term} id={glossaryAnchor(e.term)} className="scroll-mt-20 px-4 py-3.5 sm:grid sm:grid-cols-[12rem_1fr] sm:gap-6">
                    <dt>
                      <span className="text-[0.9375rem] font-semibold">{e.term}</span>
                      {e.expansion && (
                        <span className="block text-[0.8125rem] text-subtle">{e.expansion}</span>
                      )}
                    </dt>
                    <dd className="mt-1 text-[0.9375rem] leading-relaxed text-muted sm:mt-0">
                      {e.plain}
                      {e.sayIt && (
                        <span className="mt-1.5 block border-l-2 border-accent/40 pl-3 text-[0.875rem] text-text">
                          <span className="text-[0.6875rem] font-semibold uppercase tracking-[0.08em] text-accent">
                            Say it like
                          </span>{' '}
                          “{e.sayIt}”
                        </span>
                      )}
                    </dd>
                  </div>
                ))}
              </dl>
            </section>
          )
        })}
      </div>
    </div>
  )
}
