'use client'

import Link from 'next/link'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { Block, Section } from '@/lib/parse'
import type { Scenario } from '@/lib/scenario'
import { scenarioHref } from '@/lib/scenario'
import {
  clearScenario,
  loadAnswers,
  loadExtraRows,
  loadScores,
  loadStatus,
  notifyProgress,
  saveAnswers,
  saveExtraRows,
  saveScores,
  saveStatus,
  type Answers,
  type ExtraRows,
  type Scores,
  type Status,
} from '@/lib/storage'
import { Blocks } from './Blocks'
import { AnswerKeyReveal } from './AnswerKeyReveal'
import { ScenarioToolbar } from './ScenarioToolbar'

const SAVE_DEBOUNCE_MS = 400

export function ScenarioView({ scenario }: { scenario: Scenario }) {
  const id = `${scenario.ref.trackId}/${scenario.ref.slug}`

  // State starts empty on both server and client so the first client render matches
  // the prerendered HTML exactly; saved values arrive in the effect below.
  const [answers, setAnswers] = useState<Answers>({})
  const [scores, setScores] = useState<Scores>({})
  const [extraRows, setExtraRows] = useState<ExtraRows>({})
  const [status, setStatus] = useState<Status>('not-started')
  const [hydrated, setHydrated] = useState(false)
  const [storageAvailable, setStorageAvailable] = useState(true)
  const [savedAt, setSavedAt] = useState<number | null>(null)
  const [revealAll, setRevealAll] = useState(false)

  useEffect(() => {
    setAnswers(loadAnswers(id))
    setScores(loadScores(id))
    setExtraRows(loadExtraRows(id))
    setStatus(loadStatus(id))
    try {
      const probe = '__fd_probe__'
      window.localStorage.setItem(probe, '1')
      window.localStorage.removeItem(probe)
    } catch {
      setStorageAvailable(false)
    }
    setHydrated(true)
  }, [id])

  // Debounced so typing does not write on every keystroke. The timer is cleared on
  // unmount, and a pending write is flushed first so navigating away keeps the edit.
  const pending = useRef<Answers | null>(null)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const flush = useCallback(() => {
    if (pending.current) {
      saveAnswers(id, pending.current)
      pending.current = null
      notifyProgress()
    }
  }, [id])

  useEffect(() => () => flush(), [flush])

  const handleAnswer = useCallback(
    (fieldId: string, value: string) => {
      setAnswers((prev) => {
        const next = { ...prev, [fieldId]: value }
        pending.current = next
        if (timer.current) clearTimeout(timer.current)
        timer.current = setTimeout(() => {
          flush()
          setSavedAt(Date.now())
        }, SAVE_DEBOUNCE_MS)
        return next
      })
    },
    [flush],
  )

  const handleScore = useCallback(
    (rowId: string, value: number) => {
      setScores((prev) => {
        const next = prev[rowId] === value ? omit(prev, rowId) : { ...prev, [rowId]: value }
        saveScores(id, next)
        notifyProgress()
        setSavedAt(Date.now())
        return next
      })
    },
    [id],
  )

  const handleAddRow = useCallback(
    (blockId: string) => {
      setExtraRows((prev) => {
        const next = { ...prev, [blockId]: (prev[blockId] ?? 0) + 1 }
        saveExtraRows(id, next)
        return next
      })
    },
    [id],
  )

  const handleStatus = useCallback(
    (next: Status) => {
      setStatus(next)
      saveStatus(id, next)
      notifyProgress()
    },
    [id],
  )

  const handleReset = useCallback(() => {
    const message =
      'Clear your saved answers, scores and status for this scenario?\n\n' +
      'This cannot be undone. Export first if you want to keep them.'
    if (!window.confirm(message)) return
    clearScenario(id)
    pending.current = null
    if (timer.current) clearTimeout(timer.current)
    setAnswers({})
    setScores({})
    setExtraRows({})
    setStatus('not-started')
    setSavedAt(null)
    notifyProgress()
  }, [id])

  const handleExport = useCallback(() => {
    flush()
    downloadMarkdown(scenario, answers, scores)
  }, [flush, scenario, answers, scores])

  // "Saved" is a transient acknowledgement, not persistent state.
  useEffect(() => {
    if (savedAt === null) return
    const t = setTimeout(() => setSavedAt(null), 2000)
    return () => clearTimeout(t)
  }, [savedAt])

  const totalFields = useMemo(() => countFields(scenario.sections), [scenario.sections])
  const answered = useMemo(
    () => Object.values(answers).filter((v) => v.trim() !== '').length,
    [answers],
  )

  return (
    <article className="pb-20">
      <ScenarioToolbar
        status={status}
        onStatus={handleStatus}
        answered={answered}
        total={totalFields}
        savedAt={savedAt}
        storageAvailable={storageAvailable && hydrated}
        revealAll={revealAll}
        onRevealAll={setRevealAll}
        onExport={handleExport}
        onReset={handleReset}
      />

      <div className="space-y-12">
        {scenario.sections.map((section) => (
          <section key={section.index} id={`section-${section.index}`} className="scroll-mt-32">
            <div className="mb-4 flex items-baseline gap-3">
              <span className="text-[0.8125rem] font-bold tabular-nums text-accent">
                {String(section.index).padStart(2, '0')}
              </span>
              <h2 className="text-xl font-semibold tracking-[-0.011em]">{section.title}</h2>
            </div>

            <Blocks
              blocks={section.blocks}
              answers={answers}
              scores={scores}
              extraRows={extraRows}
              onAnswer={handleAnswer}
              onScore={handleScore}
              onAddRow={handleAddRow}
            />

            <AnswerKeyReveal sections={section.answerKey} forceOpen={revealAll} />
          </section>
        ))}
      </div>

      {scenario.closing && <ClosingCard section={scenario.closing} />}

      <nav className="no-print mt-16 grid gap-3 border-t border-border pt-6 sm:grid-cols-2">
        {scenario.prev ? (
          <Link
            href={scenarioHref(scenario.prev)}
            className="group rounded-lg border border-border bg-surface p-4 transition-colors hover:border-border-strong"
          >
            <div className="mb-1 text-[0.75rem] text-subtle">← Previous</div>
            <div className="text-[0.9375rem] font-medium group-hover:text-accent">
              {scenario.prev.title}
            </div>
          </Link>
        ) : (
          <div />
        )}
        {scenario.next && (
          <Link
            href={scenarioHref(scenario.next)}
            className="group rounded-lg border border-border bg-surface p-4 text-right transition-colors hover:border-border-strong sm:col-start-2"
          >
            <div className="mb-1 text-[0.75rem] text-subtle">Next →</div>
            <div className="text-[0.9375rem] font-medium group-hover:text-accent">
              {scenario.next.title}
            </div>
          </Link>
        )}
      </nav>
    </article>
  )
}

/**
 * The answer key's closing section, given its own card. It is the one piece of the
 * key that is a script rather than a checklist — the thing you rehearse out loud.
 */
function ClosingCard({ section }: { section: Section }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="mt-14 overflow-hidden rounded-xl border border-accent/30 bg-accent-soft">
      <div className="px-5 py-4">
        <div className="mb-1 text-[0.6875rem] font-bold uppercase tracking-[0.1em] text-accent">
          The closer
        </div>
        <h3 className="text-lg font-semibold">{section.title}</h3>
        <p className="mt-1 text-[0.875rem] text-muted">
          Rehearse this out loud before you look at it. Summarising the whole design in
          two minutes is its own skill, and it is usually the last thing you are asked for.
        </p>
        {!open && (
          <button
            type="button"
            onClick={() => setOpen(true)}
            className="no-print mt-3 rounded-md bg-accent px-3 py-1.5 text-[0.8125rem] font-semibold text-white transition-colors hover:bg-accent-hover"
          >
            Show the model answer
          </button>
        )}
      </div>
      {open && (
        <div className="border-t border-accent/20 bg-surface px-5 py-4">
          <Blocks blocks={section.blocks} />
        </div>
      )}
    </div>
  )
}

function omit<T extends Record<string, unknown>>(obj: T, key: string): T {
  const next = { ...obj }
  delete next[key]
  return next
}

function countFields(sections: Section[]): number {
  let total = 0
  const walk = (blocks: Block[]) => {
    for (const b of blocks) {
      if (b.kind === 'list') {
        for (const item of b.items) if (item.kind !== 'text') total++
      }
      if (b.kind === 'table') {
        for (const row of b.rows) for (const cell of row) if (cell.editable) total++
      }
    }
  }
  for (const section of sections) walk(section.blocks)
  return total
}

/**
 * Rebuilds the worksheet as markdown with the reader's answers filled into the blanks,
 * so practice work leaves the browser in the same shape it arrived in.
 */
function downloadMarkdown(scenario: Scenario, answers: Answers, scores: Scores): void {
  const lines: string[] = [`# ${scenario.title} — my answers`, '']

  for (const section of scenario.sections) {
    lines.push(`## ${section.index}. ${section.title}`, '')
    for (const block of section.blocks) {
      if (block.kind === 'prose') lines.push(htmlToText(block.html), '')
      if (block.kind === 'subheading') lines.push(`### ${block.text}`, '')
      if (block.kind === 'list') {
        for (const item of block.items) {
          if (item.kind === 'text') lines.push(`- ${htmlToText(item.html)}`)
          if (item.kind === 'input') lines.push(`- ${answers[item.id] ?? ''}`)
          if (item.kind === 'field')
            lines.push(`- ${item.label}: ${answers[item.id] ?? ''}`)
        }
        lines.push('')
      }
      if (block.kind === 'table') {
        lines.push(`| ${block.headers.join(' | ')} |`)
        lines.push(`|${block.headers.map(() => '---').join('|')}|`)
        for (const row of block.rows) {
          const cells = row.map((cell) =>
            cell.editable ? (answers[cell.id] ?? '').replace(/\n/g, ' ') : htmlToText(cell.text),
          )
          lines.push(`| ${cells.join(' | ')} |`)
        }
        lines.push('')
      }
      if (block.kind === 'scorecard') {
        lines.push('| Area | My score |', '|---|---|')
        for (const row of block.rows) {
          lines.push(`| ${row.area} | ${scores[row.id] ?? '—'} |`)
        }
        lines.push('')
      }
    }
  }

  const blob = new Blob([lines.join('\n')], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${scenario.ref.slug}-my-answers.md`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

function htmlToText(html: string): string {
  return html
    .replace(/<br\s*\/?>/g, ' ')
    .replace(/<\/p>\s*<p>/g, '\n\n')
    .replace(/<[^>]*>/g, '')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .trim()
}
