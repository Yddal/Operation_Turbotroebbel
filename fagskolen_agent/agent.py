from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

MCP_SERVER = "http://127.0.0.1:8000/mcp"

toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(    
        url=MCP_SERVER,     
        #headers={"Authorization": "Bearer your-auth-token"}
    ),
)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="Tells the current weather in a specified city.",
    instruction="You are a helpful assistant that tells current weather or GPS coordiantes for a city. \
        You can only tell the weather at the moment. You can only tell the GPS coordiantes for a given location or city. \
        Use the get_coordinates to get GPS coordinates for a location. \
        Provide the weather tool with GPS coordiantes to get the weather for a city.",
    tools=[toolset],
    )