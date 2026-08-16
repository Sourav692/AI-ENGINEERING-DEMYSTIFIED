[26682] Using existing client port: 9553
[26682] [26682] Connecting to remote server: https://mcp.notion.com/mcp
[26682] Using transport strategy: http-first
[26682] Connected to remote server using StreamableHTTPClientTransport
[26682] Local STDIO server running
[26682] Proxy established successfully between local STDIO and remote StreamableHTTPClientTransport
[26682] Press Ctrl+C to exit
[26682] [Local→Remote] initialize
[26682] {
  "jsonrpc": "2.0",
  "id": 0,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {},
    "clientInfo": {
      "name": "mcp (via mcp-remote 0.1.18)",
      "version": "0.1.0"
    }
  }
}
[26682] [Remote→Local] 0
[26682] [Local→Remote] notifications/initialized
[26682] [Local→Remote] tools/list
[26682] [Remote→Local] 1
[26682] 
Shutting down...
----------------------------------------------------------------------------------------------------
id='2a54f3dc-60b1-4853-8528-e46064189346' source='user' models_usage=None metadata={} created_at=datetime.datetime(2025, 8, 3, 5, 30, 50, 340493, tzinfo=datetime.timezone.utc) content='Create a new page titled  "PageFromMCPNotion"' type='TextMessage'
----------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------
id='cd7c41cf-fd60-49ee-97e8-63dbc683b51b' source='notion_agent' models_usage=RequestUsage(prompt_tokens=6405, completion_tokens=354) metadata={} created_at=datetime.datetime(2025, 8, 3, 5, 30, 55, 299341, tzinfo=datetime.timezone.utc) content=[FunctionCall(id='call_lS4UzD4am33nUGUzleeCywdR', arguments='{"pages":[{"properties":{"title":"PageFromMCPNotion"}}]}', name='create-pages')] type='ToolCallRequestEvent'
----------------------------------------------------------------------------------------------------
[26708] Using existing client port: 9553
[26708] [26708] Connecting to remote server: https://mcp.notion.com/mcp
[26708] Using transport strategy: http-first
[26708] Connected to remote server using StreamableHTTPClientTransport
[26708] Local STDIO server running
[26708] Proxy established successfully between local STDIO and remote StreamableHTTPClientTransport
[26708] Press Ctrl+C to exit
[26708] [Local→Remote] initialize
[26708] {
  "jsonrpc": "2.0",
  "id": 0,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {},
    "clientInfo": {
      "name": "mcp (via mcp-remote 0.1.18)",
      "version": "0.1.0"
    }
  }
}
[26708] [Remote→Local] 0
[26708] [Local→Remote] notifications/initialized
[26708] [Local→Remote] tools/call
[26708] [Remote→Local] 1
[26708] [Local→Remote] tools/list
[26708] [Remote→Local] 2
[26708] 
Shutting down...
----------------------------------------------------------------------------------------------------
id='bd165ca1-5c70-41e9-ad79-c8d76fd394b9' source='notion_agent' models_usage=None metadata={} created_at=datetime.datetime(2025, 8, 3, 5, 31, 0, 288284, tzinfo=datetime.timezone.utc) content=[FunctionExecutionResult(content='[{"type": "text", "text": "{\\"pages\\":[{\\"id\\":\\"244b4980-6e95-8171-8213-f9961bb45b6b\\",\\"url\\":\\"https://www.notion.so/244b49806e9581718213f9961bb45b6b\\",\\"properties\\":{\\"title\\":\\"PageFromMCPNotion\\"}}]}", "annotations": null}]', name='create-pages', call_id='call_lS4UzD4am33nUGUzleeCywdR', is_error=False)] type='ToolCallExecutionEvent'
----------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------
id='1ed5460e-6536-4bf4-82d0-3d8a13e06954' source='notion_agent' models_usage=RequestUsage(prompt_tokens=198, completion_tokens=62) metadata={} created_at=datetime.datetime(2025, 8, 3, 5, 31, 2, 45318, tzinfo=datetime.timezone.utc) content='Your new page "PageFromMCPNotion" has been created. You can access it here:  \nhttps://www.notion.so/244b49806e9581718213f9961bb45b6b  \nTERMINATE' type='TextMessage'
----------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------
messages=[TextMessage(id='2a54f3dc-60b1-4853-8528-e46064189346', source='user', models_usage=None, metadata={}, created_at=datetime.datetime(2025, 8, 3, 5, 30, 50, 340493, tzinfo=datetime.timezone.utc), content='Create a new page titled  "PageFromMCPNotion"', type='TextMessage'), ToolCallRequestEvent(id='cd7c41cf-fd60-49ee-97e8-63dbc683b51b', source='notion_agent', models_usage=RequestUsage(prompt_tokens=6405, completion_tokens=354), metadata={}, created_at=datetime.datetime(2025, 8, 3, 5, 30, 55, 299341, tzinfo=datetime.timezone.utc), content=[FunctionCall(id='call_lS4UzD4am33nUGUzleeCywdR', arguments='{"pages":[{"properties":{"title":"PageFromMCPNotion"}}]}', name='create-pages')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(id='bd165ca1-5c70-41e9-ad79-c8d76fd394b9', source='notion_agent', models_usage=None, metadata={}, created_at=datetime.datetime(2025, 8, 3, 5, 31, 0, 288284, tzinfo=datetime.timezone.utc), content=[FunctionExecutionResult(content='[{"type": "text", "text": "{\\"pages\\":[{\\"id\\":\\"244b4980-6e95-8171-8213-f9961bb45b6b\\",\\"url\\":\\"https://www.notion.so/244b49806e9581718213f9961bb45b6b\\",\\"properties\\":{\\"title\\":\\"PageFromMCPNotion\\"}}]}", "annotations": null}]', name='create-pages', call_id='call_lS4UzD4am33nUGUzleeCywdR', is_error=False)], type='ToolCallExecutionEvent'), TextMessage(id='1ed5460e-6536-4bf4-82d0-3d8a13e06954', source='notion_agent', models_usage=RequestUsage(prompt_tokens=198, completion_tokens=62), metadata={}, created_at=datetime.datetime(2025, 8, 3, 5, 31, 2, 45318, tzinfo=datetime.timezone.utc), content='Your new page "PageFromMCPNotion" has been created. You can access it here:  \nhttps://www.notion.so/244b49806e9581718213f9961bb45b6b  \nTERMINATE', type='TextMessage')] stop_reason="Text 'TERMINATE' mentioned"
----------------------------------------------------------------------------------------------------
(.venv) mayank@Mayanks-MacBook-Pro Autogen % 