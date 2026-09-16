'use client'

import { useEffect, useRef, useState } from 'react'
import { STATUS_LABELS, type Status } from '@/lib/storage'

const STATUSES: Status[] = ['not-started', 'practiced', 'mastered']

export function ScenarioToolbar({
  status,
  onStatus,
  answered,
  total,
  savedAt,
  storageAvailable,
  revealAll,
  onRevealAll,
  onExport,
  onReset,
}: {
  status: Status
  onStatus: (s: Status) => void
  answered: number
  total: number
  savedAt: number | null
  storageAvailable: boolean
  revealAll: boolean
  onRevealAll: (v: boolean) => void
  onExport: () => void
  onReset: () => void
}) {
  return (
    <div className="no-print sticky top-[3.75rem] z-20 -mx-4 mb-8 border-y border-border bg-bg/85 px-4 py-2.5 backdrop-blur-md sm:mx-0 sm:rounded-lg sm:border sm:px-3">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
        <div className="flex items-center gap-2">
          <div
            className="h-1.5 w-20 overflow-hidden rounded-full bg-surface-2"
            role="progressbar"
            aria-valuenow={answered}
            aria-valuemin={0}
            aria-valuemax={total}
            aria-label="Worksheet completion"
          >
            <div
              className="h-full rounded-full bg-accent transition-[width] duration-300"
              style={{ width: `${total ? (answered / total) * 100 : 0}%` }}
            />
          </div>
          <span className="tabular-nums text-[0.75rem] text-subtle">
            {answered}/{total}
          </span>
        </div>

        <div className="h-4 w-px bg-border" aria-hidden />

        <div className="flex gap-0.5 rounded-md bg-surface-2 p-0.5" role="group" aria-label="Scenario status">
          {STATUSES.map((s) => (
            <button
              key={s}
              type="button"
              aria-pressed={status === s}
              onClick={() => onStatus(s)}
              className={`rounded px-2 py-1 text-[0.75rem] font-medium transition-colors ${
                status === s
                  ? 'bg-surface text-text shadow-[var(--shadow)]'
                  : 'text-muted hover:text-text'
              }`}
            >
              {STATUS_LABELS[s]}
            </button>
          ))}
        </div>

        <Timer />

        <div className="ml-auto flex items-center gap-1">
          {savedAt !== null && (
            <span className="mr-1 flex items-center gap-1 text-[0.75rem] text-success">
              <svg viewBox="0 0 16 16" aria-hidden className="h-3 w-3">
                <path d="M3 8.5l3.5 3.5L13 5" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Saved
            </span>
          )}
          {!storageAvailable && (
            <span
              className="mr-1 text-[0.75rem] text-warning"
              title="Your browser is blocking local storage, so answers cannot be kept between visits. Export to save your work."
            >
              Not saving
            </span>
          )}
          <ToolbarButton onClick={() => onRevealAll(!revealAll)}>
            {revealAll ? 'Hide all keys' : 'Reveal all keys'}
          </ToolbarButton>
          <ToolbarButton onClick={onExport}>Export</ToolbarButton>
          <ToolbarButton onClick={() => window.print()}>Print</ToolbarButton>
          <ToolbarButton onClick={onReset} danger>
            Reset
          </ToolbarButton>
        </div>
      </div>
    </div>
  )
}

function ToolbarButton({
  children,
  onClick,
  danger,
}: {
  children: React.ReactNode
  onClick: () => void
  danger?: boolean
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-md px-2 py-1 text-[0.75rem] font-medium transition-colors ${
        danger
          ? 'text-subtle hover:bg-surface-2 hover:text-warning'
          : 'text-muted hover:bg-surface-2 hover:text-text'
      }`}
    >
      {children}
    </button>
  )
}

const DURATIONS = [15, 30, 45]

/**
 * Optional countdown for practising under interview pressure. Deliberately quiet
 * until started, and it only counts down — nothing depends on it, and running out
 * does not interrupt what you are doing.
 */
function Timer() {
  const [remaining, setRemaining] = useState<number | null>(null)
  const [running, setRunning] = useState(false)
  const [picking, setPicking] = useState(false)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (!running) return
    intervalRef.current = setInterval(() => {
      setRemaining((r) => {
        if (r === null) return null
        if (r <= 1) {
          setRunning(false)
          return 0
        }
        return r - 1
      })
    }, 1000)
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [running])

  if (remaining === null) {
    return (
      <div className="relative">
        <ToolbarButton onClick={() => setPicking((v) => !v)}>Timer</ToolbarButton>
        {picking && (
          <div className="absolute left-0 top-full z-30 mt-1 flex gap-0.5 rounded-md border border-border bg-surface p-1 shadow-[var(--shadow-lg)]">
            {DURATIONS.map((minutes) => (
              <button
                key={minutes}
                type="button"
                onClick={() => {
                  setRemaining(minutes * 60)
                  setRunning(true)
                  setPicking(false)
                }}
                className="rounded px-2 py-1 text-[0.75rem] font-medium text-muted transition-colors hover:bg-surface-2 hover:text-text"
              >
                {minutes}m
              </button>
            ))}
          </div>
        )}
      </div>
    )
  }

  const minutes = Math.floor(remaining / 60)
  const seconds = remaining % 60
  const expired = remaining === 0

  return (
    <div className="flex items-center gap-1">
      <span
        className={`tabular-nums text-[0.8125rem] font-semibold ${expired ? 'text-warning' : 'text-text'}`}
        role="timer"
        aria-live="off"
      >
        {minutes}:{String(seconds).padStart(2, '0')}
      </span>
      {!expired && (
        <ToolbarButton onClick={() => setRunning((v) => !v)}>
          {running ? 'Pause' : 'Resume'}
        </ToolbarButton>
      )}
      <ToolbarButton
        onClick={() => {
          setRunning(false)
          setRemaining(null)
        }}
      >
        Clear
      </ToolbarButton>
    </div>
  )
}
