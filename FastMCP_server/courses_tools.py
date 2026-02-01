import mysql.connector
from database_connection import DBConnection

"""
Methods for quering the Courses table, to be exposed as tools in the MCP Server
"""

class TableCourses:
    def __init__(self, conn: DBConnection, table: str):
        self.conn = conn
        self.table = table

    def get_number_of_courses(self) -> dict:
        """
        One-line: Return the number of entries in the courses table.

        Parameters:
            None

        Returns:
            dict: {"status":"success"|"error", "result": int, "error_message": str (optional)}

        Example:
            {"status":"success","result": 124}
        """
        result = self.conn.query(f"SELECT COUNT(*) FROM {self.table}")
        if not result:
            return {"status":"error", "error_message":"Query returned no results"}
        return   {"status":"success", "result": int(result[0][0])}
    
    def get_all_course_titles(self) -> dict:
        """
        One-line: Return a list of all course titles.

        Parameters:
            None

        Returns:
            dict: {"status":"success"|"error", "result": list[str], "error_message": str (optional)}

        Example:
            {"status":"success","result":["Apputvikling","Psykisk helsearbeid"]}
        """
        result = self.conn.query(f"SELECT course_title FROM {self.table}")
        if not result:
            return {"status":"error", "error_message":"Query returned no results"}
        return {"status":"success", "result": [title[0] for title in result]}
    

    def get_course_ID(self, course_title: str) -> dict:
        """
        One-line: Return course IDs for a given course title (exact match).

        Parameters:
            course_title (str): Exact course title to search for.

        Returns:
            dict: {"status":"success"|"error", "result": list[str], "error_message": str (optional)}

        Example:
            {"status":"success","result":["01TD01B"]}

        Notes:
            - If not found, return {"status":"success","result":[]}.
            - Use parameterized queries to prevent SQL injection.
        """
        result = self.conn.query(f'SELECT course_id FROM {self.table} WHERE course_title = "{course_title}"')
        if not result:
            return {"status":"error", "error_message":"Course not found"}
        return {"status":"success", "result": [course[0] for course in result]}
    

    def get_course_datafields(self) -> dict:
        """
        One-line: Return available data field names for the courses table.

        Parameters:
            None

        Returns:
            dict: {"status":"success"|"error", "result": list[str], "error_message": str (optional)}

        Example:
            {"status":"success","result":["course_id","course_title","credits"]}
        """
        results = self.conn.query(f"DESCRIBE {self.table}")
        if not results:
            return {"status":"error", "error_message":"Query returned no results"}
        return {"status":"success", "result": [result[0] for result in results[1:]]}


    def get_course_datafields_values(self, course_id: str, fields: list[str]) -> dict:
        """
        One-line: Return requested data field values for a course.

        Parameters:
            course_id (str): Course ID to query.
            fields (list[str]): List of column names to retrieve.

        Returns:
            dict: {"status":"success"|"error", "result": dict(field_name->value), "error_message": str (optional)}

        Example:
            {"status":"success","result":{"credits":"5"}}

        Notes:
            - If course not found, return {"status":"success","result":{}}.
            - Validate fields and use parameterized queries.
        """
        result = self.conn.query(f'SELECT {",".join(fields)} FROM {self.table} WHERE course_id = "{course_id}"')
        if not result:
            return {"status":"error", "error_message":"Course not found"}
        return {"status":"success", "result": dict(zip(fields,result[0]))}
    
if __name__ == "__main__":

    DATABASE = "fagskolen"
    COURSES_TABLE = "courses"

    # verify method outputs
    try:
        db_conn = DBConnection()
        courses = TableCourses(db_conn, f"{DATABASE}.{COURSES_TABLE}")

        #result = courses.get_number_of_courses()
        #result = courses.get_all_course_titles()
        #result = courses.get_course_ID("Apputvikling")
        #result = courses.get_course_datafields()
        result = courses.get_course_datafields_values("01TD01B", ["credits"])
        
        print(result)


    except mysql.connector.Error as err:
        print(f"Error: {err}")