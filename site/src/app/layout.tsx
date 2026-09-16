import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import { getSearchIndex } from '@/lib/content'
import { SITE } from '@/lib/registry'
import { SearchDialog } from '@/components/SearchDialog'
import { ThemeToggle } from '@/components/ThemeToggle'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

export const metadata: Metadata = {
  title: {
    default: `${SITE.name} — ${SITE.tagline}`,
    template: `%s · ${SITE.name}`,
  },
  description: SITE.description,
  openGraph: {
    title: `${SITE.name} — ${SITE.tagline}`,
    description: SITE.description,
    type: 'website',
  },
}

/**
 * Applies the stored theme before first paint. Inline and synchronous on purpose:
 * anything async here means a flash of the wrong theme on every load.
 */
const THEME_SCRIPT = `
try {
  var stored = localStorage.getItem('fd:v1:theme');
  var dark = stored ? stored === 'dark'
    : window.matchMedia('(prefers-color-scheme: dark)').matches;
  if (dark) document.documentElement.classList.add('dark');
} catch (e) {}
`

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const searchIndex = await getSearchIndex()

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
      </head>
      <body className={`${inter.variable} min-h-screen`}>
        <a
          href="#main"
          className="no-print sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-accent focus:px-3 focus:py-2 focus:text-sm focus:font-semibold focus:text-white"
        >
          Skip to content
        </a>

        <header className="no-print sticky top-0 z-30 border-b border-border bg-bg/85 backdrop-blur-md">
          <div className="mx-auto flex h-[3.75rem] max-w-5xl items-center gap-4 px-4 sm:px-6">
            <Link
              href="/"
              aria-label={`${SITE.name} home`}
              className="flex items-center gap-2.5 font-semibold tracking-[-0.011em]"
            >
              <Logo />
              <span>{SITE.name}</span>
            </Link>
            <nav className="ml-2 hidden gap-1 sm:flex">
              <HeaderLink href="/">Modules</HeaderLink>
              <HeaderLink href="/guide">How to use</HeaderLink>
            </nav>
            <div className="ml-auto flex items-center gap-1.5">
              <SearchDialog entries={searchIndex} />
              <ThemeToggle />
            </div>
          </div>
        </header>

        <main id="main" className="mx-auto max-w-5xl px-4 sm:px-6">
          {children}
        </main>

        <footer className="no-print mt-24 border-t border-border">
          <div className="mx-auto flex max-w-5xl flex-col gap-2 px-4 py-8 text-[0.8125rem] text-subtle sm:flex-row sm:items-center sm:px-6">
            <p>
              {SITE.name} — {SITE.tagline}
            </p>
            <p className="sm:ml-auto">
              Your answers are stored in this browser only.{' '}
              <Link href="/guide" className="text-muted underline underline-offset-2 hover:text-text">
                How this works
              </Link>
            </p>
          </div>
        </footer>
      </body>
    </html>
  )
}

function HeaderLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="rounded-md px-2.5 py-1.5 text-[0.875rem] text-muted transition-colors hover:bg-surface-2 hover:text-text"
    >
      {children}
    </Link>
  )
}

function Logo() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden className="h-[1.375rem] w-[1.375rem] text-accent">
      <rect x="2" y="2" width="20" height="20" rx="5" fill="currentColor" opacity="0.12" />
      <path
        d="M7 15.5L11 8l4 7.5M8.6 13h4.8"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.9"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="17" cy="8" r="1.6" fill="currentColor" />
    </svg>
  )
}
