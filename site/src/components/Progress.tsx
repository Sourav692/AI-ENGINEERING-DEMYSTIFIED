'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import type { ScenarioRef } from '@/lib/scenario'
import { scenarioHref } from '@/lib/scenario'
import {
  loadProgress,
  PROGRESS_EVENT,
  STATUS_LABELS,
  type Status,
} from '@/lib/storage'

/**
 * Progress lives in the reader's browser, so every component that shows it renders a
 * neutral placeholder on the server and fills in after mount. Without that the
 * prerendered HTML and the first client render disagree and React discards the tree.
 */
function useProgress(scenarios: ScenarioRef[]) {
  const [progress, setProgress] = useState<Record<string, Status> | null>(null)

  useEffect(() => {
    const read = () => {
      const next: Record<string, Status> = {}
      for (const s of scenarios) {
        next[`${s.trackId}/${s.slug}`] = loadProgress(`${s.trackId}/${s.slug}`).status
      }
      setProgress(next)
    }
    read()
    window.addEventListener(PROGRESS_EVENT, read)
    window.addEventListener('storage', read)
    return () => {
      window.removeEventListener(PROGRESS_EVENT, read)
      window.removeEventListener('storage', read)
    }
  }, [scenarios])

  return progress
}

export function ModuleProgress({ scenarios }: { scenarios: ScenarioRef[] }) {
  const progress = useProgress(scenarios)
  // Reading modules count pages read, not worksheets mastered.
  const reading = scenarios.some((s) => s.reading)

  const done = progress
    ? Object.values(progress).filter((s) => s === 'mastered').length
    : 0
  const started = progress
    ? Object.values(progress).filter((s) => s === 'practiced').length
    : 0
  const total = scenarios.length
  const percent = total ? Math.round((done / total) * 100) : 0

  const next = progress
    ? scenarios.find((s) => progress[`${s.trackId}/${s.slug}`] !== 'mastered')
    : undefined

  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-3">
      <div className="flex items-center gap-3">
        <Ring percent={progress ? percent : 0} />
        <div>
          <div className="text-[0.9375rem] font-semibold tabular-nums">
            {progress ? `${done} of ${total}` : `${total} ${reading ? 'case studies' : 'scenarios'}`}
          </div>
          <div className="text-[0.75rem] text-subtle">
            {progress
              ? started > 0
                ? `${reading ? 'read' : 'mastered'} · ${started} in progress`
                : reading
                  ? 'read'
                  : 'mastered'
              : reading
                ? 'to read'
                : 'with answer keys'}
          </div>
        </div>
      </div>

      {next && (
        <Link
          href={scenarioHref(next)}
          className="rounded-md bg-accent px-3.5 py-2 text-[0.875rem] font-semibold text-white transition-colors hover:bg-accent-hover"
        >
          {done + started > 0 ? 'Continue' : 'Start'} → {next.title}
        </Link>
      )}
    </div>
  )
}

export function Ring({ percent, size = 40 }: { percent: number; size?: number }) {
  const stroke = 3.5
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden className="shrink-0 -rotate-90">
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="var(--surface-2)"
        strokeWidth={stroke}
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="var(--accent)"
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={circumference * (1 - percent / 100)}
        style={{ transition: 'stroke-dashoffset 500ms ease' }}
      />
    </svg>
  )
}

const READING_LABELS: Record<Status, string> = {
  'not-started': 'Not started',
  practiced: 'In progress',
  mastered: 'Read',
}

const DOT: Record<Status, string> = {
  'not-started': 'border-border-strong',
  practiced: 'border-accent bg-accent/40',
  mastered: 'border-success bg-success',
}

export function ScenarioList({ scenarios }: { scenarios: ScenarioRef[] }) {
  const progress = useProgress(scenarios)

  return (
    <ul className="divide-y divide-border overflow-hidden rounded-xl border border-border bg-surface">
      {scenarios.map((scenario) => {
        const status = progress?.[`${scenario.trackId}/${scenario.slug}`] ?? 'not-started'
        return (
          <li key={scenario.slug}>
            <Link
              href={scenarioHref(scenario)}
              className="group flex items-center gap-3.5 px-4 py-3 transition-colors hover:bg-surface-2"
            >
              <span
                aria-hidden
                className={`h-2.5 w-2.5 shrink-0 rounded-full border-2 ${DOT[status]}`}
              />
              <span className={`${scenario.tag ? 'w-8' : 'w-6'} shrink-0 text-[0.8125rem] font-semibold tabular-nums text-subtle`}>
                {scenario.tag ?? String(scenario.order).padStart(2, '0')}
              </span>
              <span className="flex-1 text-[0.9375rem] font-medium group-hover:text-accent">
                {scenario.title}
              </span>
              {progress && status !== 'not-started' && (
                <span className="hidden shrink-0 text-[0.75rem] text-subtle sm:inline">
                  {scenario.reading ? READING_LABELS[status] : STATUS_LABELS[status]}
                </span>
              )}
              <svg viewBox="0 0 16 16" aria-hidden className="h-3.5 w-3.5 shrink-0 text-subtle transition-transform group-hover:translate-x-0.5">
                <path d="M6 3l5 5-5 5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </Link>
          </li>
        )
      })}
    </ul>
  )
}
