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
    
    def get_study_program_categories(self) -> list:
        """
        Get a list of the different study program catagories.
        """
        results = self.conn.query(f"SELECT DISTINCT study_category FROM {self.table} WHERE study_category IS NOT null")
        return [result[0] for result in results]
    
    def get_study_programs_names(self) -> list:
        '''
        Get the name of all the available datafields in the table.
        Returns a list names for all the datafields in the table.
        '''
        result = self.conn.query(f"SELECT study_title FROM {self.table}")
        return [title[0] for title in result]
    

    def get_datafields(self) -> list[str]:
        """
        Get the names of all the available datafields for a study program.
        """
        results = self.conn.query(f"DESCRIBE {self.table}")
        return [result[0] for result in results[2:]]



    def get_datafields_values(self, program_name:str, fields: list[str]) -> dict[str,str]:
        '''
        Returns the values of datafiels for a study program.
        Two paramterers must be provided.
        The first parameter is the name of the study program as a string.
        The Second parameter is a list of the names for the requested datafields as a list of strings.
        Returns a dictonary with all the datafield names and values.
        '''
        result = self.conn.query(f'SELECT {",".join(fields)} FROM {self.table} WHERE study_title = "{program_name}"')
        return dict(zip(fields,result[0]))
    

    '''
    SELECT `COLUMN_NAME` 
    FROM `INFORMATION_SCHEMA`.`COLUMNS` 
    WHERE `TABLE_SCHEMA`='fagskolen' 
    AND `TABLE_NAME`='study_programs';
    '''

    '''
    DESCRIBE fagskolen.study_programs;
    '''
    
    
if __name__ == "__main__":
    DATABASE = "fagskolen"
    STUDY_PROGRAM_TABLE = "study_programs"
    try:
        db_conn = DBConnection()
        programs = TableStudyPrograms(db_conn, f"{DATABASE}.{STUDY_PROGRAM_TABLE}")

        #results = programs.get_number_of_study_programs()
        results = programs.get_study_program_categories()
        #results = programs.get_study_programs_names()
        #results = programs.get_datafields()
        #results = programs.get_datafields_values("Akuttgeriatri", ["location_id", "credits"])
        print(results)

    except mysql.connector.Error as err:
        print(f"Error: {err}")