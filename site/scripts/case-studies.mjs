/**
 * Syncs the FDE Case Studies module: the three-layer interview guides under
 * `06_Interview_Prep/Case_Study_Groups/`, one folder per group (G01–G20).
 *
 * Unlike the worksheet modules, these are reading pages. Each group folder holds four
 * documents, and each becomes a tab on the group's page:
 *
 *   Gxx_Name_Main.md        -> main        (the interview guide; opens by default)
 *   Gxx_Name_Deep_Dive.md   -> deep-dive
 *   Gxx_Name_Cheat_Sheet.md -> cheat-sheet
 *   Gxx_Name.md             -> full-pack   (the original consolidated, sourced pack)
 *
 * Groups are shown under themes, and a theme is a track: that keeps the module page,
 * progress and prev/next working through the same manifest shape as every other module.
 *
 * Links are rewritten here, once, so the site never renders a path into the repo:
 * a link to another group's document becomes that group's page on the site (only
 * if the group is published), and every other repo link points at the file on GitHub.
 */

import { existsSync, statSync } from 'node:fs'
import { mkdir, readdir, readFile, writeFile } from 'node:fs/promises'
import { basename, dirname, join, relative, resolve } from 'node:path'

export const CASE_STUDY_MODULE_ID = '15-fde-case-studies'

const GITHUB_BLOB = 'https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/blob/main/'
const GITHUB_TREE = 'https://github.com/Sourav692/AI-ENGINEERING-DEMYSTIFIED/tree/main/'

/**
 * Groups published on the site. Extend this list to publish more; a group missing
 * from it keeps its GitHub links but gets no page. `null` publishes every group.
 */
const PUBLISHED = null

/** Tab order is display order; the first tab opens by default. */
export const DOC_TABS = [
  { id: 'main', label: 'Main', suffix: '_Main' },
  { id: 'deep-dive', label: 'Deep Dive', suffix: '_Deep_Dive' },
  { id: 'cheat-sheet', label: 'Cheat Sheet', suffix: '_Cheat_Sheet' },
  { id: 'full-pack', label: 'Full Pack', suffix: '' },
]

/**
 * Themes, in display order. Track ids must stay unique across the whole site —
 * saved progress is keyed `trackId/slug`. A future "standalone" theme slots in as
 * one more entry here.
 */
const THEMES = [
  {
    id: 'knowledge-retrieval',
    title: 'Knowledge & Retrieval',
    blurb:
      'Systems that answer from an organisation’s own documents and data, where the ' +
      'hard part is who may see what, and proving where each answer came from.',
    groups: ['G01', 'G06', 'G08', 'G11'],
  },
  {
    id: 'agents-that-act',
    title: 'Agents That Act',
    blurb:
      'Agents that change things in real systems — tickets, deploys, CRMs, shipments. ' +
      'The design is mostly about what the agent may do alone and what needs a human.',
    groups: ['G02', 'G03', 'G04', 'G05', 'G09', 'G16', 'G17'],
  },
  {
    id: 'platforms-and-scale',
    title: 'Platforms & Scale',
    blurb:
      'Shared platforms and high-volume services: tenant isolation, batch throughput, ' +
      'consumer-scale chat and the serving layer underneath them.',
    groups: ['G07', 'G10', 'G15', 'G18', 'G20'],
  },
  {
    id: 'delivery-evaluation-operations',
    title: 'Delivery, Evaluation & Operations',
    blurb:
      'Getting from a scoping doc to a system in production, deciding when it is safe ' +
      'to release, and diagnosing it once it is live.',
    groups: ['G12', 'G13', 'G14'],
  },
  {
    id: 'model-development',
    title: 'Model Development',
    blurb: 'Building and adapting the model itself: data, fine-tuning, post-training and evaluation.',
    groups: ['G19'],
  },
]

const isPublished = (group) => PUBLISHED === null || PUBLISHED.includes(group)

/** `G01_Enterprise_Knowledge_Assistant` -> `enterprise-knowledge-assistant` */
const slugOf = (folder) => folder.replace(/^G\d+_/, '').replace(/_/g, '-').toLowerCase()

/** Name from the Main guide's heading: `# G01 — Enterprise Knowledge Assistant: Interview Guide`. */
function nameFrom(mainMarkdown, folder) {
  const line = mainMarkdown.split('\n').find((l) => l.startsWith('# ')) ?? ''
  const match = line.match(/^#\s+G\d+\s*[—–-]\s*(.+?)\s*:\s*(Main\s+)?Interview Guide\s*$/i)
  return match ? match[1] : folder.replace(/^G\d+_/, '').replace(/_/g, ' ')
}

async function listGroups(root) {
  const entries = await readdir(root, { withFileTypes: true })
  const groups = new Map()
  for (const e of entries) {
    const m = e.isDirectory() && e.name.match(/^(G\d{2})_/)
    if (m) groups.set(m[1], e.name)
  }
  return groups
}

/**
 * Resolves one markdown link target found in `sourceFile`.
 * Returns the rewritten href, or null to leave the link untouched.
 */
function rewriteHref(href, sourceFile, ctx) {
  if (/^(https?:|mailto:|#|\/)/i.test(href)) return null
  const [pathPart, anchor = ''] = href.split('#')
  if (!pathPart) return null

  let abs = resolve(dirname(sourceFile), decodeURI(pathPart))

  // Packs written before the three-layer folders existed link to `Gxx_Name.md` at the
  // top of Case_Study_Groups. That file now lives inside its own folder.
  if (!existsSync(abs)) {
    const moved = join(dirname(abs), basename(abs, '.md'), basename(abs))
    if (existsSync(moved)) abs = moved
  }

  const rel = relative(ctx.root, abs)
  const inGroups = !rel.startsWith('..')
  if (inGroups) {
    const folder = rel.split(/[\\/]/)[0]
    const group = folder.match(/^(G\d{2})_/)?.[1]
    const target = group && ctx.pages.get(group)
    if (target) {
      const file = basename(abs, '.md')
      const tab = DOC_TABS.find((t) => t.suffix && file.endsWith(t.suffix)) ??
        (file === folder ? DOC_TABS.find((t) => t.id === 'full-pack') : null)
      const hash = tab ? `#${tab.id}` : ''
      return `${target}${hash}`
    }
  }

  const repoRel = relative(ctx.repoRoot, abs).split(/[\\/]/).map(encodeURIComponent).join('/')
  if (repoRel.startsWith('..')) return null
  const isDir = existsSync(abs) && statSync(abs).isDirectory()
  return `${isDir ? GITHUB_TREE : GITHUB_BLOB}${repoRel}${anchor && !isDir ? `#${anchor}` : ''}`
}

function rewriteLinks(markdown, sourceFile, ctx) {
  // Inline links only: `[text](target)`. Image links share the syntax and are
  // rewritten the same way, which is what a repo image would need too.
  return markdown.replace(/\]\(([^)\s]+)(\s+"[^"]*")?\)/g, (whole, href, title = '') => {
    const next = rewriteHref(href, sourceFile, ctx)
    return next === null ? whole : `](${next}${title})`
  })
}

export async function syncCaseStudies({ repoRoot, outDir }) {
  const root = join(repoRoot, '06_Interview_Prep', 'Case_Study_Groups')
  const groups = await listGroups(root)

  const listed = THEMES.flatMap((t) => t.groups)
  const unlisted = [...groups.keys()].filter((g) => !listed.includes(g))
  if (unlisted.length) {
    throw new Error(`Case study groups with no theme: ${unlisted.join(', ')} — add them to THEMES`)
  }

  // Page URL for each published group, so cross-links can point at the site.
  const pages = new Map()
  for (const theme of THEMES) {
    for (const g of theme.groups) {
      if (groups.has(g) && isPublished(g)) {
        pages.set(g, `/modules/${CASE_STUDY_MODULE_ID}/${theme.id}/${slugOf(groups.get(g))}`)
      }
    }
  }
  const ctx = { root, repoRoot, pages }

  const tracks = []
  for (const theme of THEMES) {
    const scenarios = []
    for (const g of theme.groups) {
      if (!pages.has(g)) continue
      const folder = groups.get(g)
      const slug = slugOf(folder)
      const outBase = join(outDir, 'modules', CASE_STUDY_MODULE_ID, theme.id, slug)
      await mkdir(outBase, { recursive: true })

      let title = null
      for (const tab of DOC_TABS) {
        const file = join(root, folder, `${folder}${tab.suffix}.md`)
        if (!existsSync(file)) throw new Error(`Missing ${tab.label} document: ${file}`)
        const markdown = await readFile(file, 'utf8')
        if (tab.id === 'main') title = nameFrom(markdown, folder)
        await writeFile(join(outBase, `${tab.id}.md`), rewriteLinks(markdown, file, ctx))
      }

      scenarios.push({ slug, order: Number(g.slice(1)), title, tag: g })
    }
    if (scenarios.length) {
      tracks.push({ id: theme.id, title: theme.title, blurb: theme.blurb, scenarios })
    }
  }

  if (tracks.length === 0) throw new Error('FDE Case Studies produced no published groups')
  return { id: CASE_STUDY_MODULE_ID, kind: 'reading', tracks }
}
