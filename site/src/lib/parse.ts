import { marked } from 'marked'

/**
 * Turns a worksheet or answer-key markdown file into a structured document.
 *
 * The parser is deliberately generic: it never looks at a scenario's name or a
 * section's number to decide how to render it. Everything interactive is derived
 * from emptiness in the source markdown — an empty table cell, a bare `-` bullet,
 * a `Label:` line with nothing after the colon. That is what lets a future module's
 * worksheets become interactive without touching this file.
 */

export type Cell = { text: string; editable: boolean; id: string }

export type ListItem =
  | { kind: 'text'; html: string }
  | { kind: 'input'; id: string }
  | { kind: 'field'; label: string; id: string }

export type Block =
  | { kind: 'prose'; html: string }
  | { kind: 'subheading'; text: string }
  | { kind: 'list'; items: ListItem[] }
  | { kind: 'table'; headers: string[]; rows: Cell[][]; growable: boolean }
  | { kind: 'scorecard'; headers: string[]; rows: ScorecardRow[] }

export type ScorecardRow = {
  area: string
  levels: { value: number; label: string }[]
  id: string
}

export type Section = {
  /** 1-based position in the document; also the heading number when present. */
  index: number
  /** Heading text with any leading `N. ` stripped. */
  title: string
  /** Normalised for matching worksheet sections to answer-key sections. */
  key: string
  blocks: Block[]
}

export type ParsedDocument = {
  title: string
  intro: Block[]
  sections: Section[]
}

marked.setOptions({ gfm: true })

function inline(text: string): string {
  return marked.parseInline(text.trim(), { async: false }) as string
}

function block(text: string): string {
  return marked.parse(text.trim(), { async: false }) as string
}

/** `## 3. Users and workflows` -> `users-and-workflows` */
export function normaliseKey(heading: string): string {
  return heading
    .replace(/^\d+\.\s*/, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

function splitRow(line: string): string[] {
  const trimmed = line.trim().replace(/^\|/, '').replace(/\|$/, '')
  return trimmed.split('|').map((cell) => cell.trim())
}

function isSeparatorRow(line: string): boolean {
  return /^\|?[\s:|-]+\|[\s:|-]*$/.test(line.trim()) && line.includes('-')
}

/**
 * A scorecard is a table whose columns are a 1/3/5 rubric plus an empty Score column.
 * It gets its own block kind because a free-text input would lose the rubric's meaning
 * — the whole point is choosing between three described levels.
 */
function isScorecard(headers: string[]): boolean {
  const lower = headers.map((h) => h.toLowerCase())
  return (
    lower.includes('score') &&
    ['1', '3', '5'].every((level) => lower.includes(level))
  )
}

function parseTable(lines: string[], blockId: string): Block {
  const headers = splitRow(lines[0])
  const bodyLines = lines.slice(isSeparatorRow(lines[1] ?? '') ? 2 : 1)

  if (isScorecard(headers)) {
    const levelColumns = ['1', '3', '5'].map((level) =>
      headers.findIndex((h) => h.toLowerCase() === level),
    )
    const rows: ScorecardRow[] = bodyLines.map((line, rowIndex) => {
      const cells = splitRow(line)
      return {
        area: cells[0] ?? '',
        levels: [1, 3, 5].map((value, i) => ({
          value,
          label: cells[levelColumns[i]] ?? '',
        })),
        id: `${blockId}:r${rowIndex}`,
      }
    })
    return { kind: 'scorecard', headers, rows }
  }

  const rows: Cell[][] = bodyLines.map((line, rowIndex) => {
    const cells = splitRow(line)
    return headers.map((_, colIndex) => {
      const text = cells[colIndex] ?? ''
      return {
        text: text ? inline(text) : '',
        editable: text === '',
        id: `${blockId}:r${rowIndex}:c${colIndex}`,
      }
    })
  })

  // A table the reader is expected to fill in usually ships with a single blank row,
  // which is a template rather than a limit — let them add more.
  const growable = rows.some((row) => row.every((cell) => cell.editable))

  return { kind: 'table', headers, rows, growable }
}

function parseListItem(
  raw: string,
  blockId: string,
  itemIndex: number,
): ListItem {
  const text = raw.replace(/^[-*]\s?/, '').trim()
  const id = `${blockId}:i${itemIndex}`

  if (text === '') return { kind: 'input', id }

  // `Latency target:` / `Ingestion and ACL:` — a prompt with nothing answering it.
  const field = text.match(/^([^:]{1,60}):$/)
  if (field) return { kind: 'field', label: field[1].trim(), id }

  return { kind: 'text', html: inline(text) }
}

function parseBlocks(lines: string[], sectionId: string): Block[] {
  const blocks: Block[] = []
  let i = 0
  let blockIndex = 0

  const nextBlockId = () => `${sectionId}:b${blockIndex++}`

  while (i < lines.length) {
    const line = lines[i]

    if (line.trim() === '') {
      i++
      continue
    }

    if (line.startsWith('### ')) {
      blocks.push({ kind: 'subheading', text: line.replace(/^###\s+/, '').trim() })
      i++
      continue
    }

    if (line.trim().startsWith('|')) {
      const start = i
      while (i < lines.length && lines[i].trim().startsWith('|')) i++
      blocks.push(parseTable(lines.slice(start, i), nextBlockId()))
      continue
    }

    if (/^[-*]\s|^[-*]$/.test(line.trim())) {
      const start = i
      while (i < lines.length && /^[-*]\s|^[-*]$/.test(lines[i].trim())) i++
      const blockId = nextBlockId()
      blocks.push({
        kind: 'list',
        items: lines
          .slice(start, i)
          .map((raw, index) => parseListItem(raw.trim(), blockId, index)),
      })
      continue
    }

    // Numbered lists and paragraphs both fall through to marked, which handles
    // ordered lists, emphasis and inline code without any special casing here.
    const start = i
    while (
      i < lines.length &&
      lines[i].trim() !== '' &&
      !lines[i].startsWith('### ') &&
      !lines[i].trim().startsWith('|') &&
      !/^[-*]\s|^[-*]$/.test(lines[i].trim())
    ) {
      i++
    }
    const html = block(lines.slice(start, i).join('\n'))
    if (html) blocks.push({ kind: 'prose', html })
  }

  return blocks
}

export function parseDocument(markdown: string): ParsedDocument {
  const lines = markdown.split('\n')

  let title = ''
  const introLines: string[] = []
  const rawSections: { heading: string; lines: string[] }[] = []
  let current: { heading: string; lines: string[] } | null = null

  for (const line of lines) {
    if (line.startsWith('# ')) {
      title = line.replace(/^#\s+/, '').trim()
      continue
    }
    if (line.startsWith('## ')) {
      current = { heading: line.replace(/^##\s+/, '').trim(), lines: [] }
      rawSections.push(current)
      continue
    }
    if (current) current.lines.push(line)
    else introLines.push(line)
  }

  const sections: Section[] = rawSections.map((section, index) => {
    const numbered = section.heading.match(/^(\d+)\.\s*(.*)$/)
    const position = numbered ? Number(numbered[1]) : index + 1
    return {
      index: position,
      title: numbered ? numbered[2] : section.heading,
      key: normaliseKey(section.heading),
      blocks: parseBlocks(section.lines, `s${position}`),
    }
  })

  return {
    title,
    intro: parseBlocks(introLines, 'intro'),
    sections,
  }
}
