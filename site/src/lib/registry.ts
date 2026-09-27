import { SITE_NAME, SITE_TAGLINE } from './editorial'

/**
 * The full FDE preparation path. Modules are listed here whether or not they have
 * content yet, so the roadmap is visible from the first visit and each future module
 * already has its place, title and URL decided.
 *
 * To bring a module online: add its tracks to `scripts/sync-content.mjs` and flip
 * `status` to 'live'.
 */

export type ModuleStatus = 'live' | 'planned'

export type ModuleMeta = {
  id: string
  number: number
  title: string
  blurb: string
  status: ModuleStatus
  /** Reading pages (tabbed guides) rather than fill-in worksheets. */
  kind?: 'reading'
}

export const SITE = {
  name: SITE_NAME,
  tagline: SITE_TAGLINE,
  description:
    'Practice worksheets, case studies and a last-day review for Forward Deployed Engineer ' +
    'interviews. Work a real customer scenario end to end — discovery, requirements, ' +
    'architecture, evaluation, rollout — then check yourself against what a strong answer covers.',
} as const

export const MODULES: ModuleMeta[] = [
  {
    id: '01-customer-discovery-and-decomposition',
    number: 1,
    title: 'Customer Discovery and Problem Decomposition',
    blurb:
      'Turn an ambiguous customer problem into users, workflows, requirements and a ' +
      'defensible architecture. 22 practice scenarios with model answers.',
    status: 'live',
  },
  {
    id: '02-architecture-and-system-design',
    number: 2,
    title: 'Architecture and System Design',
    blurb: 'Control plane vs data plane, integration patterns, and designing for the constraint that actually bites.',
    status: 'planned',
  },
  {
    id: '03-enterprise-data-rag-and-agents',
    number: 3,
    title: 'Enterprise Data, RAG, and Agents',
    blurb: 'Permission-aware retrieval, connectors and freshness, tool-using agents inside real enterprise boundaries.',
    status: 'planned',
  },
  {
    id: '04-evaluation-security-and-red-team',
    number: 4,
    title: 'Evaluation, Security, and Red Teaming',
    blurb: 'Golden sets, leakage suites, prompt injection, and the gates that decide whether a system ships.',
    status: 'planned',
  },
  {
    id: '05-production-debugging-observability-and-optimization',
    number: 5,
    title: 'Production Debugging and Observability',
    blurb: 'Tracing a bad answer back to its cause, SLOs for probabilistic systems, latency and cost tuning.',
    status: 'planned',
  },
  {
    id: '06-coding-interview-practice',
    number: 6,
    title: 'Coding Interview Practice',
    blurb: 'The coding round an FDE actually gets: integration glue, data wrangling, and API work under time pressure.',
    status: 'planned',
  },
  {
    id: '07-mock-interviews-and-scorecards',
    number: 7,
    title: 'Mock Interviews and Scorecards',
    blurb: 'Full-length mocks with the interviewer rubric, so you can score your own performance honestly.',
    status: 'planned',
  },
  {
    id: '08-final-readiness-assessment',
    number: 8,
    title: 'Final Readiness Assessment',
    blurb: 'A self-assessment across every dimension the loop tests, and what to do about the gaps it finds.',
    status: 'planned',
  },
  {
    id: '09-mcp-a2a-and-llmops',
    number: 9,
    title: 'MCP, A2A, and LLMOps',
    blurb: 'Agent protocols and the operational layer underneath them: deployment, versioning, rollback.',
    status: 'planned',
  },
  {
    id: '10-case-study-reference-library',
    number: 10,
    title: 'Case Study Reference Library',
    blurb: 'Worked references to read when a scenario stumps you, organised by the constraint at its centre.',
    status: 'planned',
  },
  {
    id: '11-hands-on-labs',
    number: 11,
    title: 'Hands-On Labs',
    blurb: 'Build the thing you just designed. Labs that turn a whiteboard answer into running code.',
    status: 'planned',
  },
  {
    id: '12-answer-language-and-interview-day',
    number: 12,
    title: 'Answer Language and Interview Day',
    blurb: 'The phrasing that separates a strong answer from a correct one, plus interview-day logistics.',
    status: 'planned',
  },
  {
    id: '13-career-and-portfolio-assets',
    number: 13,
    title: 'Career and Portfolio Assets',
    blurb: 'Résumé framing, portfolio projects and STAR stories that hold up to an FDE panel.',
    status: 'planned',
  },
  {
    id: '14-behavioural-and-leadership-round',
    number: 14,
    title: 'Behavioural and Leadership Practice',
    blurb:
      'The non-technical half of the loop: customer-facing competencies for the hiring ' +
      'manager, and leadership-principle answers. The model answers are a personal ' +
      'template — every one needs your own evidence before it is yours.',
    status: 'live',
  },
  {
    id: '15-fde-case-studies',
    number: 15,
    title: 'Case Studies',
    blurb:
      'Twenty grouped system designs, each read at three depths — Interview Guide, ' +
      'Technical Deep Dive and Quick Review, backed by Sources and Full Design — plus ' +
      'thirteen further cases, from complete designs to product-judgement questions.',
    status: 'live',
    kind: 'reading',
  },
]

export function getModule(id: string): ModuleMeta | undefined {
  return MODULES.find((m) => m.id === id)
}

export const LIVE_MODULES = MODULES.filter((m) => m.status === 'live')
