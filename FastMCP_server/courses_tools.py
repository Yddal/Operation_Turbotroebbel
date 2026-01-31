import mysql.connector
from database_connection import DBConnection

"""
Methods for quering the Courses table, to be exposed as tools in the MCP Server
"""

class TableCourses:
    def __init__(self, conn: DBConnection, table: str):
        self.conn = conn
        self.table = table

    def get_number_of_courses(self) -> int:
        '''
        get number of entries in the courses table, returns int
        '''
        result = self.conn.query(f"SELECT COUNT(*) FROM {self.table}")
        return result[0][0]
    
    def get_all_course_titles(self) -> list:
        '''
        get the title of all the courses, returns list of all course titles
        '''
        result = self.conn.query(f"SELECT course_title FROM {self.table}")
        return [title[0] for title in result]
    

    def get_course_ID(self, course_title) -> list:
        """
        Get all information about the study. Send the filter search for what you want from the database in the variable course_title
        """
        result = self.conn.query(f'SELECT course_id FROM {self.table} WHERE course_title = "{course_title}"')

        return result
    
    def get_datafields(self) -> list[str]:
        """
        Get the names of all the available datafields for a course.
        """
        results = self.conn.query(f"DESCRIBE {self.table}")
        return [result[0] for result in results[1:]]


    def get_datafields_values(self, course_id:str, fields: list[str]) -> dict[str,str]:
        '''
        Returns the values of datafiels for a course.
        Two paramterers must be provided.
        The first parameter is the ID of the course as a string.
        The Second parameter is a list of the names for the requested datafields as a list of strings.
        Returns a dictonary with all the datafield names and values.
        '''
        result = self.conn.query(f'SELECT {",".join(fields)} FROM {self.table} WHERE course_id = "{course_id}"')
        if not result:
            return {}
        return dict(zip(fields,result[0]))
    
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
        #result = courses.get_datafields()
        result = courses.get_datafields_values("01TD01B", ["credits"])
        
        print(result)


    except mysql.connector.Error as err:
        print(f"Error: {err}")