import Link from 'next/link'
import { notFound } from 'next/navigation'
import type { Metadata } from 'next'
import { familyMeta, getAllScenarios, getCaseStudy, getRelated, getScenario } from '@/lib/content'
import { getModule } from '@/lib/registry'
import { MODES } from '@/lib/editorial'
import { ScenarioView } from '@/components/ScenarioView'
import { CaseStudyView } from '@/components/CaseStudyView'
import { BeforeYouStart, Fact, MetaStrip, WhereNext } from '@/components/PageIntro'
import { qualifiedTitle, type CaseStudy, type ScenarioRef } from '@/lib/scenario'

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
          title: `${study.ref.tag} · ${qualifiedTitle(study.ref)}`,
          description: `FDE case study: ${study.title} — ${study.docs.map((d) => d.label.toLowerCase()).join(', ')}.`,
        }
      : {}
  }
  const scenario = await getScenario(moduleId, track, slug)
  if (!scenario) return {}
  const meta = familyMeta(track)
  return {
    title: qualifiedTitle({ title: scenario.title, qualifier: scenario.ref.qualifier }),
    description: `${MODES[meta.mode].label}: ${scenario.title}. ${meta.outcomes[0]}.`,
  }
}

/** Practice and behavioural pages sit under Practice; reading pages under Case Studies. */
function Breadcrumbs({ moduleId, page, reading }: { moduleId: string; page: ScenarioRef; reading: boolean }) {
  const meta = getModule(moduleId)
  return (
    <nav aria-label="Breadcrumb" className="no-print mb-6 flex flex-wrap items-center gap-1.5 text-[0.8125rem] text-subtle">
      {reading ? (
        <Link href={`/modules/${moduleId}`} className="transition-colors hover:text-text">
          Case Studies
        </Link>
      ) : (
        <>
          <Link href="/#practice" className="transition-colors hover:text-text">
            Practice
          </Link>
          <span aria-hidden>/</span>
          <Link href={`/modules/${moduleId}`} className="transition-colors hover:text-text">
            {meta?.title ?? moduleId}
          </Link>
        </>
      )}
      <span aria-hidden>/</span>
      <Link href={`/modules/${moduleId}#${page.trackId}`} className="transition-colors hover:text-text">
        {page.trackTitle}
      </Link>
      {page.qualifier && (
        <>
          <span aria-hidden>/</span>
          <span className="text-muted">{page.qualifier}</span>
        </>
      )}
    </nav>
  )
}

export default async function ScenarioPage({ params }: { params: Promise<Params> }) {
  const { module: moduleId, track, scenario: slug } = await params
  const moduleMeta = getModule(moduleId)
  if (moduleMeta?.kind === 'reading') return <CaseStudyPage moduleId={moduleId} track={track} slug={slug} />

  const scenario = await getScenario(moduleId, track, slug)
  if (!scenario) notFound()
  const meta = familyMeta(track)
  const related = await getRelated(scenario.ref)

  return (
    <div className="py-10">
      <Breadcrumbs moduleId={moduleId} page={scenario.ref} reading={false} />

      <header className="mb-8 max-w-3xl">
        <div className="mb-2 flex items-center gap-2.5">
          <span className="text-[0.8125rem] font-bold tabular-nums text-accent">
            {meta.personalisation ? 'Question set' : 'Scenario'} {String(scenario.ref.order).padStart(2, '0')}
          </span>
          <span className="text-[0.8125rem] text-subtle">{scenario.ref.trackTitle}</span>
        </div>
        <h1 className="text-[2rem] font-bold leading-[1.2] tracking-[-0.02em]">
          {scenario.title}
        </h1>
        <div className="mt-3">
          <MetaStrip
            meta={meta}
            minutes={null}
            extra={
              meta.personalisation && (
                <>
                  <span aria-hidden>·</span>
                  <span className="font-semibold text-text">
                    Personalisation required
                    {scenario.fillSlots > 0 &&
                      ` — ${scenario.fillSlots} detail${scenario.fillSlots === 1 ? '' : 's'} in the model answers to replace with your own`}
                  </span>
                </>
              )
            }
          />
        </div>
        <BeforeYouStart meta={meta} />
      </header>

      <ScenarioView scenario={scenario} requireComplete={Boolean(meta.personalisation)} />

      <WhereNext reviews={related.reviews} counterpart={related.counterpart} next={null} />
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
  const meta = familyMeta(track)
  const related = await getRelated(study.ref)
  const minutes = study.docs.reduce((sum, d) => sum + d.minutes, 0)

  return (
    <div className="py-10">
      <Breadcrumbs moduleId={moduleId} page={study.ref} reading />

      <header className="mb-6 max-w-3xl">
        <div className="mb-2 flex items-center gap-2.5">
          <span className="rounded bg-accent px-1.5 py-0.5 text-[0.6875rem] font-bold tabular-nums text-white">
            {study.ref.tag}
          </span>
          <span className="text-[0.8125rem] text-subtle">{study.ref.trackTitle}</span>
        </div>
        <h1 className="text-[2rem] font-bold leading-[1.2] tracking-[-0.02em]">{study.title}</h1>
        <div className="mt-3">
          <MetaStrip
            meta={meta}
            minutes={study.docs.length === 1 ? minutes : null}
            extra={
              study.docs.length > 1 && (
                <>
                  <span aria-hidden>·</span>
                  <span>
                    {study.docs.length} documents, {minutes} min in total
                  </span>
                </>
              )
            }
          />
        </div>
        <BeforeYouStart meta={meta}>
          <ReadingOrder study={study} />
        </BeforeYouStart>
      </header>

      <CaseStudyView study={study} />

      <WhereNext reviews={related.reviews} counterpart={related.counterpart} next={null} />
    </div>
  )
}

/**
 * The tabs in the order worth reading them, with time per tab, plus where the sources
 * live and any superseded versions — so every tab can reach the provenance without
 * repeating it.
 */
function ReadingOrder({ study }: { study: CaseStudy }) {
  const practice = study.ref.practice
  return (
    <>
      {study.docs.length > 1 && (
        <Fact term="Reading order">
          <ol className="list-decimal space-y-0.5 pl-4 marker:text-subtle">
            {study.docs.map((d) => (
              <li key={d.tab}>
                <a href={`#${d.tab}`} className="text-accent hover:text-accent-hover">
                  {d.label}
                </a>{' '}
                <span className="text-subtle">· {d.minutes} min</span>
              </li>
            ))}
          </ol>
        </Fact>
      )}
      <Fact term="Sources">
        {study.sources ? (
          <>
            The references for every tab are in{' '}
            <a href={`#${study.sources.anchor}`} className="text-accent hover:text-accent-hover">
              {study.sources.label} → {study.sources.title}
            </a>
            .
          </>
        ) : (
          'This case does not cite external sources; treat vendor-specific details as illustrative.'
        )}
        {practice && (
          <>
            {' '}
            An{' '}
            <Link
              href={`/modules/01-customer-discovery-and-decomposition/${practice}`}
              className="text-accent hover:text-accent-hover"
            >
              interactive Practice Worksheet
            </Link>{' '}
            saves your answers as you type.
          </>
        )}
        {study.ref.archived?.length ? (
          <>
            {' '}
            Earlier versions, kept for reference:{' '}
            {study.ref.archived.map((a, i) => (
              <span key={a.href}>
                {i > 0 && ', '}
                <a href={a.href} target="_blank" rel="noopener noreferrer" className="text-accent hover:text-accent-hover">
                  {a.label}
                </a>
              </span>
            ))}
            .
          </>
        ) : null}
      </Fact>
    </>
  )
}
