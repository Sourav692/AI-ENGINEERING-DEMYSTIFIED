# Monolith vs Microservices

> **Level** 🟢 Foundations · **Module** 02 · **Doc** 3 of 5 · **Time** ~25 min
> **Prerequisites:** [The 12-Part Framework](01_The_12_Part_Framework.md)
> **Source material:** `4. FDE_Related_Preparation/System_Design and Delivery/4. Monolith vs Microservice Architecture.md`

## Why this matters

This is one of the most common design questions, and it is almost always misread as a loyalty test. It is not. Interviewers are evaluating whether you understand the *trade-offs*: a monolith and a set of microservices solve the same problem with a different set of costs, and the right answer depends on team size, scaling profile and release cadence — not on fashion. The same trade-off applies one layer up the stack to AI systems, which is why it is in this handbook.

## Monolithic architecture

The entire application built, deployed and scaled as one unit. All business functionality lives in the same application, usually backed by one shared database, packaged as one deployable artefact.

```
Monolithic Application
+----------------------------------------------------+
| Authentication          Product Catalog             |
| Shopping Cart           Payment                      |
| Inventory               Order Management             |
| Notification            Reporting                    |
+----------------------------------------------------+
                          |
                   Single Database
```

Every capability is a module inside one boundary. No network hop between them — a request moves module to module as a plain function call, and the whole thing scales, deploys and fails together.

**What togetherness gives you:**

- **Simple development** — one project, no network calls between modules; Controller → Service → Repository → Database, all in-process.
- **Easy deployment** — build, deploy, done. Nothing to coordinate.
- **Easier debugging** — one process; a debugger traces Login → Cart → Payment → Order without crossing a service boundary.
- **Better performance** — a function call costs microseconds; a REST call between services costs milliseconds.

**What it costs as it grows:**

- **Difficult to scale** — if only Payment is overloaded, you still scale everything.
- **Large codebase** — from 10 to 100 to 1,000 developers, merge conflicts multiply and build and test times climb.
- **Single point of failure** — a memory leak in one module crashes the whole application.
- **Slower releases** — changing a notification template can mean redeploying everything.

## Microservices architecture

Independent services, each owning one business capability — its logic *and* its data — talking to the outside through a shared API gateway and to each other over REST, gRPC, messaging or events.

```
                              API Gateway
                                   |
   -----------------------------------------------------------------
   |         |         |          |          |            |
  Auth    Product     Cart     Payment     Orders     Notification
 Service  Service    Service   Service     Service      Service
   |         |         |          |          |            |
   DB        DB        DB         DB         DB           DB
```

**What independence gives you:**

- **Independent scaling** — Payment gets five instances; Product stays as it was.
- **Independent deployment** — update Search without redeploying Authentication or Orders.
- **Team independence** — Payments, Orders, Search, AI, Platform each owned by a team with its own release schedule.
- **Fault isolation** — Notification fails; Payments, Orders and Search keep running.
- **Technology flexibility** — Java for Authentication, Python for Search and the AI agent, Go for Recommendation, C# for Billing.

**What independence costs:**

- **Network communication** — REST, gRPC, Kafka between services; network failures are now a real possibility.
- **Distributed transactions** — Shipping fails after Payment succeeded; you need compensation logic (the Saga pattern).
- **Data consistency** — each service owns its database; a cross-service join is no longer a query.
- **Debugging** — one request travels User → Gateway → Auth → Order → Payment → Notification; distributed tracing becomes essential.
- **Operational complexity** — service discovery, gateway, load balancing, observability, tracing, circuit breakers, retries, rate limiting: infrastructure the monolith never asked for.

## Side by side

| Aspect | Monolith | Microservices |
|---|---|---|
| Deployment | Single | Independent |
| Scaling | Entire application | Individual services |
| Codebase | One large | Multiple smaller |
| Database | Usually shared | Per service |
| Communication | Function calls | REST, gRPC, messaging |
| Fault isolation | Lower | Higher |
| Development speed (small teams) | Faster | Slower, initially |
| Operational complexity | Lower | Higher |
| Best for | Startups, MVPs, small products | Large enterprise systems |

## The same trade-off in an AI system

A monolithic AI assistant packages authentication, prompt building, RAG, embeddings, vector search, LLM calls, tool calls and logging into one process. A microservices AI platform splits those into independently owned services.

```
Monolithic AI Assistant                    Microservices AI Platform
+------------------------------+                    API Gateway
| Authentication                |                        |
| Prompt Builder                |     -----------------------------------------
| RAG                           |     |        |        |         |          |
| Embedding Generation          |   Auth   Prompt    Agent     Model     Observability
| Vector Search                 |         Mgmt       Orch.    Gateway
| LLM Calls                     |                       |
| Tool Calls                    |          -----------------------------
| Logging                       |          |        |         |        |
+------------------------------+        RAG     Embedding    Tool    Memory
                                        Service   Service   Service  Service
Suitable for:                                        |
 - Proof of concept                          Vector Database
 - Internal chatbot
 - Small teams
 - Limited scale
```

The left suits a proof of concept, an internal chatbot, a small team. The right lets Prompt Management, Agent Orchestration, the Model Gateway and Observability evolve independently, with an orchestrator calling RAG, Embedding, Tool and Memory services that share one vector database — each potentially owned by a different team.

The three source projects in this handbook (Modules 04, 05, 10) are each a *modular monolith*: one Python package with clean module boundaries (`authz/`, `ingest/`, `retrieval/`, `graph/`), no network hops between them, and a coverage map that says which of those boundaries would become services first at scale. That is the honest shape for what they are.

## When to choose which

**A monolith when** speed and simplicity matter more than independence: MVP or prototype; fewer than 10–15 developers; fast-evolving requirements; modest scale.

**Microservices when** independence matters more than simplicity: modules with different scaling needs; multiple teams that must work independently; independent deployments matter; high availability and fault isolation are required; the system has outgrown one codebase.

## The evolution model

Monolith and microservices are not two options you pick once. Most real systems move from one toward the other as a specific set of pressures builds: traffic grows unevenly across modules, the team splits into squads, release cadence starts to matter more than raw simplicity.

```
 Modular Monolith  ── extract clear business boundaries ──►  Microservices
 MVP · small team          (Payments · Search · AI)          Multiple teams
 < 15 devs                    as they emerge                 independent scale

        growing traffic · growing team size · growing need for independent releases →
```

Start as a well-structured modular monolith — boundaries already clean, just not yet given network boundaries. Extract a service only when a concrete pressure justifies it: Payments needs independent compliance controls; Search needs its own scaling curve; the AI team needs to ship without waiting on everyone else's release train.

## Interview lens

Treat "which would you choose?" as a sequencing question:

> *"I don't view monoliths and microservices as competing approaches — they're stages in a system's evolution. For a new product I'd start with a well-structured modular monolith because it minimises operational complexity and enables rapid iteration. As the product matures, traffic grows and teams expand, I'd identify clear business boundaries — Payments, Search, AI — and gradually extract them into microservices. That avoids premature complexity while keeping a path to independent scaling and deployment when the business justifies it."*

That answer demonstrates judgement rather than assuming microservices are always superior.

## Checkpoint

- Name four things a monolith gives you for free and four it costs at scale.
- Name five infrastructure components microservices require that a monolith does not.
- What is a modular monolith, and why is it the right starting shape?
- Give three concrete pressures that justify extracting a specific service.
- Map the AI-platform microservices diagram onto the AI additions from the 12-part framework.

**Next →** [Worked Example — The Travel Agent](04_Worked_Example_Travel_Agent.md)
