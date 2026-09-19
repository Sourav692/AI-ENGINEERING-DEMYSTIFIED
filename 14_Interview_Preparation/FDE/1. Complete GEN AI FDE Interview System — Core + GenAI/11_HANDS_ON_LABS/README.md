# Advanced GenAI Production Architecture Reference

**Status:** OPTIONAL REFERENCE
**Implementation status:** PARTIALLY IMPLEMENTED
**Fully runnable end to end:** NO
**Required for study:** NO
**Primary purpose:** Advanced architecture, interface, and extension-point study
**Recommended audience:** Candidates preparing for senior or production-focused GenAI FDE architecture discussions
**Primary hands-on lab:** `../01_CANONICAL_GENAI_FDE_INTERVIEW_LAB`

This repository is an educational production-architecture reference. It demonstrates component boundaries, interfaces, safety patterns, deployment structures, and potential enterprise extensions.

It is not the canonical hands-on lab and should not be presented as a fully implemented production system.

Some database, model-provider, vector-store, migration, infrastructure, and MCP tool components are intentionally included as reference structures or extension points. Candidates should use them to discuss production design decisions or complete them as optional advanced exercises.

## Tested Environment

This release was tested using:

* Operating system: [insert actual operating system]
* Python version: [insert actual version]
* Node.js version: [insert actual version, when frontend is used]
* Docker version: [insert actual version]
* Docker Compose version: [insert actual version]
* Test command: `[insert exact command]`
* Application start command: `[insert exact command]`
* Last verified: [YYYY-MM-DD]

## Verified Capabilities

* [ ] Backend application starts successfully
* [ ] Frontend application starts successfully
* [ ] Docker image builds successfully
* [ ] Docker Compose environment starts successfully
* [ ] Automated tests pass
* [ ] Sample data can be loaded
* [ ] Retrieval workflow returns results
* [ ] Permission-leakage evaluation runs
* [ ] Grounding evaluation runs
* [ ] Agent guardrails can be demonstrated
* [ ] Audit or observability output can be inspected

Only checked capabilities are officially verified for this release.

## Candidate Completion Criteria

The lab is considered completed only when the candidate can provide the following evidence:

* [ ] The application starts using the documented setup instructions.
* [ ] The automated test suite completes successfully.
* [ ] A sample document or record is ingested.
* [ ] A retrieval request returns relevant information.
* [ ] Permission-aware behaviour is demonstrated.
* [ ] At least one evaluation suite is executed.
* [ ] One agent or tool-safety control is demonstrated.
* [ ] One failure scenario is reproduced and explained.
* [ ] The candidate creates or updates an architecture diagram.
* [ ] The candidate explains three limitations of the implementation.
* [ ] The candidate presents the system in a ten-minute interview walkthrough.

### Interview-ready completion threshold

The candidate should be able to explain:

1. The customer problem addressed by the lab.
2. The main system components.
3. How data enters the system.
4. How retrieval and generation work.
5. How permissions are enforced.
6. How quality is evaluated.
7. How failures are detected.
8. Which components would need to change for production deployment.
9. One cost-versus-quality trade-off.
10. One security-versus-usability trade-off.


