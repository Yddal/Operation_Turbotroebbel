import mysql.connector


class DBConnection:
    def __init__(self, host: str = "127.0.0.1", user: str = "root", password: str = "admin"):
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.db.cursor()

    def query(self, query: str) -> list:
        '''
        executes a SQL query and returns the result
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    '''
    def __del__(self):
        self.cursor.close()
        self.db.close()
    '''


