# evals3-i

Multi-turn and tool use evaluation scripts with DeepEval framework.

## Setup

Install dependencies with `uv`:

```bash
uv sync
```

## Running Tests

Run evaluations:

```bash
python test_conv.py
python test_tools1.py
python test_tools2.py
python test_tools3.py
```

## Requirements

- Python 3.12

### LLM Provider Configuration

By default, this setup uses **OpenRouter** by configuring an alternative base URL. You have the following options:

- **OpenRouter** (default): Use your OpenRouter API key for the `OPENAI_API_KEY` environment variable. The base URL used is `https://openrouter.ai/api/v1`.
- **OpenAI directly**: Use your OpenAI API key with the standard OpenAI base URL.

**Important:** Regardless of which option you choose, make sure to use OpenAI models for utmost consistency with the evaluation framework defaults.
