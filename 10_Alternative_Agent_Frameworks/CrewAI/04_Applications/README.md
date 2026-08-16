# Projects with CrewAI

Ten project folders built with [CrewAI](https://github.com/crewAIInc/crewAI), progressing from single-crew patterns to advanced flows, conditional tasks, memory integration, custom tools, and Databricks deployment.

## Projects

| # | Project | What It Demonstrates |
|---|---------|----------------------|
| 01 | [Some Simple AI Agents](#01-some-simple-ai-agents) | Flows, DALL-E, Mem0 memory, CodeInterpreterTool, ConditionalTask, custom tools, async, hierarchical processes |
| 02 | [Personalized Education Assistant](#02-personalized-education-assistant) | Learning material curation with Pydantic structured output |
| 03 | [Multi-Agent Mock Interviewer](#03-multi-agent-mock-interviewer) | Interview prep with Streamlit UI, Whisper STT, Databricks Apps deployment |
| 04 | [Social Media Agent](#04-social-media-agent) | Platform-specific content pipelines for Twitter, LinkedIn, Instagram |
| 05 | [Research and Write Article](#05-research-and-write-article) | Sequential crew: Content Planner, Writer, Editor |
| 06 | [Customer Support Automation](#06-customer-support-automation) | Support agent with QA specialist and delegation |
| 07 | [Customer Outreach Campaign](#07-customer-outreach-campaign) | Lead profiling with DirectoryReadTool, FileReadTool, custom SentimentAnalysisTool |
| 08 | [Automate Event Planning](#08-automate-event-planning) | Venue, logistics, and marketing agents with async execution and human-in-the-loop |
| 09 | [Financial Analysis Collaboration](#09-financial-analysis-collaboration) | Multi-agent trading: Data Analyst, Strategy Developer, Trade Advisor, Risk Advisor |
| 10 | [Tailor Job Applications](#10-tailor-job-applications) | Resume tailoring with MDXSearchTool, FileReadTool, and scraping |

---

### 01. Some Simple AI Agents

Eight examples covering a broad range of CrewAI capabilities.

| Notebook | Focus |
|----------|-------|
| `1. Fitness_Progress_Tracker` | Web search with SerperDevTool for fitness plans |
| `2. Dynamic_Travel_Advisor` | CrewAI Flows — `@start`, `@listen`, `@router`, validation, state management |
| `3. Advanced_Images_Generation` | Prompt improvement + DALL-E + custom DownloadImageTool |
| `4. Personalized_Book_Recommendation` | Mem0 memory integration with `memory_config` |
| `5. Data_Analyst_Agent` | CodeInterpreterTool for Python data analysis |
| `6. Fraud_Detection` | ConditionalTask with Pydantic output and escalation logic |
| `7. Employee_Onboarding_Workflow` | Custom EmailGeneratorTool and async crews |
| `8. Automated_Document_Summarization` | Hierarchical process with FileReadTool and per-agent LLM configs |

---

### 02. Personalized Education Assistant

A crew that curates personalized learning materials, using Pydantic models for structured output formatting.

---

### 03. Multi-Agent Mock Interviewer

A full-stack interview preparation system deployed on Databricks Apps.

**Agents:** Company Research Specialist, Q&A Preparer, Answer Evaluator, Follow-up Question Specialist, New Topic Question Specialist

**Architecture:**
1. **Preparation crew** — company research then question generation (Pydantic `QuestionAnswerPair`)
2. **Evaluation crew** — evaluates the user's answer
3. **Follow-up crew** — generates follow-up or new-topic questions

| File | Purpose |
|------|---------|
| `interview_practice_system.py` | CrewAI agent and crew logic |
| `chatbot_ui.py` | Streamlit conversational UI |
| `app.yaml` | Databricks Apps configuration |
| `databricks.yml` | Databricks Asset Bundles |

**Run:**

```bash
cd "03. Building a Multi-Agent AI-Powered Mock Interviewer using CrewAI"
pip install -r requirements.txt
streamlit run chatbot_ui.py
```

**Dependencies:** `crewai[tools]>=0.114.0`, `streamlit`, `streamlit-mic-recorder`, `openai-whisper`, `pydantic`

---

### 04. Social Media Agent

Platform-specific content generation agents for Twitter, LinkedIn, and Instagram, each tailored with different content strategies and formatting rules.

---

### 05. Research and Write Article

A sequential three-agent crew: **Content Planner** researches the topic, **Writer** drafts the article, and **Editor** refines the final output.

**Dependencies:** `crewai==0.28.8`, `crewai_tools==0.1.6`, `langchain_community==0.0.29`

---

### 06. Customer Support Automation

A customer support agent paired with a QA specialist, demonstrating agent delegation for quality-assured responses.

---

### 07. Customer Outreach Campaign

Lead profiling and outreach campaign generation using DirectoryReadTool, FileReadTool, and a custom SentimentAnalysisTool. Includes instruction templates for different engagement strategies:
- Tech startups outreach
- Small business engagement
- Enterprise solutions framework

---

### 08. Automate Event Planning

Multi-agent event planning with venue search, logistics coordination, and marketing — featuring async execution and human-in-the-loop approval workflows.

---

### 09. Financial Analysis Collaboration

A multi-agent financial trading analysis workflow: **Data Analyst** collects market data, **Strategy Developer** designs trading strategies, **Trade Advisor** recommends executions, and **Risk Advisor** evaluates risk.

---

### 10. Tailor Job Applications

Automated resume tailoring using MDXSearchTool and FileReadTool to match job descriptions, with web scraping for job posting extraction.

---

## CrewAI Patterns Covered

| Pattern | Projects |
|---------|----------|
| Sequential crews | 02, 04, 05, 06, 07, 08, 09, 10 |
| CrewAI Flows (`@start`, `@listen`, `@router`) | 01 |
| ConditionalTask | 01 |
| Custom tools (`BaseTool`) | 01, 07 |
| Pydantic structured output | 01, 02, 03, 08 |
| Memory (Mem0) | 01 |
| CodeInterpreterTool | 01 |
| DALL-E image generation | 01 |
| Async execution | 01, 03, 08 |
| Human-in-the-loop | 08 |
| Agent delegation | 06, 09 |
| Hierarchical process | 01 |
| Custom LLM config per agent | 01 |
| Databricks Apps deployment | 03 |
| Web search & scraping | 01–10 |

## Technologies

| Category | Technologies |
|----------|-------------|
| **Agent Framework** | CrewAI (0.28–0.114+) |
| **LLM Providers** | OpenAI (GPT-4, GPT-4o-mini) |
| **Memory** | Mem0 |
| **Image Generation** | DALL-E |
| **Speech-to-Text** | OpenAI Whisper |
| **Web Search** | SerperDevTool, ScrapeWebsiteTool |
| **Web UI** | Streamlit |
| **Deployment** | Databricks Apps, Databricks Asset Bundles |

## Prerequisites

- Python 3.9+
- API keys: OpenAI, Serper (for web search projects)
- Create a `.env` file with your API keys

## Resources

- [Building Advanced AI Agents with CrewAI](https://courses.analyticsvidhya.com/courses/take/building-advanced-ai-agents-with-crewai/downloads/62045275-course-handouts) (Analytics Vidhya)
