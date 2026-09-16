'use client'

/**
 * Per-browser persistence for worksheet answers, scores and status.
 *
 * Everything here assumes storage can fail. In a private window, with site data
 * blocked, or over quota, `localStorage` access throws on read as well as write —
 * so every call is guarded and the site stays fully usable with no storage at all.
 * Nothing here ever leaves the reader's browser.
 */

const PREFIX = 'fd:v1'

export type Status = 'not-started' | 'practiced' | 'mastered'

export const STATUS_LABELS: Record<Status, string> = {
  'not-started': 'Not started',
  practiced: 'Practiced',
  mastered: 'Mastered',
}

function read<T>(key: string, fallback: T): T {
  if (typeof window === 'undefined') return fallback
  try {
    const raw = window.localStorage.getItem(key)
    return raw ? (JSON.parse(raw) as T) : fallback
  } catch {
    return fallback
  }
}

function write(key: string, value: unknown): boolean {
  if (typeof window === 'undefined') return false
  try {
    window.localStorage.setItem(key, JSON.stringify(value))
    return true
  } catch {
    return false
  }
}

function remove(key: string): void {
  if (typeof window === 'undefined') return
  try {
    window.localStorage.removeItem(key)
  } catch {
    /* nothing to do — the value was never stored */
  }
}

const answersKey = (scenario: string) => `${PREFIX}:answers:${scenario}`
const scoresKey = (scenario: string) => `${PREFIX}:scores:${scenario}`
const statusKey = (scenario: string) => `${PREFIX}:status:${scenario}`
const rowsKey = (scenario: string) => `${PREFIX}:rows:${scenario}`

export type Answers = Record<string, string>
export type Scores = Record<string, number>
/** Extra table rows the reader has added, keyed by table block id. */
export type ExtraRows = Record<string, number>

export const loadAnswers = (s: string) => read<Answers>(answersKey(s), {})
export const saveAnswers = (s: string, v: Answers) => write(answersKey(s), v)

export const loadScores = (s: string) => read<Scores>(scoresKey(s), {})
export const saveScores = (s: string, v: Scores) => write(scoresKey(s), v)

export const loadExtraRows = (s: string) => read<ExtraRows>(rowsKey(s), {})
export const saveExtraRows = (s: string, v: ExtraRows) => write(rowsKey(s), v)

export const loadStatus = (s: string) => read<Status>(statusKey(s), 'not-started')
export const saveStatus = (s: string, v: Status) => write(statusKey(s), v)

export function clearScenario(scenario: string): void {
  remove(answersKey(scenario))
  remove(scoresKey(scenario))
  remove(statusKey(scenario))
  remove(rowsKey(scenario))
}

export function clearEverything(): void {
  if (typeof window === 'undefined') return
  try {
    const keys: string[] = []
    for (let i = 0; i < window.localStorage.length; i++) {
      const key = window.localStorage.key(i)
      if (key?.startsWith(`${PREFIX}:`)) keys.push(key)
    }
    for (const key of keys) window.localStorage.removeItem(key)
  } catch {
    /* storage unavailable — there is nothing to clear */
  }
}

/** Number of answered fields, used for the per-scenario completion indicator. */
export function countAnswered(scenario: string): number {
  const answers = loadAnswers(scenario)
  return Object.values(answers).filter((v) => v.trim() !== '').length
}

export type ScenarioProgress = { status: Status; answered: number; scored: number }

export function loadProgress(scenario: string): ScenarioProgress {
  return {
    status: loadStatus(scenario),
    answered: countAnswered(scenario),
    scored: Object.keys(loadScores(scenario)).length,
  }
}

/**
 * Notifies same-tab listeners. The native `storage` event only fires in *other*
 * tabs, so components that render progress alongside an editor need this.
 */
export const PROGRESS_EVENT = 'fd:progress'

export function notifyProgress(): void {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new Event(PROGRESS_EVENT))
}
