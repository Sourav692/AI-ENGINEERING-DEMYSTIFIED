# Resume Genie Agent — Test Queries

A checklist of queries to verify every routing path, tool chain, and edge case.

---

## Prerequisites

Before testing, ensure:
- Resume PDF is uploaded in the sidebar
- For JD-dependent tests, paste the sample JD (see bottom of this file) in the sidebar

---

## 1. Single Tool — Resume Checker (no JD needed)

| # | Query | Expected Route | Expected Output |
|---|-------|---------------|-----------------|
| 1.1 | `Evaluate my resume` | router → resume_checker → responder | Score/100, strengths, weaknesses, skills, career paths |
| 1.2 | `Review my resume for quality` | router → resume_checker → responder | Same structured evaluation |
| 1.3 | `What are the weaknesses in my resume?` | router → resume_checker → responder | Evaluation with focus on weaknesses |

---

## 2. Single Tool — Resume Scorer (requires JD)

| # | Query | Expected Route | Expected Output |
|---|-------|---------------|-----------------|
| 2.1 | `Score my resume against this job description` | router → resume_scorer → responder | Score, match %, keywords, ATS score, skill gaps |
| 2.2 | `How well does my resume match this JD?` | router → resume_scorer → responder | Same ATS analysis |
| 2.3 | `Compare my resume to the job posting` | router → resume_scorer → responder | Same ATS analysis |

---

## 3. Single Tool — Cover Letter (requires JD)

| # | Query | Expected Route | Expected Output |
|---|-------|---------------|-----------------|
| 3.1 | `Write me a cover letter for this role` | router → cover_letter → responder | 300–450 word cover letter |
| 3.2 | `Generate a cover letter` | router → cover_letter → responder | 300–450 word cover letter |
| 3.3 | `Draft a cover letter tailored to this job` | router → cover_letter → responder | 300–450 word cover letter |

---

## 4. Single Tool — Career Coach (no JD needed)

| # | Query | Expected Route | Expected Output |
|---|-------|---------------|-----------------|
| 4.1 | `How should I prepare for a data engineering interview?` | router → career_coach → END | Interview prep advice grounded in resume |
| 4.2 | `What salary should I expect for my next role?` | router → career_coach → END | Salary guidance based on experience |
| 4.3 | `What skills should I learn next?` | router → career_coach → END | Skill recommendations based on resume |
| 4.4 | `Help me with my job search strategy` | router → career_coach → END | Job search advice |

---

## 5. Multi-Tool Chaining (requires JD)

| # | Query | Expected Route | Expected Output |
|---|-------|---------------|-----------------|
| 5.1 | `Give me a full analysis for this job` | router → resume_checker → resume_scorer → cover_letter → responder | Combined output with 3 sections separated by `---` |
| 5.2 | `Prepare me completely for this job application` | router → resume_checker → resume_scorer → cover_letter → responder | Combined output |
| 5.3 | `Do everything — check, score, and write a cover letter` | router → resume_checker → resume_scorer → cover_letter → responder | Combined output |

---

## 6. Multi-Tool Chaining Without JD

| # | Query | Expected Route | Expected Output |
|---|-------|---------------|-----------------|
| 6.1 | `Give me a full analysis` (no JD pasted) | router → resume_checker → responder | Only resume_checker runs (JD-dependent tools filtered out) |

---

## 7. Edge Cases — Missing JD

| # | Query | Condition | Expected Behavior |
|---|-------|-----------|-------------------|
| 7.1 | `Write a cover letter` | No JD in sidebar | Agent responds: "I need a job description..." |
| 7.2 | `Score my resume against the JD` | No JD in sidebar | Agent responds: "I need a job description..." |

---

## 8. Conversation Memory

| # | Step | Query | Expected Behavior |
|---|------|-------|-------------------|
| 8.1 | First | `What are my main weaknesses?` | Lists weaknesses from resume |
| 8.2 | Follow-up | `How do I fix those?` | References the weaknesses from step 8.1 |
| 8.3 | Follow-up | `Which of those is most important?` | Continues the thread from 8.1 and 8.2 |

---

## 9. Ambiguous / General Queries

| # | Query | Expected Route | Notes |
|---|-------|---------------|-------|
| 9.1 | `Hello` | router → career_coach | Should not crash, responds conversationally |
| 9.2 | `Thanks!` | router → career_coach | Polite acknowledgment |
| 9.3 | `What can you do?` | router → career_coach | Explains available capabilities |

---

## Sample Job Description (for JD-dependent tests)

Paste this in the sidebar before running tests 2.x, 3.x, 5.x:

```
What You'll Bring:

Bachelor's or higher in a quantitative field (e.g., statistics, mathematics,
computer science, engineering) with a strong academic record.
8 years or above experience in supporting clients and at least 4 years in
analytics, ideally in industries like financial services, insurance, or
digital marketing.
Proven success in end-to-end model development for at least 4 years.
Strong analytical, critical thinking, and problem-solving skills with a
proactive mindset.
Advanced programming skills and aptitude: proficiency with statistical
programs such as R or Python; experience with other programming languages
(SQL, C/C++, Java, Ab Initio) and platforms (Hive, Spark)
Capable of leading complex analytics projects with minimal supervision and
cross-functional collaboration.
Excellent project/time management; able to handle multiple initiatives in a
fast-paced environment.
Strong business acumen and communication skills; able to influence
stakeholders at all levels.
Deep understanding of industry trends and customer needs to identify business
opportunities.
Skilled in translating technical insights into actionable business
recommendations.
Occasional travel required.
```

---

## Reading the Logs

When running `streamlit run agent/app.py`, check the terminal for log output:

```
[ROUTER]    query="Evaluate my resume" → decision=resume_checker
[NODE]      resume_checker started
[NODE]      resume_checker completed (2847 chars, 3.21s)
[RESPONDER] 1 tool output(s) → final message (2847 chars)
```

For multi-tool chains:
```
[ROUTER]    query="Full analysis" → decision=multi|resume_checker,resume_scorer,cover_letter
[NODE]      resume_checker started
[NODE]      resume_checker completed (2891 chars, 3.45s)
[NODE]      resume_scorer started
[NODE]      resume_scorer completed (3102 chars, 4.12s)
[NODE]      cover_letter started
[NODE]      cover_letter completed (1856 chars, 2.89s)
[RESPONDER] 3 tool output(s) → final message (8105 chars)
```
