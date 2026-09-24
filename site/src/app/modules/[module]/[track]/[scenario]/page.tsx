import Link from 'next/link'
import { notFound } from 'next/navigation'
import type { Metadata } from 'next'
import { getAllScenarios, getCaseStudy, getScenario } from '@/lib/content'
import { getModule } from '@/lib/registry'
import { ScenarioView } from '@/components/ScenarioView'
import { CaseStudyView } from '@/components/CaseStudyView'
import type { CaseStudy } from '@/lib/scenario'

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
  if (getModule(moduleId)?.kind === 'reading') {
    const study = await getCaseStudy(moduleId, track, slug)
    return study
      ? {
          title: `${study.ref.tag} · ${study.title}`,
          description: `FDE case study: ${study.title} — interview guide, deep dive, cheat sheet and full pack.`,
        }
      : {}
  }
  const scenario = await getScenario(moduleId, track, slug)
  if (!scenario) return {}
  return {
    title: scenario.title,
    description: `FDE case study worksheet and answer key: ${scenario.title}.`,
  }
}

export default async function ScenarioPage({ params }: { params: Promise<Params> }) {
  const { module: moduleId, track, scenario: slug } = await params
  const meta = getModule(moduleId)
  if (meta?.kind === 'reading') return <CaseStudyPage moduleId={moduleId} track={track} slug={slug} />

  const scenario = await getScenario(moduleId, track, slug)
  if (!scenario) notFound()

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

async function CaseStudyPage({
  moduleId,
  track,
  slug,
}: {
  moduleId: string
  track: string
  slug: string
}) {
  const study = await getCaseStudy(moduleId, track, slug)
  if (!study) notFound()
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
        <span className="text-muted">{study.ref.trackTitle}</span>
      </nav>

      <header className="mb-6 max-w-3xl">
        <div className="mb-2 flex items-center gap-2.5">
          <span className="rounded bg-accent px-1.5 py-0.5 text-[0.6875rem] font-bold tabular-nums text-white">
            {study.ref.tag}
          </span>
          <span className="text-[0.8125rem] text-subtle">{study.ref.trackTitle}</span>
        </div>
        <h1 className="text-[2rem] font-bold leading-[1.2] tracking-[-0.02em]">{study.title}</h1>
        <CaseStudyIntro study={study} />
      </header>

      <CaseStudyView study={study} />
    </div>
  )
}

/**
 * The line under a case study's title says how to read *its* tabs. Grouped cases share
 * one four-tab shape; standalone cases vary, and a one-document case needs no advice.
 */
function CaseStudyIntro({ study }: { study: CaseStudy }) {
  const tabs = study.docs.map((d) => d.tab)
  const practice = study.ref.practice
  let text: string | null = null
  if (tabs[0] === 'main') {
    text =
      'Start with Main, the guide you would talk through in the interview. Deep Dive holds ' +
      'the detail for follow-up questions, Cheat Sheet is the one-page revision, and Full ' +
      'Pack is the complete sourced write-up behind all three.'
  } else if (tabs.includes('worksheet')) {
    text =
      'Try the Worksheet before opening the Answer Key. The two tutorials walk the same case ' +
      'at length: V2 in cram form, V1 as the original chapter tutorial.'
  } else if (tabs.length > 1) {
    text = 'Each tab is a separate document on this case, in the order worth reading them.'
  }
  if (!text && !practice) return null
  return (
    <p className="no-print mt-3 text-[0.9375rem] leading-relaxed text-muted">
      {text}
      {practice && (
        <>
          {' '}
          The worksheet is also available as an{' '}
          <Link
            href={`/modules/01-customer-discovery-and-decomposition/${practice}`}
            className="font-medium text-accent underline underline-offset-2 hover:text-accent-hover"
          >
            interactive worksheet in Module 01
          </Link>
          , where your answers are saved as you type.
        </>
      )}
    </p>
  )
}
