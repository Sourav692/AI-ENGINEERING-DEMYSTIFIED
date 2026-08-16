# Resume Genie -- Tool Reference

This document describes the functionality, inputs, outputs, and implementation details of each tool in the Resume Genie suite.

All tools share the same backend stack:

- **LLM**: Llama 3.3 70B Versatile via Groq
- **PDF extraction**: PyPDFLoader (`langchain_community`)
- **Orchestration**: LangChain (`langchain_groq`, `langchain_core`)
- **Streaming**: All tools stream LLM output token-by-token in the UI

---

## 1. Cover Letter Generator

**Script**: `scripts/cover_letter_generator.py`
**Notebook**: `notebooks/Cover_Letter_Generator.ipynb`
**Dashboard tab**: "Cover Letter Generator"

### Purpose

Generates a tailored, professional cover letter by matching a candidate's resume to a specific job description.

### Inputs

| Input | Type | Required |
|-------|------|----------|
| Resume | PDF upload | Yes |
| Job Description | Text (pasted) | Yes |

### Output

A 300-450 word cover letter in standard business format:

- **Header** -- date, employer contact or salutation
- **Opening paragraph** -- position applied for, why the candidate is a strong fit
- **Body (1-2 paragraphs)** -- strongest matching qualifications backed by concrete resume evidence
- **Closing paragraph** -- reiterate interest, call to action, thanks

The output streams in real-time and can be downloaded as a `.md` file.

### Key constraints

- Never fabricates experience, skills, or facts not present in the resume
- Uses concrete examples from the resume wherever possible
- Shows enthusiasm without over-promising

### How it works

1. User uploads a PDF resume and pastes the job description
2. PyPDFLoader extracts text from the PDF via a temp file
3. Resume text + JD are injected into `COVER_LETTER_PROMPT` (a LangChain `PromptTemplate`)
4. The prompt is piped through `ChatGroq` using LCEL (`prompt | llm`)
5. Response streams token-by-token into a Streamlit `st.empty()` container
6. A download button appears after generation completes

---

## 2. Resume-JD Matcher (Resume Scorer)

**Script**: `scripts/resume_scorer.py`
**Notebook**: `notebooks/Resume_Scorer.ipynb`
**Dashboard tab**: "Resume-JD Matcher"

### Purpose

Scores how well a resume matches a specific job description, with detailed ATS optimization feedback.

### Inputs

| Input | Type | Required |
|-------|------|----------|
| Resume | PDF upload | Yes |
| Job Description | Text (pasted) | Yes |

### Output

A structured analysis with the following sections:

| Section | Description |
|---------|-------------|
| **Score** | Overall match score out of 100 |
| **Overall Match %** | Estimated chance of passing ATS + recruiter screen |
| **Keywords matched** | JD keywords/phrases found in the resume |
| **Missing keywords** | Critical JD keywords absent from the resume |
| **Readability Score** | Score out of 100 for clarity, grammar, formatting, action verbs |
| **ATS Compatibility Score** | Score out of 100 for machine-readable layout, section headings, keyword density |
| **2-liner summary** | One sentence on overall fit, one on biggest weakness |
| **Skill gap analysis** | 4-8 bullet points identifying the most impactful gaps |
| **Improvement suggestions** | Prioritized, actionable recommendations (content + formatting) |
| **Industry-specific feedback** | 2-5 bullets tailored to the role's industry/function |

### Scoring rubrics

- **Score (0-100)**: Weighted combination of keyword presence, skill relevance, experience recency and level, achievements quantification, role progression
- **Overall Match %**: Estimated chance of passing initial ATS + recruiter screen
- **Readability**: Clarity, grammar, formatting, length, action verbs, density of fluff
- **ATS Compatibility**: Standard section headings, keyword density (not stuffing), no tables/graphics, machine-readable layout

### Key constraints

- Every statement, score, and suggestion is based strictly on resume and JD content
- Never invents, assumes, or adds any experience, skills, or facts not in the resume
- Rates honestly -- if the match is very poor, it says so clearly

### How it works

1. User uploads a PDF resume and pastes the job description
2. PyPDFLoader extracts resume text
3. JD + resume text are injected into `PROMPT_TEMPLATE` using `.format()`
4. The formatted prompt is streamed through `ChatGroq`
5. Response renders in real-time via `st.empty()`
6. Handles rate limit errors with a user-friendly warning

---

## 3. Resume Checker

**Script**: `scripts/resume_checker.py`
**Notebook**: `notebooks/Resume_Checker.ipynb`
**Dashboard tab**: "Resume Checker"

### Purpose

Standalone resume evaluation -- no job description needed. Provides a general quality assessment with career path suggestions.

### Inputs

| Input | Type | Required |
|-------|------|----------|
| Resume | PDF upload | Yes |

### Output

A structured evaluation with six sections:

| Section | Description |
|---------|-------------|
| **Score** | Overall quality score out of 100 (clarity, relevance, format, comprehensiveness, keywords) |
| **Strengths** | At least three strengths identified in the resume |
| **Weaknesses** | At least three areas for improvement |
| **Skills Mentioned** | Skills explicitly listed in the resume |
| **Recommended Skills** | Additional skills that would strengthen the resume |
| **Next Career Path** | Suggested next career moves for the candidate |

### Evaluation criteria

The score is a composite of five dimensions:

- **Clarity** -- how easy the resume is to read and understand
- **Relevance** -- how well experience ties to the candidate's target field
- **Format** -- consistency of headings, bullet points, layout, scannability
- **Comprehensiveness** -- depth of education, certifications, achievements, quantified results
- **Keywords** -- presence of industry-standard terms that ATS systems scan for

### How it works

1. User uploads a PDF resume (no JD required)
2. PyPDFLoader extracts text; empty PDFs are rejected with an error
3. Resume text is injected into `EVAL_PROMPT` via a LangChain `PromptTemplate`
4. The prompt is piped through `ChatGroq` using LCEL (`prompt_template | llm`)
5. Response streams token-by-token
6. Errors display a full stack trace via `st.exception()` for debugging

---

## 4. Career Coach Chat

**Script**: `scripts/ai_career_coach.py`
**Notebook**: `notebooks/AI_Career_Coach.ipynb`
**Dashboard tab**: "Career Coach Chat"

### Purpose

An interactive chatbot grounded in the candidate's resume. Acts as a professional career coach for open-ended conversations about career development.

### Inputs

| Input | Type | Required |
|-------|------|----------|
| Resume | PDF upload | Yes |
| Chat messages | Text (typed) | Yes (ongoing) |

### Capabilities

The career coach can help with:

- **Career Guidance** -- exploring next roles, career pivots, growth paths
- **Resume Improvements** -- specific feedback on structure, content, and tailoring
- **Interview Preparation** -- behavioral questions, technical prep, case studies
- **Job Search Strategy** -- networking, LinkedIn optimization, targeting companies
- **Skill Gap Analysis** -- identifying areas to upskill, certifications to pursue

### UI layout

The interface uses a split-pane design:

- **Left column** -- displays the full extracted resume text in an expandable area
- **Right column** -- the chat interface with message history and input

### Conversation management

- **System message**: Injects the full resume text as context so every response is grounded in the candidate's actual background
- **Chat history**: Maintained in `st.session_state` as a list of `HumanMessage` / `AIMessage` objects (LangChain message types)
- **Message flow**: `[SystemMessage] + [chat_history]` is sent to the LLM on every turn
- **Persistence**: History persists within the Streamlit session; cleared on page refresh

### How it works

1. User uploads a PDF resume
2. PyPDFLoader extracts text and stores it in `st.session_state.resume_context`
3. A `SystemMessage` is constructed with the full resume as context + role instructions
4. User types a message via `st.chat_input()`
5. The message is appended to `chat_history` as a `HumanMessage`
6. `[system_message] + chat_history` is streamed through `ChatGroq`
7. Response renders token-by-token in a chat bubble
8. The AI response is appended to `chat_history` as an `AIMessage`
9. `st.rerun()` refreshes the UI to display the updated conversation

---

## Unified Dashboard

**Script**: `scripts/main_dashboard.py`

The dashboard wraps all four tools into a single Streamlit app with sidebar navigation.

### Features

- **Sidebar tool selector** -- radio buttons to switch between tools instantly
- **Shared PDF loader** -- `extract_resume_text()` is cached with `@st.cache_data` to avoid re-parsing the same PDF
- **Shared LLM instance** -- `get_llm()` is cached with `@st.cache_resource` so the `ChatGroq` client is initialized once
- **Sidebar inputs** -- for tools that need a JD (Cover Letter, Resume-JD Matcher), the JD text area and PDF uploader appear in the sidebar
- **Logo** -- displays the app logo (`assets/logo.png`) in the sidebar

### Running

```bash
# All tools via dashboard
streamlit run scripts/main_dashboard.py

# Individual tools
streamlit run scripts/cover_letter_generator.py
streamlit run scripts/resume_scorer.py
streamlit run scripts/resume_checker.py
streamlit run scripts/ai_career_coach.py
```
