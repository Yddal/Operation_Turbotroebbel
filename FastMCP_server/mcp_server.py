from fastmcp import FastMCP
import asyncio
from database_connection import DBConnection
from study_program_tools import TableStudyPrograms
from courses_tools import TableCourses

DATABASE = "fagskolen"
STUDY_PROGRAM_TABLE = "study_programs"
COURSES_TABLE = "courses"

mcp = FastMCP(name="MyServer")

async def main():
    # Use run_async() in async contexts
    await mcp.run_async(transport="http", port=8000)

if __name__ == "__main__":
    # establish database connection
    db_conn = DBConnection()

    # create isntances
    study_programs = TableStudyPrograms(db_conn, f"{DATABASE}.{STUDY_PROGRAM_TABLE}")
    courses = TableCourses(db_conn, f"{DATABASE}.{COURSES_TABLE}")

    # add methods as tools for study programs
    mcp.tool(study_programs.get_number_of_study_programs)
    mcp.tool(study_programs.get_study_program_categories)
    mcp.tool(study_programs.get_category_study_programs)
    mcp.tool(study_programs.get_study_programs_names)
    mcp.tool(study_programs.get_datafields)
    mcp.tool(study_programs.get_datafields_values)


    # add methods as tools for courses
    mcp.tool(courses.get_number_of_courses)
    mcp.tool(courses.get_corse_names)
    mcp.tool(courses.get_course_info)

    asyncio.run(main())
    