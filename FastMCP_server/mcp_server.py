"""
MCP server exposing Fagskolen i Viken database query tools.

Purpose:
    Provide tools for agent workflows to query study programs, courses, course
    lookups and locations. All tools return JSON-serializable dicts of the
    form: {"status": "success"|"error"|"not_found", "result": ..., "error_message": ...}.

Exposed tools (examples):
    - get_study_program_categories
    - get_study_programs_names
    - get_category_study_programs
    - get_datafields / get_datafields_values
    - get_all_course_titles / get_course_ID / get_datafields_values
    - get_study_program_courseIDs
    - get_study_program_location

Notes:
    - Tools should validate inputs and avoid returning non-JSON types.
    - Ensure parameterized queries are used to prevent SQL injection.
"""

from fastmcp import FastMCP
import asyncio
from database_connection import DBConnection
from study_program_tools import TableStudyPrograms
from courses_tools import TableCourses
from courseid_lookup_tools import TableStudyCoursesLookup
from location_lookup_tools import TableStudyProgramLocationLookup

DATABASE = "fagskolen"
STUDY_PROGRAM_TABLE = "study_programs"
COURSES_TABLE = "courses"
STUDY_PROGRAM_COURSE_ID_TABLE = "lookuptalbe_study_course"
STUDY_PROGRAM_LOCATION_TABLE = "study_place"

mcp = FastMCP(name="MyServer")

async def main():
    # Use run_async() in async contexts
    await mcp.run_async(transport="http", port=8001)

if __name__ == "__main__":
    # establish database connection
    db_conn = DBConnection()

    # add methods as tools for study programs
    study_programs = TableStudyPrograms(db_conn, f"{DATABASE}.{STUDY_PROGRAM_TABLE}")
    mcp.tool(study_programs.get_number_of_study_programs)
    mcp.tool(study_programs.get_study_program_categories)
    mcp.tool(study_programs.get_category_study_programs)
    mcp.tool(study_programs.get_study_programs_names)
    mcp.tool(study_programs.get_study_program_datafields)
    mcp.tool(study_programs.get_study_program_datafields_values)

    # add methods as tools for courses
    courses = TableCourses(db_conn, f"{DATABASE}.{COURSES_TABLE}")
    mcp.tool(courses.get_number_of_courses)
    mcp.tool(courses.get_all_course_titles)
    mcp.tool(courses.get_course_ID)
    mcp.tool(courses.get_course_datafields)
    mcp.tool(courses.get_course_datafields_values)
    
    # add methods as tools for study program course lookup
    courseid_lookup = TableStudyCoursesLookup(db_conn, f"{DATABASE}.{STUDY_PROGRAM_COURSE_ID_TABLE}")
    mcp.tool(courseid_lookup.get_study_program_courseIDs)

    # add methods as tools for study program location lookup
    location_lookup = TableStudyProgramLocationLookup(db_conn, f"{DATABASE}.{STUDY_PROGRAM_LOCATION_TABLE}")
    mcp.tool(location_lookup.get_study_program_location)

    asyncio.run(main())
    