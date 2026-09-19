# Assignments and Quizzes: AI Customer Support Agent Copilot

## Part 1: Assignments (Practical Implementation)

These assignments are designed to extend your current project and deepen your understanding of tool-using agents, memory systems, RAG pipelines, and production-ready AI app development.

---

### Assignment 1: Add a New Tool - Customer Sentiment Analyzer
**Objective**: Extend the copilot with sentiment-aware response support.

- **Task**:
  1. Create a new file `customer_support_agent/integrations/tools/sentiment_tools.py`.
  2. Implement a `analyze_ticket_sentiment(subject: str, description: str)` function.
  3. Decorate it with `@tool` from LangChain and add a clear usage-focused docstring.
  4. Return structured JSON (sentiment, confidence, escalation_risk, summary, recommended_action).
  5. Register this tool in `customer_support_agent/integrations/tools/support_tools.py`.
  6. Verify the tool appears in `tool_calls` inside `context_used` during draft generation.
  7. Test with inputs like:
     - "I have been charged 3 times and nobody is helping."
     - "Just checking account limits for next month."

- **Deliverable**:
  - New tool file with implementation.
  - Updated tool registry.
  - Example API response showing sentiment tool execution in draft context.

- **Bonus**:
  - Add basic keyword fallback logic if LLM tool call fails.
  - Add caching for repeated subject/description pairs.

---

### Assignment 2: Improve Memory Reliability with Fallback Handling
**Objective**: Make memory integration more resilient in production.

- **Task**:
  1. Update `customer_support_agent/services/copilot_service.py` so memory operations degrade gracefully when Mem0 initialization fails.
  2. Ensure draft generation still works even when memory is unavailable.
  3. Guard calls in:
     - `_search_memory_scopes()`
     - `list_customer_memories()`
     - `save_accepted_resolution()`
  4. Add explicit error markers in `context_used["errors"]` when memory is skipped.
  5. Add one API-level response note for memory endpoints when backend memory is unavailable.
  6. Test both cases:
     - with valid embedding provider keys
     - without embedding provider keys

- **Deliverable**:
  - Updated copilot logic with defensive memory checks.
  - Demo of successful draft generation in memory-disabled mode.
  - Demo of successful draft generation in memory-enabled mode.

- **Bonus**:
  - Add runtime metrics (`memory_enabled`, `memory_query_time_ms`) inside `context_used`.

---

### Assignment 3: Add Full Draft Lifecycle Operations
**Objective**: Complete draft workflow for real support operations.

- **Task**:
  1. Add a new endpoint `POST /api/drafts/{draft_id}/regenerate` to regenerate a draft for the same ticket.
  2. Add endpoint `POST /api/drafts/{draft_id}/mark-pending` to reopen accepted/discarded drafts.
  3. Add repository method to list all drafts for a ticket (`get_all_for_ticket(ticket_id)`).
  4. Add endpoint `GET /api/tickets/{ticket_id}/draft-history`.
  5. Update Streamlit UI (`app.py`) to:
     - show draft history
     - allow selecting prior versions
     - regenerate from current ticket context
  6. Ensure accepted draft still updates ticket status and memory resolution.

- **Deliverable**:
  - Updated routers/services/repositories with new draft lifecycle support.
  - UI demo showing multiple draft versions and history retrieval.

- **Bonus**:
  - Add "agent notes" field while accepting a draft and store it in `context_used`.

---

### Assignment 4: Add Automated Testing with Pytest
**Objective**: Increase confidence and prevent regressions.

- **Task**:
  1. Expand `tests/` with at least 6 test cases:
     - `test_health.py` (existing health check can be reused/refined)
     - `test_tickets_api.py` (create/list/get ticket)
     - `test_drafts_api.py` (generate/update/accept draft flow)
     - `test_knowledge_service.py` (ingestion and search behavior with temp directories)
     - `test_customers_repository.py` (create_or_get/get_by_email correctness)
     - `test_support_tools.py` (tool outputs and JSON structure)
  2. Mock external provider dependencies where required.
  3. Add pytest configuration in `pyproject.toml` (or `pytest.ini`) for clean test discovery.
  4. Run `uv run pytest -v`.

- **Deliverable**:
  - Minimum 6 passing tests.
  - Test output log showing all tests pass.
  - Updated dev dependencies if needed.

- **Bonus**:
  - Add coverage report (`pytest --cov`) and enforce a minimum threshold.

---

### Assignment 5: Strengthen CI/CD and Deployment Workflows
**Objective**: Make delivery pipeline production-ready.

- **Task**:
  1. Update `.github/workflows/ci.yml`:
     - trigger on push and PR
     - run linting (`ruff` or `flake8`)
     - run tests with verbosity and optional coverage
  2. Add `.github/workflows/deploy.yml` (or update existing deploy workflow) to:
     - build Docker images
     - optionally push image to GHCR
     - deploy to EC2 only after test success
  3. Add branch protection recommendation in docs (require CI checks before merge).
  4. Add status badges to `README.md`.
  5. Add a deployment rollback note in `docs/EC2_deployment_flow.md`.

- **Deliverable**:
  - Updated CI/CD workflow files.
  - Passing Actions run screenshot/log.
  - README updated with badges and quick pipeline explanation.

- **Bonus**:
  - Add manual approval gate for production deploy.

---

## Part 2: Quizzes (Conceptual Understanding)

### Quiz 1: Agent Orchestration and Tool Calling

**Q1. In this project, what is the main purpose of LangChain `create_agent` in `copilot_service.py`?**

a) To run Streamlit UI components  
b) To orchestrate reasoning and tool usage before generating the final draft  
c) To connect SQLite to FastAPI  
d) To replace all REST APIs  

*Answer: b) To orchestrate reasoning and tool usage before generating the final draft*

---

**Q2. Why are tool outputs normalized into `tool_calls` inside `context_used`?**

a) To reduce model token usage only  
b) To support transparency/debuggability for what the agent actually used  
c) To speed up SQLite writes  
d) To avoid using memory  

*Answer: b) To support transparency/debuggability for what the agent actually used*

---

**Q3. What is the role of `@tool` in `support_tools.py`?**

a) Encrypt the function output  
b) Register function metadata so the agent can discover and invoke it  
c) Make function asynchronous automatically  
d) Convert function into API endpoint  

*Answer: b) Register function metadata so the agent can discover and invoke it*

---

### Quiz 2: Memory and RAG

**Q4. Why does the project use both Mem0 memory and Chroma knowledge retrieval?**

a) They are duplicates, used for backup only  
b) Memory stores customer-specific history; RAG retrieves general policy/domain documents  
c) Chroma stores API routes and Mem0 stores logs  
d) Both are required by FastAPI  

*Answer: b) Memory stores customer-specific history; RAG retrieves general policy/domain documents*

---

**Q5. What is the purpose of `effective_google_embedding_model` in settings?**

a) To set API host and port  
b) To normalize/upgrade deprecated embedding model aliases to a supported one  
c) To disable memory automatically  
d) To configure Streamlit theme  

*Answer: b) To normalize/upgrade deprecated embedding model aliases to a supported one*

---

**Q6. Why are memory scopes split into customer-level and company-level IDs?**

a) To double token usage  
b) To let agent use both individual history and org-level recurring patterns  
c) To store data in two databases  
d) To support only enterprise plans  

*Answer: b) To let agent use both individual history and org-level recurring patterns*

---

### Quiz 3: API and Backend Architecture

**Q7. What does FastAPI lifespan setup do in `app_factory.py`?**

a) Restarts the server every request  
b) Ensures required directories and DB schema are initialized at app startup  
c) Clears all draft data on deploy  
d) Runs tests before requests  

*Answer: b) Ensures required directories and DB schema are initialized at app startup*

---

**Q8. Why is `get_copilot()` wrapped with `@lru_cache` in dependencies?**

a) To avoid importing FastAPI repeatedly  
b) To reuse expensive copilot initialization instead of rebuilding it per request  
c) To cache HTTP responses  
d) To store user sessions  

*Answer: b) To reuse expensive copilot initialization instead of rebuilding it per request*

---

**Q9. What happens when a draft is accepted via `PATCH /api/drafts/{draft_id}`?**

a) Nothing changes in ticket state  
b) Ticket is set to resolved and accepted resolution is attempted to be saved into memory  
c) Ticket is deleted automatically  
d) Knowledge base is re-ingested  

*Answer: b) Ticket is set to resolved and accepted resolution is attempted to be saved into memory*

---

### Quiz 4: Data Layer and Reliability

**Q10. Why are repositories split into `customers`, `tickets`, and `drafts` modules?**

a) Python import limitation  
b) Modular data access for maintainability, testability, and clear boundaries  
c) Required by SQLite engine  
d) For UI performance only  

*Answer: b) Modular data access for maintainability, testability, and clear boundaries*

---

**Q11. What bug can occur if `get_by_email()` queries by `id` instead of `email`?**

a) Chroma index corruption  
b) Customer lookup failures causing tool responses to show false "customer not found"  
c) FastAPI startup failure  
d) Docker compose healthcheck failure  

*Answer: b) Customer lookup failures causing tool responses to show false "customer not found"*

---

**Q12. Why should fallback responses exist when LLM/tool output is empty?**

a) Only to improve UI colors  
b) To maintain user-facing reliability and avoid blank/failed draft responses  
c) To skip logging  
d) To reduce DB size  

*Answer: b) To maintain user-facing reliability and avoid blank/failed draft responses*

---

### Quiz 5: Docker, CI/CD, and Deployment

**Q13. Why are `pyproject.toml` and lock file copied before application code in Docker build?**

a) Docker syntax requirement  
b) To leverage layer caching for dependencies and speed up rebuilds  
c) To reduce Python memory usage  
d) To avoid exposing ports  

*Answer: b) To leverage layer caching for dependencies and speed up rebuilds*

---

**Q14. Why is API health check important in deployment workflow?**

a) It formats logs  
b) It verifies service is actually live after deployment before considering rollout successful  
c) It updates dependencies  
d) It enables Streamlit caching  

*Answer: b) It verifies service is actually live after deployment before considering rollout successful*

---

**Q15. What is the value of running tests before deploy in GitHub Actions?**

a) It increases Docker image size  
b) It reduces risk of shipping broken functionality to production  
c) It disables branch protection  
d) It replaces manual QA entirely  

*Answer: b) It reduces risk of shipping broken functionality to production*

---

### Quiz 6: Streamlit and User Workflow

**Q16. Why does the Streamlit app expose "Context used" for drafts?**

a) For debugging model behavior and increasing trust in generated responses  
b) To allow direct SQL editing  
c) To disable tool calls  
d) To store API secrets  

*Answer: a) For debugging model behavior and increasing trust in generated responses*

---

**Q17. What is the benefit of showing memory probe results in UI?**

a) Adds random output for demos  
b) Helps verify stored customer memory quality and relevance for future responses  
c) Replaces ticket creation  
d) Avoids using knowledge base  

*Answer: b) Helps verify stored customer memory quality and relevance for future responses*

---

### Quiz 7: Error Handling and Engineering Best Practices

**Q18. Why should APIs return clear HTTP errors (400/404/500) with helpful messages?**

a) For prettier Swagger UI only  
b) To improve operability, debugging speed, and frontend error handling  
c) To bypass validation  
d) To reduce response time  

*Answer: b) To improve operability, debugging speed, and frontend error handling*

---

**Q19. Why is it useful to keep integration code (`memory`, `rag`, `tools`) separate from service logic?**

a) Reduces git history size  
b) Encourages clean architecture and easier replacement/testing of providers  
c) Required by LangChain  
d) Prevents Docker builds from failing  

*Answer: b) Encourages clean architecture and easier replacement/testing of providers*

---

**Q20. What is the biggest advantage of structured `context_used` versioning?**

a) It removes need for tests  
b) It supports backward compatibility and safer evolution of response tracing format  
c) It speeds up embeddings  
d) It avoids environment variables  

*Answer: b) It supports backward compatibility and safer evolution of response tracing format*

---

## Submission Guidelines

1. **Assignments**: Submit a GitHub repository link with:
   - Clear commit history per assignment
   - Updated README with setup and run steps
   - Screenshots/recordings for each completed feature

2. **Quizzes**: Submit answers in your LMS/Google Form/mentor document as instructed.

3. **Code Quality Expectations**:
   - Proper error handling and edge-case coverage
   - Clear function names and modular file organization
   - Tool docstrings that are LLM-usable
   - No hardcoded API keys or credentials
   - Passing tests before submission
