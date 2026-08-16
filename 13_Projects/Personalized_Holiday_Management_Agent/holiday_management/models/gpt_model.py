from autogen_ext.models.openai import OpenAIChatCompletionClient
from holiday_management.config.settings import OPENAI_API_KEY, MODEL_NAME
from dotenv import load_dotenv

load_dotenv()

model_client = OpenAIChatCompletionClient(
    model= MODEL_NAME,
    openai_api_key= OPENAI_API_KEY
    
)