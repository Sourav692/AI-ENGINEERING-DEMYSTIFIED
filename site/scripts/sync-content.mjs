#!/usr/bin/env node
/**
 * Copies the FDE prep markdown out of the learning repo and into `site/content/`.
 * The source folders under `06_Interview_Prep/FDE/` stay the only place anyone
 * edits; `content/` is generated, but it is committed rather than ignored, because a
 * deploy rooted at `site/` cannot see the sources (see `sourcesPresent` below).
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
const SOURCE_ROOT = join(REPO_ROOT, '06_Interview_Prep/FDE')
const OUT_DIR = join(SITE_DIR, 'content')

const BEHAVIOURAL_ROOT = join(SOURCE_ROOT, 'Behavioral_and_Leadership')

/**
 * Every live module and the tracks inside it. Track ids must be unique across all
 * modules, not just within one: saved progress is keyed `trackId/slug`, so two
 * modules sharing a track id would share a reader's answers too.
 */
const MODULES = [
  {
    id: '01-customer-discovery-and-decomposition',
    tracks: [
      {
        id: 'core',
        title: 'Core Scenarios',
        blurb:
          'Ten generic GenAI FDE case studies. Start here — they cover the discovery ' +
          'and decomposition moves that every scenario builds on.',
        worksheetDir: join(
          SOURCE_ROOT,
          'Complete GEN AI FDE Interview System — Core + GenAI',
          '01_CUSTOMER_DISCOVERY_AND_DECOMPOSITION',
          '04_CASE_STUDY_WORKSHEET',
        ),
        answerKeyDir: join(
          SOURCE_ROOT,
          'Complete GEN AI FDE Interview System — Core + GenAI',
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
    ],
  },
  {
    id: '14-behavioural-and-leadership-round',
    tracks: [
      {
        id: 'hiring-manager',
        title: 'Hiring Manager Round',
        blurb:
          'Five customer-facing competencies, four questions each. The round that ' +
          'decides whether you can be put in front of a customer — not whether you ' +
          'can design a system.',
        worksheetDir: join(BEHAVIOURAL_ROOT, 'hiring_manager_round'),
        answerKeyDir: join(BEHAVIOURAL_ROOT, 'hiring_manager_round', 'answer_keys'),
      },
      {
        id: 'leadership-principles',
        title: 'Leadership Principles',
        blurb:
          'Thirteen principles plus the staff-level cross-cutting set, each with the ' +
          'spoken answers your own engagements already support — and an honest mark ' +
          'on the ones they do not.',
        worksheetDir: join(BEHAVIOURAL_ROOT, 'leadership_principles'),
        answerKeyDir: join(BEHAVIOURAL_ROOT, 'leadership_principles', 'answer_keys'),
      },
    ],
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
    .replace(
      /\s*[-–—]\s*(Case Study Worksheet|Practice Worksheet|Answer Key)\s*$/i,
      '',
    )
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

async function syncTrack(moduleId, track) {
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

    const outBase = join(OUT_DIR, 'modules', moduleId, track.id)
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

/**
 * The sources live outside `site/`, so a deploy whose root directory is `site/`
 * never sees them. `content/` is therefore committed, and when the sources are
 * absent we build from that committed copy instead of failing.
 *
 * This only applies when the sources are missing wholesale. If they are present
 * but produce nothing, that is a broken path and still fails the build.
 */
async function sourcesPresent() {
  try {
    await readdir(SOURCE_ROOT)
    return true
  } catch {
    return false
  }
}

async function contentPresent() {
  try {
    const manifest = JSON.parse(
      await readFile(join(OUT_DIR, 'manifest.json'), 'utf8'),
    )
    return manifest.modules?.[0]?.tracks?.length > 0
  } catch {
    return false
  }
}

async function main() {
  if (!(await sourcesPresent())) {
    if (await contentPresent()) {
      console.log(
        `content sync: sources not present at ${SOURCE_ROOT}\n` +
          '  building from the committed content/ snapshot instead.',
      )
      return
    }
    throw new Error(
      `Sources not found at:\n  ${SOURCE_ROOT}\n` +
        'and content/ holds no usable snapshot, so there is nothing to build from.',
    )
  }

  await rm(OUT_DIR, { recursive: true, force: true })
  await mkdir(OUT_DIR, { recursive: true })

  const modules = []
  const warnings = []

  for (const mod of MODULES) {
    const tracks = []
    for (const track of mod.tracks) {
      const result = await syncTrack(mod.id, track)
      tracks.push(result.manifest)
      warnings.push(...result.warnings)
    }
    modules.push({ id: mod.id, tracks })
  }

  const manifest = { generatedAt: new Date().toISOString(), modules }
  await writeFile(join(OUT_DIR, 'manifest.json'), JSON.stringify(manifest, null, 2))

  const allTracks = modules.flatMap((m) => m.tracks)
  const total = allTracks.reduce((sum, t) => sum + t.scenarios.length, 0)
  for (const warning of warnings) console.warn(`  warning: ${warning}`)
  console.log(
    `content sync: ${total} scenarios across ${allTracks.length} tracks ` +
      `in ${modules.length} modules ` +
      `(${allTracks.map((t) => `${t.id}=${t.scenarios.length}`).join(', ')})`,
  )
}

main().catch((error) => {
  console.error(`\ncontent sync failed:\n${error.message}\n`)
  process.exit(1)
})
