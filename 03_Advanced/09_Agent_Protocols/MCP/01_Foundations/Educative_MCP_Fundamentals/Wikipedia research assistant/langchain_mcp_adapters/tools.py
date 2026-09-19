"""Tools adapter for MCP to LangChain integration"""
from typing import Any, List
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, create_model, Field
from mcp import ClientSession


async def load_mcp_tools(session: ClientSession) -> List[StructuredTool]:
    """
    Load tools from an MCP server session and convert them to LangChain tools.
    
    Args:
        session: An initialized MCP ClientSession
        
    Returns:
        List of LangChain StructuredTool objects
    """
    # Get the list of tools from the MCP server
    response = await session.list_tools()
    tools = []
    
    for tool in response.tools:
        # Create a closure to capture the tool name and session
        def make_tool_func(tool_name: str, mcp_session: ClientSession):
            async def tool_func(**kwargs: Any) -> str:
                """Dynamic tool function that calls MCP server"""
                try:
                    result = await mcp_session.call_tool(tool_name, arguments=kwargs)
                    # Extract content from the result
                    if result.content:
                        # Handle different content types
                        content_parts = []
                        for content in result.content:
                            if hasattr(content, 'text'):
                                content_parts.append(content.text)
                            elif hasattr(content, 'data'):
                                content_parts.append(str(content.data))
                            else:
                                content_parts.append(str(content))
                        return "\n".join(content_parts)
                    return str(result)
                except Exception as e:
                    return f"Error calling tool {tool_name}: {str(e)}"
            return tool_func
        
        # Create the tool function with closure
        tool_func = make_tool_func(tool.name, session)
        
        # Parse the input schema to create Pydantic model
        input_schema = tool.inputSchema
        
        # Create fields for the Pydantic model
        fields = {}
        if input_schema and 'properties' in input_schema:
            for prop_name, prop_details in input_schema['properties'].items():
                field_type = str  # Default type
                field_description = prop_details.get('description', '')
                field_default = ...  # Required by default
                
                # Determine if field is required
                required_fields = input_schema.get('required', [])
                if prop_name not in required_fields:
                    field_default = None
                    field_type = str | None
                
                fields[prop_name] = (field_type, Field(default=field_default, description=field_description))
        
        # Create the Pydantic model dynamically
        if fields:
            ArgsSchema = create_model(
                f"{tool.name}Args",
                **fields
            )
        else:
            # No arguments
            ArgsSchema = None
        
        # Create the LangChain tool
        langchain_tool = StructuredTool(
            name=tool.name,
            description=tool.description or f"MCP tool: {tool.name}",
            coroutine=tool_func,
            args_schema=ArgsSchema
        )
        
        tools.append(langchain_tool)
    
    return tools
