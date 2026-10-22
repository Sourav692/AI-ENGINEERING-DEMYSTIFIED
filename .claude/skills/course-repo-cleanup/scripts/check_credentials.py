#!/usr/bin/env python3
"""Check which API credentials in a .env actually work — one cheap authenticated call each.

Run before any bulk notebook run: a key that is set but rejected (expired, wrong provider,
exhausted quota) otherwise surfaces as a confusing failure halfway through a module. Only
variables that are set are checked; values are never printed.

A 401 from one provider does not always mean a bad key: the same variable name (e.g.
WEATHER_API_KEY) is used by different services, so several providers may be probed for it.

Usage: check_credentials.py [--env .env] [--markdown]
"""
from __future__ import annotations

import argparse
import os

import requests
from dotenv import load_dotenv

TIMEOUT = 20


def bearer(url, var):
    def call():
        headers = {"Authorization": f"Bearer {os.environ[var]}"}
        return requests.get(url, headers=headers, timeout=TIMEOUT)
    return call


CHECKS = [  # (label, env var(s) that must be set, request)
    ("OpenAI", ["OPENAI_API_KEY"], bearer("https://api.openai.com/v1/models", "OPENAI_API_KEY")),
    ("Anthropic", ["ANTHROPIC_API_KEY"], lambda: requests.get(
        "https://api.anthropic.com/v1/models",
        headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"},
        timeout=TIMEOUT)),
    ("OpenRouter", ["OPENROUTER_API_KEY"],
     bearer("https://openrouter.ai/api/v1/key", "OPENROUTER_API_KEY")),
    ("Groq", ["GROQ_API_KEY"], bearer("https://api.groq.com/openai/v1/models", "GROQ_API_KEY")),
    ("Nebius", ["NEBIUS_API_KEY"],
     bearer("https://api.studio.nebius.com/v1/models", "NEBIUS_API_KEY")),
    ("Google Gemini", ["GOOGLE_API_KEY"], lambda: requests.get(
        "https://generativelanguage.googleapis.com/v1beta/models",
        params={"key": os.environ["GOOGLE_API_KEY"]}, timeout=TIMEOUT)),
    ("Tavily", ["TAVILY_API_KEY"], lambda: requests.post(
        "https://api.tavily.com/search",
        json={"api_key": os.environ["TAVILY_API_KEY"], "query": "test", "max_results": 1},
        timeout=TIMEOUT)),
    ("LangSmith", ["LANGCHAIN_API_KEY"], lambda: requests.get(
        "https://api.smith.langchain.com/api/v1/sessions", params={"limit": 1},
        headers={"x-api-key": os.environ["LANGCHAIN_API_KEY"]}, timeout=TIMEOUT)),
    ("LangSmith", ["LANGSMITH_API_KEY"], lambda: requests.get(
        "https://api.smith.langchain.com/api/v1/sessions", params={"limit": 1},
        headers={"x-api-key": os.environ["LANGSMITH_API_KEY"]}, timeout=TIMEOUT)),
    ("Databricks", ["DATABRICKS_HOST", "DATABRICKS_TOKEN"], lambda: requests.get(
        f"{os.environ['DATABRICKS_HOST'].rstrip('/')}/api/2.0/serving-endpoints",
        headers={"Authorization": f"Bearer {os.environ['DATABRICKS_TOKEN']}"}, timeout=TIMEOUT)),
    # same variable name, different services: report each so a wrong-provider 401 is recognisable
    ("WEATHER_API_KEY @ OpenWeatherMap", ["WEATHER_API_KEY"], lambda: requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"q": "London", "appid": os.environ["WEATHER_API_KEY"]}, timeout=TIMEOUT)),
    ("WEATHER_API_KEY @ weatherapi.com", ["WEATHER_API_KEY"], lambda: requests.get(
        "https://api.weatherapi.com/v1/current.json",
        params={"key": os.environ["WEATHER_API_KEY"], "q": "London"}, timeout=TIMEOUT)),
]

PRESENCE_ONLY = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "OPENBB_PAT", "SERPAPI_API_KEY"]
TRACING_SWITCHES = ["LANGSMITH_TRACING", "LANGCHAIN_TRACING_V2"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", default=".env")
    ap.add_argument("--markdown", action="store_true",
                    help="print a Markdown table for the tracker")
    a = ap.parse_args()
    load_dotenv(a.env)

    rows = []
    for label, needs, call in CHECKS:
        if not all(os.environ.get(v) for v in needs):
            continue
        try:
            r = call()
            status = "ok" if r.ok else f"FAIL (HTTP {r.status_code})"
        except Exception as e:  # network errors, bad host
            status = f"FAIL ({type(e).__name__})"
        rows.append((label, ", ".join(needs), status))
    for v in PRESENCE_ONLY:
        rows.append((v, v, "set (not call-tested)" if os.environ.get(v) else "not set"))
    for v in TRACING_SWITCHES:
        if os.environ.get(v, "").lower() == "true":
            rows.append((v, v, "tracing ON — every run sends traces; check the account quota"))

    if a.markdown:
        print("| Service | Variable(s) | Status |\n|---|---|---|")
        for r in rows:
            print(f"| {r[0]} | `{r[1]}` | {r[2]} |")
    else:
        for r in rows:
            print(f"{r[0]:34} {r[2]}")


if __name__ == "__main__":
    main()
