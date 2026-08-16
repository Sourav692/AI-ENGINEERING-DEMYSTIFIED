# Test Questions for Deep Agent

A curated set of prompts to exercise each subagent, skill, and multi-agent delegation pattern.

---

## 1. Research Agent (Tavily)

**Subagent:** `research-agent` | **Tool:** `internet_search`

### Current Events / News

- "What are the latest developments in AI regulation in the EU in 2026?"
- "What happened at the most recent Apple WWDC keynote?"

### Technical Research

- "What are the best Python libraries for building real-time websocket servers in 2026? Compare their pros and cons."
- "Research the current state of LangGraph vs CrewAI vs AutoGen for multi-agent orchestration."

### Finance

- "What is the current market cap of NVIDIA and how has the stock performed this quarter?"

### Fact-checking / Background

- "Is Python 3.13 stable yet? What are its key new features?"
- "What are the breaking changes in Pydantic v3?"

---

## 2. Senior Developer + Code Reviewer

**Subagents:** `senior-developer`, `code-reviewer` | **Tools:** `name_project`, filesystem

- "Build a Python CLI tool that converts CSV files to JSON."
- "Write a URL shortener API using FastAPI with an in-memory store."
- "Create a Python script that validates email addresses using regex and outputs a report."

---

## 3. AIA Genie Spaces (Single Domain)

### Customer Analytics

**Subagent:** `aia-customer-analytics` | **Tool:** `ask_customer_analytics`

- "Which customer segments have the highest claim frequency?"
- "How many customers are there by region?"
- "What is the distribution of customers by gender?"

### Distribution Channels

**Subagent:** `aia-distribution-channels` | **Tool:** `ask_distribution_channels`

- "Who are the top agents by premium sold?"
- "How do distribution channels compare in policy count?"
- "What is the average premium per agent by region?"

### Policy Underwriting

**Subagent:** `aia-policy-underwriting` | **Tool:** `ask_policy_underwriting`

- "What is the total premium by distribution channel?"
- "What are the renewal rates by product type?"
- "How many policies are active vs lapsed?"

### Claims Analytics

**Subagent:** `aia-claims-analytics` | **Tool:** `ask_claims_analytics`

- "Which regions have the highest fraud scores?"
- "What is the total number of claims by region?"
- "What is the average claim processing time?"

---

## 4. Cross-Domain AIA Analytics (Multiple Genie Subagents)

These questions require the main agent to delegate to 2-4 AIA subagents and synthesize the results.

- "Which customer segments have the highest fraud scores, and how does that correlate with their distribution channel?" → `aia-customer-analytics` + `aia-claims-analytics` + `aia-distribution-channels`

- "Compare the top 5 agents by premium sold with the claim amounts in their regions. Are high-selling agents also in high-claim regions?" → `aia-distribution-channels` + `aia-claims-analytics`

- "What is the renewal rate by customer segment, and which segments file the most claims?" → `aia-policy-underwriting` + `aia-customer-analytics` + `aia-claims-analytics`

- "Give me a full business health dashboard: total customers, active policies, total premiums, claim volume, and top performing agents." → All 4 AIA subagents

---

## 5. Research + AIA Analytics (Genie + Tavily)

These questions combine internal data analysis with external web research.

- "How do AIA's fraud scores compare to industry benchmarks? First check our fraud data, then research insurance industry average fraud rates." → `aia-claims-analytics` + `research-agent`

- "What are the best practices for improving policy renewal rates? First show me our current renewal rates by product, then research industry strategies." → `aia-policy-underwriting` + `research-agent`

---

## 6. Analytics + Code (Genie + Developer + Reviewer)

These questions pull data from Genie spaces and then build code artifacts from the results.

- "Pull the customer segment distribution and claim frequency from our data, then build a Python script that generates a matplotlib dashboard visualizing those metrics." → `aia-customer-analytics` + `aia-claims-analytics` + `senior-developer` + `code-reviewer`

- "Get fraud scores by region from our claims data, then write a Python anomaly detection script that flags regions with scores above 2 standard deviations." → `aia-claims-analytics` + `senior-developer` + `code-reviewer`

---

## 7. Combined Research + Code (Tavily + Developer)

- "Research the best approach for building a CLI weather app in Python, then build it." → `research-agent` + `senior-developer` + `code-reviewer`

---

## 8. Long-Term Memory (Cross-Thread Persistence)

> Run these with `python long_term_memory_agent.py`. Use `new` to start a fresh thread between prompts.

**Subagent:** `memory-manager` | **Tools:** `save_memory`, `recall_memories`, `forget_memory`

### Saving Memories

- "Remember that my name is Alice and I work on the analytics team."
- "Remember I prefer concise answers with code examples."
- "Remember that we decided to use FastAPI for the new API layer."
- "Remember the project deadline is March 15, 2026."

### Recalling Across Threads

> Type `new` to start a new thread, then:

- "What do you know about me?"
- "What preferences have I shared with you?"
- "What decisions have we made about the project?"

### Forgetting

- "Forget my name."
- "Forget the project deadline."

### Memory + Other Subagents

These combine long-term memory with other capabilities:

- "Remember I prefer matplotlib over plotly. Now build me a Python script that visualizes sales data." → `memory-manager` + `senior-developer`

- "Recall what you know about my project, then research best practices for the tech stack we chose." → `memory-manager` + `research-agent`

- "Remember that the Bangkok region is our focus area. Now show me claims data for that region." → `memory-manager` + `aia-claims-analytics`

### Multi-Turn Memory Scenario

> Complete sequence across threads:

1. "Remember my name is Alice, I'm on the data engineering team, and I prefer Python with type hints."
2. Type `new`
3. "What do you remember about me? Use my preferences to build a CSV-to-Parquet converter."
4. Type `new`
5. "Based on what you know about me, research the best data pipeline tools for my team's needs."

---

## 9. Ultimate Multi-Skill (All Subagents)

> "~~Build me an executive summary report: pull total customers by segment, total premiums by channel, top 10 agents, and fraud hotspots from our data. Then research how AIA compares to competitors in the Thai insurance market. Finally, write a Python script that generates this as a formatted PDF report."~~

*> *\
> Build me a fraud risk report: pull our top customer segments by size, top 5 agents by premium volume, and the regions with highest fraud activity from our data. Then research current insurance fraud detection best*

→ All 4 AIA + `research-agent` + `senior-developer` + `code-reviewer`