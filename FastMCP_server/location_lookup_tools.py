import mysql.connector
from database_connection import DBConnection

"""
Methods for quering the Study Courses lookup table, to be exposed as tools in the MCP Server
"""

class TableStudyCoursesLookup:
    def __init__(self, conn: DBConnection, table: str):
        self.conn = conn
        self.table = table
    
    def get_study_program_courseIDs(self, study_title:str) -> list[str]:
        """
        Get a list of course IDs for a given study program title.
        Returns a list of course IDs. Empty list if no courses found.
        """
        results = self.conn.query(f"SELECT DISTINCT course_id FROM {self.table} WHERE study_title = '{study_title}'")
        return [result[0] for result in results]
    
   
    
if __name__ == "__main__":
    DATABASE = "fagskolen"
    STUDY_PROGRAM_COURSE_ID_TABLE = "lookuptalbe_study_course"

    # verify method outputs
    try:
        db_conn = DBConnection()
        programs = TableStudyCoursesLookup(db_conn, f"{DATABASE}.{STUDY_PROGRAM_COURSE_ID_TABLE}")

        results = programs.get_study_program_courseIDs("Elkraft")
        
        print(results)

    except mysql.connector.Error as err:
        print(f"Error: {err}")