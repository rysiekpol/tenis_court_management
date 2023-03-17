import sqlite3
from sqlite3 import Error


class DatabaseInitializer(object):
    def __init__(self, db):
        self.db_file = db
        self.initialize()

    def initialize(self):
        """ create a database connection to a SQLite database """
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS clients (name TEXT, start_time DATE, end_time DATE)''')
                conn.close()

    def insert(self, name, start_time, end_time):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                c = conn.cursor()
                c.execute("INSERT INTO clients VALUES (?, ?, ?)", (name, start_time, end_time))
                conn.commit()
                conn.close()

    def check_availability(self, date):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM clients WHERE end_time>=?", (date,))
                rows = cur.fetchall()
                conn.close()
                if len(rows) > 0:
                    return False
                return True


