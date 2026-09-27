import Link from 'next/link'
import { notFound } from 'next/navigation'
import type { Metadata } from 'next'
import { familyMeta, getAllScenarios, getTracks } from '@/lib/content'
import { getModule, MODULES } from '@/lib/registry'
import { ModuleProgress, ScenarioList } from '@/components/Progress'
import { MetaStrip } from '@/components/PageIntro'
import { STORY_BANK } from '@/lib/editorial'

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
        href={meta.kind === 'reading' ? '/' : '/#practice'}
        className="mb-6 inline-flex items-center gap-1.5 text-[0.8125rem] text-subtle transition-colors hover:text-text"
      >
        ← {meta.kind === 'reading' ? 'Home' : 'All practice'}
      </Link>

      <header className="max-w-2xl">
        {/* The roadmap number stays out of the eyebrow: with twelve parts still planned,
            "Module 14" reads as if 2–13 were missing. The learning mode says more. */}
        <div className="mb-2 text-[0.8125rem] font-semibold uppercase tracking-[0.1em] text-accent">
          {meta.kind === 'reading' ? 'Case studies' : 'Practice'}
        </div>
        <h1 className="text-[2rem] font-bold leading-tight tracking-[-0.02em]">
          {meta.title}
        </h1>
        <p className="mt-4 text-[1.0625rem] leading-relaxed text-muted">{meta.blurb}</p>
      </header>

      <div className="mt-7 rounded-xl border border-border bg-surface p-5">
        <ModuleProgress scenarios={moduleScenarios} />
      </div>

      {moduleId === STORY_BANK.moduleId && (
        <Link
          href={STORY_BANK.href}
          className="group mt-4 block rounded-xl border border-border bg-surface p-5 transition-colors hover:border-accent"
        >
          <div className="text-[0.9375rem] font-semibold group-hover:text-accent">
            {STORY_BANK.title} →
          </div>
          <p className="mt-1 text-[0.875rem] leading-relaxed text-muted">{STORY_BANK.blurb}</p>
        </Link>
      )}

      <div className="mt-12 space-y-12">
        {tracks.map((track) => {
          const refs = moduleScenarios.filter((s) => s.trackId === track.id)
          return (
            <section key={track.id} id={track.id} className="scroll-mt-20">
              <div className="mb-4 max-w-2xl">
                <h2 className="text-[1.25rem] font-semibold tracking-[-0.014em]">
                  {track.title}
                </h2>
                <p className="mt-1.5 text-[0.9375rem] leading-relaxed text-muted">
                  {track.blurb}
                </p>
                <div className="mt-2">
                  <MetaStrip meta={familyMeta(track.id)} minutes={null} />
                </div>
              </div>
              <ScenarioList scenarios={refs} />
            </section>
          )
        })}
      </div>
    </div>
  )
}
