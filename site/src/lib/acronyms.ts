/**
 * Spells out an acronym the first time it appears on a page:
 *
 *   RAG  ->  <abbr title="retrieval-augmented generation: Fetch the relevant…">RAG</abbr> (retrieval-augmented generation)
 *
 * Later uses on the same page get nothing, the way a careful writer would do it. The
 * caller owns the `seen` set, so "the same page" can mean one tab, one worksheet, or one
 * static review. Sources are never edited — this runs on rendered HTML, in the app for
 * markdown pages and in `scripts/last-day.mjs` for the static reviews.
 *
 * Deliberately left alone: headings, links, code, existing <abbr>, and any use that is
 * already spelled out nearby ("retrieval-augmented generation (RAG)"). In table cells
 * and on the one-page recall cards the expansion goes in the hover text only, so tight
 * layouts do not grow.
 *
 * No imports: the sync scripts load this file directly under Node. Callers pass the
 * glossary in.
 */

export type AcronymEntry = {
  term: string
  expansion?: string
  plural?: string
  plain: string
  expand?: boolean
}

type Compiled = { pattern: RegExp; byTerm: Map<string, AcronymEntry> }

const cache = new WeakMap<AcronymEntry[], Compiled>()

function compile(entries: AcronymEntry[]): Compiled {
  const hit = cache.get(entries)
  if (hit) return hit
  const usable = entries.filter((e) => e.expansion && e.expand !== false && /^[A-Z][A-Z0-9/ ]*[A-Z0-9]$/.test(e.term))
  const byTerm = new Map(usable.map((e) => [e.term, e]))
  const alternation = [...byTerm.keys()]
    .sort((a, b) => b.length - a.length)
    .map((t) => t.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&'))
    .join('|')
  // Not inside a compound like NL-to-SQL or CI/CD, and not part of a longer word.
  const pattern = new RegExp(`(?<![\\w/\\-.])(${alternation})(s?)(?![\\w/\\-])`, 'g')
  const compiled = { pattern, byTerm }
  cache.set(entries, compiled)
  return compiled
}

const SKIP = new Set(['a', 'abbr', 'code', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'script', 'style', 'nav', 'title', 'button'])
const CELL = new Set(['td', 'th'])

const attr = (text: string) =>
  text.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

function pluralise(e: AcronymEntry): string {
  return e.plural ?? `${e.expansion}s`
}

export function expandAcronyms(
  html: string,
  seen: Set<string>,
  entries: AcronymEntry[],
  { inline = true }: { inline?: boolean } = {},
): string {
  const { pattern, byTerm } = compile(entries)
  let skip = 0
  let cell = 0
  return html.replace(/(<[^>]+>)|([^<]+)/g, (whole, tag: string | undefined, text: string | undefined) => {
    if (tag) {
      const name = tag.match(/^<\/?\s*([a-zA-Z0-9]+)/)?.[1]?.toLowerCase()
      if (!name || tag.endsWith('/>')) return tag
      const closing = tag.startsWith('</')
      if (SKIP.has(name)) skip = Math.max(0, skip + (closing ? -1 : 1))
      if (CELL.has(name)) cell = Math.max(0, cell + (closing ? -1 : 1))
      return tag
    }
    if (!text || skip > 0) return whole
    return text.replace(pattern, (match: string, term: string, s: string, offset: number) => {
      if (seen.has(term)) return match
      const entry = byTerm.get(term)
      if (!entry?.expansion) return match
      seen.add(term)
      const expansion = s ? pluralise(entry) : entry.expansion
      const before = text.slice(Math.max(0, offset - 120), offset).toLowerCase()
      const after = text.slice(offset + match.length, offset + match.length + 7)
      const alreadySpelled =
        before.includes(entry.expansion.toLowerCase().slice(0, 18)) || /^\s*\(/.test(after)
      // "FDE's" would become "FDE (Forward Deployed Engineer)'s" — hover text only there.
      const possessive = /^(['’]|&#39;|&rsquo;)/.test(after)
      const abbr = `<abbr class="gloss" title="${attr(`${entry.expansion}: ${entry.plain}`)}">${term}${s}</abbr>`
      if (alreadySpelled || possessive || !inline || cell > 0) return abbr
      return `${abbr} <span class="gloss-exp">(${expansion})</span>`
    })
  })
}
