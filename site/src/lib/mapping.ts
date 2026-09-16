/**
 * Maps a worksheet section to the answer-key sections that speak to it.
 *
 * This is Module 01's map. Its two documents have different shapes on purpose — the
 * worksheet is 11 sections of scaffold, the answer key is 13 sections of prose — so
 * the relationship is declared here rather than inferred. Keys are `normaliseKey()`
 * output.
 *
 * A section with no entry here falls back to matching an answer-key section of the
 * same key (see `content.ts`). That is what the behavioural tracks rely on, and it
 * is a no-op for Module 01: the only two keys present in both of its documents,
 * `evaluation-plan` and `rollout-plan`, are already mapped to themselves below.
 *
 * Two deliberate gaps:
 *   - `users-and-workflows` has no counterpart. Synthesising one from other key
 *     sections would present a recombination as the key's own words.
 *   - `final-2-minute-spoken-answer` has no worksheet counterpart, so it is rendered
 *     as the closing card on the scenario page instead of inside a reveal.
 */

export const ANSWER_KEY_MAP: Record<string, string[]> = {
  'clarify-the-customer-problem': ['strong-discovery-questions'],
  requirements: [
    'strong-functional-requirements',
    'strong-non-functional-requirements',
  ],
  'data-and-integration-map': ['data-model-integration-assumptions'],
  'proposed-architecture': ['architecture-explanation'],
  'evaluation-plan': ['evaluation-plan'],
  'failure-modes': ['red-team-risks'],
  'rollout-plan': ['rollout-plan'],
  'weak-vs-strong-answer': ['weak-answer', 'average-answer', 'strong-answer'],
  'candidate-scorecard': ['interviewer-scorecard'],
}

/** Rendered as the featured closing card rather than inside a section reveal. */
export const CLOSING_SECTION_KEY = 'final-2-minute-spoken-answer'
