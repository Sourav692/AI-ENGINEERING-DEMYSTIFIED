import { marked, type Links, type Token, type Tokens, type TokensList } from 'marked'

/**
 * Parses a reading document (the FDE Case Studies guides) for display.
 *
 * Worksheets go through `parse.ts`, which turns every empty table cell into an input.
 * That is exactly wrong here: these guides are finished prose, and their tables have
 * deliberately blank cells. So this path renders markdown as markdown, and only
 * splits it where the page needs structure:
 *
 *  - at each `## ` heading, so a tab gets a table of contents and search can land on
 *    a section;
 *  - at each ```mermaid fence, which the page draws as a diagram instead of printing
 *    its source.
 *
 * Section ids are prefixed with the tab id, because all four tabs are in the DOM at
 * once and two of them can share a heading such as "Key Takeaways".
 */

export type ReadingChunk = { kind: 'html'; html: string } | { kind: 'diagram'; code: string }

export type ReadingSection = {
  /** Anchor id, unique across the whole page. */
  id: string
  /** Null for the lead-in above the first `## ` heading. */
  title: string | null
  chunks: ReadingChunk[]
}

export type ReadingDocument = {
  title: string
  sections: ReadingSection[]
}

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/<[^>]*>/g, '')
    .replace(/&[a-z]+;/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60)
}

/**
 * Wide tables scroll inside their own box rather than stretching the page, and
 * outbound links open in a new tab so the reader keeps their place in the guide.
 */
function finish(html: string): string {
  return html
    .replace(/<table>/g, '<div class="table-wrap"><table>')
    .replace(/<\/table>/g, '</table></div>')
    .replace(/<a href="(https?:[^"]+)"/g, '<a href="$1" target="_blank" rel="noopener noreferrer"')
}

function render(tokens: Token[], links: Links): string {
  const list: TokensList = Object.assign([...tokens], { links })
  return finish(marked.parser(list, { gfm: true, async: false }) as string)
}

export function parseReading(markdown: string, idPrefix: string): ReadingDocument {
  const tokens = marked.lexer(markdown, { gfm: true })
  const links = tokens.links ?? {}

  let title = ''
  const sections: ReadingSection[] = []
  const used = new Set<string>()
  let current: ReadingSection = { id: `${idPrefix}-intro`, title: null, chunks: [] }
  let pending: Token[] = []

  const flush = () => {
    if (pending.length === 0) return
    const html = render(pending, links).trim()
    if (html) current.chunks.push({ kind: 'html', html })
    pending = []
  }

  for (const token of tokens) {
    if (token.type === 'heading' && token.depth === 1 && !title) {
      title = (token as Tokens.Heading).text
      continue
    }
    if (token.type === 'heading' && token.depth === 2) {
      flush()
      if (current.chunks.length) sections.push(current)
      const text = (token as Tokens.Heading).text
      let id = `${idPrefix}-${slugify(text) || 'section'}`
      for (let n = 2; used.has(id); n++) id = `${idPrefix}-${slugify(text)}-${n}`
      used.add(id)
      current = {
        id,
        title: marked.parseInline(text, { async: false }) as string,
        chunks: [],
      }
      continue
    }
    if (token.type === 'code' && (token as Tokens.Code).lang?.trim() === 'mermaid') {
      flush()
      current.chunks.push({ kind: 'diagram', code: (token as Tokens.Code).text })
      continue
    }
    pending.push(token)
  }
  flush()
  if (current.chunks.length || current.title) sections.push(current)

  return { title, sections }
}

/** HTML to plain text: tags dropped, the entities marked emits decoded. */
export function toPlainText(html: string): string {
  return html
    .replace(/<[^>]*>/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, ' ')
    .trim()
}

/** Plain text of a section, for the search index. */
export function readingText(section: ReadingSection): string {
  return toPlainText(section.chunks.map((c) => (c.kind === 'html' ? c.html : '')).join(' '))
}
