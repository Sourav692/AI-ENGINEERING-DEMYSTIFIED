/**
 * Runs the parser over every synced worksheet and answer key and asserts the
 * structural invariants the UI depends on. Run with `npm run check:content`.
 *
 * This exists because the fillable regions are inferred from emptiness rather than
 * declared, so a formatting change in a source file can silently turn an input into
 * static text. That would look fine and be wrong.
 */

import { readFile, readdir } from 'node:fs/promises'
import { join, resolve } from 'node:path'
import { parseDocument } from '../src/lib/parse.ts'
import type { Block } from '../src/lib/parse.ts'

const CONTENT = resolve(import.meta.dirname, '..', 'content')
const MODULE_DIR = join(CONTENT, 'modules', '01-customer-discovery-and-decomposition')

type Counts = {
  inputs: number
  fields: number
  editableCells: number
  scorecards: number
  growableTables: number
}

function count(blocks: Block[], counts: Counts): void {
  for (const b of blocks) {
    if (b.kind === 'list') {
      for (const item of b.items) {
        if (item.kind === 'input') counts.inputs++
        if (item.kind === 'field') counts.fields++
      }
    }
    if (b.kind === 'table') {
      for (const row of b.rows) {
        for (const cell of row) if (cell.editable) counts.editableCells++
      }
      if (b.growable) counts.growableTables++
    }
    if (b.kind === 'scorecard') counts.scorecards++
  }
}

const failures: string[] = []
const rows: string[] = []

for (const track of ['core', 'system-design']) {
  const worksheetDir = join(MODULE_DIR, track, 'worksheets')
  const files = (await readdir(worksheetDir)).filter((f) => f.endsWith('.md')).sort()

  for (const file of files) {
    const slug = file.replace(/\.md$/, '')
    const doc = parseDocument(await readFile(join(worksheetDir, file), 'utf8'))
    const counts: Counts = {
      inputs: 0,
      fields: 0,
      editableCells: 0,
      scorecards: 0,
      growableTables: 0,
    }
    for (const section of doc.sections) count(section.blocks, counts)

    const total =
      counts.inputs + counts.fields + counts.editableCells + counts.scorecards

    // Every worksheet in this format has 11 sections, a scorecard, and a
    // substantial number of blanks. Deviation means the parser or the source moved.
    if (doc.sections.length !== 11) {
      failures.push(`${track}/${slug}: expected 11 sections, got ${doc.sections.length}`)
    }
    if (counts.scorecards !== 1) {
      failures.push(`${track}/${slug}: expected 1 scorecard, got ${counts.scorecards}`)
    }
    if (total < 20) {
      failures.push(`${track}/${slug}: only ${total} fillable regions — suspiciously few`)
    }
    if (!doc.title) failures.push(`${track}/${slug}: no title`)

    rows.push(
      `  ${(track + '/' + slug).padEnd(52)} ` +
        `${String(doc.sections.length).padStart(2)} sec  ` +
        `${String(counts.editableCells).padStart(3)} cells  ` +
        `${String(counts.inputs).padStart(2)} bullets  ` +
        `${String(counts.fields).padStart(2)} fields  ` +
        `${counts.growableTables} growable`,
    )
  }

  const keyDir = join(MODULE_DIR, track, 'answer-keys')
  for (const file of (await readdir(keyDir)).filter((f) => f.endsWith('.md'))) {
    const doc = parseDocument(await readFile(join(keyDir, file), 'utf8'))
    const counts: Counts = {
      inputs: 0,
      fields: 0,
      editableCells: 0,
      scorecards: 0,
      growableTables: 0,
    }
    for (const section of doc.sections) count(section.blocks, counts)
    // Answer keys are reference text. Anything editable in one means the parser is
    // treating authored content as a blank.
    if (counts.inputs + counts.editableCells > 0) {
      failures.push(
        `${track}/answer-keys/${file}: ${counts.inputs + counts.editableCells} ` +
          `unexpected editable regions in an answer key`,
      )
    }
    if (doc.sections.length < 10) {
      failures.push(`${track}/answer-keys/${file}: only ${doc.sections.length} sections`)
    }
  }
}

console.log(rows.join('\n'))

if (failures.length) {
  console.error(`\n${failures.length} problem(s):`)
  for (const f of failures) console.error(`  ✗ ${f}`)
  process.exit(1)
}
console.log(`\n✓ all worksheets and answer keys parse cleanly`)
