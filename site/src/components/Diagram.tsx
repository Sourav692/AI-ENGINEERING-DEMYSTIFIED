'use client'

import { useEffect, useId, useState } from 'react'

/**
 * Renders a ```mermaid fence as a diagram.
 *
 * Mermaid is imported inside the effect rather than at module scope so its ~500KB
 * only loads on pages that actually contain a diagram — and only once the answer
 * key holding it is revealed, since that is when this component first mounts.
 *
 * Two behaviours are load-bearing:
 *  - `suppressErrorRendering` stops mermaid injecting its own error node into the
 *    DOM on a bad graph, which would scribble outside React's tree. A failed parse
 *    falls back to showing the source, so the content is never simply missing.
 *  - The theme lives as a class on `<html>` and is toggled at runtime, so an
 *    observer re-renders the SVG on a flip. Mermaid bakes colours into the markup;
 *    without this, a diagram rendered in light mode stays dark-on-dark afterwards.
 */
/**
 * Resolves a CSS custom property to a hex colour.
 *
 * Going through a canvas looks roundabout, but the tokens in `globals.css` are
 * `oklch()` and `getComputedStyle` serialises those to `lab()` — a notation
 * mermaid's colour library cannot parse. Rasterising one pixel converts any colour
 * space to plain sRGB, so the diagram gets the site's exact palette either way.
 */
function token(name: string): string {
  const probe = document.createElement('div')
  probe.style.color = `var(${name})`
  document.body.appendChild(probe)
  const resolved = getComputedStyle(probe).color
  probe.remove()

  const ctx = document.createElement('canvas').getContext('2d')
  if (!ctx) return resolved
  ctx.fillStyle = resolved
  ctx.fillRect(0, 0, 1, 1)
  const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data
  return `#${[r, g, b].map((v) => v.toString(16).padStart(2, '0')).join('')}`
}

/**
 * Mermaid's stock palettes (lavender nodes on pale yellow) read as a foreign object
 * on this page, so the diagram is drawn from the site's own tokens instead.
 *
 * Deliberately no accent: `globals.css` reserves the indigo for interactive
 * affordances and progress, and a diagram is neither.
 */
function themeVariables(dark: boolean) {
  const text = token('--text')
  const line = token('--text-muted')
  const surface = token('--surface-2')
  const cluster = token('--bg')

  return {
    darkMode: dark,
    fontFamily: 'inherit',
    fontSize: '15px',
    background: token('--surface'),
    primaryColor: surface,
    primaryTextColor: text,
    primaryBorderColor: token('--border-strong'),
    secondaryColor: cluster,
    tertiaryColor: cluster,
    mainBkg: surface,
    nodeBorder: token('--border-strong'),
    nodeTextColor: text,
    textColor: text,
    titleColor: text,
    lineColor: line,
    edgeLabelBackground: token('--surface'),
    clusterBkg: cluster,
    clusterBorder: token('--border'),
  }
}

export function Diagram({ code }: { code: string }) {
  // `useId` contains characters that are illegal in a DOM id and in the selector
  // mermaid builds from it, so keep only what survives both.
  const seed = useId().replace(/[^a-zA-Z0-9]/g, '')
  const [svg, setSvg] = useState('')
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    let cancelled = false
    let rendered: 'dark' | 'light' | null = null

    async function render() {
      const theme = document.documentElement.classList.contains('dark') ? 'dark' : 'light'
      if (theme === rendered) return
      rendered = theme

      try {
        const mermaid = (await import('mermaid')).default
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: 'strict',
          suppressErrorRendering: true,
          fontFamily: 'inherit',
          theme: 'base',
          themeVariables: themeVariables(theme === 'dark'),
          // Mermaid's default is to fit the SVG to its container. A wide `flowchart
          // LR` then scales down far enough that its labels are unreadable — the one
          // here is 2200px of diagram in a 900px column. Draw it at its natural size
          // and let the container scroll instead.
          flowchart: { useMaxWidth: false },
        })
        const result = await mermaid.render(`mmd-${seed}-${theme}`, code)
        if (!cancelled) {
          setSvg(result.svg)
          setFailed(false)
        }
      } catch {
        if (!cancelled) {
          rendered = null
          setFailed(true)
        }
      }
    }

    render()

    const observer = new MutationObserver(() => void render())
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    })

    return () => {
      cancelled = true
      observer.disconnect()
    }
  }, [code, seed])

  if (failed) {
    return (
      <figure className="my-1 space-y-1.5">
        <pre className="code-block">
          <code>{code}</code>
        </pre>
        <figcaption className="text-[0.75rem] text-subtle">
          This diagram could not be drawn; its source is shown instead.
        </figcaption>
      </figure>
    )
  }

  if (!svg) {
    return (
      <div
        role="status"
        className="rounded-lg border border-border bg-surface-2 px-4 py-6 text-center text-[0.8125rem] text-subtle"
      >
        Drawing diagram…
      </div>
    )
  }

  return (
    <div
      className="mermaid-figure overflow-x-auto rounded-lg border border-border bg-surface p-3"
      // Mermaid output is generated from the markdown we ship, and is sanitised by
      // its own `securityLevel: 'strict'` before it gets here.
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  )
}
