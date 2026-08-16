# Build context: repo root.
# Run: docker build -f app/Dockerfile -t deep-agent .

FROM node:20-slim AS frontend-build

WORKDIR /frontend
COPY app/frontend/package.json app/frontend/package-lock.json ./
RUN npm ci
COPY app/frontend/ ./
RUN npm run build


FROM python:3.12-slim

WORKDIR /app

# Backend deps
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Backend source
COPY app/backend/ ./backend/

# Skills (loaded by the deep agent at runtime)
COPY skills/ ./skills/

# Built frontend (served as static files by FastAPI)
COPY --from=frontend-build /frontend/build ./frontend/build/

EXPOSE 8000

CMD ["uvicorn", "deep_agent.main:app", "--app-dir", "backend/src", "--host", "0.0.0.0", "--port", "8000"]
