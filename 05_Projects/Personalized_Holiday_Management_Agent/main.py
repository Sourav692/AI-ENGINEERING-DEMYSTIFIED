from autogen_agentchat.messages import TextMessage
from holiday_management.teams.holiday_team import team 
import asyncio

async def main():
    task = TextMessage(content="I want to plan a trip to Paris for 5 days. Can you help me with that?", source="User")
    response = await team.run(task=task)

    for message in response.messages:
        print(f"{message.source}: {message.content}")


if __name__ == "__main__":
    asyncio.run(main())