/**
 * Editorial registry: every visible name, every content mode, and the metadata each
 * page states about itself — who it is for, what it assumes, what it teaches, how long
 * it takes, and where to go next.
 *
 * One file on purpose. The sync scripts import it (Node strips the types) to write
 * track titles into the manifest and to rename the static Last-Day pages, and the app
 * imports it to render headers, breadcrumbs, search and the learning map. A name
 * changed here changes everywhere; a name changed anywhere else is drift, and
 * `check:content` looks for it.
 *
 * Nothing here is a route, file name or storage key. Those stay fixed so bookmarks
 * and saved progress keep working — only what the reader sees is decided here.
 *
 * Keep this file free of runtime imports: `scripts/*.mjs` load it directly.
 */

// ---------------------------------------------------------------- content modes

export type ContentMode =
  | 'orientation'
  | 'practice'
  | 'behavioural'
  | 'case-study'
  | 'revision'

export const MODES: Record<ContentMode, { label: string; summary: string }> = {
  orientation: {
    label: 'Orientation',
    summary: 'Explains how the material fits together and where to start.',
  },
  practice: {
    label: 'Practice',
    summary:
      'A worksheet you fill in, section by section, then check against a model answer and score yourself.',
  },
  behavioural: {
    label: 'Behavioural practice',
    summary:
      'A personalisation template: the structure of a strong answer, with gaps only your own experience can fill.',
  },
  'case-study': {
    label: 'Case study',
    summary: 'A complete system design to read, at several depths, from interview answer to sourced detail.',
  },
  revision: {
    label: 'Revision',
    summary:
      'Condensed recall for concepts you have already studied — not a first introduction to them.',
  },
}

export type Difficulty = 'Foundation' | 'Intermediate' | 'Advanced'

/**
 * Where a page's claims come from. `lastReviewed` stays null until a page has had a
 * dated fact check against primary sources — no date is shown rather than an invented
 * one.
 */
export type SourceStatus = 'original' | 'derived' | 'sourced' | 'personal'

export const SOURCE_STATUS_LABELS: Record<SourceStatus, string> = {
  original: 'Original material for this site',
  derived: 'Condensed from the sources credited on the How It Works page',
  sourced: 'Cites its sources in the Sources and Full Design tab',
  personal: "Built from one candidate's engagements — adapt, do not recite",
}

export type Link = { label: string; href: string }

export type EditorialMeta = {
  mode: ContentMode
  audience: string
  difficulty: Difficulty
  prerequisites: string[]
  outcomes: string[]
  howToUse: string
  /** Minutes. Reading pages compute this from word count per tab instead. */
  minutes: number | null
  sourceStatus: SourceStatus
  lastReviewed: string | null
  /** Behavioural pages: the model answers contain `[FILL: …]` slots. */
  personalisation?: boolean
}

// ---------------------------------------------------------------- site and nav

export const SITE_NAME = 'Forward Deployed'
export const SITE_TAGLINE = 'FDE interview practice and system-design review'

export const NAV = [
  { label: 'Practice', href: '/#practice' },
  { label: 'Case Studies', href: '/modules/15-fde-case-studies' },
  { label: 'Last-Day Review', href: '/fde-last-day-prep' },
  { label: 'How It Works', href: '/guide' },
] as const

export const LAST_DAY = {
  title: 'Last-Day Review',
  eyebrow: 'Focused final review',
  href: '/fde-last-day-prep',
} as const

// ---------------------------------------------------------------- tracks

/**
 * Display name and description of every track, keyed by the track id that routes and
 * saved progress use. The sync scripts write these into the manifest.
 */
export const TRACKS: Record<string, { title: string; blurb: string }> = {
  core: {
    title: 'Discovery Foundations',
    blurb:
      'Ten GenAI customer problems. Start here: they practise the discovery and ' +
      'decomposition moves every later scenario builds on.',
  },
  'system-design': {
    title: 'System Design Practice',
    blurb:
      'Twelve harder scenarios, each built around one dangerous constraint — permission ' +
      'fidelity, tenant isolation, air-gapped deployment, release gating.',
  },
  'hiring-manager': {
    title: 'Hiring Manager Questions',
    blurb:
      'Five customer-facing competencies, four questions each: whether you can be put in ' +
      'front of a customer, not whether you can design a system.',
  },
  'leadership-principles': {
    title: 'Leadership Principle Questions',
    blurb:
      'Thirteen principles plus a staff-level cross-cutting set. Each model answer shows ' +
      'the shape of a strong story and marks the details you must supply yourself.',
  },
  'knowledge-retrieval': {
    title: 'Knowledge and Retrieval',
    blurb:
      'Systems that answer from an organisation’s own documents and data, where the hard ' +
      'part is who may see what, and proving where each answer came from.',
  },
  'agents-that-act': {
    title: 'Agents and Copilots in Real Workflows',
    blurb:
      'Systems that work inside real tools — tickets, deploys, CRMs, shipments. Some act on ' +
      'their own within limits; others draft and a person commits. The design is mostly ' +
      'about deciding which is which.',
  },
  'platforms-and-scale': {
    title: 'AI Platforms and Scale',
    blurb:
      'Shared platforms and high-volume services: tenant isolation, batch throughput, ' +
      'consumer-scale chat and the serving layer underneath them.',
  },
  'delivery-evaluation-operations': {
    title: 'Delivery, Evaluation, and Operations',
    blurb:
      'Getting from a scoping document to a system in production, deciding when it is ' +
      'safe to release, and diagnosing it once it is live.',
  },
  'model-development': {
    title: 'Model Development and Post-Training',
    blurb: 'Building and adapting the model itself: data, fine-tuning, post-training and evaluation.',
  },
  'standalone-designs': {
    title: 'Additional System Designs',
    blurb:
      'Complete designs that do not belong to one of the themes above, from an ' +
      'air-gapped deployment to a gateway in front of every model call.',
  },
  'judgement-and-decomposition': {
    title: 'Product Judgement and Problem Decomposition',
    blurb:
      'Questions that test how you think rather than what you draw: which use cases to ' +
      'fund, how to scale a prototype, what to do with poor data, and how to break an ' +
      'open-ended problem down in sixty minutes.',
  },
}

export const PRACTICE_TRACKS = ['core', 'system-design']

/**
 * Visible titles that differ from the source document's own heading, keyed `track/slug`.
 * Used where a source title's noun does not match what the system actually does — see
 * the autonomy rule in the style guide: an assistant answers or recommends, a copilot
 * drafts inside someone's workflow for them to commit, an agent picks and runs actions
 * within limits, an automation follows a fixed workflow. Sources keep their headings.
 */
export const TITLE_OVERRIDES: Record<string, string> = {
  // Only answers questions over governed metrics; it never drafts or acts.
  'core/executive-dashboard-copilot': 'Executive Dashboard Assistant',
  // "Automation Agent" named it twice; it proposes and performs actions within policy.
  'core/service-now-ticket-agent': 'ServiceNow Ticket Agent',
  // Drafts remediation notes for a human to approve — the same shape as G08 and the
  // legal contract copilot, so the same noun.
  'core/financial-compliance-reviewer': 'Financial Compliance Review Copilot',
}
export const BEHAVIOURAL_TRACKS = ['hiring-manager', 'leadership-principles']

// ---------------------------------------------------------------- reading-page tabs

/**
 * Every tab a reading page can have. `id` is the stored, linked identifier and never
 * changes; `label` is what the reader sees; `purpose` is the one line shown at the top
 * of the tab. The source file names in `scripts/case-studies.mjs` point at these ids.
 */
export const TABS: Record<string, { label: string; purpose: string }> = {
  main: {
    label: 'Interview Guide',
    purpose:
      'Start here. The answer you would talk through in the interview, readable on its own.',
  },
  'deep-dive': {
    label: 'Technical Deep Dive',
    purpose:
      'Read after the Interview Guide. The detail behind each component, for follow-up questions.',
  },
  'cheat-sheet': {
    label: 'Quick Review',
    purpose: 'The whole case on one page, for recall before an interview. Assumes the guide.',
  },
  'full-pack': {
    label: 'Sources and Full Design',
    purpose:
      'The complete, referenced write-up behind the other tabs. The sources for every tab live here.',
  },
  worksheet: {
    label: 'Practice Worksheet',
    purpose:
      'Attempt the case yourself first. Read-only here — use the interactive version to save answers.',
  },
  'answer-key': {
    label: 'Model Answer',
    purpose: 'Compare after attempting the worksheet: the ground a strong answer covers.',
  },
  'tutorial-v2': {
    label: 'Tutorial',
    purpose: 'The full lesson: how to reason through this case from first question to rollout.',
  },
  casebook: {
    label: 'Interview Casebook',
    purpose: 'Start here. The case as you would present it, with the likely follow-ups.',
  },
  'full-design': {
    label: 'Reference Design',
    purpose: 'The complete long-form design behind the casebook, for depth and follow-ups.',
  },
  'worked-example': {
    label: 'Worked Example',
    purpose: 'Start here. One travel-agent problem taken through every part of the framework.',
  },
  'framework-overview': {
    label: '12-Part Framework',
    purpose: 'The general framework the worked example applies, to reuse on any design question.',
  },
  guide: {
    label: 'Interview Guide',
    purpose: 'The complete case in one document — no companion tabs are needed.',
  },
  'interview-template': {
    label: 'Answer Template',
    purpose: 'A reusable structure for answering this question under time pressure.',
  },
}

/** Reading speed used for expected-time estimates. Dense technical prose, so slow. */
export const WORDS_PER_MINUTE = 180

// ---------------------------------------------------------------- Last-Day Review

export type Review = {
  number: number
  dir: string
  title: string
  blurb: string
  /** Practice worksheets to do first: `track/slug`. */
  learnFirst: string[]
  /** Case studies that show the concept in a complete system: `track/slug`. */
  goDeeper: string[]
}

export const REVIEW_DOCS = {
  concise: { file: 'concise-interview-module.html', label: 'Interview Review' },
  card: { file: 'one-page-memory-card.html', label: 'One-Page Recall Card' },
} as const

export const TRIGGER_SHEET = {
  title: 'Trigger-to-Concept Quick Reference',
  dir: 'trigger-to-concept-cheat-sheet',
  file: 'trigger-to-concept-cheat-sheet.html',
  blurb:
    'Every trigger phrase from the eighteen reviews in one searchable table — what to ' +
    'think, what to ask next, and which review covers it.',
} as const

export const REVIEWS: Review[] = [
  { number: 1, dir: 'module-01-fde-problem-decomposition', title: 'Problem Framing and Decomposition',
    blurb: 'The six-bucket discovery model and the ten questions that turn a vague ask into a problem statement.',
    learnFirst: ['core/internal-knowledge-assistant', 'core/sales-copilot'],
    goDeeper: ['judgement-and-decomposition/decomposition-classics-67-68-69', 'delivery-evaluation-operations/scoping-to-deployed-agent', 'judgement-and-decomposition/prioritize-ai-use-cases'] },
  { number: 2, dir: 'module-02-functional-requirements', title: 'Functional Requirements',
    blurb: 'Twelve reusable functional-requirement patterns and the trigger phrases that signal each one.',
    learnFirst: ['core/service-now-ticket-agent', 'core/legal-contract-copilot'],
    goDeeper: ['agents-that-act/customer-support-automation', 'agents-that-act/sales-copilot'] },
  { number: 3, dir: 'module-03-non-functional-requirements', title: 'Quality Attributes and Non-Functional Requirements',
    blurb: 'Turning “fast, safe, reliable, cheap” into measurable targets with a stated workload and window.',
    learnFirst: ['core/healthcare-prior-auth-assistant', 'core/financial-compliance-reviewer'],
    goDeeper: ['platforms-and-scale/consumer-scale-chat-service', 'judgement-and-decomposition/scale-prototype-to-production'] },
  { number: 4, dir: 'module-04-core-architecture-building-blocks', title: 'Core Architecture Components',
    blurb: 'API gateway versus model gateway, router versus orchestrator, and the seven blocks that recur in every design.',
    learnFirst: ['system-design/enterprise-chatbot-platform', 'system-design/configurable-platform-customer-specific-workflows'],
    goDeeper: ['standalone-designs/production-llm-gateway', 'standalone-designs/travel-agent-worked-example'] },
  { number: 5, dir: 'module-05-rag-and-enterprise-data', title: 'Retrieval-Augmented Generation and Enterprise Data',
    blurb: 'Recall versus precision, grounded versus correct, and the debugging order for a broken retrieval pipeline.',
    learnFirst: ['system-design/enterprise-knowledge-assistant-rag', 'core/internal-knowledge-assistant'],
    goDeeper: ['knowledge-retrieval/enterprise-knowledge-assistant', 'knowledge-retrieval/nl-over-governed-data', 'knowledge-retrieval/document-review-copilot', 'judgement-and-decomposition/build-when-customer-data-is-poor'] },
  { number: 6, dir: 'module-06-agentic-architecture', title: 'Agent Architecture and Orchestration',
    blurb: 'Workflow versus bounded agent, and what actually justifies the coordination cost of more than one agent.',
    learnFirst: ['system-design/tool-using-ai-agent-with-safety-controls', 'core/sre-triage-agent'],
    goDeeper: ['knowledge-retrieval/deep-research-agent', 'agents-that-act/enterprise-coding-assistant', 'standalone-designs/self-adapting-agent', 'standalone-designs/personal-assistant-with-memory'] },
  { number: 7, dir: 'module-07-tools-actions-and-enterprise-integration', title: 'Tools, Actions, and Enterprise Integrations',
    blurb: 'Controlled tool layers, scoped credentials, and read versus write operations against real systems.',
    learnFirst: ['core/service-now-ticket-agent', 'system-design/ai-customer-support-automation'],
    goDeeper: ['agents-that-act/tool-using-agent-with-safety-controls', 'agents-that-act/logistics-exception-handling'] },
  { number: 8, dir: 'module-08-guardrails-policy-and-human-approval', title: 'Guardrails, Policy, and Human Approval',
    blurb: 'Recommend versus act, durable human-in-the-loop workflows, approval binding, and fail-closed sensitive writes.',
    learnFirst: ['system-design/tool-using-ai-agent-with-safety-controls', 'core/healthcare-prior-auth-assistant'],
    goDeeper: ['agents-that-act/tool-using-agent-with-safety-controls', 'agents-that-act/sre-incident-response-agent'] },
  { number: 9, dir: 'module-09-scaling-ai-systems', title: 'Scaling AI Systems',
    blurb: 'Noisy-neighbour fairness, admission control, and finding the bottleneck when more workers do not help.',
    learnFirst: ['system-design/high-volume-batch-inference-system', 'system-design/secure-multi-tenant-ai-platform'],
    goDeeper: ['platforms-and-scale/high-volume-batch-pipeline', 'platforms-and-scale/consumer-scale-chat-service', 'platforms-and-scale/llm-inference-serving'] },
  { number: 10, dir: 'module-10-latency-optimization', title: 'Latency and Performance',
    blurb: 'Tail latency, the critical path, streaming versus completion, and when asynchronous work actually helps.',
    learnFirst: ['system-design/natural-language-to-sql-analytics-assistant', 'core/executive-dashboard-copilot'],
    goDeeper: ['agents-that-act/real-time-call-assistant', 'platforms-and-scale/llm-inference-serving'] },
  { number: 11, dir: 'module-11-cost-optimization', title: 'Cost and Efficiency',
    blurb: 'Cost attribution, context growth, model routing, and cost per successful task — not per request.',
    learnFirst: ['system-design/high-volume-batch-inference-system', 'core/retail-demand-explainer'],
    goDeeper: ['platforms-and-scale/high-volume-batch-pipeline', 'platforms-and-scale/agent-platform-for-non-technical-users', 'standalone-designs/production-llm-gateway'] },
  { number: 12, dir: 'module-12-reliability-and-failure-handling', title: 'Reliability and Failure Recovery',
    blurb: 'Idempotency, bounded retry, retry amplification, durable recovery, and dead-letter handling.',
    learnFirst: ['system-design/reliable-workflow-orchestration-system'],
    goDeeper: ['standalone-designs/reliable-workflow-orchestration', 'agents-that-act/logistics-exception-handling'] },
  { number: 13, dir: 'module-13-ai-evaluation', title: 'Evaluating AI Systems',
    blurb: 'Task success versus good wording, deterministic checks versus semantic rubrics, and online versus offline evidence.',
    learnFirst: ['system-design/llm-evaluation-and-release-gating-platform'],
    goDeeper: ['delivery-evaluation-operations/evaluation-and-release-gating', 'model-development/model-development-and-post-training'] },
  { number: 14, dir: 'module-14-release-and-change-management', title: 'Release and Change Management',
    blurb: 'Shadow versus canary, scoped rollout, rollback versus undo, and version-compatible in-flight state.',
    learnFirst: ['system-design/llm-evaluation-and-release-gating-platform', 'system-design/configurable-platform-customer-specific-workflows'],
    goDeeper: ['delivery-evaluation-operations/evaluation-and-release-gating', 'delivery-evaluation-operations/scoping-to-deployed-agent', 'standalone-designs/configurable-platform-customer-workflows'] },
  { number: 15, dir: 'module-15-observability-and-production-operations', title: 'Observability and Production Operations',
    blurb: 'Logs versus metrics versus traces versus audit trail, and SLI/SLO/SLA discipline for a probabilistic system.',
    learnFirst: ['system-design/observability-customer-facing-ai-application'],
    goDeeper: ['delivery-evaluation-operations/observability-and-production-diagnosis', 'agents-that-act/sre-incident-response-agent'] },
  { number: 16, dir: 'module-16-security-and-enterprise-multi-tenancy', title: 'Security, Tenant Isolation, and Multi-Tenancy',
    blurb: 'Authentication versus authorisation versus business policy, least privilege, and end-to-end tenant isolation.',
    learnFirst: ['system-design/secure-multi-tenant-ai-platform', 'system-design/ai-system-for-an-air-gapped-environment', 'core/multi-tenant-saas-support'],
    goDeeper: ['platforms-and-scale/secure-multi-tenant-ai-platform', 'standalone-designs/air-gapped-ai-system'] },
  { number: 17, dir: 'module-17-trade-off-thinking', title: 'Architecture Trade-Offs',
    blurb: 'Justifying complexity against a requirement, and stating the trade-off out loud instead of hiding it.',
    learnFirst: ['system-design/enterprise-chatbot-platform', 'core/retail-demand-explainer'],
    goDeeper: ['judgement-and-decomposition/scale-prototype-to-production', 'judgement-and-decomposition/build-when-customer-data-is-poor', 'platforms-and-scale/agent-platform-for-non-technical-users'] },
  { number: 18, dir: 'module-18-end-to-end-fde-interview-execution', title: 'End-to-End Interview Walkthrough',
    blurb: 'Discover → require → design → stress-test → ship and operate, walked through as one continuous answer.',
    learnFirst: ['system-design/enterprise-chatbot-platform', 'core/internal-knowledge-assistant'],
    goDeeper: ['standalone-designs/travel-agent-worked-example', 'standalone-designs/enterprise-chatbot-platform', 'standalone-designs/recruiting-platform'] },
]

export const reviewLabel = (n: number) => `Review ${String(n).padStart(2, '0')}`

export const reviewHref = (r: Review, doc: keyof typeof REVIEW_DOCS = 'concise') =>
  `/fde-last-day-prep/${r.dir}/${REVIEW_DOCS[doc].file}`

/** The two Last-Day documents that are Next.js reading pages rather than static HTML. */
export const LAST_DAY_GUIDES = [
  {
    id: 'roadmap',
    source: 'Roadmap.md',
    title: 'Learning Roadmap',
    eyebrow: 'Start here',
    blurb:
      'The mental model behind all eighteen reviews: what to ask, what requirement it ' +
      'creates, which component answers it, and the trade-off it introduces.',
  },
  {
    id: 'rapid-revision',
    source: 'Rapid_Revision_Guide.md',
    title: 'Rapid Revision Guide',
    eyebrow: 'Final rehearsal',
    blurb:
      'The whole interview flow compressed into one pass — discovery, requirements, ' +
      'components, retrieval, agents and operations — for the last read before the loop.',
  },
] as const

// ---------------------------------------------------------------- curriculum roadmap

/**
 * The 15-part roadmap mixes topics, activities, libraries and career work, so it is
 * shown in these phases rather than as one numbered list. Keys are module numbers.
 */
export const ROADMAP_PHASES: { title: string; blurb: string; modules: number[] }[] = [
  { title: 'Core topics', blurb: 'What an FDE system-design answer has to cover.', modules: [1, 2, 3, 4, 5, 9] },
  { title: 'Practice and assessment', blurb: 'Rehearsing under interview conditions.', modules: [6, 7, 8] },
  { title: 'Projects and reference', blurb: 'Worked systems to read and build.', modules: [15, 10, 11] },
  { title: 'Interview and career', blurb: 'The non-technical half of the loop.', modules: [14, 12, 13] },
]

/**
 * Where each roadmap module's topic is covered today, as review numbers. Planned modules
 * are not empty-handed: the reviews and case studies already cover much of their ground.
 */
export const ROADMAP_COVERAGE: Record<number, number[]> = {
  1: [1, 2, 3],
  2: [4, 9, 10, 11, 12, 17],
  3: [5, 6, 7, 8],
  4: [8, 13, 16],
  5: [10, 11, 12, 15],
  6: [],
  7: [18],
  8: [18],
  9: [7, 14],
  10: [],
  11: [],
  12: [18],
  13: [],
  14: [],
  15: [],
}

// ---------------------------------------------------------------- scorecard remediation

/** Weak on a scorecard row? These reviews cover it. Keys are the row's area label. */
export const SCORECARD_REMEDIATION: Record<string, number[]> = {
  'Problem framing': [1, 2, 3],
  Architecture: [4, 17],
  Evaluation: [13],
  'Production thinking': [12, 14, 15],
  Communication: [18],
}

// ---------------------------------------------------------------- page metadata

const FDE_AUDIENCE =
  'Engineers preparing for Forward Deployed, solutions or applied-AI engineering interviews'

/** Family defaults, keyed by track id. Every published page resolves through one. */
export const FAMILY_META: Record<string, EditorialMeta> = {
  core: {
    mode: 'practice',
    audience: FDE_AUDIENCE,
    difficulty: 'Intermediate',
    prerequisites: [
      'Working familiarity with LLM applications: prompting, retrieval and tool calls',
    ],
    outcomes: [
      'Turn a vague customer request into users, workflows and measurable requirements',
      'Propose a first architecture and say how you would evaluate and roll it out',
    ],
    howToUse:
      'Time-box it to about 45 minutes. Draft each section before opening its model answer — ' +
      'a rough attempt teaches more than a blank one, and you do not need to fill every cell.',
    minutes: 45,
    sourceStatus: 'original',
    lastReviewed: null,
  },
  'system-design': {
    mode: 'practice',
    audience: FDE_AUDIENCE,
    difficulty: 'Advanced',
    prerequisites: [
      'Two or three Discovery Foundations scenarios completed',
      'Comfort with retrieval, agents, queues and multi-tenant cloud architecture',
    ],
    outcomes: [
      'Find the one constraint that makes the scenario dangerous before designing',
      'Defend an architecture, evaluation plan and rollout under follow-up questions',
    ],
    howToUse:
      'Allow about an hour. Work the discovery sections properly — they decide the design — ' +
      'then compare each section with the model answer and score yourself honestly.',
    minutes: 60,
    sourceStatus: 'derived',
    lastReviewed: null,
  },
  'hiring-manager': {
    mode: 'behavioural',
    audience: 'Candidates with real customer-facing delivery experience to draw on',
    difficulty: 'Intermediate',
    prerequisites: [
      'A short list of six to ten real engagements you can talk about in detail',
    ],
    outcomes: [
      'Draft a STAR answer for each question from your own evidence',
      'Know which of your stories supports which question, and where you have gaps',
    ],
    howToUse:
      'Draft each answer out loud, then in writing, before revealing the model answer. The ' +
      'model answers are one candidate’s template: replace every highlighted detail with ' +
      'your own. Mastered stays locked until every field on the page has your answer.',
    minutes: 40,
    sourceStatus: 'personal',
    lastReviewed: null,
    personalisation: true,
  },
  'leadership-principles': {
    mode: 'behavioural',
    audience: 'Candidates with real delivery and leadership experience to draw on',
    difficulty: 'Advanced',
    prerequisites: [
      'A short list of six to ten real engagements you can talk about in detail',
      'The Hiring Manager Questions, if you have not practised behavioural answers before',
    ],
    outcomes: [
      'Map your own stories onto each principle, and be honest about the ones they do not cover',
      'Deliver each answer in about two minutes without reciting a template',
    ],
    howToUse:
      'Use the grounding labels to see which answers need your input. Every highlighted ' +
      'detail in a model answer is a placeholder — never say it aloud; replace it. Mastered ' +
      'stays locked until every field on the page has your answer.',
    minutes: 40,
    sourceStatus: 'personal',
    lastReviewed: null,
    personalisation: true,
  },
}

const CASE_STUDY_BASE: Omit<EditorialMeta, 'difficulty' | 'outcomes'> = {
  mode: 'case-study',
  audience: FDE_AUDIENCE,
  prerequisites: [
    'Comfort with retrieval, agents and basic cloud architecture — the related reviews below cover each',
  ],
  howToUse:
    'Read the tabs in order. The Interview Guide stands alone; later tabs assume it. Mark ' +
    'each tab as read to track the case as one unit.',
  minutes: null,
  sourceStatus: 'sourced',
  lastReviewed: null,
}

for (const track of [
  'knowledge-retrieval',
  'agents-that-act',
  'platforms-and-scale',
  'delivery-evaluation-operations',
  'model-development',
]) {
  FAMILY_META[track] = {
    ...CASE_STUDY_BASE,
    // Round 1 of the fact check (CONTENT-18): every high- and medium-priority claim in
    // the twenty grouped cases checked against official docs and papers.
    lastReviewed: '2026-09-27',
    difficulty: 'Advanced',
    outcomes: [
      'Explain the system end to end at interview depth, including its dangerous constraint',
      'Answer follow-up questions on components, failure modes, evaluation and rollout',
    ],
  }
}

FAMILY_META['standalone-designs'] = {
  ...CASE_STUDY_BASE,
  difficulty: 'Advanced',
  howToUse:
    'Read the tabs left to right; a single-document case is complete on its own. Where a ' +
    'Practice Worksheet exists, attempt it before the Model Answer.',
  sourceStatus: 'derived',
  outcomes: [
    'Explain a complete design and the trade-offs behind it',
    'Reuse its structure on an unfamiliar design question',
  ],
}

FAMILY_META['judgement-and-decomposition'] = {
  ...CASE_STUDY_BASE,
  difficulty: 'Intermediate',
  prerequisites: ['No specific technical prerequisite — these test reasoning, not components'],
  howToUse:
    'Before reading, spend five minutes sketching your own answer. Then read the guide and ' +
    'compare the structure, not just the conclusion.',
  sourceStatus: 'original',
  outcomes: [
    'Structure an open-ended or business-judgement question in the first five minutes',
    'Explain what you would do first, and why, when the data or scope is poor',
  ],
}

export const REVISION_META: EditorialMeta = {
  mode: 'revision',
  audience: FDE_AUDIENCE,
  difficulty: 'Intermediate',
  prerequisites: [
    'You have already studied these concepts — through the practice worksheets and case studies, or elsewhere',
  ],
  outcomes: [
    'Recall the mental model, gotchas and trigger phrases for each topic under time pressure',
  ],
  howToUse:
    'Read the Interview Review once, then test yourself with the One-Page Recall Card. If a ' +
    'concept is new rather than rusty, open the “learn first” link instead.',
  minutes: 12,
  sourceStatus: 'original',
  lastReviewed: '2026-09-27',
}

export const ORIENTATION_META: EditorialMeta = {
  mode: 'orientation',
  audience: FDE_AUDIENCE,
  difficulty: 'Foundation',
  prerequisites: ['None — this is the place to start'],
  outcomes: [
    'Know the order of an FDE design answer and which review covers each step',
  ],
  howToUse:
    'Read it once end to end before the reviews. Come back to the mental model whenever a ' +
    'review feels disconnected from the rest.',
  minutes: null,
  sourceStatus: 'original',
  lastReviewed: null,
}

export const FINAL_REHEARSAL_META: EditorialMeta = {
  ...REVISION_META,
  prerequisites: ['The eighteen reviews, or equivalent study'],
  outcomes: ['Walk the full interview flow from memory in one pass'],
  // Not part of fact-check round 1, so it must not inherit the reviews' date.
  lastReviewed: null,
  howToUse:
    'Read it the evening before or the morning of the interview. Anything that does not come ' +
    'back quickly points to the review to reopen.',
  minutes: null,
}

/**
 * The fields every published page must resolve. `check:content` fails a page that
 * resolves any of them to nothing.
 */
export const REQUIRED_META_FIELDS = [
  'mode',
  'audience',
  'difficulty',
  'prerequisites',
  'outcomes',
  'howToUse',
  'sourceStatus',
] as const

// ---------------------------------------------------------------- cross-links

/** Reviews that name this page as learn-first or go-deeper material. */
export function reviewsFor(ref: string): Review[] {
  return REVIEWS.filter((r) => r.learnFirst.includes(ref) || r.goDeeper.includes(ref))
}

/**
 * Practice worksheets and the case study that works the same problem space in full.
 * Keyed by practice `track/slug`, valued by case-study `track/slug`. The first five
 * are the same scenario published twice; the rest are close relatives. Each page
 * links to the other.
 */
export const RELATED_CASE: Record<string, string> = {
  'system-design/secure-multi-tenant-ai-platform': 'platforms-and-scale/secure-multi-tenant-ai-platform',
  'system-design/ai-system-for-an-air-gapped-environment': 'standalone-designs/air-gapped-ai-system',
  'system-design/reliable-workflow-orchestration-system': 'standalone-designs/reliable-workflow-orchestration',
  'system-design/configurable-platform-customer-specific-workflows': 'standalone-designs/configurable-platform-customer-workflows',
  'system-design/enterprise-chatbot-platform': 'standalone-designs/enterprise-chatbot-platform',
  'system-design/enterprise-knowledge-assistant-rag': 'knowledge-retrieval/enterprise-knowledge-assistant',
  'system-design/natural-language-to-sql-analytics-assistant': 'knowledge-retrieval/nl-over-governed-data',
  'system-design/ai-customer-support-automation': 'agents-that-act/customer-support-automation',
  'system-design/tool-using-ai-agent-with-safety-controls': 'agents-that-act/tool-using-agent-with-safety-controls',
  'system-design/llm-evaluation-and-release-gating-platform': 'delivery-evaluation-operations/evaluation-and-release-gating',
  'system-design/high-volume-batch-inference-system': 'platforms-and-scale/high-volume-batch-pipeline',
  'system-design/observability-customer-facing-ai-application': 'delivery-evaluation-operations/observability-and-production-diagnosis',
  'core/sales-copilot': 'agents-that-act/sales-copilot',
  'core/sre-triage-agent': 'agents-that-act/sre-incident-response-agent',
}

export const RELATED_PRACTICE: Record<string, string> = Object.fromEntries(
  Object.entries(RELATED_CASE).map(([p, c]) => [c, p]),
)

/**
 * Content-type qualifier appended where a scenario name is not unique across the site —
 * search results, breadcrumbs, browser titles and prev/next. The canonical title itself
 * stays unqualified. Which titles collide is worked out from the manifest, so a new
 * duplicate is qualified without anyone remembering to list it.
 */
export function qualifierFor(mode: ContentMode): string {
  return mode === 'case-study' ? 'Case Study' : 'Practice Worksheet'
}

export const normaliseTitle = (title: string) => title.toLowerCase().replace(/[^a-z0-9]+/g, '')

