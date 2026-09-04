# Case 4 — AI-Powered Recruiting Platform

> **Level** 🔴 Design Mastery · **Module** 09 · **Doc** 4 of 6 · **Time** ~30 min
> **Prerequisites:** Module 02, Module 04 doc 7 (judges), Module 05 doc 5 (human approval)
> **Source material:** `4. FDE_Related_Preparation/System_Design and Delivery/8. AI Powered Recruiting Platform Design.md`

## The prompt

Design an AI-powered recruiting platform that screens resumes, matches candidates to job descriptions, generates interview questions, scores candidates, schedules interviews and assists hiring managers — end to end, from upload to hiring decision.

## Step 1 — Define the problem space

Recruiters upload a job description, receive resumes in bulk, get candidates ranked by fit, generate questions and scorecards, schedule interviews, receive a recommendation — **while remaining in control of the final decision.** That last clause is the whole design constraint: an AI-*assisted* workflow, not an autonomous hiring system.

| Question | Answer | What it decides |
|---|---|---|
| Enterprise hiring or staffing agencies? | Differs | Multi-tenancy and volume assumptions |
| Real-time or batch matching? | Batch for bulk ingestion; near-real-time for recruiter search | Two processing modes |
| Can recruiters override AI recommendations? | Yes, always | Human-in-the-loop is first-class |
| Fully automated or human-assisted decisions? | Human-assisted | Every downstream choice bends toward explainability |
| Compliance — GDPR, EEOC? | Yes | Fairness monitoring and audit are non-negotiable |

**Functional:** upload JD and resumes; extract structured info; rank by fit; semantic search across profiles; generate questions and scorecards; recommend decisions; schedule; summarise feedback; recruiter chatbot; learn from past decisions. **Non-functional:** thousands of resumes/hour; accuracy; low hallucination; secure PII; scale; **explainable rankings**; compliance; cost.

## Step 2 — High-level architecture: two intake paths, one ranked pipeline

```
Recruiter Portal
│
Authentication Service
│
API Gateway / Load Balancer
┌──────────────┴──────────────┐
Resume Upload          Job Description Upload
│                              │
OCR / Document Parser         JD Parser
└──────────────┬──────────────┘
     Structured Extraction Service
                │
       Candidate Profile Builder
                │
       Embedding Generation Service
                │
       Vector Database (candidate & JD embeddings)
                │
       Similarity Search Engine
                │
          Candidate Ranking
┌──────────────┴──────────────┐
Interview Question         AI Judge
Generator                  Scoring
└──────────────┬──────────────┘
         Evaluation Pipeline
                │
        Human Recruiter Review
                │
         Interview Scheduler
                │
          Candidate Portal
```

**Structured extraction is the seam between "documents" and "data":** everything before it deals with PDFs and free text; everything after deals with comparable, rankable profiles. Module 06's chunking-by-format lesson — resumes vary wildly, and the parser has to produce one consistent shape.

## Step 3 — The flow

1. **JD upload** — parsed into required and preferred skills, experience, education, certifications, location, salary.
2. **Resume upload** — PDF, DOCX, a LinkedIn profile, an ATS record.
3. **Structured extraction** — structured fields, not raw text; that is what makes search and ranking reliable.
4. **Embeddings** — for the JD, the profile, skills, projects, experience, certifications — semantic meaning, not keywords.
5. **Similarity search** — *"LLM Engineer"* retrieves candidates mentioning Generative AI, RAG, prompt engineering, agentic AI.
6. **Ranking** — multiple weighted signals; an explainable list, not pass/fail.
7. **Interview questions** — role-specific, based on the JD, the candidate's experience, missing skills, past projects.
8. **AI judge** — after interviews or assessments: technical correctness, communication, problem-solving, alignment — structured feedback and preliminary scores.
9. **Human review** — a recruiter or hiring manager reviews ranking, scores, summaries and recommendations, and **makes the final decision** — accountability and bias reduction.
10. **Scheduling** — availability, slots, invites, notifications, ATS update.

## Step 4 — The deep dive: explainable ranking

The ranking engine combines several signals rather than one similarity number: semantic similarity, required-skills match, experience level, domain expertise, location, certifications, availability, historical hiring success where applicable. **Weighting the signals explicitly, rather than letting one opaque score decide, is what makes a ranking explainable to a recruiter and defensible in an audit.**

An illustrative weighting: semantic similarity ~30% · skills match ~25% · experience ~20% · domain expertise ~15% · other signals ~10%. A recruiter can see *why* a candidate ranked where they did, not just that they did.

The AI judge follows the same principle: standardised scoring with rationale — and **it does not make the final decision.** The evaluation pipeline combines similarity, completeness, judge scores, interview feedback, recruiter and hiring-manager input, with **confidence thresholds that make manual review mandatory** below a bar. Module 04's rule — never gate a consequential decision on an LLM judge alone — applied to people's careers.

## Step 5 — Scaling to thousands of resumes an hour

Stateless application servers; **asynchronous document processing** (parsing and embedding as background jobs, never blocking the upload); distributed vector databases; GPU-backed inference absorbing the burst when a new posting triggers thousands of comparisons; **event-driven ingestion** decoupling upload from parse, extract, embed and rank; multi-region for latency and candidate-PII residency; caching embeddings and generated outputs; queue-based processing for peak seasons.

## Security and fairness — candidate data is sensitive; hiring decisions carry legal weight

Encrypt at rest and in transit; protect PII; RBAC for recruiters and hiring managers; **audit logs for every AI recommendation and hiring action**; GDPR, CCPA, EEOC; candidate deletion requests; **monitor models for fairness and bias across protected groups — continuously, not once.**

```
AI Ranking & Scores → Human Recruiter Review → Approve or Override → Final Hiring Decision
                        (continuous bias and fairness monitoring over the whole path)
```

AI ranking never bypasses a human.

## Trade-offs

| Decision | Pros | Cons |
|---|---|---|
| Keyword matching | Fast, simple | Misses semantically similar candidates |
| Embedding-based search | Better discovery | Compute cost |
| Fully automated hiring | Faster | Legal and ethical risk |
| Human-in-the-loop | Oversight, fairness | Slower |
| Large reasoning model | Better summaries and questions | Latency, cost |
| Smaller model | Faster, cheaper | Lower reasoning |

## Follow-ups to have ready

**How do you reduce bias?** Remove or mask demographic information where appropriate; diverse training and evaluation data; continuous fairness metrics; human approval required; transparent explanations for rankings; regular audits.

**How do you improve matching accuracy?** Semantic embeddings over keywords; multiple ranking signals; recruiter feedback into the ranking model; precision and recall against historical outcomes; prompt and retrieval tuning on feedback.

**How do you personalise for recruiters?** Learn from previous decisions; prioritise candidates similar to successful hires *while monitoring for bias*; question difficulty by seniority; team-specific skills; recruiter-configurable weights.

## Summary

An end-to-end AI workflow — structured extraction, semantic matching, explainable ranking, AI-judged evaluation — with a human in control of the final decision and fairness, PII protection and compliance treated as design constraints rather than checkboxes. **Every stage is AI-assisted; no stage is AI-decided.**

## Checkpoint

- Why is structured extraction the most important seam in the architecture?
- Why is an explicit weighted ranking more defensible than a single model score?
- What does the AI judge do and not do, and what forces manual review?
- Name three fairness mechanisms and say which is continuous.
- Why is the personalisation answer's "similar to successful hires" a bias risk, and what mitigates it?

**Next →** [Case 5 — Logistics Exception Handling](05_Logistics_Exception_Handling.md)
