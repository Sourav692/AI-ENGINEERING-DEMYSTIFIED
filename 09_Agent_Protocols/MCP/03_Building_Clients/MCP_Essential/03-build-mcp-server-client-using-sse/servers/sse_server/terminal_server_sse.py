#!/usr/bin/env python

"""
terminal_server_sse.py

This file demonstrates how to build an MCP (Model Context Protocol) server using Server-Sent Events (SSE).
SSE is a web standard that enables real-time, one-way communication from server to client over HTTP.

Why SSE for MCP?
- SSE maintains a persistent HTTP connection, perfect for streaming responses
- Built on standard HTTP, so it works through firewalls and proxies
- Simpler than WebSockets for one-way communication (server → client)
- Ideal for AI agents that need to push updates, results, or streaming responses

Architecture Overview:
The flow works like this:
1. Client (browser/agent) opens SSE connection to /sse endpoint
2. Server maintains this connection and waits for tool calls
3. Client sends tool requests via POST to /messages/ endpoint
4. Server processes the tool call and streams results back via the SSE connection
5. This enables real-time, bidirectional communication over HTTP

Key Components:
- FastMCP: Simplifies tool definition with decorators (@mcp.tool())
- SseServerTransport: Handles the SSE protocol and message routing
- Starlette: Lightweight ASGI web framework for HTTP handling
- Uvicorn: High-performance ASGI server
"""

#   Architecture Diagram:
#   
#   [ MCP Client / AI Agent ]
#            |
#     (1) Opens SSE connection to /sse
#            |
#   [ Uvicorn ASGI Server ]
#            |
#     (2) Routes requests through Starlette
#            |
#    [ Starlette Web App ]
#            |
#     (3) Handles /sse and /messages/ endpoints
#            |
#    [ SseServerTransport ]
#            |
#     (4) Manages SSE protocol and message routing
#            |
#     [ FastMCP Server ]
#            |
#     (5) Executes @mcp.tool() functions
#            |
#   [ Your Tools: run_command, add_numbers ]

import os
import subprocess  # For executing shell commands in the run_command tool
from mcp.server.fastmcp import FastMCP  # High-level wrapper that simplifies MCP server creation
from mcp.server import Server  # Core MCP server implementation (used internally by FastMCP)
from mcp.server.sse import SseServerTransport  # SSE transport layer for real-time communication

from starlette.applications import Starlette  # Lightweight ASGI web framework
from starlette.routing import Route, Mount  # URL routing components
from starlette.requests import Request  # HTTP request wrapper

import uvicorn  # Production-ready ASGI server

# --------------------------------------------------------------------------------------
# STEP 1: Initialize the MCP Server
# --------------------------------------------------------------------------------------
# FastMCP acts as a decorator-based wrapper around the core MCP server
# It allows us to define tools using simple @mcp.tool() decorators
mcp = FastMCP("terminal")  # "terminal" is the server identifier for MCP protocol

# Working directory for shell commands - this is where all commands will be executed
# In production, you might want to make this configurable or sandboxed
DEFAULT_WORKSPACE = "/root/mcp/workspace"

# --------------------------------------------------------------------------------------
# TOOL 1: Shell Command Execution
# --------------------------------------------------------------------------------------
@mcp.tool()
async def run_command(command: str) -> str:
    """
    Executes shell commands in a controlled environment.

    Example usages:
    - List files: 'ls'
    - Print working directory: 'pwd'
    - Create a file: 'echo "Hello" > file.txt'
    - Show file contents: 'cat file.txt'
    - Remove a file: 'rm file.txt'

    Args:
        command (str): Shell command to execute

    Returns:
        str: Output from the command
    """
    try:
        # subprocess.run() executes the command in a controlled manner
        result = subprocess.run(
            command,                    # The command string to execute
            shell=True,                 # Enable shell interpretation (allows pipes, etc.)
            cwd=DEFAULT_WORKSPACE,      # Set working directory
            capture_output=True,        # Capture both stdout and stderr
            text=True                   # Return strings instead of bytes
        )
        
        # Return stdout if available, otherwise stderr (for error messages)
        return result.stdout or result.stderr
    except Exception as e:
        # Handle any unexpected errors (permissions, invalid commands, etc.)
        return f"Error executing command: {str(e)}"


# --------------------------------------------------------------------------------------
# TOOL 2: Mathematical Operations
# --------------------------------------------------------------------------------------
@mcp.tool()
async def add_numbers(a: float, b: float) -> float:
    """
    Simple mathematical addition tool.
    
    This demonstrates how to create tools with multiple parameters and type hints.
    MCP automatically handles parameter validation and type conversion based on
    the function signature.

    Args:
        a (float): First number to add
        b (float): Second number to add

    Returns:
        float: Sum of the two input numbers
    """
    return a + b


# --------------------------------------------------------------------------------------
# STEP 2: Create the Web Application Layer
# --------------------------------------------------------------------------------------
def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """
    Creates a Starlette web application that exposes MCP tools via SSE.
    
    This function sets up two critical endpoints:
    1. /sse - For establishing the persistent SSE connection
    2. /messages/ - For receiving tool call requests via POST
    
    The SSE transport handles the protocol details, while Starlette manages HTTP routing.

    Args:
        mcp_server (Server): The core MCP server instance containing our tools
        debug (bool): Enable detailed logging for development

    Returns:
        Starlette: Configured web application ready to serve MCP requests
    """
    
    # Create the SSE transport layer
    # "/messages/" is the base path where clients send tool requests
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        """
        Handles new SSE client connections.
        
        This is where the magic happens:
        1. Client connects to /sse endpoint
        2. We establish an SSE connection (persistent HTTP connection)
        3. We create read/write streams for bidirectional communication
        4. We hand these streams to the MCP server for protocol handling
        
        The connection stays open until the client disconnects or an error occurs.
        """
        
        # sse.connect_sse() creates the SSE connection and returns communication streams
        async with sse.connect_sse(
            request.scope,      # ASGI scope (contains request metadata)
            request.receive,    # ASGI receive callable (for incoming data)
            request._send,      # ASGI send callable (for outgoing SSE events)
        ) as (read_stream, write_stream):
            
            # Hand off the streams to the MCP server for protocol handling
            # The MCP server will:
            # - Send initialization messages
            # - Listen for tool calls on read_stream
            # - Send responses via write_stream
            # - Handle all MCP protocol details
            await mcp_server.run(
                read_stream,                                    # For receiving tool requests
                write_stream,                                   # For sending tool responses
                mcp_server.create_initialization_options(),     # Server capabilities/metadata
            )

    # Configure the Starlette application with our endpoints
    return Starlette(
        debug=debug,    # Enable debug mode for development
        routes=[
            # SSE endpoint: Clients connect here to establish the persistent connection
            Route("/sse", endpoint=handle_sse),
            
            # Messages endpoint: Clients POST tool requests here
            # The SSE transport automatically routes these to the appropriate connection
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


# --------------------------------------------------------------------------------------
# STEP 3: Server Startup and Configuration
# --------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Extract the underlying MCP server from our FastMCP wrapper
    # FastMCP is a convenience layer; the real server is stored internally
    mcp_server = mcp._mcp_server  # Access the core server instance

    # Set up command-line argument parsing for flexible deployment
    import argparse
    parser = argparse.ArgumentParser(description='Run MCP Server with SSE Transport')
    parser.add_argument('--host', default='0.0.0.0', 
                       help='Host address to bind to (0.0.0.0 for all interfaces)')
    parser.add_argument('--port', type=int, default=8081, 
                       help='Port number to listen on')
    args = parser.parse_args()

    # Create the Starlette web application with our MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    print(f"Starting MCP SSE Server...")
    print(f"SSE endpoint: http://{args.host}:{args.port}/sse")
    print(f"Messages endpoint: http://{args.host}:{args.port}/messages/")
    print(f"Available tools: run_command, add_numbers")
    print(f"Clients can connect via SSE and call tools in real-time!")

    # Launch the server using Uvicorn (production-ready ASGI server)
    uvicorn.run(
        starlette_app,      # The Starlette app we created
        host=args.host,     # Bind address
        port=args.port      # Port number
    )