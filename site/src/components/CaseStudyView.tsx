'use client'

import Link from 'next/link'
import { useCallback, useEffect, useRef, useState } from 'react'
import type { CaseStudy } from '@/lib/scenario'
import { scenarioHref } from '@/lib/scenario'
import type { ReadingDocument } from '@/lib/reading'
import { loadRead, notifyProgress, saveRead } from '@/lib/storage'
import { Diagram } from './Diagram'

/**
 * A reading page: one case study, four documents, one tab each.
 *
 * All four tabs are in the DOM and inactive ones are `hidden`. That costs a little
 * HTML and buys two things: search results can link straight to a section in any
 * tab, and the URL hash alone decides what is shown — `#deep-dive` opens a tab,
 * `#deep-dive-acl-normalization` opens the tab that holds that section and scrolls
 * to it. Nothing depends on query strings, so every page stays statically built.
 *
 * Diagrams are the exception: mermaid measures text as it lays a graph out, and in a
 * hidden panel everything measures zero. A panel's diagrams mount the first time the
 * panel is shown.
 */

function tabForHash(
  hash: string,
  tabs: string[],
): { tab: string; anchor: string | null } | null {
  const id = decodeURIComponent(hash.replace(/^#/, ''))
  if (!id) return null
  if (tabs.includes(id)) return { tab: id, anchor: null }
  // Longest id first, so `tutorial-v1-…` is not claimed by a shorter tab id.
  const owner = [...tabs].sort((a, b) => b.length - a.length).find((t) => id.startsWith(`${t}-`))
  return owner ? { tab: owner, anchor: id } : null
}

export function CaseStudyView({ study }: { study: CaseStudy }) {
  const progressId = `${study.ref.trackId}/${study.ref.slug}`
  const tabIds = study.docs.map((d) => d.tab)
  const tabKey = tabIds.join('|')
  const [active, setActive] = useState<string>(tabIds[0])
  const [visited, setVisited] = useState<Set<string>>(() => new Set([tabIds[0]]))
  const [read, setRead] = useState<string[]>([])
  const [hydrated, setHydrated] = useState(false)
  const tabsRef = useRef<HTMLDivElement>(null)

  const show = useCallback((tab: string) => {
    setActive(tab)
    setVisited((prev) => (prev.has(tab) ? prev : new Set(prev).add(tab)))
  }, [])

  // The hash and saved progress exist only in the browser, so both are read after
  // mount; the prerendered HTML always shows the first tab with nothing marked.
  /* eslint-disable react-hooks/set-state-in-effect -- hydration-safe by design */
  useEffect(() => {
    setRead(loadRead(progressId))
    setHydrated(true)

    const apply = () => {
      const target = tabForHash(window.location.hash, tabKey.split('|'))
      if (!target) return
      show(target.tab)
      if (target.anchor) {
        // Scroll once the panel is unhidden, then again after the router settles: on
        // a navigation from another page (a search result), Next.js applies its own
        // scroll after this effect and would otherwise leave the section off-screen.
        const scroll = () => document.getElementById(target.anchor!)?.scrollIntoView()
        requestAnimationFrame(scroll)
        setTimeout(scroll, 250)
      }
    }
    apply()
    window.addEventListener('hashchange', apply)
    return () => window.removeEventListener('hashchange', apply)
  }, [progressId, show, tabKey])
  /* eslint-enable react-hooks/set-state-in-effect */

  const selectTab = (tab: string, scroll = false) => {
    show(tab)
    // replaceState, not a hash assignment: a tab click should not pile up history
    // entries, and should not make the browser jump to an element.
    window.history.replaceState(null, '', `#${tab}`)
    if (scroll) {
      const top = (tabsRef.current?.getBoundingClientRect().top ?? 0) + window.scrollY - 72
      window.scrollTo({ top: Math.max(top, 0) })
    }
  }

  const toggleRead = (tab: string) => {
    setRead((prev) => {
      const next = prev.includes(tab) ? prev.filter((t) => t !== tab) : [...prev, tab]
      saveRead(progressId, next, study.docs.length)
      notifyProgress()
      return next
    })
  }

  return (
    <article>
      {/* One document needs no tab bar; the mark-as-read control below still works. */}
      {study.docs.length > 1 && (
      <div
        ref={tabsRef}
        className="no-print sticky top-[3.75rem] z-20 -mx-4 mb-8 border-y border-border bg-bg/85 px-4 backdrop-blur-md sm:mx-0 sm:rounded-lg sm:border sm:px-2"
      >
        <div role="tablist" aria-label="Case study documents" className="flex gap-1 overflow-x-auto py-1.5 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {study.docs.map(({ tab: id, label }) => {
            const selected = active === id
            const done = hydrated && read.includes(id)
            return (
              <button
                key={id}
                type="button"
                role="tab"
                id={`tab-${id}`}
                aria-selected={selected}
                aria-controls={`panel-${id}`}
                onClick={() => selectTab(id)}
                className={`flex shrink-0 items-center gap-1.5 rounded-md px-3 py-1.5 text-[0.875rem] font-medium transition-colors ${
                  selected
                    ? 'bg-accent-soft text-accent'
                    : 'text-muted hover:bg-surface-2 hover:text-text'
                }`}
              >
                {done && <Check className="h-3.5 w-3.5 text-success" />}
                {label}
              </button>
            )
          })}
          {hydrated && (
            <span className="ml-auto hidden shrink-0 self-center pr-2 text-[0.75rem] tabular-nums text-subtle sm:inline">
              {read.length} of {study.docs.length} read
            </span>
          )}
        </div>
      </div>
      )}

      {study.docs.map(({ tab, label, doc }, i) => {
        const nextTab = study.docs[i + 1]
        const done = read.includes(tab)
        return (
          <div
            key={tab}
            id={`panel-${tab}`}
            role="tabpanel"
            aria-labelledby={`tab-${tab}`}
            hidden={active !== tab}
          >
            <Panel doc={doc} drawDiagrams={visited.has(tab)} />

            <div className="no-print mt-12 flex flex-wrap items-center gap-3 rounded-xl border border-border bg-surface p-4">
              <button
                type="button"
                onClick={() => toggleRead(tab)}
                aria-pressed={done}
                className={`flex items-center gap-2 rounded-md px-3.5 py-2 text-[0.875rem] font-semibold transition-colors ${
                  done
                    ? 'bg-success-soft text-success hover:opacity-90'
                    : 'bg-accent text-white hover:bg-accent-hover'
                }`}
              >
                {done && <Check className="h-4 w-4" />}
                {done ? `${label} marked as read` : `Mark ${label} as read`}
              </button>
              {nextTab && (
                <button
                  type="button"
                  onClick={() => selectTab(nextTab.tab, true)}
                  className="ml-auto rounded-md border border-border px-3.5 py-2 text-[0.875rem] font-semibold transition-colors hover:border-border-strong"
                >
                  Next: {nextTab.label} →
                </button>
              )}
            </div>
          </div>
        )
      })}

      <nav className="no-print mt-16 grid gap-3 border-t border-border pt-6 sm:grid-cols-2">
        {study.prev ? (
          <Link
            href={scenarioHref(study.prev)}
            className="group rounded-lg border border-border bg-surface p-4 transition-colors hover:border-border-strong"
          >
            <div className="mb-1 text-[0.75rem] text-subtle">← Previous · {study.prev.tag}</div>
            <div className="text-[0.9375rem] font-medium group-hover:text-accent">
              {study.prev.title}
            </div>
          </Link>
        ) : (
          <div />
        )}
        {study.next && (
          <Link
            href={scenarioHref(study.next)}
            className="group rounded-lg border border-border bg-surface p-4 text-right transition-colors hover:border-border-strong sm:col-start-2"
          >
            <div className="mb-1 text-[0.75rem] text-subtle">Next · {study.next.tag} →</div>
            <div className="text-[0.9375rem] font-medium group-hover:text-accent">
              {study.next.title}
            </div>
          </Link>
        )}
      </nav>
    </article>
  )
}

function Panel({ doc, drawDiagrams }: { doc: ReadingDocument; drawDiagrams: boolean }) {
  const toc = doc.sections.filter((s) => s.title)
  return (
    <div className="lg:grid lg:grid-cols-[13rem_minmax(0,1fr)] lg:gap-10">
      <aside className="no-print hidden lg:block">
        {toc.length > 1 && (
          <nav aria-label="On this page" className="sticky top-[8.5rem] max-h-[calc(100vh-10rem)] overflow-y-auto">
            <div className="mb-2 text-[0.6875rem] font-semibold uppercase tracking-[0.1em] text-subtle">
              On this page
            </div>
            <ul className="space-y-1.5 border-l border-border">
              {toc.map((s) => (
                <li key={s.id}>
                  <a
                    href={`#${s.id}`}
                    className="-ml-px block border-l border-transparent pl-3 text-[0.8125rem] leading-snug text-muted transition-colors hover:border-accent hover:text-text"
                    dangerouslySetInnerHTML={{ __html: s.title! }}
                  />
                </li>
              ))}
            </ul>
          </nav>
        )}
      </aside>

      <div className="min-w-0">
        {doc.title && (
          <div className="mb-6 border-b border-border pb-4 text-[0.8125rem] font-semibold uppercase tracking-[0.08em] text-subtle">
            {doc.title}
          </div>
        )}
        <div className="space-y-10">
          {doc.sections.map((section) => (
            <section key={section.id} id={section.id} className="scroll-mt-32">
              {section.title && (
                <h2
                  className="mb-4 text-[1.375rem] font-semibold leading-snug tracking-[-0.014em]"
                  dangerouslySetInnerHTML={{ __html: section.title }}
                />
              )}
              <div className="space-y-4">
                {section.chunks.map((chunk, i) =>
                  chunk.kind === 'diagram' ? (
                    drawDiagrams ? (
                      <Diagram key={i} code={chunk.code} />
                    ) : (
                      <div key={i} className="h-40 rounded-lg border border-dashed border-border" />
                    )
                  ) : (
                    <div
                      key={i}
                      className="prose reading"
                      dangerouslySetInnerHTML={{ __html: chunk.html }}
                    />
                  ),
                )}
              </div>
            </section>
          ))}
        </div>
      </div>
    </div>
  )
}

function Check({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 16 16" aria-hidden className={className}>
      <path
        d="M3.5 8.5l3 3 6-7"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
