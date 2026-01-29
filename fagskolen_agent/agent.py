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

Verify_agent = Agent(
    #model='gemini-2.5-flash',
    model='gemini-2.5-flash-lite',
    name='Verify_agent',
    description="Verify the incoming information and send ut to the user",
    instruction="Your job is to verify that the question from the user has been answered. \
        if the question is not answered, refer the user to this website: https://fagskolen-viken.no/ ",
    )

Presenting_agent = Agent(
    #model='gemini-2.5-flash',
    model='gemini-2.5-flash-lite',
    name='Presenting_agent',
    description="Go through the data and structure it to be readable for a user.",
    instruction="You are a helpful assistant that structures incoming data to a presentable way for a human. \
        You will get information from the retriever_agent and structure it for humans to answer their questions.",
    sub_agents=[Verify_agent],
    )

retriver_agent = Agent(
    #model='gemini-2.5-flash',
    model='gemini-2.5-flash-lite',
    name='retriver_agent',
    description="Retrives information about the study programs and courses available at Fagskolen i Viken",
    instruction="You are responsible for retriving information about the study programs and courses at Fagskolen i Viken. \
        You can only retrieve the requested information using the provided tools. \
        Do not respond to other requests. \
        Return the information in a understandable format for a LLM and send it to the Presenting_agent subagent",
    tools=[toolset],
    sub_agents=[Presenting_agent],
    )

root_agent = Agent(
    #model='gemini-2.5-flash',
    model='gemini-2.5-flash-lite',
    name='Planner_agent',
    description="Understand what the user want and forward the information",
    instruction="You are a helpful assistant that answer questions about Fagskolen i Viken. \
        Your job is to structure the message to the retriever_agent subagent and ask for data based on user input. \
        Do not answer questions unrelated to Fagskolen i Viken studies and courses. \
        If you cannot retrieve any information refer the user to this website: https://fagskolen-viken.no/",
    sub_agents=[retriver_agent],
    )
