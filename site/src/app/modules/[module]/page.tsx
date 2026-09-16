import Link from 'next/link'
import { notFound } from 'next/navigation'
import type { Metadata } from 'next'
import { getAllScenarios, getTracks } from '@/lib/content'
import { getModule, MODULES } from '@/lib/registry'
import { ModuleProgress, ScenarioList } from '@/components/Progress'

export function generateStaticParams() {
  return MODULES.filter((m) => m.status === 'live').map((m) => ({ module: m.id }))
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ module: string }>
}): Promise<Metadata> {
  const { module: moduleId } = await params
  const meta = getModule(moduleId)
  return meta ? { title: meta.title, description: meta.blurb } : {}
}

export default async function ModulePage({
  params,
}: {
  params: Promise<{ module: string }>
}) {
  const { module: moduleId } = await params
  const meta = getModule(moduleId)
  if (!meta || meta.status !== 'live') notFound()

  const tracks = await getTracks(moduleId)
  // Scoped to this module: `getAllScenarios()` spans every live module, and the
  // progress ring and track lists on this page must only count what is on it.
  const moduleScenarios = (await getAllScenarios()).filter(
    (s) => s.moduleId === moduleId,
  )

  return (
    <div className="py-12">
      <Link
        href="/"
        className="mb-6 inline-flex items-center gap-1.5 text-[0.8125rem] text-subtle transition-colors hover:text-text"
      >
        ← All modules
      </Link>

      <header className="max-w-2xl">
        <div className="mb-2 text-[0.8125rem] font-semibold uppercase tracking-[0.1em] text-accent">
          Module {String(meta.number).padStart(2, '0')}
        </div>
        <h1 className="text-[2rem] font-bold leading-tight tracking-[-0.02em]">
          {meta.title}
        </h1>
        <p className="mt-4 text-[1.0625rem] leading-relaxed text-muted">{meta.blurb}</p>
      </header>

      <div className="mt-7 rounded-xl border border-border bg-surface p-5">
        <ModuleProgress scenarios={moduleScenarios} />
      </div>

      <div className="mt-12 space-y-12">
        {tracks.map((track) => {
          const refs = moduleScenarios.filter((s) => s.trackId === track.id)
          return (
            <section key={track.id}>
              <div className="mb-4 max-w-2xl">
                <h2 className="text-[1.25rem] font-semibold tracking-[-0.014em]">
                  {track.title}
                </h2>
                <p className="mt-1.5 text-[0.9375rem] leading-relaxed text-muted">
                  {track.blurb}
                </p>
              </div>
              <ScenarioList scenarios={refs} />
            </section>
          )
        })}
      </div>
    </div>
  )
}
