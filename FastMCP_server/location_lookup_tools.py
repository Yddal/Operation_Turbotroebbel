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
        One-line: Return the name of the study location for a given location ID.

        Parameters:
            location_id (int): Unique integer id for the location.

        Returns:
            dict: {"status":"success"|"not_found"|"error", "result": str|None, "error_message": str (optional)}

        Example:
            {"status":"success","result":"Drammen campus"}
            {"status":"error","result": None}

        Notes:
            - Prefer returning a 'not_found' status when the id exists but no name is found.
        """
        results = self.conn.query(f"SELECT DISTINCT location_name FROM {self.table} WHERE location_id = '{location_id}'")
        if not results:
            return {"status":"not_found", "error_message": f"Location ID {location_id} not found"}
        return {"status":"success", "result": results[0][0]}
  
    
   
    
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