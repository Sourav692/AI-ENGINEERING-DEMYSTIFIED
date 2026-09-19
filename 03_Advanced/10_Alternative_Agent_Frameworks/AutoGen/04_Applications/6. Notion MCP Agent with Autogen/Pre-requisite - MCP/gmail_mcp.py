import requests
"""
This module provides a client for interacting with a Gmail MCP (Multi-Channel Platform) server API.
Classes:
    GmailMCPClient: A client for communicating with the Gmail MCP server to list and retrieve tool information.
GmailMCPClient:
    Methods:
        __init__(base_url, api_key=None):
            Initializes the client with the given base URL and optional API key for authentication.
        list_tools():
            Retrieves a list of available tools from the MCP server.
            Returns:
                list: A list of tool dictionaries, each containing tool metadata.
        get_tool(tool_id):
            Retrieves detailed information about a specific tool by its ID.
            Args:
                tool_id (str): The unique identifier of the tool.
            Returns:
                dict: A dictionary containing detailed information about the tool.
Example usage:
    - Instantiate the client with the MCP server URL and API key.
    - List all available tools.
    - Retrieve details for a specific tool.
# Example of possible tools that may be present:
# - {'id': 'send_email', 'name': 'Send Email'}
# - {'id': 'read_inbox', 'name': 'Read Inbox'}
# - {'id': 'search_emails', 'name': 'Search Emails'}
# - {'id': 'delete_email', 'name': 'Delete Email'}
# - {'id': 'list_labels', 'name': 'List Labels'}
"""

class GmailMCPClient:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})

    def list_tools(self):
        url = f"{self.base_url}/tools"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_tool(self, tool_id):
        url = f"{self.base_url}/tools/{tool_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

# Example usage:
if __name__ == "__main__":
    # Replace with your actual MCP server URL and API key if needed
    mcp_url = "https://your-gmail-mcp-server.com/api"
    api_key = "YOUR_API_KEY"

    client = GmailMCPClient(mcp_url, api_key)
    tools = client.list_tools()
    print("Available tools:")
    for tool in tools:
        print(f"- {tool['id']}: {tool['name']}")

    # To get details of a specific tool:
    if tools:
        tool_id = tools[0]['id']
        tool_details = client.get_tool(tool_id)
        print(f"\nDetails for tool {tool_id}:")
        print(tool_details)

