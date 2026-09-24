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
 * The standalone cases under `Case_Study_Groups/Standalone/` have no fixed shape — one to
 * five documents each — so they are declared in `STANDALONE` with a label per file, and
 * each file becomes a tab. The manifest carries each page's tab list, so the app never
 * assumes four tabs.
 *
 * Cases are shown under themes, and a theme is a track: that keeps the module page,
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
 * Standalone cases are always published.
 */
const PUBLISHED = null

/** A group's tabs. Order is display order; the first tab opens by default. */
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
  {
    id: 'standalone-designs',
    title: 'Standalone Designs',
    blurb:
      'Full system designs with no sibling in the groups above \u2014 each is its own ' +
      'problem, from an air-gapped deployment to a gateway in front of every model call.',
    groups: [],
  },
  {
    id: 'judgement-and-decomposition',
    title: 'Judgement & Decomposition',
    blurb:
      'Questions that test how you think rather than what you draw: which use cases to ' +
      'fund, how to scale a prototype, what to do with poor data, and how to break an ' +
      'open-ended problem down in sixty minutes.',
    groups: [],
  },
]

/**
 * Standalone cases, keyed by folder under `Case_Study_Groups/Standalone/`. `number`
 * orders them and is the case number from CASE_STUDY_INDEX.xlsx; `tag` is the badge.
 * Every `.md` in the folder must be listed, so a new file cannot silently go unpublished.
 * `practice` names the same case's interactive worksheet in Module 01 (`track/slug`),
 * which the page links to — the Worksheet tab here is read-only.
 */
const WORKSHEET_SET = [
  ['1_Worksheet.md', 'Worksheet'],
  ['2_Answer_Key.md', 'Answer Key'],
  ['3_Tutorial_V2.md', 'Tutorial V2'],
  ['4_Tutorial_V1.md', 'Tutorial V1'],
]
const guide = (file) => [[file, 'Guide']]

const STANDALONE = [
  { folder: '04_Recruiting_Platform', theme: 'standalone-designs', number: 4, title: 'AI-Powered Recruiting Platform',
    files: [['1_Handbook_Casebook_Recruiting_Platform.md', 'Casebook'], ['2_FDE_Recruiting_Platform_Design_long.md', 'Full Design']] },
  { folder: '14_Travel_Agent_Worked_Example', theme: 'standalone-designs', number: 14, title: 'Travel Agent: the 12-Part Framework Worked Through',
    files: [['1_Handbook_Worked_Example_Travel_Agent.md', 'Worked Example'], ['2_FDE_System_Design_Overview_source.md', 'Framework Overview']] },
  { folder: '19_Air_Gapped_AI_System', theme: 'standalone-designs', number: 19, title: 'AI System for an Air-Gapped Environment', files: WORKSHEET_SET,
    practice: 'system-design/ai-system-for-an-air-gapped-environment' },
  { folder: '23_Reliable_Workflow_Orchestration', theme: 'standalone-designs', number: 23, title: 'Reliable Workflow Orchestration System', files: WORKSHEET_SET,
    practice: 'system-design/reliable-workflow-orchestration-system' },
  { folder: '25_Configurable_Platform_Customer_Workflows', theme: 'standalone-designs', number: 25, title: 'Configurable Platform for Customer-Specific Workflows', files: WORKSHEET_SET,
    practice: 'system-design/configurable-platform-customer-specific-workflows' },
  { folder: '26_Enterprise_Chatbot_Platform', theme: 'standalone-designs', number: 26, title: 'Enterprise Chatbot Platform',
    files: [...WORKSHEET_SET, ['5_Tutorial_V1_uncondensed.md', 'Tutorial V1 (Uncondensed)']],
    practice: 'system-design/enterprise-chatbot-platform' },
  { folder: '80_Self_Adapting_Agent', theme: 'standalone-designs', number: 80, title: 'Agent That Adapts to New Tasks', files: guide('80_Self_Adapting_Agent.md') },
  { folder: '98_Personal_Assistant_With_Memory', theme: 'standalone-designs', number: 98, title: 'Personal Assistant That Remembers You', files: guide('98_Personal_Assistant_With_Memory.md') },
  { folder: '100_Production_LLM_Gateway', theme: 'standalone-designs', number: 100, title: 'Production LLM Gateway', files: guide('100_Production_LLM_Gateway.md') },
  { folder: '60_Prioritize_AI_Use_Cases', theme: 'judgement-and-decomposition', number: 60, title: 'Prioritise AI Use Cases for a Large Enterprise', files: guide('60_Prioritize_AI_Use_Cases.md') },
  { folder: '61_Scale_Prototype_To_Production', theme: 'judgement-and-decomposition', number: 61, title: 'Scale a Prototype from 100 to 100,000 Users', files: guide('61_Scale_Prototype_To_Production.md') },
  { folder: '62_Build_When_Customer_Data_Is_Poor', theme: 'judgement-and-decomposition', number: 62, title: 'Build When the Customer\u2019s Data Is Poor', files: guide('62_Build_When_Customer_Data_Is_Poor.md') },
  { folder: 'Decomposition_Classics_67_68_69', theme: 'judgement-and-decomposition', number: 67, tag: '#67\u201369', title: 'Decomposition Classics: 911, Bank Fraud, Medication Errors',
    files: guide('Decomposition_Classics_67_68_69.md') },
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

const tabId = (label) => label.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')

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

  const isDir = existsSync(abs) && statSync(abs).isDirectory()
  const page = ctx.pages.get(isDir ? abs : dirname(abs))
  if (page) {
    const tab = isDir ? null : page.tabsByFile.get(basename(abs))
    return `${page.url}${tab ? `#${tab}` : ''}`
  }

  const repoRel = relative(ctx.repoRoot, abs).split(/[\\/]/).map(encodeURIComponent).join('/')
  if (repoRel.startsWith('..')) return null
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

/** Every page to publish, whatever its source shape, as one list. */
async function collectCases(root) {
  const groups = await listGroups(root)
  const listed = THEMES.flatMap((t) => t.groups)
  const unlisted = [...groups.keys()].filter((g) => !listed.includes(g))
  if (unlisted.length) {
    throw new Error(`Case study groups with no theme: ${unlisted.join(', ')} — add them to THEMES`)
  }

  const cases = []
  for (const theme of THEMES) {
    for (const g of theme.groups) {
      if (!groups.has(g) || !isPublished(g)) continue
      const folder = groups.get(g)
      const dir = join(root, folder)
      const tabs = DOC_TABS.map((t) => ({ id: t.id, label: t.label, file: `${folder}${t.suffix}.md` }))
      const main = await readFile(join(dir, tabs[0].file), 'utf8')
      cases.push({ theme: theme.id, dir, slug: slugOf(folder), tag: g, order: Number(g.slice(1)), title: nameFrom(main, folder), tabs })
    }
  }

  const standaloneRoot = join(root, 'Standalone')
  const onDisk = (await readdir(standaloneRoot, { withFileTypes: true })).filter((e) => e.isDirectory()).map((e) => e.name)
  const declared = STANDALONE.map((c) => c.folder)
  const undeclared = onDisk.filter((f) => !declared.includes(f))
  if (undeclared.length) throw new Error(`Standalone folders not declared in STANDALONE: ${undeclared.join(', ')}`)

  for (const c of STANDALONE) {
    if (!THEMES.some((t) => t.id === c.theme)) throw new Error(`${c.folder}: unknown theme ${c.theme}`)
    const dir = join(standaloneRoot, c.folder)
    const files = (await readdir(dir)).filter((f) => f.endsWith('.md'))
    const missing = c.files.map(([f]) => f).filter((f) => !files.includes(f))
    const extra = files.filter((f) => !c.files.some(([d]) => d === f))
    if (missing.length || extra.length) {
      throw new Error(`${c.folder}: declared files do not match disk (missing: ${missing.join(', ') || '—'}; undeclared: ${extra.join(', ') || '—'})`)
    }
    cases.push({
      theme: c.theme,
      dir,
      slug: c.folder.replace(/^\d+_/, '').replace(/_/g, '-').toLowerCase(),
      tag: c.tag ?? `#${c.number}`,
      order: c.number,
      title: c.title,
      tabs: c.files.map(([file, label]) => ({ id: tabId(label), label, file })),
      practice: c.practice,
    })
  }
  return cases
}

export async function syncCaseStudies({ repoRoot, outDir }) {
  const root = join(repoRoot, '06_Interview_Prep', 'Case_Study_Groups')
  const cases = await collectCases(root)

  // Page URL and file -> tab for every published folder, so cross-links point at the
  // site instead of the repo.
  const pages = new Map()
  for (const c of cases) {
    pages.set(c.dir, {
      url: `/modules/${CASE_STUDY_MODULE_ID}/${c.theme}/${c.slug}`,
      tabsByFile: new Map(c.tabs.map((t) => [t.file, t.id])),
    })
  }
  const ctx = { root, repoRoot, pages }

  const tracks = []
  for (const theme of THEMES) {
    const scenarios = []
    const inTheme = cases.filter((c) => c.theme === theme.id).sort((a, b) => a.order - b.order)
    for (const c of inTheme) {
      const outBase = join(outDir, 'modules', CASE_STUDY_MODULE_ID, theme.id, c.slug)
      await mkdir(outBase, { recursive: true })
      for (const tab of c.tabs) {
        const file = join(c.dir, tab.file)
        if (!existsSync(file)) throw new Error(`Missing ${tab.label} document: ${file}`)
        await writeFile(join(outBase, `${tab.id}.md`), rewriteLinks(await readFile(file, 'utf8'), file, ctx))
      }
      scenarios.push({
        slug: c.slug,
        order: c.order,
        title: c.title,
        tag: c.tag,
        tabs: c.tabs.map(({ id, label }) => ({ id, label })),
        ...(c.practice && { practice: c.practice }),
      })
    }
    if (scenarios.length) {
      tracks.push({ id: theme.id, title: theme.title, blurb: theme.blurb, scenarios })
    }
  }

  if (tracks.length === 0) throw new Error('FDE Case Studies produced no published pages')
  return { id: CASE_STUDY_MODULE_ID, kind: 'reading', tracks }
}
