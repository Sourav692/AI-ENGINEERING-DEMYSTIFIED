# Knowledge Graph Builder with LangExtract

A Streamlit application that constructs knowledge graphs from unstructured text using Google's [LangExtract](https://github.com/google/langextract) library. Extracts entities and relationships, then visualizes them as interactive knowledge graphs.

## Quick Start

### Prerequisites

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) package manager
- Google Gemini API key (`GOOGLE_API_KEY`)

### 1. Navigate to the App Directory

```bash
cd 02_First_Agents/apps/langextract/knowledge-graphs-with-langextract
```

### 2. Install Dependencies

```bash
uv pip install -r requirements.txt
```

### 3. Set Up API Key

Create a `.env` file:

```bash
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
```

Or use Streamlit secrets (`.streamlit/secrets.toml`):

```toml
GOOGLE_API_KEY = "your_gemini_api_key_here"
```

### 4. Run the Application

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Features

- **Relationship Extraction**: Identifies entities and their relationships from free-form text
- **Graph Visualization**: Renders extracted relationships as an interactive knowledge graph
- **Query Filtering**: Focus on specific entity types or relationships
- **Multiple Document Support**: Process several documents simultaneously

## Project Structure

```text
knowledge-graphs-with-langextract/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Project dependencies
├── src/                   # Core processing logic
├── data/                  # Sample documents
├── templates/             # Few-shot example templates
└── .streamlit/
    └── secrets.toml       # Streamlit secrets (alternative to .env)
```

## Getting a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Add the key to your `.env` file

## License

Part of the LangGraph Demystified repository. See the root [LICENSE](../../../../LICENSE) for details.
