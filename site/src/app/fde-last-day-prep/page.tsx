import Link from 'next/link'
import type { Metadata } from 'next'

/**
 * Static HTML pages, not markdown run through content.ts. These 19 pages are
 * finished, self-contained documents (their own CSS, fonts, and — for the trigger
 * sheet — client-side search) generated for a last-day cram pass, so they are served
 * as-is from `public/fde-last-day-prep/` rather than reparsed into the
 * worksheet/reading pipeline. That pipeline exists to turn blank markdown cells into
 * inputs or split guides into tabs — neither applies here.
 */

const TITLE = 'FDE Last-Day Prep'
const BLURB =
  'Eighteen condensed interview modules plus one searchable trigger-to-concept cheat ' +
  'sheet — the run-through for the night before an FDE loop. Each module ships two ' +
  'views: a concise interview module and a one-page memory card.'

export const metadata: Metadata = {
  title: TITLE,
  description: BLURB,
}

type Entry = {
  number: number
  title: string
  blurb: string
  dir: string
}

const MODULES: Entry[] = [
  { number: 1, title: 'FDE Problem Decomposition', dir: 'module-01-fde-problem-decomposition', blurb: 'The six-bucket discovery model and the ten questions that turn a vague ask into a problem statement.' },
  { number: 2, title: 'Functional Requirements', dir: 'module-02-functional-requirements', blurb: 'Twelve reusable FR patterns and the trigger phrases that signal each one.' },
  { number: 3, title: 'Non-Functional Requirements', dir: 'module-03-non-functional-requirements', blurb: 'Turning "fast, safe, reliable, cheap" into measurable targets with a stated workload and window.' },
  { number: 4, title: 'Core Architecture Building Blocks', dir: 'module-04-core-architecture-building-blocks', blurb: 'API Gateway vs Model Gateway, router vs orchestrator, and the seven blocks that recur in every design.' },
  { number: 5, title: 'RAG & Enterprise Data', dir: 'module-05-rag-and-enterprise-data', blurb: 'Recall vs precision, grounded vs correct, and the debugging order for a broken retrieval pipeline.' },
  { number: 6, title: 'Agentic Architecture', dir: 'module-06-agentic-architecture', blurb: 'Workflow vs bounded agent, and what actually justifies the coordination cost of more than one.' },
  { number: 7, title: 'Tools, Actions & Enterprise Integration', dir: 'module-07-tools-actions-and-enterprise-integration', blurb: 'Controlled tool layers, scoped credentials, and read vs write operations against real systems.' },
  { number: 8, title: 'Guardrails, Policy & Human Approval', dir: 'module-08-guardrails-policy-and-human-approval', blurb: 'Recommend vs act, durable HITL workflows, approval binding, and fail-closed sensitive writes.' },
  { number: 9, title: 'Scaling AI Systems', dir: 'module-09-scaling-ai-systems', blurb: 'Noisy-neighbor fairness, admission control, and finding the bottleneck when more workers do not help.' },
  { number: 10, title: 'Latency Optimization', dir: 'module-10-latency-optimization', blurb: 'Tail latency, the critical path, streaming vs completion, and when async actually helps.' },
  { number: 11, title: 'Cost Optimization', dir: 'module-11-cost-optimization', blurb: 'Cost attribution, context growth, model routing, and cost per successful task — not per request.' },
  { number: 12, title: 'Reliability & Failure Handling', dir: 'module-12-reliability-and-failure-handling', blurb: 'Idempotency, bounded retry, retry amplification, durable recovery, and dead-letter handling.' },
  { number: 13, title: 'AI Evaluation', dir: 'module-13-ai-evaluation', blurb: 'Task success vs good wording, deterministic checks vs semantic rubrics, and online vs offline evidence.' },
  { number: 14, title: 'Release & Change Management', dir: 'module-14-release-and-change-management', blurb: 'Shadow vs canary, scoped rollout, rollback vs undo, and version-compatible in-flight state.' },
  { number: 15, title: 'Observability & Production Operations', dir: 'module-15-observability-and-production-operations', blurb: 'Logs vs metrics vs traces vs audit trail, and SLI/SLO/SLA discipline for a probabilistic system.' },
  { number: 16, title: 'Security & Enterprise Multi-Tenancy', dir: 'module-16-security-and-enterprise-multi-tenancy', blurb: 'Authentication vs authorization vs business policy, least privilege, and end-to-end tenant isolation.' },
  { number: 17, title: 'Trade-Off Thinking', dir: 'module-17-trade-off-thinking', blurb: 'Justifying complexity against a requirement, and stating the trade-off out loud instead of hiding it.' },
  { number: 18, title: 'End-to-End FDE Interview Execution', dir: 'module-18-end-to-end-fde-interview-execution', blurb: 'Discover → require → design → stress-test → ship/operate, walked through as one continuous answer.' },
]

const CHEAT_SHEET = {
  title: 'Trigger → Concept Cheat Sheet',
  dir: 'trigger-to-concept-cheat-sheet',
  file: 'trigger-to-concept-cheat-sheet.html',
  blurb:
    'Every trigger phrase across all 18 modules in one searchable table — what to think, ' +
    'what to ask next, and which module it belongs to.',
}

export default function FdeLastDayPrepPage() {
  return (
    <div className="py-14 sm:py-20">
      <section className="max-w-2xl">
        <p className="mb-3 text-[0.8125rem] font-semibold uppercase tracking-[0.1em] text-accent">
          Last-day cram pass
        </p>
        <h1 className="text-[2.25rem] font-bold leading-[1.15] tracking-[-0.022em] sm:text-[2.75rem]">
          {TITLE}
        </h1>
        <p className="mt-5 text-[1.0625rem] leading-relaxed text-muted">{BLURB}</p>
      </section>

      <section className="mt-10">
        <Link
          href={`/fde-last-day-prep/${CHEAT_SHEET.dir}/${CHEAT_SHEET.file}`}
          className="group flex flex-col gap-4 rounded-xl border border-accent/30 bg-accent-soft/40 p-5 transition-colors hover:border-accent sm:flex-row sm:items-center"
        >
          <div className="flex-1">
            <span className="text-[0.8125rem] font-semibold uppercase tracking-[0.1em] text-accent">
              Searchable reference
            </span>
            <h2 className="mt-1 text-[1.25rem] font-semibold tracking-[-0.014em] group-hover:text-accent">
              {CHEAT_SHEET.title}
            </h2>
            <p className="mt-1.5 text-[0.9375rem] leading-relaxed text-muted">
              {CHEAT_SHEET.blurb}
            </p>
          </div>
          <span className="shrink-0 text-[0.9375rem] font-semibold text-accent">
            Open the cheat sheet →
          </span>
        </Link>
      </section>

      <section className="mt-14">
        <div className="mb-5 flex items-baseline justify-between gap-4">
          <h2 className="text-[1.375rem] font-semibold tracking-[-0.014em]">The 18 modules</h2>
          <span className="text-[0.8125rem] text-subtle">
            {MODULES.length} of {MODULES.length} available
          </span>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {MODULES.map((m) => (
            <div
              key={m.dir}
              className="flex flex-col rounded-xl border border-border bg-surface p-5 shadow-[var(--shadow)] transition-colors hover:border-border-strong"
            >
              <div className="mb-2 flex items-center gap-2.5">
                <span className="rounded bg-accent px-1.5 py-0.5 text-[0.6875rem] font-bold tabular-nums text-white">
                  {String(m.number).padStart(2, '0')}
                </span>
              </div>
              <h3 className="text-[1.0625rem] font-semibold">{m.title}</h3>
              <p className="mt-1.5 text-[0.875rem] leading-relaxed text-muted">{m.blurb}</p>
              <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-border pt-4 text-[0.875rem] font-semibold">
                <Link
                  href={`/fde-last-day-prep/${m.dir}/concise-interview-module.html`}
                  className="text-accent transition-colors hover:text-accent-hover"
                >
                  Concise module →
                </Link>
                <Link
                  href={`/fde-last-day-prep/${m.dir}/one-page-memory-card.html`}
                  className="text-accent transition-colors hover:text-accent-hover"
                >
                  Memory card →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
