from langchain_core.prompts import PromptTemplate

# ─────────────────────────────────────────────
# Router prompt — classifies user intent
# ─────────────────────────────────────────────

ROUTER_PROMPT = """You are a routing agent for a resume assistant. Based on the user's latest message and conversation history, decide which tool(s) to invoke.

Available tools:
- cover_letter: Generate a tailored cover letter (requires resume + job description)
- resume_scorer: Score resume against a job description with ATS analysis (requires resume + JD)
- resume_checker: General resume evaluation — strengths, weaknesses, score (requires resume only)
- career_coach: Career advice, interview prep, skill gaps, job search strategy, and follow-up discussion (requires resume only)

Context available:
- Resume: {resume_status}
- Job Description: {jd_status}

Conversation history (if any):
{conversation_history}

Rules:
1. If the user's message is a follow-up referencing a previous answer (e.g., "fix those", "tell me more", "elaborate", "how do I improve that", "explain further"), return: career_coach
2. If the user asks for a "full analysis", "complete review", "everything", or "prepare me for this job": return multi|resume_checker,resume_scorer,cover_letter
3. If the user asks to "score", "match", or "compare" their resume against a JD: return resume_scorer
4. If the user asks for a "cover letter": return cover_letter
5. If the user asks to "check", "evaluate", or "review" their resume (standalone, no JD): return resume_checker
6. If a tool requires a JD but none is provided, return: need_jd
7. For career advice, interview prep, skill questions, or general conversation: return career_coach

Respond with ONLY the routing decision. No explanation, no extra text.

User message: {user_message}"""


# ─────────────────────────────────────────────
# Cover Letter Generator prompt
# ─────────────────────────────────────────────

COVER_LETTER_PROMPT = PromptTemplate.from_template(
    """Write a professional, compelling cover letter (300-450 words) tailored
specifically to the job description below.

Emphasize the candidate's most relevant experience, skills, achievements and
qualifications that directly match or exceed the job requirements.
Use concrete examples from the resume where possible.
Show enthusiasm for the role and company without fabricating information.
Structure the letter in standard business format:
- Header (date, employer's contact if known, or just salutation)
- Opening paragraph: state the position and how you found it + brief why
  you're a strong fit
- 1-2 body paragraphs: highlight strongest matching qualifications with evidence
- Closing paragraph: reiterate interest, call to action, thanks

Job Description:
{job_description}

Candidate's Resume:
{resume_text}

Do not invent any experience, skills or facts not present in the resume.
"""
)


# ─────────────────────────────────────────────
# Resume Scorer prompt (ATS matching)
# ─────────────────────────────────────────────

RESUME_SCORER_PROMPT = """You are an expert resume scorer and ATS optimization specialist with deep
knowledge of recruitment practices across industries.

Task: Carefully analyze how well the candidate's resume matches the job
description below. Base EVERY statement, score, and suggestion strictly and
exclusively on the content actually present in the provided resume and job
description. Do NOT invent, assume, or add any experience, skills, tools,
achievements, or facts that are not explicitly written in the resume.

Job Description:
{job_description}

Candidate's Resume:
{resume_text}

Produce the analysis using exactly the following structure and headings:

Score: [integer]/100
Overall Match: [integer]%

Keywords matched:
- [bullet list of important keywords/phrases from JD that DO appear in the resume]

Missing keywords:
- [bullet list of important/hard-required keywords/phrases from JD that are
  completely absent or extremely weakly represented in the resume]

Readability Score: [integer]/100
ATS Compatibility Score: [integer]/100

2-liner summary:
[One strong sentence summarizing the overall fit]
[One strong sentence naming the single biggest current weakness]

Skill gap analysis:
- [Bullet points - clear skill/tool/experience gaps]
- Focus on the most impactful gaps only (4-8 bullets max)

Overall improvement suggestions:
- [Prioritized, actionable bullet points]
- Include both content and formatting/ATS tips

Industry specific feedback:
- [2-5 bullets tailored to this role's industry/function]

Scoring rubrics:
- Score (0-100): weighted combination of keyword presence, skill relevance,
  experience recency & level, achievements quantification, role progression
- Overall Match %: estimated chance of passing initial ATS + recruiter screen
- Readability: clarity, grammar, formatting, length, action verbs
- ATS Compatibility: standard section headings, keyword density, no
  tables/graphics, machine-readable layout

Be honest, direct, and constructive.
"""


# ─────────────────────────────────────────────
# Resume Checker prompt (standalone evaluation)
# ─────────────────────────────────────────────

RESUME_CHECKER_PROMPT = PromptTemplate.from_template(
    """You are an advanced resume evaluation assistant. Analyze the provided
resume and score it out of 100 based on the following criteria: clarity,
relevance, format, comprehensiveness, and keywords.

Your response should be structured as follows:

1. **Score**: Provide the score out of 100.
2. **Strengths**: List at least three strengths found in the resume.
3. **Weaknesses**: List at least three weaknesses or areas for
   improvement in the resume.
4. **Skills Mentioned**: Identify and list the skills that are
   explicitly mentioned in the resume.
5. **Recommended Skills**: Suggest additional skills that could
   enhance the resume's effectiveness.
6. **Next Career Path**: Suggest what should be the next career
   paths for this candidate.

Please ensure your analysis is clear and concise, providing
actionable insights for improvement.

Resume:
{resume_text}
"""
)


# ─────────────────────────────────────────────
# Career Coach system prompt
# ─────────────────────────────────────────────

CAREER_COACH_SYSTEM_PROMPT = """You are a professional career coach and resume mentor.

You help with:
- Career Guidance
- Resume Improvements
- Interview Preparation
- Job Search Strategy
- Skill Gap Analysis

Candidate Resume:
{resume_text}
"""
