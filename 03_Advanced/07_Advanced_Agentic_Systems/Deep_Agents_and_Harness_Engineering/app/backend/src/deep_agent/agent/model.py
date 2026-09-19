"""LLM model factory."""

from databricks_langchain import ChatDatabricks

from deep_agent.config import MODEL_ENDPOINT, MODEL_TEMPERATURE


def build_model() -> ChatDatabricks:
    return ChatDatabricks(
        endpoint=MODEL_ENDPOINT,
        temperature=MODEL_TEMPERATURE,
    )
