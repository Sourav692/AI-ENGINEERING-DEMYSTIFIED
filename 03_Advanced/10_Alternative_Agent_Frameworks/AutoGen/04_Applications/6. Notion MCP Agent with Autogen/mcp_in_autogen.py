from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio 
import time
from autogen_ext.tools.mcp import McpWorkbench,StdioServerParams
import os

async def main(main_task ):

    params = StdioServerParams(
    command = 'uvx',
    args=['mcp-server-time','--local-timezone=America/New_York']
    )

    model = OpenAIChatCompletionClient(
        model='gpt-4o',
        api_key=os.getenv('OPENAI_API_KEY')
    )

    async with McpWorkbench(server_params=params) as workbench:

        # tools = await workbench.list_tools()
        # print(tools)
        agent = AssistantAgent(
            name='Agent',
            system_message='You are a helpful assistant',
            model_client=model,
            workbench=workbench,
            reflect_on_tool_use=True
        )


        task = 'What is the time right now in London ?'

        async for message in agent.run_stream(task=main_task):
            print("-"*100)
            print(message)
            print('-'*100)

if(__name__=='__main__'):
    main_task = 'Get time in London'
    asyncio.run(main(main_task))