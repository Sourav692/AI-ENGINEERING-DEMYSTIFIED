

# Personalized Holiday Management Agent 

### 1. Project Introduction

**Holiday Agent** is an autonomous, multi-agent AI system designed to solve the problem of complex travel planning. Unlike standard chatbots that often "hallucinate" non-existent hotels or train schedules, Holiday Agent separates the reasoning process into distinct phases: **Planning, Researching**.

The system takes a vague user prompt (e.g., *"I want a 7-day trip to Japan focusing on anime and food"*) and orchestrates a team of specialized AI agents to build a concrete, day-by-day itinerary. It validates data in real-time ensure open hours, prices, and locations are accurate before generating the final travel guide.

**Key Features:**

* **Sequential Reasoning:** Separates high-level logic from specific fact-checking.
* **Hallucination Prevention:** The writing agent is only allowed to use facts verified by the research agent.
* **Structured Output:** Generates clean, formatted Markdown itineraries ready for export.

---

### 2. Technology Stack

The project is built on a modern Python ecosystem designed for reliability and agentic workflows.

* **Core Language:** `Python 3.10+`
* **LLM Orchestration:** `OpenAI API` (GPT-4o for complex logic, GPT-3.5-Turbo for simple tasks).
* **Data Validation:** `Pydantic` (Ensures agents output strict JSON formats for reliable parsing).
* **Environment Management:** `python-dotenv` (Security for API keys).
* **File Handling:** Standard Python `pathlib` for managing configuration and Markdown outputs.

---

### 3. System Architecture

The architecture follows a **Sequential Multi-Agent Pattern**. A central "State" object serves as the memory that is passed down a production line of agents.

#### The Workflow

The system operates in a linear pipeline:

1. **User Input:** The entry point where constraints (budget, location, dates) are defined.
2. **State Initialization:** A `State` object is created to hold the `request`, `draft_plan`, `research_data`, and `final_output`.
3. **Agent 1: The Planner (Strategy Layer):**
* *Responsibility:* Analyzes the user request and builds a "Skeleton Itinerary."
* *Focus:* Geography, pacing, and logistics. It ensures Day 1 and Day 2 are geographically close.
* *Output:* A list of generic activities (e.g., "Morning: Visit Shinjuku Gyoen").


4. **Agent 2: The Researcher (Data Layer):**
* *Responsibility:* Takes the Skeleton Itinerary and performs targeted web searches.
* *Focus:* Verification. It finds addresses, ticket prices, and operating hours.
* *Output:* A structured dictionary of validated facts.




#### Directory Mapping

* `agents/`: Contains the logic for the Planner, Researcher, and Writer.
* `teams/`: Contains the `TravelTeam` class which manages the hand-offs between agents.
* `utils/state.py`: Defines the data structure passed between the agents.

---

### 4. Future Scalability

* **Parallel Execution:** The Researcher agent can be upgraded to research multiple days simultaneously to reduce latency.
* **Tool Expansion:** Adding direct booking capabilities via APIs (e.g., Skyscanner or Booking.com).
* **PDF Export:** Adding a utility to convert the final Markdown into a stylized PDF.

---
