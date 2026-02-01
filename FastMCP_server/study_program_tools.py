import mysql.connector
from database_connection import DBConnection

"""
Methods for quering the Study Programs table, to be exposed as tools in the MCP Server
"""

class TableStudyPrograms:
    def __init__(self, conn: DBConnection, table: str):
        self.conn = conn
        self.table = table

    def get_number_of_study_programs(self) -> dict:
        """
        One-line: Return the number of entries in the study programs table.

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
        return {"status":"success", "result": int(result[0][0])}
    

    def get_study_program_categories(self) -> dict:
        """
        One-line: Return distinct study program categories.

        Parameters:
            None

        Returns:
            dict: JSON-serializable dict with keys:
                - status: "success" | "error"
                - result: list[str] (category names) when status == "success"
                - error_message: str when status == "error"

        Example:
            {"status": "success", "result": ["Helse", "Teknikk"]}

        Notes:
            - If no categories exist, return {"status":"success","result":[]}.
            - The returned object must be JSON-serializable.
        """
        results = self.conn.query(f"SELECT DISTINCT study_category FROM {self.table} WHERE study_category IS NOT null")
        if not results:
            return {"status":"error", "error_message":"Query returned no results"}
        return {"status":"success", "result": [result[0] for result in results]}
    

    def get_category_study_programs(self, category: str) -> dict:
        """
        One-line: Return study program names for a given category.

        Parameters:
            category (str): The study program category to query (exact match).

        Returns:
            dict: {
                "status": "success" | "error",
                "result": list[str],  # names of programs
                "error_message": str (optional)
            }

        Example:
            {"status":"success", "result":["Akuttgeriatri", "Ambulanse"]}

        Notes:
            - Validate 'category' is a non-empty string.
            - Use parameterized queries to avoid SQL injection.
        """
        result = self.conn.query(f'SELECT study_title FROM {self.table} WHERE study_category = "{category}"')
        if not result:
            return {"status":"error", "error_message":"Category not found"}
        return {"status":"success", "result": [title[0] for title in result]}
    

    def get_study_programs_names(self) -> dict:
        """
        One-line: Return all available study program names.

        Parameters:
            None

        Returns:
            dict: {"status":"success"|"error", "result": list[str], "error_message": str (optional)}

        Example:
            {"status":"success", "result":["Akuttgeriatri","Elkraft"]}

        Notes:
            - Return an empty list in 'result' if no programs exist.
        """
        result = self.conn.query(f"SELECT study_title FROM {self.table}")
        if not result:
            return {"status":"error", "error_message":"Query returned no results"}
        return {"status":"success", "result": [title[0] for title in result]}
    

    def get_study_program_datafields(self) -> dict:
        """
        One-line: Return available data field names for the study_programs table.

        Parameters:
            None

        Returns:
            dict: {"status":"success"|"error", "result": list[str], "error_message": str (optional)}

        Example:
            {"status":"success","result":["study_title","location_id","credits"]}

        Notes:
            - The result should list column names and be JSON-serializable.
        """
        results = self.conn.query(f"DESCRIBE {self.table}")
        if not results:
            return {"status":"error", "error_message":"Query returned no results"}
        return {"status":"success", "result": [result[0] for result in results[2:]]}


    def get_study_program_datafields_values(self, program_name: str, fields: list[str]) -> dict:
        """
        One-line: Return requested data field values for a study program.

        Parameters:
            program_name (str): Exact study program name to query.
            fields (list[str]): List of column names to retrieve (must be valid fields).

        Returns:
            dict: {
                "status": "success" | "error",
                "result": dict(field_name -> value) when status == "success",
                "error_message": str (optional)
            }

        Example:
            {"status":"success","result":{"location_id":"2","credits":"30"}}

        Notes:
            - If the program is not found, return {"status":"success","result":{}}.
            - Validate field names and use parameterized queries to prevent SQL injection.
        """
        result = self.conn.query(f'SELECT {",".join(fields)} FROM {self.table} WHERE study_title = "{program_name}"')
        if not result:
            return {"status":"error", "error_message":"Study program not found"}
        return {"status":"success", "result": dict(zip(fields,result[0]))}
    
    
if __name__ == "__main__":
    DATABASE = "fagskolen"
    STUDY_LOCATION_TABLE = "study_programs"

    # verify method outputs
    try:
        db_conn = DBConnection()
        programs = TableStudyPrograms(db_conn, f"{DATABASE}.{STUDY_LOCATION_TABLE}")

        #results = programs.get_number_of_study_programs()
        #results = programs.get_study_program_categories()
        #results = programs.get_category_study_programs("Helse")
        #results = programs.get_study_programs_names()
        #results = programs.get_study_program_datafields()
        results = programs.get_study_program_datafields_values("Akuttgeriatri", ["location_id", "credits"])
        
        print(results)

    except mysql.connector.Error as err:
        print(f"Error: {err}")