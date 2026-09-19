# 🎓 Personalized Education Assistant

> A sequential **CrewAI-powered** system that delivers personalized educational recommendations — curating learning materials, generating quizzes, and suggesting project ideas tailored to each user's topics of interest and expertise level.

---

## 📋 Overview

This project builds a multi-agent pipeline using [CrewAI](https://www.crewai.com/) that takes a user's topics of interest and expertise level as input, then produces:

1. **Curated Learning Materials** — videos, articles, and exercises
2. **Personalized Quizzes** — to assess understanding
3. **Project Suggestions** — hands-on ideas matched to skill level

---

## 🔑 Key Concepts

| Concept | Description |
|---|---|
| **Sequential Process** | Tasks are executed one after another in a defined order. |
| **Content Curation** | Learning materials are selected based on user-provided topics. |
| **Quiz Generation** | Quizzes are dynamically created to test comprehension. |
| **Project Suggestions** | Practical project ideas are recommended based on expertise level. |

---

## 🛠️ Custom Tool

### Project Suggestion Tool

A custom CrewAI tool that generates project ideas tailored to:
- **Expertise Level** — Beginner, Intermediate, or Advanced
- **Topics of Interest** — User-specified subjects

---

## 📦 Structured Outputs

All outputs are defined using **Pydantic models** for type safety and consistency:

- `LearningMaterial` — Structured representation of curated resources
- `Quiz` — Question sets with answers and explanations
- `ProjectIdea` — Project proposals with difficulty, description, and tech stack

---

## 🤖 Agents & Tasks

### Agents (3)

| # | Agent | Role |
|---|---|---|
| 1 | **Learning Material Agent** | Curates learning resources (videos, articles, exercises) based on the user's topics of interest. |
| 2 | **Quiz Creator Agent** | Generates personalized quizzes to evaluate understanding of the curated materials. |
| 3 | **Project Idea Agent** | Recommends practical, hands-on project ideas aligned with the user's expertise level. |

### Tasks (3)

| # | Task | Description |
|---|---|---|
| 1 | Generate Learning Materials | Search and compile relevant educational content for the given topics. |
| 2 | Create Quizzes | Build assessment questions based on the curated learning materials. |
| 3 | Suggest Project Ideas | Propose real-world projects matched to the user's skill level and interests. |

---

## 📤 Expected Outputs

| Output | Description |
|---|---|
| **Learning Materials** | Curated lists of videos, articles, and exercises tailored to the user's topics of interest. |
| **Quizzes** | Personalized quiz questions designed to assess comprehension of the learning materials. |
| **Project Suggestions** | Practical project ideas aligned with the user's expertise level (beginner → advanced). |

---

## ⚙️ Requirements

### API Keys

You will need the following API keys to run this project:

#### 1. `SERPER_API_KEY`

| | |
|---|---|
| **Purpose** | Fetches search results from Google via the [Serper API](https://serper.dev/) to find relevant learning resources. |
| **How to Obtain** | Create an account on [serper.dev](https://serper.dev/), then generate your API key from the dashboard. |

#### 2. `OPENAI_API_KEY`

| | |
|---|---|
| **Purpose** | Provides access to OpenAI models (e.g., GPT-4) for powering the AI agents. |
| **How to Obtain** | Sign up at [platform.openai.com](https://platform.openai.com/), then generate an API key from **Settings → API Keys**. |

---

## 🚀 Getting Started

```bash
# 1. Clone the repository
git clone <repo-url>

# 2. Navigate to the project directory
cd "Projects with CrewAI/02. Personalized Education Assistant"

# 3. Install dependencies
pip install crewai crewai-tools

# 4. Set your environment variables
export SERPER_API_KEY="your-serper-key"
export OPENAI_API_KEY="your-openai-key"

# 5. Run the application
python main.py
```

---

<p align="center">
  Built with ❤️ using <a href="https://www.crewai.com/">CrewAI</a>
</p>