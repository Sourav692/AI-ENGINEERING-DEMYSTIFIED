# Module 09 · AI System Design Casebook

> **Level** 🔴 Design Mastery · **Docs** 6 + 4 whiteboard scripts · **Time** ~3 h reading + rehearsal
> **Prerequisites:** Module 02 (the framework and the 60-minute method); Levels 2–3 for the depth behind each case

Five worked AI system designs, a map that shows what two of them cover between them and what neither does, and four complete 60-minute whiteboard scripts for the three platform projects in this handbook plus the Databricks variant. The cases teach you to *recognise* the shape of a prompt; the scripts teach you to *perform* the answer against the clock.

## Reading order

| # | Doc | The prompt | What it exercises | Time |
|---|---|---|---|---|
| 1 | [Enterprise AI Assistant](01_Enterprise_AI_Assistant.md) | An assistant over 100+ internal applications | REST vs function calling vs MCP vs agent frameworks as *layers*; the tool registry at scale; identity propagation | 30 min |
| 2 | [Customer Support Assistant](02_Customer_Support_Assistant.md) | Einstein + Zendesk + agents; 1M conversations/day | RAG vs tool calling; MCP; when a planner is justified; three memory layers; human approval; model routing | 30 min |
| 3 | [Coding Assistant](03_Coding_Assistant.md) | Copilot-class, < 300 ms | Context engineering as a funnel; cache first; model routing by task; output validation; a decomposed latency budget | 30 min |
| 4 | [Recruiting Platform](04_Recruiting_Platform.md) | Resume to hiring decision, thousands/hour | Structured extraction as the seam; explainable weighted ranking; AI judge that does not decide; fairness as a continuous control | 30 min |
| 5 | [Logistics Exception Handling](05_Logistics_Exception_Handling.md) | The FDE round — embedded with a customer | Clarifying answers that move boxes; streaming + batch unified; the Policy Gate with customs first; shared control plane, regional data planes; low-DAU high-stakes sizing | 35 min |
| 6 | [The Agentic Coverage Map](06_Agentic_Coverage_Map.md) | Cases 1 and 2 side by side | Which concepts each covers; the four gaps in both and where the handbook fills them | 20 min |

## The whiteboard scripts

`whiteboard_scripts/` holds four full scripts written to the [60-minute method](../02_System_Design_Fundamentals/05_The_60_Minute_Whiteboard_Method.md). Each is a performance artefact: minute-by-minute, with the framing sentence, the marked insight, the failure table, the close, and a cheat sheet of the lines that carry the round.

| Script | Prompt | Built in |
|---|---|---|
| [01 · Enterprise RAG with Access Control](whiteboard_scripts/01_Enterprise_RAG_With_Access_Control.md) | *"Architect a RAG system that pulls from multiple enterprise data sources with access control."* | Module 04 |
| [02 · Enterprise RAG on Databricks](whiteboard_scripts/02_Enterprise_RAG_On_Databricks.md) | The same, for a Lakehouse audience — leads with the Vector Search trap | Module 08 doc 3 |
| [03 · Agent Platform for Non-Technical Users](whiteboard_scripts/03_Agent_Platform_For_Non_Technical_Users.md) | *"Design an AI agent platform for non-technical users to configure workflow automations across multiple channels."* | Module 05 |
| [04 · Scoping Doc to Deployed Agent in Two Weeks](whiteboard_scripts/04_Scoping_Doc_To_Deployed_Agent_In_Two_Weeks.md) | *"Design a delivery framework that takes a customer from scoping doc to deployed AI agent in under two weeks."* | Module 10 |

How to use them: read the method, then read one script with a timer, saying the lines aloud. Then close the script and deliver the same six steps from the method alone. The scripts are the answer key, not the crib sheet.

## Checkpoint

You are ready for Module 10 when you can:

- For any of the five prompts, state the one sentence that frames the round and name the hardest part.
- Walk the combined agentic spine and raise the four gaps unprompted.
- Deliver any one of the four whiteboard scripts from the method alone, within 60 minutes, with the forward-deployed close.

**Next →** [Module 10 · FDE Delivery and Operating Model](../10_FDE_Delivery_Operating_Model/README.md)
