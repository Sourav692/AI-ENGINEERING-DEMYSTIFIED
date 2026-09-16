## Browser Demo

A lightweight browser-based demonstration interface is included in:

```text
frontend/simple-ui/
```

This interface allows candidates to demonstrate the canonical RAG workflow without building a separate frontend application.

### Step 1: Start the API

From the project root, run:

```bash
uvicorn backend.app.main:app --reload
```

By default, the API will be available at:

```text
http://127.0.0.1:8000
```

The interactive FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### Step 2: Open the browser interface

Open the following file in a browser:

```text
frontend/simple-ui/index.html
```

The interface sends requests to the locally running API and displays the generated response.

### Intended use

The included browser interface is designed for:

* local demonstrations
* interview practice
* architecture walkthroughs
* debugging exercises
* portfolio presentations

It is intentionally lightweight and should not be presented as a production-ready frontend application.

A production deployment would typically add authentication, session handling, error analytics, accessibility testing, frontend security controls and a supported framework such as React, Next.js or Streamlit.
