import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import fitness, travel, images, books, data_analyst, fraud, onboarding, summarizer

BASE_DIR = Path(__file__).parent
OUTPUTS_DIR = BASE_DIR / "outputs"
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="CrewAI Agent Hub")

app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

app.include_router(fitness.router, prefix="/api/fitness")
app.include_router(travel.router, prefix="/api/travel")
app.include_router(images.router, prefix="/api/images")
app.include_router(books.router, prefix="/api/books")
app.include_router(data_analyst.router, prefix="/api/data-analyst")
app.include_router(fraud.router, prefix="/api/fraud")
app.include_router(onboarding.router, prefix="/api/onboarding")
app.include_router(summarizer.router, prefix="/api/summarizer")


@app.get("/health")
def health():
    return {"status": "ok"}
