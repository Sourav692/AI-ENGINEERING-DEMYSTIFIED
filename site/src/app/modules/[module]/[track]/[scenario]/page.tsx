import Link from 'next/link'
import { notFound } from 'next/navigation'
import type { Metadata } from 'next'
import { getAllScenarios, getScenario } from '@/lib/content'
import { getModule } from '@/lib/registry'
import { ScenarioView } from '@/components/ScenarioView'

type Params = { module: string; track: string; scenario: string }

export async function generateStaticParams() {
  const scenarios = await getAllScenarios()
  return scenarios.map((s) => ({
    module: s.moduleId,
    track: s.trackId,
    scenario: s.slug,
  }))
}

export async function generateMetadata({
  params,
}: {
  params: Promise<Params>
}): Promise<Metadata> {
  const { module: moduleId, track, scenario: slug } = await params
  const scenario = await getScenario(moduleId, track, slug)
  if (!scenario) return {}
  return {
    title: scenario.title,
    description: `FDE case study worksheet and answer key: ${scenario.title}.`,
  }
}

export default async function ScenarioPage({ params }: { params: Promise<Params> }) {
  const { module: moduleId, track, scenario: slug } = await params
  const scenario = await getScenario(moduleId, track, slug)
  if (!scenario) notFound()

  const meta = getModule(moduleId)

  return (
    <div className="py-10">
      <nav className="no-print mb-6 flex flex-wrap items-center gap-1.5 text-[0.8125rem] text-subtle">
        <Link href="/" className="transition-colors hover:text-text">
          Modules
        </Link>
        <span aria-hidden>/</span>
        <Link href={`/modules/${moduleId}`} className="transition-colors hover:text-text">
          {meta?.title ?? moduleId}
        </Link>
        <span aria-hidden>/</span>
        <span className="text-muted">{scenario.ref.trackTitle}</span>
      </nav>

      <header className="mb-8 max-w-3xl">
        <div className="mb-2 flex items-center gap-2.5">
          <span className="text-[0.8125rem] font-bold tabular-nums text-accent">
            Case study {String(scenario.ref.order).padStart(2, '0')}
          </span>
          <span className="text-[0.8125rem] text-subtle">{scenario.ref.trackTitle}</span>
        </div>
        <h1 className="text-[2rem] font-bold leading-[1.2] tracking-[-0.02em]">
          {scenario.title}
        </h1>
        <p className="no-print mt-3 text-[0.9375rem] leading-relaxed text-muted">
          Work through the blanks yourself before opening any answer key. Everything you
          type is saved in this browser as you go.
        </p>
      </header>

      <ScenarioView scenario={scenario} />
    </div>
  )
}
