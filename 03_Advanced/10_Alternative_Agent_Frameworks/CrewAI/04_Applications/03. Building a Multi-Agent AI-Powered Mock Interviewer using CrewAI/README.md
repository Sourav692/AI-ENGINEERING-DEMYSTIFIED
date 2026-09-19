# ai-mock-interviewer
A smart mock interview assistant built with CrewAI, simulating realistic tech interviews with multi-agent conversations and feedback.

## Installation

1. Make sure you have [Poetry](https://python-poetry.org/docs/#installation) installed on your system.

2. Clone this repository:
```bash
git clone https://github.com/yourusername/ai-mock-interviewer.git
cd ai-mock-interviewer
```

3. Install dependencies:
```bash
poetry install
```

4. Activate the virtual environment:
```bash
poetry shell
```

## Development

### Run the CLI version
```bash
cd ai-mock-interviewer
poetry run ai_mock_interviewer/interview_practice_system.py
```

### Run the Streamlit Web App
```bash
cd ai-mock-interviewer
poetry run streamlit run ai_mock_interviewer/chatbot_ui.py
```

### Linting and Formatting

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting. To run the linter:

```bash
# Check for linting issues
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Format code
ruff format .
```

---

## Deploying to Databricks Apps

### Prerequisites
- A Databricks workspace with Apps enabled
- Databricks CLI installed and configured
- API keys for OpenAI and Serper

### Step 1: Store Secrets in Databricks

Create a secret scope and add your API keys:

```bash
# Create a secret scope
databricks secrets create-scope ai-mock-interviewer

# Add OpenAI API key
databricks secrets put-secret ai-mock-interviewer openai-api-key

# Add Serper API key  
databricks secrets put-secret ai-mock-interviewer serper-api-key
```

### Step 2: Prepare the Application Files

Ensure your app directory contains:
- `app.yaml` - Databricks App configuration
- `requirements.txt` - Python dependencies
- `chatbot_ui.py` - Main Streamlit application
- `interview_practice_system.py` - CrewAI backend logic

### Step 3: Deploy Using Databricks CLI

```bash
# Navigate to the app directory
cd "3. Building a Multi-Agent AI-Powered Mock Interviewer using CrewAI"

# Deploy the app
databricks apps deploy ai-mock-interviewer --source-code-path .
```

### Step 4: Deploy Using Databricks UI

1. Navigate to your Databricks workspace
2. Go to **Compute** → **Apps**
3. Click **Create App**
4. Fill in the app details:
   - **Name**: `ai-mock-interviewer`
   - **Description**: AI Mock Interviewer powered by CrewAI
5. Upload your source code (zip the directory or connect to Git)
6. Configure environment variables:
   - `OPENAI_API_KEY`: Link to secret `ai-mock-interviewer/openai-api-key`
   - `SERPER_API_KEY`: Link to secret `ai-mock-interviewer/serper-api-key`
7. Click **Deploy**

### Step 5: Using Databricks Asset Bundles (Recommended)

For production deployments, use Databricks Asset Bundles:

1. Create `databricks.yml` in your project root:

```yaml
bundle:
  name: ai-mock-interviewer

targets:
  dev:
    workspace:
      host: https://<your-workspace>.cloud.databricks.com

resources:
  apps:
    ai_mock_interviewer:
      name: ai-mock-interviewer
      description: AI Mock Interviewer powered by CrewAI
      source_code_path: .
      config:
        command:
          - streamlit
          - run
          - chatbot_ui.py
          - --server.port=8501
          - --server.address=0.0.0.0
        env:
          - name: OPENAI_API_KEY
            value_from: "{{secrets/ai-mock-interviewer/openai-api-key}}"
          - name: SERPER_API_KEY
            value_from: "{{secrets/ai-mock-interviewer/serper-api-key}}"
```

2. Deploy using the bundle:

```bash
databricks bundle deploy -t dev
databricks bundle run ai_mock_interviewer -t dev
```

### Important Notes for Databricks Apps

1. **Whisper Model**: The app uses OpenAI Whisper for speech-to-text. On first run, it downloads the model which may take time. Consider pre-loading or using a lighter model.

2. **Compute Resources**: CrewAI agents are compute-intensive. Ensure your Databricks Apps tier supports the required resources.

3. **Networking**: The app uses `SerperDevTool` which requires internet access. Ensure your workspace allows outbound connections.

4. **Alternative: Use Databricks Foundation Models**: For better integration, consider replacing direct OpenAI calls with Databricks Foundation Model APIs:
   - Use `DATABRICKS_HOST` and `DATABRICKS_TOKEN` for authentication
   - Configure CrewAI to use Databricks-hosted LLMs

### Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for LLM calls | Yes |
| `SERPER_API_KEY` | Serper API key for web search | Yes |
| `DATABRICKS_HOST` | Databricks workspace URL (auto-set in Apps) | Auto |
| `DATABRICKS_TOKEN` | Databricks access token (auto-set in Apps) | Auto |

### Troubleshooting

- **App fails to start**: Check logs in Databricks Apps console for missing dependencies
- **API key errors**: Verify secrets are properly configured and accessible
- **Timeout errors**: Increase app timeout settings or optimize agent configurations
- **Memory issues**: Whisper model requires significant memory; consider using "tiny" or "base" model
