from autogen_agentchat.agents import AssistantAgent
from holiday_management.models.gpt_model import model_client


researcher_agent = AssistantAgent(
    name="Holidaya_Researcher",
    description="A Holiday researcher agent that helps users research about their holiday destinations.",
    model_client=model_client,
    system_message="You are a Holiday researcher agent. Your task is to help users research about their holiday destinations by providing information about attractions, local culture, and travel tips."
)