'use client'

/**
 * The current theme lives on `<html>`, applied before paint by the inline script in
 * `layout.tsx`. This component holds no state of its own: which icon shows is decided
 * by CSS from that class, so there is nothing to sync after mount and no frame where
 * the wrong icon is visible.
 */
export function ThemeToggle() {
  function toggle() {
    const root = document.documentElement
    const next = root.classList.contains('dark') ? 'light' : 'dark'
    root.classList.toggle('dark', next === 'dark')
    try {
      window.localStorage.setItem('fd:v1:theme', next)
    } catch {
      /* the choice just will not survive a reload */
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label="Switch between light and dark theme"
      className="rounded-md p-1.5 text-muted transition-colors hover:bg-surface-2 hover:text-text"
    >
      <svg viewBox="0 0 24 24" aria-hidden className="hidden h-4 w-4 dark:block" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
      </svg>
      <svg viewBox="0 0 24 24" aria-hidden className="block h-4 w-4 dark:hidden" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z" />
      </svg>
    </button>
  )
}
