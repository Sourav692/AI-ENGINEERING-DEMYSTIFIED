#!/usr/bin/env python
"""
langchain_mcp_client.py
This file implements an MCP client using LangChain's MCP adapters.
"""

# 1. Imports and Setup
import asyncio                        # For asynchronous operations
import os                             # To access environment variables
import sys                            # For command-line argument processing
import json                           # For pretty-printing JSON output
from contextlib import AsyncExitStack # Ensures all async resources are properly closed
from typing import Optional, List     # For type hints
# MCP Client Imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
# LangChain Imports
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
# Environment Setup
from dotenv import load_dotenv
load_dotenv()

# 2. Custom JSON Encoder
class CustomEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles objects with a 'content' attribute.
    
    This helps us display agent responses in a readable format.
    """
    def default(self, o):
        if hasattr(o, "content"):
            return {"type": o.__class__.__name__, "content": o.content}
        return super().default(o)

# 3. LLM Configuration
# Create an instance of the Google Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001",     # You can also use "gemini-2.0-flash-exp"
    temperature=0,              # 0 = deterministic output; increase for creativity
    max_retries=2,              # Automatically retry API calls for transient errors
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# 4. Server Parameters: Command line argument processing
if len(sys.argv) < 2:
    print("Usage: python langchain_mcp_client.py <path_to_server_script>")
    sys.exit(1)
server_script = sys.argv[1]

# Configure MCP server parameters
server_params = StdioServerParameters(
    command="python" if server_script.endswith(".py") else "node",
    args=[server_script],
)
# Global variable to hold the active MCP session
mcp_client = None

# 5. Main Agent Function
"""
Here's where the magic happens - notice how simple this is compared to our previous implementation:
"""

async def run_agent():
    """
    Connect to the MCP server, load MCP tools, create a React agent, 
    and run an interactive chat loop.
    """
    global mcp_client
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Store session for tool access
            mcp_client = type("MCPClientHolder", (), {"session": session})()
            
            # Load MCP tools using LangChain's adapter - this is the key!
            tools = await load_mcp_tools(session)
            
            # Create a React agent with the LLM and tools
            agent = create_react_agent(llm, tools)
            
            print("MCP Client Started! Type 'quit' to exit.")
            while True:
                query = input("\nQuery: ").strip()
                if query.lower() == "quit":
                    break
                
                # Invoke the agent asynchronously
                response = await agent.ainvoke({"messages": query})
                
                # Format and print the response
                try:
                    formatted = json.dumps(response, indent=2, cls=CustomEncoder)
                except Exception as e:
                    formatted = str(response)
                print("\nResponse:")
                print(formatted)

# 6. Main Execution
if __name__ == "__main__":
    asyncio.run(run_agent())