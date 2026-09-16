'use client'

import { useRouter } from 'next/navigation'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { SearchEntry } from '@/lib/scenario'

/**
 * Full-text search over every worksheet and answer-key section.
 *
 * The index is built at build time and shipped as props, so searching costs one
 * pass over an in-memory array — no backend, no network, works offline.
 */
export function SearchDialog({ entries }: { entries: SearchEntry[] }) {
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [active, setActive] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLUListElement>(null)

  // Opening always starts from a clean slate. Done here rather than in an effect
  // watching `open` so the reset happens with the state change that caused it.
  const openDialog = useCallback(() => {
    setQuery('')
    setActive(0)
    setOpen(true)
    // Focus after the dialog paints, otherwise the element is not yet focusable.
    requestAnimationFrame(() => inputRef.current?.focus())
  }, [])

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setOpen((wasOpen) => {
          if (wasOpen) return false
          setQuery('')
          setActive(0)
          requestAnimationFrame(() => inputRef.current?.focus())
          return true
        })
      }
      if (e.key === 'Escape') setOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  const results = useMemo(() => search(entries, query), [entries, query])

  // A new query invalidates the highlighted row, so they change together.
  const handleQueryChange = useCallback((value: string) => {
    setQuery(value)
    setActive(0)
  }, [])

  const go = useCallback(
    (href: string) => {
      setOpen(false)
      router.push(href)
    },
    [router],
  )

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setActive((i) => Math.min(i + 1, results.length - 1))
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault()
      setActive((i) => Math.max(i - 1, 0))
    }
    if (e.key === 'Enter' && results[active]) {
      e.preventDefault()
      go(results[active].href)
    }
  }

  useEffect(() => {
    listRef.current
      ?.querySelector<HTMLElement>(`[data-index="${active}"]`)
      ?.scrollIntoView({ block: 'nearest' })
  }, [active])

  return (
    <>
      <button
        type="button"
        onClick={openDialog}
        aria-label="Search all case studies"
        aria-keyshortcuts="Meta+K Control+K"
        className="flex items-center gap-2 rounded-md border border-border bg-surface px-2.5 py-1.5 text-[0.8125rem] text-subtle transition-colors hover:border-border-strong hover:text-muted"
      >
        <svg viewBox="0 0 16 16" aria-hidden className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="7" cy="7" r="4.5" />
          <path d="M10.5 10.5L14 14" strokeLinecap="round" />
        </svg>
        <span className="hidden sm:inline">Search</span>
        <kbd className="hidden rounded border border-border bg-surface-2 px-1 font-sans text-[0.6875rem] sm:inline">
          ⌘K
        </kbd>
      </button>

      {open && (
        <div
          className="fixed inset-0 z-50 flex items-start justify-center px-4 pt-[10vh]"
          role="dialog"
          aria-modal="true"
          aria-label="Search"
        >
          <div
            className="absolute inset-0 bg-black/40 backdrop-blur-[2px]"
            onClick={() => setOpen(false)}
          />
          <div className="relative flex max-h-[70vh] w-full max-w-xl flex-col overflow-hidden rounded-xl border border-border bg-surface shadow-[var(--shadow-lg)]">
            <div className="flex items-center gap-2.5 border-b border-border px-4">
              <svg viewBox="0 0 16 16" aria-hidden className="h-4 w-4 shrink-0 text-subtle" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="7" cy="7" r="4.5" />
                <path d="M10.5 10.5L14 14" strokeLinecap="round" />
              </svg>
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => handleQueryChange(e.target.value)}
                onKeyDown={onKeyDown}
                placeholder="Search scenarios, sections and answer keys…"
                aria-label="Search"
                className="w-full bg-transparent py-3.5 text-[0.9375rem] text-text outline-none placeholder:text-subtle"
              />
            </div>

            <ul ref={listRef} className="overflow-y-auto py-1.5">
              {query.trim() === '' && (
                <li className="px-4 py-6 text-center text-[0.875rem] text-subtle">
                  Search across all 22 case studies.
                </li>
              )}
              {query.trim() !== '' && results.length === 0 && (
                <li className="px-4 py-6 text-center text-[0.875rem] text-subtle">
                  Nothing matched “{query}”.
                </li>
              )}
              {results.map((entry, i) => (
                <li key={`${entry.href}-${entry.kind}-${i}`} data-index={i}>
                  <button
                    type="button"
                    onMouseEnter={() => setActive(i)}
                    onClick={() => go(entry.href)}
                    className={`block w-full px-4 py-2.5 text-left transition-colors ${
                      i === active ? 'bg-accent-soft' : ''
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="truncate text-[0.875rem] font-medium">
                        {entry.section}
                      </span>
                      <span
                        className={`shrink-0 rounded px-1.5 py-0.5 text-[0.625rem] font-semibold uppercase tracking-wide ${
                          entry.kind === 'answer key'
                            ? 'bg-accent/15 text-accent'
                            : 'bg-surface-2 text-subtle'
                        }`}
                      >
                        {entry.kind}
                      </span>
                    </div>
                    <div className="truncate text-[0.75rem] text-subtle">{entry.title}</div>
                  </button>
                </li>
              ))}
            </ul>

            <div className="flex gap-3 border-t border-border px-4 py-2 text-[0.6875rem] text-subtle">
              <span>↑↓ navigate</span>
              <span>↵ open</span>
              <span>esc close</span>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

const MAX_RESULTS = 30

/**
 * Ranked substring matching: a hit in the section heading or scenario title beats a
 * hit in the body, and every term must appear somewhere. Good enough for a corpus
 * this size, and it avoids shipping a fuzzy-search dependency.
 */
function search(entries: SearchEntry[], query: string): SearchEntry[] {
  const terms = query.toLowerCase().split(/\s+/).filter(Boolean)
  if (terms.length === 0) return []

  const scored: { entry: SearchEntry; score: number }[] = []

  for (const entry of entries) {
    const section = entry.section.toLowerCase()
    const title = entry.title.toLowerCase()
    const text = entry.text.toLowerCase()

    let score = 0
    let matchedAll = true

    for (const term of terms) {
      if (section.includes(term)) score += 12
      else if (title.includes(term)) score += 8
      else if (text.includes(term)) score += 1
      else {
        matchedAll = false
        break
      }
    }

    if (matchedAll) scored.push({ entry, score })
  }

  return scored
    .sort((a, b) => b.score - a.score)
    .slice(0, MAX_RESULTS)
    .map((s) => s.entry)
}
