from google.adk.agents.llm_agent import Agent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools import AgentTool
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

MCP_SERVER = "http://127.0.0.1:8001/mcp"

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

use_good_models = 1

if use_good_models == 1:
    model_verify     = GEMINI_2_5_FLASH
    model_presenting = GEMINI_2_5_FLASH
    model_retriver   = GEMINI_2_5_FLASH
    model_root       = GEMINI_2_5_FLASH
else:
    model_verify     = GEMMA_3_12B
    model_presenting = GEMMA_3_27B
    model_retriver   = GEMMA_3_4B
    model_root       = GEMMA_3_1B


input_agent = Agent(
    model=model_root,
    name='input_agent',
    description="Parses user input and emits a structured query for downstream agents (stored at output_key 'Question_from_user').",
    instruction=r"""You parse raw user messages about Fagskolen i Viken. \
    1) If the user query is unrelated to Fagskolen i Viken, set "unrelated": true and respond only with a short referral message and link: https://fagskolen-viken.no. \
    2) If related, extract and normalize intent fields into a concise JSON-like structure: {"query": "<canonical text>", "focus": "<program|course|general>", "filters": {...}}. \
    3) Do NOT call tools or browse the web. Output only the structured content (plain text or JSON) to be saved under `Question_from_user`.""",
    output_key= 'Question_from_user'
    )

retriver_agent = Agent(
    model=model_retriver,
    name='retriver_agent',
    description="Retrieves data about Fagskolen i Viken study programs and courses using only the provided tools.",
    instruction=r"""Your only job is to retrieve requested information using the listed tools. \
    - Input: {Question_from_user} \
    - Use exactly these tools and commands: get_study_program_categories, get_study_programs_names, get_study_program_datafields, get_study_program_datafields_values, get_course_datafields,  get_course_datafields_values, get_study_program_courseIDs, get_course_info_ID, get_study_program_location. \
    - For each tool call include arguments as required and preserve tool outputs verbatim. \
    - Output a structured result: {"status":"success"|"error","data":{...},"tool_calls":[{name, args, result}]} \
    - Do not invent facts or consult the web.
    - Only use the provided tools. \
    - Use the get_study_program_categories tool to get the different categories for the study programs. \
    - Use the get_study_programs_names to get a complete list of the available study programs. \
    - Use the get_study_program_datafields tool list the names of the available datafields for a study program. \
    - Use the get_study_program_datafields_values tool to get the values for a specific study program and datafields. \
    - Use the get_course_datafields tool list the names of the available datafields for a course. \
    - Use the get_course_datafields_values tool to get the values for a specific course and datafields. \
    - Use the get_study_program_courseIDs tool to get the course IDs for a study program, provide the study program name as argument. \
    - Use the get_course_info_ID tool to get information about a specific course, provide the course ID as argument. \
    - Use the get_study_program_location tool to get the location of a study program, provide the location_id data field as argument. \
    - Do not respond to other requests.""",
    tools=[toolset],
    output_key='retrieved_data'
    )

Verify_agent = Agent(
    model=model_verify,
    name='Verify_agent',
    description="Validate and confirm that retrieved data answers the user's query; produce a concise verified summary or indicate missing items.",
    instruction=r"""Input: {retrieved_data} and the original query (state['Question_from_user'] if available). \
    1) Check completeness and consistency: does retrieved_data answer the user's core question? \
    2) If information is missing or ambiguous, set {"answered": false, "reason": "<why>", "next_steps":"refer to https://fagskolen-viken.no or ask user for clarification"}. \
    3) If complete, set {"answered": true, "verified_information": <clean structured summary>} and remove tool artifacts. \
    4) Do NOT use the internet; do not invent missing details. \
    Output stored under `verified_information`.""",
    output_key='verified_information'
    )

Presenting_agent = Agent(
    model=model_presenting,
    name='Presenting_agent',
    description="Format verified information into concise, human-readable text for the user (bulleted summary, short answer + optional details).",
    instruction=r"""Input: {verified_information}.
    1) If answered==false: produce a short user-facing message explaining why, and provide the referral: https://fagskolen-viken.no or a short clarifying question to the user.
    2) If answered==true: produce a 2–6 sentence summary plus bullet points for key facts (program name, location, course IDs, brief course descriptions). Use plain text for the UI and include IDs/citations from the retrieved data.
    3) Keep it brief, readable, and neutral. Do not add external information.""",
    )

sequential_agent = SequentialAgent( 
    name="sequential_agent",
    sub_agents=[input_agent, retriver_agent, Verify_agent, Presenting_agent],
    description="Takes the user questions and answer them.",
)

question_tool = AgentTool(
    agent=sequential_agent,
)

root_agent = Agent(
    model=model_root,
    name='root_agent',
    description="Coordinator agent that routes user queries about Fagskolen i Viken to the question workflow or refers unrelated queries to the official site.",
    instruction=r"""You are a polite, brief coordinator for Fagskolen i Viken questions. 
    1) If the user's query is about Fagskolen i Viken (programs, courses, locations), call the `question_tool` (which implements the sequential workflow) and return the exact final output produced by that tool.
    2) If unrelated, reply with a short referral: "I can only answer questions about Fagskolen i Viken. See https://fagskolen-viken.no for more info."
    3) Do not fetch external web info or alter the sequential workflow's final output.""",
    tools=[question_tool]
    )