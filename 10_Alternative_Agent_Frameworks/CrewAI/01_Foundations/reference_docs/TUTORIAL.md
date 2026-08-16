# Building Your First AI Agent with CrewAI

This tutorial walks you through the fundamentals of CrewAI — from creating a single agent to orchestrating multi-agent crews and building conditional workflows. By the end, you will understand the three core abstractions (**Agent**, **Task**, **Crew**) and the more advanced **Flow** API.

> **Course reference:** [Building your First AI Agent with CrewAI — Analytics Vidhya](https://courses.analyticsvidhya.com/courses/take/building-your-first-ai-agent-with-crew-ai/lessons/60042706-building-a-workflow-with-crewai)

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Core Concepts — Theory Deep Dive](#2-core-concepts--theory-deep-dive)
   - [2.1 Agent](#21-agent)
   - [2.2 Task](#22-task)
   - [2.3 Crew](#23-crew)
   - [2.4 Process](#24-process)
   - [2.5 Tools](#25-tools)
   - [2.6 Memory](#26-memory)
   - [2.7 LLM](#27-llm)
   - [2.8 Flow](#28-flow)
   - [2.9 Knowledge](#29-knowledge)
3. [Example 1 — Culinary Assistant (Single Agent)](#3-example-1--culinary-assistant-single-agent)
4. [Example 2 — Marketing Research Crew (Multi-Agent with Tools)](#4-example-2--marketing-research-crew-multi-agent-with-tools)
5. [Example 3 — Logistics Analysis (Parameterized Inputs)](#5-example-3--logistics-analysis-parameterized-inputs)
6. [Example 4 — Game Session Flow (Conditional Routing)](#6-example-4--game-session-flow-conditional-routing)
7. [Key Takeaways](#7-key-takeaways)

---

## 1. Prerequisites

### Installation

```bash
pip install crewai crewai-tools python-dotenv pydantic
```

All dependencies are listed in the repository's `requirements.txt`.

### API Keys

Create a `.env` file at the repository root with the keys your LLM provider and tools require:

```
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...          # needed for Example 2 (web search)
```

Load them in your code with:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 2. Core Concepts — Theory Deep Dive

CrewAI is built around a layered architecture. The general pattern is:

```
Define Agents  →  Define Tasks  →  Assemble a Crew  →  Kick off
```

Optionally, Crews can be embedded inside **Flows** for complex, stateful pipelines with conditional routing.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Flow (orchestration layer — optional)                             │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Crew                                                        │  │
│  │  ┌───────────┐   ┌───────────┐   ┌────────────────────────┐  │  │
│  │  │  Agent 1   │──►│  Task 1   │──►│                        │  │  │
│  │  │ (+ Tools)  │   └───────────┘   │   Process              │  │  │
│  │  │ (+ Memory) │                   │  (sequential /         │  │  │
│  │  └───────────┘   ┌───────────┐   │   hierarchical)        │  │  │
│  │  ┌───────────┐──►│  Task 2   │──►│                        │  │  │
│  │  │  Agent 2   │   └───────────┘   │  ──► Final Output      │  │  │
│  │  │ (+ Tools)  │                   └────────────────────────┘  │  │
│  │  └───────────┘                                                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  @start ──► @router ──► @listen("branch_a")                        │
│                     └──► @listen("branch_b")                       │
└─────────────────────────────────────────────────────────────────────┘
```

Below is a deep dive into every component.

---

### 2.1 Agent

An **Agent** is an autonomous entity that uses an LLM to reason, make decisions, and optionally invoke tools. Think of it as a team member with a specific job title, expertise, and set of capabilities.

#### How an Agent Works Internally

1. The agent receives a task description.
2. It constructs a prompt that includes its `role`, `goal`, `backstory`, available tools, and any context from upstream tasks.
3. The LLM generates a response — which may include a decision to call a tool.
4. If a tool call is made, the agent executes the tool, receives the result, and feeds it back to the LLM for the next reasoning step.
5. This **Observe → Think → Act** loop repeats until the agent produces a final answer, or hits `max_iter`.

#### Complete Parameter Reference

```python
from crewai import Agent

agent = Agent(
    # ── Identity (required) ──────────────────────────────────
    role="Senior Data Scientist",
    goal="Analyze and interpret complex datasets to provide actionable insights",
    backstory="With over 10 years of experience in data science and machine learning, "
              "you excel at finding patterns in complex datasets.",

    # ── LLM Configuration ────────────────────────────────────
    llm="gpt-4",                    # Model name string or LLM() instance
    function_calling_llm=None,      # Separate LLM just for tool-calling decisions

    # ── Behavioral Controls ──────────────────────────────────
    verbose=False,                  # Print internal reasoning to stdout
    allow_delegation=False,         # Can this agent delegate work to other agents?
    max_iter=20,                    # Max reasoning loop iterations
    max_rpm=None,                   # Rate limit: max requests per minute to the LLM
    max_execution_time=None,        # Hard timeout in seconds
    max_retry_limit=2,              # Retries on error before failing

    # ── Code Execution ───────────────────────────────────────
    allow_code_execution=False,     # Let the agent write and run code
    code_execution_mode="safe",     # "safe" (sandboxed) or "unsafe"

    # ── Prompt Engineering ───────────────────────────────────
    respect_context_window=True,    # Auto-truncate when context exceeds window
    use_system_prompt=True,         # Inject role/goal/backstory as system message
    system_template=None,           # Custom Jinja2 system prompt template
    prompt_template=None,           # Custom Jinja2 user prompt template
    response_template=None,         # Custom Jinja2 response template

    # ── Advanced Capabilities ────────────────────────────────
    multimodal=False,               # Process images alongside text
    reasoning=False,                # Enable chain-of-thought reasoning mode
    max_reasoning_attempts=None,    # Limit reasoning iterations
    inject_date=False,              # Inject today's date into the prompt
    date_format="%Y-%m-%d",         # Format for injected date

    # ── Tools & Knowledge ────────────────────────────────────
    tools=[],                       # List of Tool instances the agent can use
    knowledge_sources=None,         # RAG knowledge sources for the agent
    embedder=None,                  # Custom embedder config for knowledge retrieval

    # ── Callbacks ────────────────────────────────────────────
    step_callback=None,             # Called after each reasoning step
)
```

#### The Three Identity Pillars

| Parameter | What it does | Tips for writing it |
|---|---|---|
| **`role`** | Short job title — frames the agent's identity in every prompt. | Be specific: "API Documentation Specialist" beats "Writer". |
| **`goal`** | The high-level objective the agent strives toward. | State the *outcome*, not the process: "Create comprehensive API docs" not "Read code and write docs". |
| **`backstory`** | Narrative context that shapes the agent's reasoning style. | Include years of experience, domain expertise, and working style. The richer this is, the more nuanced the LLM's behavior. |

#### Delegation

When `allow_delegation=True`, an agent can decide on its own to pass part of its work to another agent in the same crew. This is useful in hierarchical setups where a manager agent orchestrates specialists. Set it to `False` when you want strict task ownership.

---

### 2.2 Task

A **Task** is a discrete unit of work assigned to an Agent. It describes *what* needs to be done and *what the output should look like*.

#### Complete Parameter Reference

```python
from crewai import Task

task = Task(
    # ── Core (required) ──────────────────────────────────────
    description="Analyze Q4 sales data and identify trends",
    expected_output="A report with top 3 trends and supporting data points",
    agent=analyst_agent,

    # ── Task Chaining ────────────────────────────────────────
    context=[upstream_task],        # List of Tasks whose outputs are injected as context

    # ── Tools ────────────────────────────────────────────────
    tools=[],                       # Task-specific tools (supplements agent's tools)

    # ── Structured Output ────────────────────────────────────
    output_json=None,               # Pydantic model — forces JSON output matching this schema
    output_pydantic=None,           # Pydantic model — returns a validated Pydantic object
    output_file=None,               # File path — writes output to disk

    # ── Execution Modes ──────────────────────────────────────
    async_execution=False,          # Run this task asynchronously
    human_input=False,              # Pause and ask a human for input before completing

    # ── Quality Controls ─────────────────────────────────────
    guardrail=None,                 # Validation function: (TaskOutput) -> (bool, Any)
    guardrail_max_retries=3,        # Max retries if guardrail validation fails

    # ── Callbacks ────────────────────────────────────────────
    callback=None,                  # Called when the task completes
)
```

#### Key Concepts

**Context Chaining** — The `context` parameter creates an explicit data-flow edge between tasks. When Task B lists Task A in its context, the full output of Task A is injected into Task B's prompt. This is how agents "build on" each other's work.

```python
research_task = Task(description="Research topic X", ...)
writing_task  = Task(description="Write article based on research", ..., context=[research_task])
```

**Structured Output** — By passing a Pydantic model to `output_json` or `output_pydantic`, you force the agent to produce machine-parseable output:

```python
from pydantic import BaseModel

class Report(BaseModel):
    title: str
    summary: str
    findings: list[str]

task = Task(
    description="Generate analysis report",
    expected_output="A structured report",
    agent=analyst,
    output_pydantic=Report,
)
```

**Guardrails** — A guardrail is a validation function that checks the task's output. If it returns `(False, error_message)`, CrewAI automatically retries the task (up to `guardrail_max_retries` times) with the error fed back to the agent.

```python
def validate_json(result):
    try:
        data = json.loads(result)
        return (True, data)
    except json.JSONDecodeError:
        return (False, "Invalid JSON — please fix the format")

task = Task(..., guardrail=validate_json, guardrail_max_retries=3)
```

**Human-in-the-Loop** — Setting `human_input=True` pauses execution and asks for human review before the task is marked complete.

---

### 2.3 Crew

A **Crew** is a team of agents working together on a set of tasks. It controls *how* tasks are assigned and executed.

#### Complete Parameter Reference

```python
from crewai import Crew, Process

crew = Crew(
    # ── Core (required) ──────────────────────────────────────
    agents=[agent1, agent2],
    tasks=[task1, task2],

    # ── Execution ────────────────────────────────────────────
    process=Process.sequential,     # or Process.hierarchical
    verbose=True,                   # Print execution details

    # ── Planning ─────────────────────────────────────────────
    planning=True,                  # LLM generates a plan before execution
    planning_llm=None,              # Separate LLM for the planning step

    # ── Memory ───────────────────────────────────────────────
    memory=True,                    # Enable short-term, long-term, entity, contextual memory
    embedder=None,                  # Custom embedder for memory retrieval

    # ── Hierarchical Process ─────────────────────────────────
    manager_llm=None,               # LLM for the auto-created manager agent
    manager_agent=None,             # Custom manager Agent instance

    # ── Performance ──────────────────────────────────────────
    cache=True,                     # Cache tool results
    max_rpm=None,                   # Global rate limit across all agents

    # ── Output ───────────────────────────────────────────────
    output_log_file=None,           # File path for execution logs
    stream=False,                   # Stream output chunks in real time
)
```

#### Execution Methods

| Method | Description |
|---|---|
| `crew.kickoff(inputs={})` | Run the crew once with optional variable substitution. |
| `crew.kickoff_for_each(inputs=[{}, {}])` | Run the same crew for a list of different inputs (batch mode). |
| `await crew.akickoff(inputs={})` | Async version of `kickoff`. |

#### Output Properties

After `kickoff()` returns, the result object provides:

| Property | What it contains |
|---|---|
| `result.raw` | The raw text output from the final task. |
| `result.tasks_output` | A list of individual task outputs. |
| `result.token_usage` | Token consumption across all LLM calls. |
| `crew.usage_metrics` | Aggregated metrics: total tokens, prompt tokens, completion tokens, request count. |

---

### 2.4 Process

A **Process** defines the execution strategy for tasks within a crew.

#### Sequential Process

```python
crew = Crew(agents=..., tasks=..., process=Process.sequential)
```

Tasks run **one after another** in the order they appear in the `tasks` list. Each task's output is available as context for the next. This is the default and most common mode.

```
Task 1 ──► Task 2 ──► Task 3 ──► Final Output
```

**When to use:** Most workflows where there is a natural ordering — research before writing, analysis before strategy.

#### Hierarchical Process

```python
crew = Crew(
    agents=...,
    tasks=...,
    process=Process.hierarchical,
    manager_llm="gpt-4o",  # required
)
```

A **manager agent** is automatically created (or you provide one via `manager_agent`). The manager reads all task descriptions and **delegates** each task to the most appropriate agent. It also validates results before moving on.

```
              Manager Agent
             /      |      \
        Agent 1  Agent 2  Agent 3
         Task A   Task B   Task C
```

**When to use:** Complex workflows where task assignment should be dynamic, or when agents have overlapping capabilities and you want intelligent delegation.

---

### 2.5 Tools

**Tools** extend what agents can do beyond pure LLM reasoning. They let agents interact with the real world — searching the web, reading files, querying databases, calling APIs.

#### How Tools Work

1. The agent's prompt includes a description of each available tool.
2. During reasoning, the LLM decides whether to call a tool and formulates the arguments.
3. CrewAI executes the tool and feeds the result back into the conversation.
4. The agent uses the tool output to continue reasoning toward a final answer.

#### Built-in Tools (from `crewai-tools`)

| Tool | What it does |
|---|---|
| `SerperDevTool` | Google search via Serper API |
| `WebsiteSearchTool` | Search within a specific website (RAG-based) |
| `FileReadTool` | Read file contents |
| `DirectoryReadTool` | List and read directory contents |
| `PDFSearchTool` | Search inside PDF documents |
| `CSVSearchTool` | Search inside CSV files |
| `ScrapeWebsiteTool` | Scrape and extract webpage content |
| `WikipediaTools` | Search Wikipedia |

#### Creating Custom Tools

There are two ways to create your own tools:

**Method 1 — Subclass `BaseTool`** (full control):

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    city: str = Field(..., description="City name to get weather for")

class WeatherTool(BaseTool):
    name: str = "weather_lookup"
    description: str = "Gets current weather for a given city"
    args_schema: type[BaseModel] = WeatherInput

    def _run(self, city: str) -> str:
        # Your API call logic here
        return f"Weather in {city}: 72°F, Sunny"
```

**Method 2 — `@tool` decorator** (quick and simple):

```python
from crewai import tool

@tool("Weather Lookup")
def weather_lookup(city: str) -> str:
    """Gets current weather for a given city."""
    return f"Weather in {city}: 72°F, Sunny"
```

#### Tool Assignment

Tools can be assigned at two levels:

- **Agent-level:** Available for all tasks the agent handles.
- **Task-level:** Available only during that specific task (supplements agent tools).

```python
agent = Agent(role="Researcher", tools=[search_tool])            # agent-level
task  = Task(description="...", agent=agent, tools=[csv_tool])   # task-level (adds to agent's tools)
```

---

### 2.6 Memory

**Memory** gives agents the ability to remember and learn across tasks and sessions. Without memory, every task starts from scratch. With memory, agents can build on prior context, avoid repeating mistakes, and improve over time.

#### Memory Types

CrewAI provides a **unified memory system** that combines four underlying types:

| Type | Storage | Scope | Purpose |
|---|---|---|---|
| **Short-Term** | ChromaDB + RAG | Current execution | Holds recent interactions and intermediate results for immediate context. |
| **Long-Term** | SQLite | Across sessions | Persists learned patterns and insights that survive between runs. |
| **Entity** | RAG | Current execution | Tracks specific entities (people, companies, concepts) and their attributes. |
| **Contextual** | Composite | Current execution | Integrates all memory types into a coherent context for each agent prompt. |

#### Enabling Memory

The simplest way to enable all memory types:

```python
crew = Crew(agents=..., tasks=..., memory=True)
```

For fine-grained control:

```python
from crewai import Memory

custom_memory = Memory(
    recency_weight=0.4,          # How much to favor recent memories
    semantic_weight=0.4,         # How much to favor semantically similar memories
    importance_weight=0.2,       # How much to favor high-importance memories
    recency_half_life_days=14,   # Decay rate for recency scoring
)

crew = Crew(agents=..., tasks=..., memory=custom_memory)
```

#### How Memory Retrieval Works

When an agent needs context, CrewAI scores each memory using a **composite scoring** formula:

```
score = (recency_weight × recency_score)
      + (semantic_weight × similarity_score)
      + (importance_weight × importance_score)
```

The top-scoring memories are injected into the agent's prompt alongside the task description.

---

### 2.7 LLM

The **LLM** wrapper provides a unified interface to any language model provider.

```python
from crewai import LLM

llm = LLM(
    model="gpt-4o",           # Provider/model string
    temperature=0.7,           # Creativity vs determinism (0.0–1.0)
    max_tokens=4000,           # Maximum output length
)
```

#### Supported Providers

CrewAI uses LiteLLM under the hood, which means you can use any of these providers by changing the model string:

| Provider | Model String Example |
|---|---|
| OpenAI | `"gpt-4"`, `"gpt-4o"`, `"gpt-4o-mini"` |
| Anthropic | `"claude-3-5-sonnet"`, `"claude-3-haiku"` |
| Google | `"gemini/gemini-pro"` |
| Groq | `"groq/llama3-70b-8192"` |
| Ollama (local) | `"ollama/llama3"` |
| Azure OpenAI | `"azure/gpt-4"` |

You can assign LLMs at multiple levels:

- **Agent-level:** `Agent(llm=...)` — the LLM this agent uses for all reasoning.
- **`function_calling_llm`:** A separate LLM optimized for tool-calling decisions.
- **`planning_llm`:** The LLM used by the Crew for generating execution plans.
- **`manager_llm`:** The LLM for the hierarchical process manager.

---

### 2.8 Flow

A **Flow** is a state machine that orchestrates complex pipelines with conditional branching, event-driven execution, and typed state. While a Crew handles linear or hierarchical task execution, a Flow handles *when* and *whether* to run things.

#### Core Decorators

| Decorator | Signature | Purpose |
|---|---|---|
| `@start()` | `def method(self)` | Entry point — runs first when `flow.kickoff()` is called. |
| `@listen(event)` | `def method(self)` | Runs when the specified event is emitted. The event can be a method reference or a string. |
| `@router(method)` | `def method(self) -> str` | Runs after the referenced method. Returns a string that routes execution to the matching `@listen`. |

#### Combinators: `and_` and `or_`

| Combinator | Behavior |
|---|---|
| `and_(method_a, method_b)` | The listener fires only after **both** methods have completed. |
| `or_(method_a, method_b)` | The listener fires when **either** method completes. |

```python
from crewai.flow.flow import Flow, listen, start, and_

class PipelineFlow(Flow):
    @start()
    def fetch_data(self):
        self.state["data"] = "raw data"

    @listen(fetch_data)
    def validate_data(self):
        self.state["valid"] = True

    @listen(and_(fetch_data, validate_data))
    def process_data(self):
        print("Both fetch and validate are done — processing now")
```

#### State Management

Flows support two state models:

**Structured State (recommended)** — Define a Pydantic model for type-safe access:

```python
from pydantic import BaseModel

class PipelineState(BaseModel):
    input_text: str = ""
    analysis: str = ""
    score: float = 0.0

class MyFlow(Flow[PipelineState]):
    @start()
    def begin(self):
        self.state.input_text = "Hello world"   # type-checked attribute access
```

**Unstructured State** — Use a plain dictionary for quick prototyping:

```python
class MyFlow(Flow):
    @start()
    def begin(self):
        self.state["input_text"] = "Hello world"  # dictionary access
```

#### Embedding Crews Inside Flows

The real power of Flows is running full Crew executions inside flow methods:

```python
class ResearchFlow(Flow[ResearchState]):
    @start()
    def gather_input(self):
        self.state.topic = "AI in healthcare"

    @listen(gather_input)
    def run_research_crew(self):
        crew = Crew(agents=[researcher, writer], tasks=[research_task, write_task])
        result = crew.kickoff(inputs={"topic": self.state.topic})
        self.state.report = result.raw

    @router(run_research_crew)
    def check_quality(self):
        return "publish" if len(self.state.report) > 500 else "revise"

    @listen("publish")
    def publish_report(self):
        print("Publishing report...")

    @listen("revise")
    def revise_report(self):
        print("Report too short — revising...")
```

---

### 2.9 Knowledge

**Knowledge Sources** allow agents to access domain-specific information via RAG (Retrieval-Augmented Generation) without requiring tool calls. The knowledge is embedded and retrieved automatically when relevant to the task.

```python
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

product_knowledge = StringKnowledgeSource(
    content="Our product supports SSO via SAML 2.0 and OAuth 2.0. "
            "Pricing starts at $49/month for teams up to 10 users."
)

support_agent = Agent(
    role="Customer Support Specialist",
    goal="Answer customer questions accurately",
    backstory="Expert in company products and policies",
    knowledge_sources=[product_knowledge],
    embedder={
        "provider": "openai",
        "config": {"model": "text-embedding-3-small"}
    },
)
```

Knowledge sources can be strings, files, directories, or custom sources. They are embedded once and queried automatically during task execution.

---

## 3. Example 1 — Culinary Assistant (Single Agent)

**File:** `1. Stateful_Applications_with_CrewAI.py`

This is the simplest possible crew: one agent, two chained tasks, and built-in planning.

### 3.1 Define the LLM

```python
from crewai import Agent, Task, Crew, LLM

llm = LLM(model="gpt-4")
```

CrewAI's `LLM` wrapper lets you swap providers (OpenAI, Anthropic, Groq, etc.) by changing the `model` string.

### 3.2 Create the Agent

```python
main_ingredient = "tomato"
dietary_restrictions = "shrimps"

culinary_assistant = Agent(
    llm=llm,
    role="Culinary Assistant",
    backstory=(
        "An experienced culinary assistant skilled in finding and tailoring "
        "recipes based on ingredients and dietary needs, and providing clear, "
        "step-by-step cooking instructions"
    ),
    goal="Find recipes, filter them to meet dietary preferences, and guide user through recipe steps.",
    verbose=True,
)
```

**Key parameters:**

| Parameter | Purpose |
|---|---|
| `role` | A short title the agent uses to frame its identity. |
| `backstory` | Gives the agent context about its expertise — this shapes how the LLM reasons. |
| `goal` | The agent's overarching objective. |
| `verbose` | When `True`, prints the agent's internal reasoning to stdout. |

### 3.3 Define Tasks

```python
find_and_filter_recipes = Task(
    description=f"Find recipes that use the ingredient: {main_ingredient} and"
                f" filter them to meet dietary restrictions: {dietary_restrictions}.",
    expected_output=f"One recipe using {main_ingredient} and matching {dietary_restrictions} restrictions.",
    agent=culinary_assistant,
)

guide_recipe_steps = Task(
    description="Provide step-by-step instructions for the selected recipe.",
    expected_output="Step-by-step cooking instructions for the chosen recipe.",
    agent=culinary_assistant,
    context=[find_and_filter_recipes],  # chains the output of the first task as input
)
```

**The `context` parameter** is how you wire tasks together. The output of `find_and_filter_recipes` is automatically injected into the prompt for `guide_recipe_steps`, so the second task can reference the recipe found by the first.

### 3.4 Assemble and Run the Crew

```python
crew = Crew(
    agents=[culinary_assistant],
    tasks=[find_and_filter_recipes, guide_recipe_steps],
    planning=True,
)

crew.kickoff()
```

Setting `planning=True` tells CrewAI to generate an execution plan before running tasks. The LLM creates a step-by-step plan for each task, which improves output quality and coherence.

---

## 4. Example 2 — Marketing Research Crew (Multi-Agent with Tools)

**File:** `2. Research Assistant in CrewAI.py`

This example demonstrates **multiple agents collaborating** and using **external tools** to gather real-time information.

### 4.1 Two Specialized Agents

```python
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

product_name = "energy drink"

market_researcher = Agent(
    role="Market Researcher",
    goal="Analyze market trends for the product launch",
    backstory="Experienced in market trends and consumer behavior analysis",
    tools=[SerperDevTool()],   # can search the web via Serper API
    verbose=True,
)

strategist = Agent(
    role="Product Strategist",
    goal="Create effective positioning strategies for the product",
    backstory="Skilled in competitive positioning and marketing strategy",
    verbose=True,
)
```

**Tools** are the mechanism by which agents interact with the outside world. `SerperDevTool` wraps the Serper API to perform Google searches. An agent decides autonomously *when* and *how* to use its tools.

### 4.2 Tasks with Sequential Dependency

```python
gather_market_insights_task = Task(
    description=f"Browse the internet to gather insights on current market trends "
                f"for the launch of the {product_name} product.",
    expected_output=f"List of relevant market trends and consumer preferences, relevant to {product_name}",
    agent=market_researcher,
)

develop_positioning_strategy_task = Task(
    description=f"Based on the market insights, create a positioning strategy for "
                f"the {product_name} product, including analysis for impact and target audience.",
    expected_output="A positioning strategy with target audience and impact notes",
    agent=strategist,
)
```

Because tasks run sequentially by default, the strategist automatically receives the researcher's findings as context.

### 4.3 Run the Crew

```python
crew = Crew(
    agents=[market_researcher, strategist],
    tasks=[gather_market_insights_task, develop_positioning_strategy_task],
    planning=True,
)

crew.kickoff()
```

The execution flow is:

```
Market Researcher (uses SerperDevTool to search the web)
        │
        ▼  output becomes context
Product Strategist (crafts positioning strategy)
```

---

## 5. Example 3 — Logistics Analysis (Parameterized Inputs)

**File:** `5. Logistic_Analysis.ipynb`

This example introduces **parameterized tasks** and the `Process.sequential` execution mode, making crews reusable across different inputs.

### 5.1 Agents

```python
from crewai import Agent, Task, Crew, Process

logistics_analyst = Agent(
    role='Logistics Analyst',
    goal='Research and analyze the current state of logistics operations for {products}',
    backstory="""You are an expert in supply chain analytics with 10 years of experience. 
    Your strength lies in identifying bottlenecks in route efficiency and 
    detecting patterns in inventory turnover. You provide data-driven insights 
    that form the foundation of strategic decisions.""",
    allow_delegation=False,
)

optimization_strategist = Agent(
    role='Optimization Strategist',
    goal='Develop a comprehensive optimization strategy for {products} based on analyst insights',
    backstory="""You are a veteran operations researcher. You specialize in 
    taking complex logistics data and turning it into actionable, high-efficiency 
    strategies. You excel at cost reduction and streamlining delivery workflows.""",
    allow_delegation=False,
)
```

Notice the `{products}` placeholder in both `goal` strings. CrewAI replaces these at runtime with actual values.

Setting `allow_delegation=False` prevents agents from passing their work to another agent in the crew.

### 5.2 Parameterized Tasks

```python
analysis_task = Task(
    description="""Conduct a detailed research into the current logistics operations 
    for the following products: {products}. 
    Focus specifically on current route efficiency and inventory turnover trends. 
    Identify at least three key areas where performance is lagging.""",
    expected_output="A detailed report on the current logistics state and bottlenecks.",
    agent=logistics_analyst,
)

strategy_task = Task(
    description="""Review the logistics analysis provided for {products}. 
    Develop a step-by-step optimization strategy to improve delivery speed 
    and reduce inventory costs. Your strategy must be practical and data-backed.""",
    expected_output="A comprehensive optimization roadmap with specific recommendations.",
    agent=optimization_strategist,
    context=[analysis_task],
)
```

The `context` parameter on `strategy_task` explicitly passes the analyst's output to the strategist — a pattern you've seen before, but here combined with parameterization.

### 5.3 Execute with Dynamic Inputs

```python
logistics_crew = Crew(
    agents=[logistics_analyst, optimization_strategist],
    tasks=[analysis_task, strategy_task],
    process=Process.sequential,
    verbose=True,
)

product_list = "Pharmaceutical supplies, cold-chain vaccines, and medical PPE"
result = logistics_crew.kickoff(inputs={'products': product_list})

print(result)
```

**`kickoff(inputs={...})`** replaces every `{products}` placeholder across all agent goals, task descriptions, and expected outputs with the provided value. This makes the same crew definition reusable for any product category.

---

## 6. Example 4 — Game Session Flow (Conditional Routing)

**File:** `4. Workflow_with_CrewAI.py`

CrewAI's **Flow** API goes beyond linear task execution. It provides a state machine with decorators for start points, routers, and event listeners.

### 6.1 Define Typed State

```python
import random
from crewai.flow.flow import Flow, listen, router, start
from pydantic import BaseModel


class GameSession(BaseModel):
    player_won: bool = False
```

A `BaseModel` subclass acts as the typed, shared state for the entire flow. Every method in the flow can read and write `self.state`.

### 6.2 Build the Flow

```python
class GameFlow(Flow[GameSession]):

    @start()
    def begin_start(self):
        print("Starting the game session")
        player_outcome = random.choice([True, False])
        self.state.player_won = player_outcome

    @router(begin_start)
    def check_outcome(self):
        if self.state.player_won:
            return "win"
        else:
            return "lose"

    @listen("win")
    def celebrate_win(self):
        print("Congratulations!")

    @listen("lose")
    def console_loss(self):
        print("Game Over!")
```

### 6.3 Decorators Explained

| Decorator | Purpose |
|---|---|
| `@start()` | Marks the entry point of the flow. Runs first when `kickoff()` is called. |
| `@router(method)` | Runs after the referenced method. Returns a string that determines which `@listen` branch executes next. |
| `@listen("event")` | Runs when the router (or another method) emits the matching event string. |

### 6.4 Execution

```python
flow = GameFlow()
flow.kickoff()
```

The execution graph looks like this:

```
begin_start  ──►  check_outcome
                      │
              ┌───────┴───────┐
              ▼               ▼
        "win" branch    "lose" branch
       celebrate_win    console_loss
```

The Flow API is useful when you need branching logic, loops, or complex orchestration that goes beyond a linear task list. In production, you can embed full Crew executions inside flow methods for sophisticated multi-agent pipelines.

---

## 7. Key Takeaways

| Concept | When to use it |
|---|---|
| **Single Agent + Tasks** | Simple, focused workflows where one persona handles everything (Example 1). |
| **Multi-Agent Crew** | Problems requiring distinct expertise — each agent brings specialized knowledge and tools (Example 2). |
| **Parameterized Inputs** | Reusable crew templates that work across different domains or datasets (Example 3). |
| **Flow with Router** | Complex pipelines with conditional branching, loops, or typed state management (Example 4). |
| **`context` on Tasks** | Chain task outputs so downstream tasks can reference upstream results. |
| **`planning=True`** | Have the LLM generate a plan before execution — improves quality for complex tasks. |
| **Tools** | Give agents the ability to interact with external services (search, APIs, databases, file systems). |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                      Flow (optional)                │
│  @start ──► @router ──► @listen("branch_a")         │
│                     └──► @listen("branch_b")        │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │                    Crew                       │  │
│  │                                               │  │
│  │  Agent 1 ──► Task 1 ──┐                       │  │
│  │  (+ Tools)            │ context               │  │
│  │                       ▼                       │  │
│  │  Agent 2 ──► Task 2 ──► Final Output          │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Running the Examples

```bash
# Example 1 — Culinary Assistant
python "01. Building your First AI Agent with CrewAI/1. Stateful_Applications_with_CrewAI.py"

# Example 2 — Marketing Research (requires SERPER_API_KEY)
python "01. Building your First AI Agent with CrewAI/2. Research Assistant in CrewAI.py"

# Example 3 — Logistics Analysis
jupyter notebook "01. Building your First AI Agent with CrewAI/5. Logistic_Analysis.ipynb"

# Example 4 — Game Session Flow
python "01. Building your First AI Agent with CrewAI/4. Workflow_with_CrewAI.py"
```

Make sure your `.env` file is configured before running any example.
