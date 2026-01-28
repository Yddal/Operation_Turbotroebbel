from fastmcp import FastMCP
import asyncio
from database_connection import DBConnection
from courses_tools import TableCourses

DATABASE = "fagskolen"
COURSES_TABLE = "courses"

mcp = FastMCP(name="MyServer")

async def main():
    # Use run_async() in async contexts
    await mcp.run_async(transport="http", port=8000)

if __name__ == "__main__":
    db_conn = DBConnection()
    courses = TableCourses(db_conn, f"{DATABASE}.{COURSES_TABLE}")

    # add methods as tools
    mcp.tool(courses.get_number_of_courses)
    mcp.tool(courses.get_corse_names)

    asyncio.run(main())