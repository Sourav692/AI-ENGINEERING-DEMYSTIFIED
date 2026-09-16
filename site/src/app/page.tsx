import Link from 'next/link'
import { getAllScenarios } from '@/lib/content'
import { MODULES, SITE } from '@/lib/registry'
import { ModuleProgress } from '@/components/Progress'

export default async function HomePage() {
  const scenarios = await getAllScenarios()
  const liveModules = MODULES.filter((m) => m.status === 'live')
  const firstLive = liveModules[0]
  const scenariosIn = (moduleId: string) =>
    scenarios.filter((s) => s.moduleId === moduleId)

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
          customer problem and judged on how you turn it into users, requirements,
          an architecture, an evaluation plan and a rollout. These worksheets make you
          do exactly that — then show you what a strong answer covers.
        </p>
        <div className="mt-7 flex flex-wrap gap-3">
          <Link
            href={`/modules/${firstLive.id}`}
            className="rounded-md bg-accent px-4 py-2.5 text-[0.9375rem] font-semibold text-white transition-colors hover:bg-accent-hover"
          >
            Start Module {String(firstLive.number).padStart(2, '0')}
          </Link>
          <Link
            href="/guide"
            className="rounded-md border border-border bg-surface px-4 py-2.5 text-[0.9375rem] font-semibold transition-colors hover:border-border-strong"
          >
            How to use this site
          </Link>
        </div>
      </section>

      <section className="mt-16">
        <div className="mb-5 flex items-baseline justify-between gap-4">
          <h2 className="text-[1.375rem] font-semibold tracking-[-0.014em]">
            The preparation path
          </h2>
          <span className="text-[0.8125rem] text-subtle">
            {liveModules.length} of {MODULES.length} modules available
          </span>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {MODULES.map((module) =>
            module.status === 'live' ? (
              // Not a link itself: the progress block contains its own "continue"
              // link, and an anchor inside an anchor is invalid — browsers close the
              // outer one early, which silently breaks the card.
              <div
                key={module.id}
                className="group flex flex-col rounded-xl border border-accent/30 bg-surface p-5 shadow-[var(--shadow)] transition-colors hover:border-accent sm:col-span-2"
              >
                <div className="mb-2 flex items-center gap-2.5">
                  <span className="rounded bg-accent px-1.5 py-0.5 text-[0.6875rem] font-bold tabular-nums text-white">
                    {String(module.number).padStart(2, '0')}
                  </span>
                  <span className="rounded-full bg-success-soft px-2 py-0.5 text-[0.6875rem] font-semibold uppercase tracking-wide text-success">
                    Available
                  </span>
                </div>
                <h3 className="text-[1.125rem] font-semibold">
                  <Link
                    href={`/modules/${module.id}`}
                    className="transition-colors hover:text-accent"
                  >
                    {module.title}
                  </Link>
                </h3>
                <p className="mt-1.5 text-[0.875rem] leading-relaxed text-muted">
                  {module.blurb}
                </p>
                <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-3 border-t border-border pt-4">
                  <ModuleProgress scenarios={scenariosIn(module.id)} />
                  <Link
                    href={`/modules/${module.id}`}
                    className="text-[0.875rem] font-semibold text-accent transition-colors hover:text-accent-hover"
                  >
                    All {scenariosIn(module.id).length} scenarios →
                  </Link>
                </div>
              </div>
            ) : (
              <div
                key={module.id}
                className="rounded-xl border border-border bg-surface-2/50 p-5"
              >
                <div className="mb-2 flex items-center gap-2.5">
                  <span className="rounded bg-surface-2 px-1.5 py-0.5 text-[0.6875rem] font-bold tabular-nums text-subtle">
                    {String(module.number).padStart(2, '0')}
                  </span>
                  <span className="text-[0.6875rem] font-semibold uppercase tracking-wide text-subtle">
                    Coming soon
                  </span>
                </div>
                <h3 className="text-[1.0625rem] font-semibold text-muted">{module.title}</h3>
                <p className="mt-1.5 text-[0.875rem] leading-relaxed text-subtle">
                  {module.blurb}
                </p>
              </div>
            ),
          )}
        </div>
      </section>
    </div>
  )
}
