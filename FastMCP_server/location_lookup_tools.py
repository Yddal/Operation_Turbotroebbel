import mysql.connector
from database_connection import DBConnection

"""
Methods for quering the Study Program location lookup table, to be exposed as tools in the MCP Server
"""

class TableStudyProgramLocationLookup:
    def __init__(self, conn: DBConnection, table: str):
        self.conn = conn
        self.table = table
    
    def get_study_program_location(self, location_id:int) -> str:
        """
        Get the name of location for a given location_id.
        Returns a name of locations.
        """
        results = self.conn.query(f"SELECT DISTINCT location_name FROM {self.table} WHERE location_id = '{location_id}'")
        if results:
            return results[0][0]
        else:
            return ""
    
   
    
if __name__ == "__main__":
    DATABASE = "fagskolen"
    STUDY_PROGRAM_LOCATION_TABLE = "study_place"

    # verify method outputs
    try:
        db_conn = DBConnection()
        programs = TableStudyProgramLocationLookup(db_conn, f"{DATABASE}.{STUDY_PROGRAM_LOCATION_TABLE}")

        results = programs.get_study_program_location(2)
        
        print(results)

    except mysql.connector.Error as err:
        print(f"Error: {err}")