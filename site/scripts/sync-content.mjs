#!/usr/bin/env node
/**
 * Copies the FDE prep markdown out of the learning repo and into `site/content/`,
 * which is generated output and gitignored. The source folders under
 * `15_FDE_Related_Preparation/` stay the only place anyone edits.
 *
 * Also writes `content/manifest.json`: the sync step is the single place that knows
 * how worksheets pair with answer keys and what order scenarios appear in, so the
 * app never has to re-derive it from filenames.
 *
 * Exits non-zero if a track produces no scenarios. Shipping an empty site is the
 * failure worth being loud about, since the sources live outside the app directory
 * and a path change here would otherwise fail silently at build time.
 */

import { mkdir, readdir, readFile, rm, writeFile } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const SITE_DIR = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const REPO_ROOT = resolve(SITE_DIR, '..')
const SOURCE_ROOT = join(REPO_ROOT, '15_FDE_Related_Preparation')
const OUT_DIR = join(SITE_DIR, 'content')

const MODULE_ID = '01-customer-discovery-and-decomposition'

const TRACKS = [
  {
    id: 'core',
    title: 'Core Scenarios',
    blurb:
      'Ten generic GenAI FDE case studies. Start here — they cover the discovery ' +
      'and decomposition moves that every scenario builds on.',
    worksheetDir: join(
      SOURCE_ROOT,
      '1. Complete GEN AI FDE Interview System — Core + GenAI',
      '01_CUSTOMER_DISCOVERY_AND_DECOMPOSITION',
      '04_CASE_STUDY_WORKSHEET',
    ),
    answerKeyDir: join(
      SOURCE_ROOT,
      '1. Complete GEN AI FDE Interview System — Core + GenAI',
      '01_CUSTOMER_DISCOVERY_AND_DECOMPOSITION',
      '04_CASE_STUDY_WORKSHEET',
      'answer_keys',
      'answer-keys-in-md',
    ),
  },
  {
    id: 'system-design',
    title: 'System Design Scenarios',
    blurb:
      'Twelve harder scenarios, each built around one dangerous constraint — ' +
      'permission fidelity, tenant isolation, air-gapped deployment, release gating.',
    worksheetDir: join(
      SOURCE_ROOT,
      'FDE_System_Design_Interview_20_Scenarios',
      'Version_3',
    ),
    answerKeyDir: join(
      SOURCE_ROOT,
      'FDE_System_Design_Interview_20_Scenarios',
      'Version_3',
      'answer_keys',
    ),
  },
]

/** `01_internal_knowledge_assistant.md` -> `internal-knowledge-assistant` */
function toSlug(filename) {
  return filename
    .replace(/\.md$/, '')
    .replace(/^\d+[_-]/, '')
    .replace(/_/g, '-')
    .toLowerCase()
}

/** Sort key from the numeric filename prefix, so disk order drives scenario order. */
function sourceNumber(filename) {
  const match = filename.match(/^(\d+)/)
  return match ? Number(match[1]) : Number.MAX_SAFE_INTEGER
}

/**
 * Title comes from the document's own `# ` heading rather than the filename, so it
 * keeps the author's capitalisation and wording. The trailing document-type suffix
 * is dropped because the site already shows which view you are looking at.
 */
function extractTitle(markdown, fallback) {
  const line = markdown.split('\n').find((l) => l.startsWith('# '))
  if (!line) return fallback
  return line
    .replace(/^#\s+/, '')
    .replace(/\s*[-–—]\s*(Case Study Worksheet|Answer Key)\s*$/i, '')
    .trim()
}

async function readMarkdownFiles(dir) {
  let entries
  try {
    entries = await readdir(dir)
  } catch (error) {
    throw new Error(`Cannot read source directory:\n  ${dir}\n  ${error.message}`)
  }
  return entries
    .filter((name) => name.endsWith('.md') && name.toLowerCase() !== 'readme.md')
    .sort((a, b) => sourceNumber(a) - sourceNumber(b) || a.localeCompare(b))
}

async function syncTrack(track) {
  const worksheetFiles = await readMarkdownFiles(track.worksheetDir)
  const answerKeyFiles = new Set(await readMarkdownFiles(track.answerKeyDir))

  const scenarios = []
  const warnings = []

  for (const [index, file] of worksheetFiles.entries()) {
    const slug = toSlug(file)
    const keyFile = file.replace(/\.md$/, '_answer_key.md')

    if (!answerKeyFiles.has(keyFile)) {
      warnings.push(`no answer key for ${track.id}/${file} (looked for ${keyFile})`)
      continue
    }

    const worksheet = await readFile(join(track.worksheetDir, file), 'utf8')
    const answerKey = await readFile(join(track.answerKeyDir, keyFile), 'utf8')

    const outBase = join(OUT_DIR, 'modules', MODULE_ID, track.id)
    await mkdir(join(outBase, 'worksheets'), { recursive: true })
    await mkdir(join(outBase, 'answer-keys'), { recursive: true })
    await writeFile(join(outBase, 'worksheets', `${slug}.md`), worksheet)
    await writeFile(join(outBase, 'answer-keys', `${slug}.md`), answerKey)

    scenarios.push({
      slug,
      // Sequential display position. The System Design track's source files carry the
      // book's chapter numbers, which have gaps (1,2,3,4,7,9,...); renumbering here
      // keeps the site's list free of holes that would read as missing content.
      order: index + 1,
      title: extractTitle(worksheet, slug),
    })
  }

  if (scenarios.length === 0) {
    throw new Error(
      `Track "${track.id}" produced no scenarios.\n` +
        `  worksheets: ${track.worksheetDir}\n` +
        `  answer keys: ${track.answerKeyDir}\n` +
        `  Found ${worksheetFiles.length} worksheet file(s) and ` +
        `${answerKeyFiles.size} answer key file(s).`,
    )
  }

  return {
    manifest: { id: track.id, title: track.title, blurb: track.blurb, scenarios },
    warnings,
  }
}

async function main() {
  await rm(OUT_DIR, { recursive: true, force: true })
  await mkdir(OUT_DIR, { recursive: true })

  const tracks = []
  const warnings = []

  for (const track of TRACKS) {
    const result = await syncTrack(track)
    tracks.push(result.manifest)
    warnings.push(...result.warnings)
  }

  const manifest = {
    generatedAt: new Date().toISOString(),
    modules: [{ id: MODULE_ID, tracks }],
  }
  await writeFile(join(OUT_DIR, 'manifest.json'), JSON.stringify(manifest, null, 2))

  const total = tracks.reduce((sum, t) => sum + t.scenarios.length, 0)
  for (const warning of warnings) console.warn(`  warning: ${warning}`)
  console.log(
    `content sync: ${total} scenarios across ${tracks.length} tracks ` +
      `(${tracks.map((t) => `${t.id}=${t.scenarios.length}`).join(', ')})`,
  )
}

main().catch((error) => {
  console.error(`\ncontent sync failed:\n${error.message}\n`)
  process.exit(1)
})
