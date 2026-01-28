import mysql.connector


class DBConnection:
    def __init__(self, host: str = "127.0.0.1", user: str = "root", password: str = "admin"):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()

    def check_connection(self):
         self.conn.ping(reconnect=True, attempts=1, delay=0)

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

if __name__ == "__main__":
        try:
            db_conn = DBConnection()
            db_conn.check_connection()
            print("Connection Established")

        except mysql.connector.Error as err:
            print(f"Error: {err}")


