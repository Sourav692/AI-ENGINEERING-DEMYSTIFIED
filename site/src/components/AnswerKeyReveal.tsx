'use client'

import { useState } from 'react'
import type { Section } from '@/lib/parse'
import { Blocks } from './Blocks'

/**
 * The per-section answer key, collapsed by default.
 *
 * Kept shut until asked because the whole value of the worksheet is attempting a
 * section before seeing what a strong answer covers.
 *
 * `defaultOpen` carries the page-level "Reveal all". The parent remounts these via
 * `key` when it flips, so the initial state comes from the prop rather than being
 * synced into state by an effect — and afterwards each section toggles on its own
 * again, so revealing everything then closing one still behaves the way you expect.
 */
export function AnswerKeyReveal({
  sections,
  defaultOpen,
}: {
  sections: Section[]
  defaultOpen: boolean
}) {
  const [open, setOpen] = useState(defaultOpen)

  if (sections.length === 0) return null

  return (
    <div className="mt-5 overflow-hidden rounded-lg border border-border bg-surface-2">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="no-print flex w-full items-center gap-2.5 px-4 py-3 text-left transition-colors hover:bg-surface"
      >
        <svg
          viewBox="0 0 16 16"
          aria-hidden
          className={`h-3.5 w-3.5 shrink-0 text-subtle transition-transform ${open ? 'rotate-90' : ''}`}
        >
          <path d="M6 3l5 5-5 5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <span className="text-[0.875rem] font-semibold text-text">
          {open ? 'Hide the answer key' : 'Compare with the answer key'}
        </span>
        {!open && (
          <span className="ml-auto text-[0.75rem] text-subtle">
            {sections.length === 1 ? '1 section' : `${sections.length} sections`}
          </span>
        )}
      </button>

      {open && (
        <div className="space-y-6 border-t border-border px-4 py-4">
          {sections.map((section) => (
            <div key={section.key}>
              <h4 className="mb-2.5 text-[0.75rem] font-bold uppercase tracking-[0.08em] text-accent">
                {section.title}
              </h4>
              <Blocks blocks={section.blocks} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
