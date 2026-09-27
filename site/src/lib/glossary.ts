/**
 * The shared glossary: every acronym and cross-cutting term the site leans on, written
 * the way you would say it in an interview — short, plain, spoken. Not a textbook.
 *
 * Two jobs:
 *  - `/glossary` lists every entry, grouped, each with an anchor.
 *  - The first time an acronym with `expand` set appears on a page, it is spelled out
 *    in brackets and given a hover definition (`src/lib/acronyms.ts`, also run over the
 *    static Last-Day pages at sync). Sources are never edited for this.
 *
 * `expand: false` is for acronyms everyone reading this already knows (API, JSON, GPU):
 * they get a glossary line but spelling them out on every page would just be noise.
 *
 * Keep this file free of runtime imports: `scripts/*.mjs` load it directly.
 */

export type GlossaryGroup =
  | 'Interview and delivery'
  | 'Models and AI'
  | 'Retrieval and data'
  | 'Agents and tools'
  | 'Security and compliance'
  | 'Reliability and operations'
  | 'Performance and cost'
  | 'Business and domain'

export type GlossaryEntry = {
  /** As written in the text. Acronyms are matched case-sensitively. */
  term: string
  /** The spelled-out form, lower-case unless it is a name. Acronyms only. */
  expansion?: string
  /** Plural of the expansion when adding "s" to the last word would be wrong. */
  plural?: string
  /** One or two spoken sentences: what it is, in plain words. */
  plain: string
  /** Optional: the line you would actually say in the interview. */
  sayIt?: string
  group: GlossaryGroup
  /** Acronyms only. False = listed in the glossary, never auto-expanded. */
  expand?: boolean
}

export const GLOSSARY: GlossaryEntry[] = [
  // ---------------------------------------------------------------- interview and delivery
  { term: 'FDE', expansion: 'Forward Deployed Engineer', group: 'Interview and delivery',
    plain: 'An engineer who sits with the customer, figures out the real problem, and ships a working system in their environment.',
    sayIt: 'My job is to turn a vague customer ask into something running in production.' },
  { term: 'STAR', expansion: 'situation, task, action, result', group: 'Interview and delivery',
    plain: 'The four-beat shape for a behavioural answer: what was going on, what you owned, what you did, what changed.' },
  { term: 'SME', expansion: 'subject-matter expert', group: 'Interview and delivery',
    plain: 'The person at the customer who actually knows the domain — the one who can tell you if an answer is right.' },
  { term: 'MVP', expansion: 'minimum viable product', group: 'Interview and delivery',
    plain: 'The smallest version that proves the idea works for real users. Not a demo — something people actually use.' },
  { term: 'NFR', expansion: 'non-functional requirement', group: 'Interview and delivery',
    plain: 'How well the system must work — speed, safety, uptime, cost — as opposed to what it does.',
    sayIt: 'Fast, safe and cheap mean nothing until I put a number and a workload on each.' },
  { term: 'FR', expansion: 'functional requirement', group: 'Interview and delivery',
    plain: 'Something the system must do: answer this question, draft that email, update that ticket.' },
  { term: 'IC', expansion: 'individual contributor', group: 'Interview and delivery',
    plain: 'Someone who leads through their own work rather than by managing people.' },
  { term: 'PM', expansion: 'product manager', group: 'Interview and delivery',
    plain: 'The person who owns what gets built and why.' },
  { term: 'GA', expansion: 'generally available', group: 'Interview and delivery',
    plain: 'A product feature that is fully released and supported — not preview or beta.' },
  { term: 'QA', expansion: 'quality assurance', group: 'Interview and delivery',
    plain: 'Checking the thing works before real users see it.' },

  // ---------------------------------------------------------------- models and AI
  { term: 'AI', expansion: 'artificial intelligence', group: 'Models and AI', expand: false,
    plain: 'Here, almost always means systems built around large language models.' },
  { term: 'ML', expansion: 'machine learning', group: 'Models and AI',
    plain: 'Models that learn patterns from data instead of following hand-written rules.' },
  { term: 'LLM', expansion: 'large language model', group: 'Models and AI',
    plain: 'The model that reads text and writes text — GPT, Claude, Llama. Powerful, but it will confidently make things up if you let it.' },
  { term: 'GPT', group: 'Models and AI', expand: false,
    plain: "OpenAI's family of large language models. Often used loosely to mean any chat model." },
  { term: 'NL', expansion: 'natural language', group: 'Models and AI',
    plain: 'Plain human language, as opposed to code or SQL.' },
  { term: 'SFT', expansion: 'supervised fine-tuning', group: 'Models and AI',
    plain: 'Training a model further on good example inputs and outputs so it copies that behaviour.' },
  { term: 'DPO', expansion: 'direct preference optimisation', group: 'Models and AI',
    plain: 'Training a model on pairs of "this answer is better than that one", without a separate reward model.' },
  { term: 'RLHF', expansion: 'reinforcement learning from human feedback', group: 'Models and AI',
    plain: 'Teaching a model which answers people prefer by rewarding the preferred ones.' },
  { term: 'OCR', expansion: 'optical character recognition', group: 'Models and AI',
    plain: 'Turning scanned pages or images into text. Often where document pipelines quietly lose accuracy.' },
  { term: 'ASR', expansion: 'automatic speech recognition', group: 'Models and AI',
    plain: 'Speech-to-text. In a live call, its delay and errors flow into everything after it.' },
  { term: 'VAD', expansion: 'voice activity detection', group: 'Models and AI',
    plain: 'Working out when someone has started or stopped talking.' },
  { term: 'Fine-tuning', group: 'Models and AI',
    plain: 'Training an existing model further on your own data. Usually the last thing to reach for, after prompting and retrieval.' },
  { term: 'Hallucination', group: 'Models and AI',
    plain: 'The model stating something that sounds right but is not supported by any source.',
    sayIt: "I don't try to stop the model guessing — I make it answer only from evidence, and check it did." },
  { term: 'LLM-as-judge', group: 'Models and AI',
    plain: 'Using a model to grade another model\'s answers against a rubric. Cheap and fast, but you calibrate it against human grades first.' },

  // ---------------------------------------------------------------- retrieval and data
  { term: 'RAG', expansion: 'retrieval-augmented generation', group: 'Retrieval and data',
    plain: 'Fetch the relevant documents first, then have the model answer only from them.',
    sayIt: "The model doesn't know the customer's data, so I retrieve the right evidence and make it answer from that, with citations." },
  { term: 'Chunking', group: 'Retrieval and data',
    plain: 'Splitting documents into pieces small enough to search and fit in a prompt, without cutting the meaning in half.' },
  { term: 'Embedding', group: 'Retrieval and data',
    plain: 'A list of numbers that captures what a piece of text means, so similar meanings end up close together.' },
  { term: 'Vector search', group: 'Retrieval and data',
    plain: 'Finding the chunks whose meaning is closest to the question, using embeddings.' },
  { term: 'Hybrid search', group: 'Retrieval and data',
    plain: 'Running keyword search and vector search together and merging the results — catches both exact terms and meaning.' },
  { term: 'BM25', group: 'Retrieval and data',
    plain: 'The standard keyword-search scoring method. Great at exact names, codes and IDs that vector search misses.' },
  { term: 'RRF', expansion: 'reciprocal rank fusion', group: 'Retrieval and data',
    plain: 'A simple way to merge two ranked result lists — each result scores by how high it sits in each list.' },
  { term: 'Reranking', group: 'Retrieval and data',
    plain: 'A second, more careful pass that reorders the top search results before they go to the model.' },
  { term: 'Grounding', group: 'Retrieval and data',
    plain: 'Tying every claim in an answer back to a source the user can check.',
    sayIt: 'Grounded is not the same as correct — the source itself can be stale or wrong.' },
  { term: 'SQL', expansion: 'structured query language', group: 'Retrieval and data', expand: false,
    plain: 'The language for asking questions of a database.' },
  { term: 'BI', expansion: 'business intelligence', group: 'Retrieval and data',
    plain: 'Dashboards and reports over company data.' },
  { term: 'EDI', expansion: 'electronic data interchange', group: 'Retrieval and data',
    plain: 'Old but everywhere: the standard file formats companies use to swap orders, invoices and shipment updates.' },
  { term: 'CSV', expansion: 'comma-separated values', group: 'Retrieval and data', expand: false,
    plain: 'A plain spreadsheet file.' },
  { term: 'JSON', group: 'Retrieval and data', expand: false,
    plain: 'The standard text format for structured data passed between systems.' },
  { term: 'PDF', group: 'Retrieval and data', expand: false,
    plain: 'The document format that looks the same everywhere — and is often painful to extract text from.' },
  { term: 'ID', expansion: 'identifier', group: 'Retrieval and data', expand: false,
    plain: 'The unique key for a record — a customer ID, a ticket ID, a request ID you can trace end to end.' },
  { term: 'DB', expansion: 'database', group: 'Retrieval and data', expand: false,
    plain: 'Where the data lives.' },

  // ---------------------------------------------------------------- agents and tools
  { term: 'API', expansion: 'application programming interface', group: 'Agents and tools', expand: false,
    plain: 'The way one system lets another call it. For an agent, every tool is usually an API call.' },
  { term: 'SDK', expansion: 'software development kit', group: 'Agents and tools', expand: false,
    plain: 'A ready-made library for talking to a service.' },
  { term: 'REST', group: 'Agents and tools', expand: false,
    plain: 'The most common style of web API: resources at URLs, read and changed with HTTP calls.' },
  { term: 'MCP', expansion: 'Model Context Protocol', group: 'Agents and tools',
    plain: 'An open standard for plugging tools and data sources into an AI app, so each tool is written once and reused.' },
  { term: 'HITL', expansion: 'human in the loop', group: 'Agents and tools',
    plain: 'A person approves or corrects the AI before anything risky happens.',
    sayIt: 'The agent recommends; a human approves the write. I make that approval durable so it survives a restart.' },
  { term: 'Tool calling', group: 'Agents and tools',
    plain: 'The model asking your code to run a function — search, look up an order, create a ticket — and using the result.' },
  { term: 'Agent loop', group: 'Agents and tools',
    plain: 'Think, pick a tool, look at the result, repeat — until the task is done or a limit is hit.' },
  { term: 'Orchestrator', group: 'Agents and tools',
    plain: 'The part that decides which step or agent runs next and keeps track of where the task is.' },
  { term: 'Guardrail', group: 'Agents and tools',
    plain: 'A check before or after the model — block unsafe input, stop a bad action, catch a leaked secret.' },
  { term: 'Prompt injection', group: 'Agents and tools',
    plain: 'Text hidden in a document or web page that tries to hijack the model: "ignore your instructions and…".',
    sayIt: "I treat everything the model reads as untrusted, and the model never holds more permission than the user." },
  { term: 'IDE', expansion: 'integrated development environment', group: 'Agents and tools',
    plain: 'The code editor a developer works in.' },
  { term: 'AST', expansion: 'abstract syntax tree', group: 'Agents and tools',
    plain: 'Code parsed into its structure — functions, calls, imports — so a tool can reason about it rather than raw text.' },

  // ---------------------------------------------------------------- security and compliance
  { term: 'PII', expansion: 'personally identifiable information', group: 'Security and compliance',
    plain: 'Anything that identifies a person — name, email, phone, account number. It needs masking, access control and care in logs.' },
  { term: 'PHI', expansion: 'protected health information', group: 'Security and compliance',
    plain: 'Health data tied to a person. Heavily regulated, especially in the US.' },
  { term: 'ACL', expansion: 'access control list', group: 'Security and compliance',
    plain: 'The list of who is allowed to see or change a thing.',
    sayIt: 'I filter by the user\'s permissions before retrieval, not after — the model should never see what the user can\'t.' },
  { term: 'RBAC', expansion: 'role-based access control', group: 'Security and compliance',
    plain: 'Permissions given by role: managers can do this, agents can do that.' },
  { term: 'ABAC', expansion: 'attribute-based access control', group: 'Security and compliance',
    plain: 'Permissions decided by attributes — region, department, data sensitivity — not just role. Finer-grained than RBAC.' },
  { term: 'SSO', expansion: 'single sign-on', group: 'Security and compliance',
    plain: 'One company login for every app. It is also where you get the user\'s identity to enforce permissions.' },
  { term: 'DLP', expansion: 'data loss prevention', group: 'Security and compliance',
    plain: 'Tools that stop sensitive data leaving where it should stay.' },
  { term: 'HMAC', expansion: 'hash-based message authentication code', group: 'Security and compliance',
    plain: 'A signature that proves a message came from who it says and was not changed on the way.' },
  { term: 'GDPR', expansion: 'General Data Protection Regulation', group: 'Security and compliance',
    plain: "The EU's data-privacy law: consent, the right to be forgotten, where data may live." },
  { term: 'HIPAA', expansion: 'Health Insurance Portability and Accountability Act', group: 'Security and compliance',
    plain: 'The US law on protecting health data.' },
  { term: 'SOC 2', group: 'Security and compliance',
    plain: 'An audit report showing a vendor handles customer data securely. Enterprise buyers ask for it before signing.' },
  { term: 'Least privilege', group: 'Security and compliance',
    plain: 'Give every user, service and agent only the access it needs for this task, and nothing more.' },
  { term: 'Tenant isolation', group: 'Security and compliance',
    plain: "Making sure one customer's data, prompts, caches and logs can never show up for another customer." },
  { term: 'Fail closed', group: 'Security and compliance',
    plain: 'When a safety check breaks or times out, block the action rather than let it through.' },
  { term: 'Blast radius', group: 'Security and compliance',
    plain: 'How much damage one mistake can do. You design to keep it small.' },
  { term: 'Red teaming', group: 'Security and compliance',
    plain: 'Deliberately attacking your own system to find how it breaks before someone else does.' },

  // ---------------------------------------------------------------- reliability and operations
  { term: 'SLO', expansion: 'service level objective', group: 'Reliability and operations',
    plain: 'The target you commit to internally: "95% of answers in under 3 seconds".',
    sayIt: 'I set the SLO on a stated workload and window, then alert when we burn through the error budget.' },
  { term: 'SLA', expansion: 'service level agreement', group: 'Reliability and operations',
    plain: 'The promise to the customer, usually with penalties. Looser than the SLO, so you have room.' },
  { term: 'SLI', expansion: 'service level indicator', group: 'Reliability and operations',
    plain: 'The actual measurement behind an SLO — latency, error rate, answer success rate.' },
  { term: 'SRE', expansion: 'site reliability engineering', group: 'Reliability and operations',
    plain: 'The team and practice that keeps production running: on-call, SLOs, incident response.' },
  { term: 'RCA', expansion: 'root cause analysis', group: 'Reliability and operations',
    plain: 'Working out why something actually broke, not just what broke.' },
  { term: 'CI/CD', expansion: 'continuous integration and continuous delivery', group: 'Reliability and operations',
    plain: 'The automated pipeline that tests and ships every change.' },
  { term: 'DLQ', expansion: 'dead-letter queue', group: 'Reliability and operations',
    plain: 'Where messages go after they keep failing, so they stop blocking everything else and someone can look at them.' },
  { term: 'FIFO', expansion: 'first in, first out', group: 'Reliability and operations',
    plain: 'Handle things in the order they arrived.' },
  { term: 'TTL', expansion: 'time to live', group: 'Reliability and operations',
    plain: 'How long a cached or stored item stays valid before it expires.' },
  { term: 'RPO', expansion: 'recovery point objective', group: 'Reliability and operations',
    plain: 'How much data you can afford to lose in a disaster, measured in time.' },
  { term: 'RTO', expansion: 'recovery time objective', group: 'Reliability and operations',
    plain: 'How long you can afford to be down in a disaster.' },
  { term: 'CMDB', expansion: 'configuration management database', group: 'Reliability and operations',
    plain: 'The IT inventory: which services exist, who owns them, what depends on what.' },
  { term: 'ITSM', expansion: 'IT service management', group: 'Reliability and operations',
    plain: 'How an IT team runs tickets, incidents and changes — ServiceNow is the typical tool.' },
  { term: 'ITIL', group: 'Reliability and operations',
    plain: 'The standard playbook for IT service management processes.' },
  { term: 'Idempotency', group: 'Reliability and operations',
    plain: 'Doing the same request twice has the same effect as doing it once — so a retry never double-refunds.',
    sayIt: 'Every write carries an idempotency key, so retries are safe.' },
  { term: 'Retry amplification', group: 'Reliability and operations',
    plain: 'Every layer retrying a failed call, so one outage turns into a flood of traffic that makes it worse.' },
  { term: 'Circuit breaker', group: 'Reliability and operations',
    plain: 'Stop calling a dependency that keeps failing for a while, instead of hammering it.' },
  { term: 'Backpressure', group: 'Reliability and operations',
    plain: 'Slowing down or rejecting new work when the system is full, instead of falling over.' },
  { term: 'Canary release', group: 'Reliability and operations',
    plain: 'Ship the new version to a small slice of traffic first, watch it, then widen.' },
  { term: 'Shadow mode', group: 'Reliability and operations',
    plain: 'Run the new system on real traffic but don\'t show its output to users — just compare it with what happened.' },
  { term: 'Golden set', group: 'Reliability and operations',
    plain: 'A fixed set of real questions with agreed right answers, run on every change to catch regressions.',
    sayIt: 'Nothing ships unless it holds up on the golden set.' },
  { term: 'Drift', group: 'Reliability and operations',
    plain: 'Quality slowly changing because the data, the users or the model changed underneath you.' },
  { term: 'Observability', group: 'Reliability and operations',
    plain: 'Being able to see why the system did what it did — logs, metrics, traces, and for AI, the prompt and evidence behind each answer.' },

  // ---------------------------------------------------------------- performance and cost
  { term: 'P50', group: 'Performance and cost',
    plain: 'Median latency: half of requests are faster than this.' },
  { term: 'P95', group: 'Performance and cost',
    plain: '95% of requests are faster than this. The number users actually feel on a bad day.' },
  { term: 'P99', group: 'Performance and cost',
    plain: '99% of requests are faster than this — the tail. It is where the slow outliers live.' },
  { term: 'Tail latency', group: 'Performance and cost',
    plain: 'How slow the slowest requests are (P95, P99). Averages hide it.' },
  { term: 'TTFT', expansion: 'time to first token', group: 'Performance and cost',
    plain: 'How long until the first word of the answer appears. With streaming, this is what feels fast or slow.' },
  { term: 'TPOT', expansion: 'time per output token', group: 'Performance and cost',
    plain: 'How fast the rest of the answer streams once it has started.' },
  { term: 'QPS', expansion: 'queries per second', group: 'Performance and cost',
    plain: 'How much traffic hits the system each second.' },
  { term: 'KV', expansion: 'key–value', group: 'Performance and cost',
    plain: 'As in "KV cache": the model\'s memory of the prompt so far, reused so it does not recompute it for every new token.' },
  { term: 'FLOP', expansion: 'floating-point operation', group: 'Performance and cost',
    plain: 'A unit of compute. Used to size how much GPU work a model needs.' },
  { term: 'GPU', expansion: 'graphics processing unit', group: 'Performance and cost', expand: false,
    plain: 'The chip models run on. Usually the biggest cost line.' },
  { term: 'CPU', group: 'Performance and cost', expand: false,
    plain: 'A general-purpose processor.' },
  { term: 'CDN', expansion: 'content delivery network', group: 'Performance and cost',
    plain: 'Servers around the world that cache content close to users.' },
  { term: 'SSE', expansion: 'server-sent events', group: 'Performance and cost',
    plain: 'A simple way for a server to stream an answer to the browser as it is written.' },
  { term: 'Noisy neighbour', group: 'Performance and cost',
    plain: 'One heavy customer on a shared platform slowing everyone else down.' },
  { term: 'Model routing', group: 'Performance and cost',
    plain: 'Sending easy requests to a small cheap model and hard ones to a big model.' },
  { term: 'Prompt caching', group: 'Performance and cost',
    plain: 'Reusing the processed start of a prompt that repeats across calls, to save time and cost.' },

  // ---------------------------------------------------------------- business and domain
  { term: 'ROI', expansion: 'return on investment', group: 'Business and domain',
    plain: 'What the customer gets back for what they spend. Say it in hours saved or money saved, not "better AI".' },
  { term: 'KPI', expansion: 'key performance indicator', group: 'Business and domain',
    plain: 'The number the business watches to judge success.' },
  { term: 'CSAT', expansion: 'customer satisfaction score', group: 'Business and domain',
    plain: 'How happy customers say they are, usually from a quick survey.' },
  { term: 'DAU', expansion: 'daily active users', group: 'Business and domain',
    plain: 'How many people use the product on a given day.' },
  { term: 'MRR', expansion: 'monthly recurring revenue', group: 'Business and domain',
    plain: 'Subscription revenue per month.' },
  { term: 'B2B', expansion: 'business-to-business', group: 'Business and domain',
    plain: 'Selling to companies rather than to consumers.' },
  { term: 'CRM', expansion: 'customer relationship management', group: 'Business and domain',
    plain: 'The sales and customer system of record — Salesforce is the usual example.' },
  { term: 'ERP', expansion: 'enterprise resource planning', group: 'Business and domain',
    plain: 'The system that runs finance, orders and inventory — SAP is the usual example.' },
  { term: 'SKU', expansion: 'stock-keeping unit', group: 'Business and domain',
    plain: 'One specific product variant a retailer tracks.' },
  { term: 'ETA', expansion: 'estimated time of arrival', group: 'Business and domain',
    plain: 'When a shipment is expected.' },
  { term: 'FAQ', expansion: 'frequently asked questions', group: 'Business and domain', expand: false,
    plain: 'The common questions and their standard answers.' },
  { term: 'CLM', expansion: 'contract lifecycle management', group: 'Business and domain',
    plain: 'The system that stores contracts and tracks them from draft to renewal.' },
  { term: 'EHR', expansion: 'electronic health record', group: 'Business and domain',
    plain: "A patient's medical record system." },
  { term: 'FHIR', group: 'Business and domain',
    plain: 'The standard API format for exchanging health records.' },
  { term: 'NBFC', expansion: 'non-banking financial company', group: 'Business and domain',
    plain: 'An Indian lender that is not a bank but is still regulated.' },
  { term: 'HR', expansion: 'human resources', group: 'Business and domain', expand: false,
    plain: 'The people team.' },
]

/**
 * Words written in capitals that are not acronyms — emphasis, labels, section markers,
 * names and ids. `check:content` ignores these when it looks for undefined acronyms.
 */
export const NOT_ACRONYMS = new Set([
  'NEEDS', 'YOUR', 'INPUT', 'PARTLY', 'GROUNDED', 'FILL', 'EMPTY', 'MEASURE', 'THE', 'POST',
  'GEN', 'WHAT', 'WHY', 'HOW', 'WHO', 'SHADOW', 'DESIGN', 'AUDIT', 'SUCCESS', 'LIVE', 'GET',
  'DRAFT', 'SCALE', 'QUALITY', 'DENIED', 'INVALID', 'TESTING', 'FAILURE', 'DO', 'TODAY', 'COST',
  'QUEUE', 'CONTEXT', 'UNIQ', 'CHANGES', 'WITH', 'ANSWER', 'NOT', 'FORWARD', 'SYSTEM', 'THAT',
  'VERIFY', 'ROUTE', 'IN', 'DATA', 'LATENCY', 'TOOL', 'SAFETY', 'MUCH', 'FAR', 'REV', 'MOD',
  // Regions, well-known names and products, units, versions
  'US', 'EU', 'APAC', 'EMEA', 'AMER', 'AWS', 'SAP', 'VIP', 'OS', 'IT', 'IP', 'KB', 'GB', 'MB',
  'UI', 'UX', 'URL', 'HTTP', 'HTTPS', 'ASCII', 'SHA256', 'V1', 'V2', 'Q3', 'CD', 'CI', 'SOC',
  'DM',
])

export const glossaryAnchor = (term: string) =>
  term.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
