import mysql.connector
from database_connection import DBConnection

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
    
    def get_corse_names(self) -> list:
        '''
        get the names of all the courses, returns list of all course names
        '''
        result = self.conn.query(f"SELECT course_title FROM {self.table}")
        return [title[0] for title in result]
    
if __name__ == "__main__":
    DATABASE = "fagskolen"
    COURSES_TABLE = "courses"
    try:
        db_conn = DBConnection()
        courses = TableCourses(db_conn, f"{DATABASE}.{COURSES_TABLE}")

        result = courses.get_number_of_courses()
        print(result)
        result = courses.get_corse_names()
        print(result)

    except mysql.connector.Error as err:
        print(f"Error: {err}")