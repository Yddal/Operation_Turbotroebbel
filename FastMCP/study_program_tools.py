import mysql.connector
from database_connection import DBConnection

class TableStudyPrograms:
    def __init__(self, conn: DBConnection, table: str):
        self.conn = conn
        self.table = table

    def get_number_of_study_programs(self) -> int:
        '''
        get number of entries in the study program table, returns int
        '''
        result = self.conn.query(f"SELECT COUNT(*) FROM {self.table}")
        return result[0][0]
    
    def get_study_programs_names(self) -> list:
        '''
        get the names of all the study programs, returns list of all study program names
        '''
        result = self.conn.query(f"SELECT study_title FROM {self.table}")
        return [title[0] for title in result]
    
if __name__ == "__main__":
    DATABASE = "fagskolen"
    STUDY_PROGRAM_TABLE = "study_programs"
    try:
        db_conn = DBConnection()
        courses = TableStudyPrograms(db_conn, f"{DATABASE}.{STUDY_PROGRAM_TABLE}")

        result = courses.get_number_of_study_programs()
        print(result)
        result = courses.get_study_programs_names()
        print(result)

    except mysql.connector.Error as err:
        print(f"Error: {err}")