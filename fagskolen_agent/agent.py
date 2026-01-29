from google.adk.agents.llm_agent import Agent
from google.adk.agents.sequential_agent import SequentialAgent
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

# models
GEMMA_3_1B = "gemma-3-1b-it"
GEMMA_3_4B = "gemma-3-4b-it"
GEMMA_3_12B = "gemma-3-12b-it"
GEMMA_3_27B = "gemma-3-27b-it"
GEMINI_2_5_FLASH = "gemini-2.5-flash"


model_verify     = GEMINI_2_5_FLASH
model_presenting = GEMINI_2_5_FLASH
model_retriver   = GEMINI_2_5_FLASH
model_root       = GEMINI_2_5_FLASH

Verify_agent = Agent(
    model=model_verify,
    name='Verify_agent',
    description="Verify the incoming information and send ut to the user",
    instruction="Your job is to verify that the question from the user has been answered. \
        if the question is not answered, refer the user to this website: https://fagskolen-viken.no/ ",
    )

Presenting_agent = Agent(
    model=model_presenting,
    name='Presenting_agent',
    description="Go through the data and structure it to be readable for a user.",
    instruction="You are a helpful assistant that structures incoming data to a presentable way for a human. \
        You will get information from the retriever_agent and structure it for humans to answer their questions.",
    )

retriver_agent = Agent(
    model=model_retriver,
    name='retriver_agent',
    description="Retrives information about the study programs and courses available at Fagskolen i Viken",
    instruction="You are responsible for retriving information about the study programs and courses at Fagskolen i Viken. \
        You can only retrieve the requested information using the provided tools. \
        Use the get_study_program_categories tool to get the different categories for the study programs. \
        Use the get_study_programs_names to get a complete list of the available study programs. \
        Use the get_datafields tool to get the names of the available datafields for a study program. \
        Use the get_datafields_values tool to get more information about a study. \
        Do not respond to other requests. \
        Return the information in a understandable format for a LLM and send it to the Presenting_agent subagent",
    tools=[toolset],
    )

input_agent = Agent(
    model=model_root,
    name='input_agent',
    description="Understand what the user want and forward the information",
    instruction="You are a helpful assistant that answer questions about Fagskolen i Viken. \
        Your job is to structure the message to the retriever_agent subagent and ask for data based on user input. \
        Do not answer questions unrelated to Fagskolen i Viken studies and courses. \
        If you cannot retrieve any information refer the user to this website: https://fagskolen-viken.no/",
    )


root_agent = SequentialAgent( 
    name="root_agent",
    sub_agents=[input_agent, retriver_agent, Presenting_agent, Verify_agent],
    description="Executes a sequence of code writing, reviewing, and refactoring.",  

)