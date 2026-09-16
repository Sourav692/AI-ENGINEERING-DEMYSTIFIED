'use client'

import { useEffect, useRef, type ChangeEvent } from 'react'

/**
 * A textarea that grows with its content. Worksheet answers range from three words
 * to a paragraph, and a fixed-height box either wastes space or hides what you wrote.
 */
export function AutoTextarea({
  value,
  onChange,
  placeholder,
  ariaLabel,
  className = '',
}: {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  ariaLabel: string
  className?: string
}) {
  const ref = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${el.scrollHeight}px`
  }, [value])

  return (
    <textarea
      ref={ref}
      rows={1}
      value={value}
      aria-label={ariaLabel}
      placeholder={placeholder}
      onChange={(e: ChangeEvent<HTMLTextAreaElement>) => onChange(e.target.value)}
      className={`w-full resize-none overflow-hidden rounded-md border border-border bg-surface px-2.5 py-1.5 text-[0.9375rem] leading-relaxed text-text transition-colors placeholder:text-subtle/70 hover:border-border-strong focus:border-accent focus:outline-none focus:ring-2 focus:ring-[var(--accent-ring)] ${className}`}
    />
  )
}
