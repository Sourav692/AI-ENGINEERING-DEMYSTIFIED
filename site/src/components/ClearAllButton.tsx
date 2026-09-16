'use client'

import { useState } from 'react'
import { clearEverything, notifyProgress } from '@/lib/storage'

export function ClearAllButton() {
  const [cleared, setCleared] = useState(false)

  function handleClick() {
    const message =
      'Clear every saved answer, score and status across all scenarios?\n\n' +
      'This cannot be undone.'
    if (!window.confirm(message)) return
    clearEverything()
    notifyProgress()
    setCleared(true)
  }

  return (
    <div className="flex items-center gap-3">
      <button
        type="button"
        onClick={handleClick}
        className="rounded-md border border-border bg-surface px-3.5 py-2 text-[0.875rem] font-semibold transition-colors hover:border-warning hover:text-warning"
      >
        Clear all my saved answers
      </button>
      {cleared && (
        <span className="text-[0.875rem] text-success" role="status">
          Cleared.
        </span>
      )}
    </div>
  )
}
