import json
import random
from mcp.server.fastmcp import FastMCP

from student_repo import fetch_studieformer

# Initialize FastMCP server
server = FastMCP("fagskolen_mcp_server")

@server.prompt(
        title="Weather Information Prompt",
        description="Prompt to get weather information for a specified location",
)

@server.prompt(
    title="Developer Info Prompt",
    description="Prompt to get information about the developer of this server",
)

@server.tool(
    name="get_weather",
    title="Get Weather",
    description="Get weather information for a given location"
)

async def get_weather(location: str) -> str:
    """Get weather information for a given location.

    Args:
        location: Location to get weather for, e.g., city name, state, or coordinates
    
    """
    if not location:
        return "Location is required."
    
    # mock weather data
    conditions = [ "Sunny", "Rainy", "Cloudy", "Snowy" ]
    weather = {
        "location": location,
        "temperature": f"{random.randint(10, 90)}°F",
        "condition": random.choice(conditions),
    }
    return json.dumps(weather, ensure_ascii=False)

# Ny verktøy
@server.tool(
    name="get_developer_info",
    title="Get Developer Info",
    description="Get information about the developer of this server"
)

async def get_developer_info() -> str:
    """Get information about the developer of this server.

    Returns:
        A string containing developer information.
    """
    developer_info = {
        "name": "Your Name",
        "role": "Software Developer",
        "contact": "shahin@afk.no"
    }
    return json.dumps(developer_info, ensure_ascii=False)


@server.tool(
    name="get_studieformer",
    title="Get Studieformer",
    description="List study modes (studieformer) for fagskolen programs from the database"
)
async def get_studieformer() -> str:
    studieformer = fetch_studieformer()
    return json.dumps(studieformer, ensure_ascii=False)
