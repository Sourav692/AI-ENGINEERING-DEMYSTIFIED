'use client'

import type { Block, Cell } from '@/lib/parse'
import { AutoTextarea } from './AutoTextarea'
import { Diagram } from './Diagram'

/**
 * Renders parsed markdown blocks. The same component draws worksheets and answer
 * keys; passing no `answers` handler makes everything read-only, which is what the
 * answer-key reveals use.
 */

export type BlocksProps = {
  blocks: Block[]
  answers?: Record<string, string>
  scores?: Record<string, number>
  extraRows?: Record<string, number>
  onAnswer?: (id: string, value: string) => void
  onScore?: (id: string, value: number) => void
  onAddRow?: (blockId: string) => void
}

export function Blocks(props: BlocksProps) {
  return (
    <div className="space-y-4">
      {props.blocks.map((block, i) => (
        <BlockView key={i} block={block} {...props} />
      ))}
    </div>
  )
}

function BlockView({ block, ...p }: { block: Block } & BlocksProps) {
  switch (block.kind) {
    case 'prose':
      return <div className="prose" dangerouslySetInnerHTML={{ __html: block.html }} />

    case 'subheading':
      return (
        <h4 className="pt-2 text-[0.8125rem] font-semibold uppercase tracking-[0.08em] text-muted">
          {block.text}
        </h4>
      )

    case 'list':
      return (
        <ul className="space-y-2">
          {block.items.map((item, i) => {
            if (item.kind === 'text') {
              return (
                <li key={i} className="flex gap-2.5 leading-relaxed">
                  <span aria-hidden className="mt-[0.55em] h-1 w-1 shrink-0 rounded-full bg-subtle" />
                  <span className="prose" dangerouslySetInnerHTML={{ __html: item.html }} />
                </li>
              )
            }
            if (item.kind === 'input') {
              return (
                <li key={i} className="flex gap-2.5">
                  <span aria-hidden className="mt-[0.55em] h-1 w-1 shrink-0 rounded-full bg-accent/50" />
                  <div className="flex-1">
                    <Editable
                      id={item.id}
                      label="Answer"
                      placeholder="Your answer…"
                      {...p}
                    />
                  </div>
                </li>
              )
            }
            return (
              <li key={i} className="grid gap-1.5 sm:grid-cols-[minmax(0,13rem)_1fr] sm:items-start sm:gap-3">
                <span className="pt-1.5 text-[0.9375rem] font-medium text-muted">
                  {item.label}
                </span>
                <Editable id={item.id} label={item.label} placeholder="…" {...p} />
              </li>
            )
          })}
        </ul>
      )

    case 'table':
      return <TableView block={block} {...p} />

    case 'scorecard':
      return <ScorecardView block={block} {...p} />

    case 'diagram':
      return <Diagram code={block.code} />

    case 'code':
      return (
        <pre className="code-block" data-lang={block.lang || undefined}>
          <code>{block.code}</code>
        </pre>
      )
  }
}

function Editable({
  id,
  label,
  placeholder,
  answers,
  onAnswer,
}: {
  id: string
  label: string
  placeholder?: string
} & BlocksProps) {
  if (!onAnswer) return <span className="text-subtle">—</span>
  return (
    <AutoTextarea
      value={answers?.[id] ?? ''}
      onChange={(value) => onAnswer(id, value)}
      ariaLabel={label}
      placeholder={placeholder}
    />
  )
}

function TableView({ block, ...p }: { block: Extract<Block, { kind: 'table' }> } & BlocksProps) {
  const blockId = block.rows[0]?.[0]?.id.replace(/:r\d+:c\d+$/, '') ?? ''
  const extra = p.extraRows?.[blockId] ?? 0

  const addedRows: Cell[][] = Array.from({ length: extra }, (_, r) =>
    block.headers.map((_, c) => ({
      text: '',
      editable: true,
      id: `${blockId}:r${block.rows.length + r}:c${c}`,
    })),
  )
  const rows = [...block.rows, ...addedRows]

  return (
    <div className="space-y-2">
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full border-collapse text-left text-[0.9375rem]">
          <thead>
            <tr className="bg-surface-2">
              {block.headers.map((header, i) => (
                <th
                  key={i}
                  scope="col"
                  className="border-b border-border px-3 py-2.5 text-[0.75rem] font-semibold uppercase tracking-[0.06em] text-muted"
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, r) => (
              <tr key={r} className="border-b border-border last:border-0">
                {row.map((cell, c) => (
                  <td key={c} className="align-top px-3 py-2">
                    {cell.editable ? (
                      <Editable
                        id={cell.id}
                        label={`${block.headers[c]} row ${r + 1}`}
                        {...p}
                      />
                    ) : (
                      <span
                        className="prose block [&>p]:my-0"
                        dangerouslySetInnerHTML={{ __html: cell.text || '—' }}
                      />
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {block.growable && p.onAddRow && (
        <button
          type="button"
          onClick={() => p.onAddRow?.(blockId)}
          className="no-print rounded-md px-2 py-1 text-[0.8125rem] font-medium text-accent transition-colors hover:bg-accent-soft"
        >
          + Add row
        </button>
      )}
    </div>
  )
}

function ScorecardView({
  block,
  scores,
  onScore,
}: { block: Extract<Block, { kind: 'scorecard' }> } & BlocksProps) {
  return (
    <div className="space-y-2.5">
      {block.rows.map((row) => {
        const selected = scores?.[row.id]
        return (
          <div key={row.id} className="rounded-lg border border-border bg-surface p-3">
            <div className="mb-2.5 text-[0.9375rem] font-semibold">{row.area}</div>
            <div className="grid gap-2 sm:grid-cols-3">
              {row.levels.map((level) => {
                const active = selected === level.value
                const interactive = Boolean(onScore)
                return (
                  <button
                    key={level.value}
                    type="button"
                    disabled={!interactive}
                    aria-pressed={active}
                    onClick={() => onScore?.(row.id, level.value)}
                    className={`rounded-md border p-2.5 text-left transition-colors ${
                      active
                        ? 'border-accent bg-accent-soft'
                        : 'border-border bg-surface-2 ' +
                          (interactive ? 'hover:border-border-strong' : '')
                    } ${interactive ? 'cursor-pointer' : 'cursor-default'}`}
                  >
                    <div
                      className={`mb-1 text-[0.6875rem] font-bold uppercase tracking-[0.08em] ${
                        active ? 'text-accent' : 'text-subtle'
                      }`}
                    >
                      Level {level.value}
                    </div>
                    <div className="text-[0.875rem] leading-snug text-muted">
                      {level.label}
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}
