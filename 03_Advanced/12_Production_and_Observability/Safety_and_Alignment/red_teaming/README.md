# Red teaming

Demo project for red teaming.

## Setup

Install dependencies with:

```bash
uv sync
```

## Running Tests

```bash
python test_rt.py
```

## Requirements

- Python 3.12
- uv package manager

### LLM Provider Configuration

By default, this setup uses **OpenRouter** by configuring an alternative base URL. You have the following options:

- **OpenRouter** (default): Use your OpenRouter API key for the `OPENAI_API_KEY` environment variable. The base URL used is `https://openrouter.ai/api/v1`.
- **OpenAI directly**: Use your OpenAI API key with the standard OpenAI base URL.

**Important:** Regardless of which option you choose, make sure to use OpenAI models for utmost consistency with the evaluation framework defaults.
