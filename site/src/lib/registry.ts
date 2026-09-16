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
}

export const SITE = {
  name: 'Forward Deployed',
  tagline: 'The end-to-end FDE interview prep system',
  description:
    'Practice worksheets and answer keys for Forward Deployed Engineer interviews. ' +
    'Work a real customer scenario end to end — discovery, requirements, architecture, ' +
    'evaluation, rollout — then check yourself against what a strong answer covers.',
} as const

export const MODULES: ModuleMeta[] = [
  {
    id: '01-customer-discovery-and-decomposition',
    number: 1,
    title: 'Customer Discovery & Decomposition',
    blurb:
      'Turn an ambiguous customer problem into users, workflows, requirements and a ' +
      'defensible architecture. 22 case studies with answer keys.',
    status: 'live',
  },
  {
    id: '02-architecture-and-system-design',
    number: 2,
    title: 'Architecture & System Design',
    blurb: 'Control plane vs data plane, integration patterns, and designing for the constraint that actually bites.',
    status: 'planned',
  },
  {
    id: '03-enterprise-data-rag-and-agents',
    number: 3,
    title: 'Enterprise Data, RAG & Agents',
    blurb: 'Permission-aware retrieval, connectors and freshness, tool-using agents inside real enterprise boundaries.',
    status: 'planned',
  },
  {
    id: '04-evaluation-security-and-red-team',
    number: 4,
    title: 'Evaluation, Security & Red Team',
    blurb: 'Golden sets, leakage suites, prompt injection, and the gates that decide whether a system ships.',
    status: 'planned',
  },
  {
    id: '05-production-debugging-observability-and-optimization',
    number: 5,
    title: 'Production Debugging & Observability',
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
    title: 'Mock Interviews & Scorecards',
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
    title: 'MCP, A2A & LLMOps',
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
    title: 'Answer Language & Interview Day',
    blurb: 'The phrasing that separates a strong answer from a correct one, plus interview-day logistics.',
    status: 'planned',
  },
  {
    id: '13-career-and-portfolio-assets',
    number: 13,
    title: 'Career & Portfolio Assets',
    blurb: 'Résumé framing, portfolio projects and STAR stories that hold up to an FDE panel.',
    status: 'planned',
  },
  {
    id: '14-behavioural-and-leadership-round',
    number: 14,
    title: 'Behavioural & Leadership Round',
    blurb:
      'The non-technical half of the loop. Customer-facing competencies for the hiring ' +
      'manager round, and leadership-principle answers grounded in engagements you ' +
      'actually ran — including an honest mark on the ones they do not cover.',
    status: 'live',
  },
]

export function getModule(id: string): ModuleMeta | undefined {
  return MODULES.find((m) => m.id === id)
}

export const LIVE_MODULES = MODULES.filter((m) => m.status === 'live')
