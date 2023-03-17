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
                cur.execute("SELECT * FROM clients WHERE ? <= end_time AND date(?) == date(end_time)", (date,date,))
                rows = cur.fetchall()
                conn.close()
                if len(rows) > 0:
                    return False
                return True

    def get_reservations(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM clients")
                rows = cur.fetchall()
                conn.close()
                return rows

    def check_too_many_reservations(self, name, date):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM clients WHERE strftime('%W',?) == strftime('%W',start_time) AND name == ?", (date,name,))
                rows = cur.fetchall()
                conn.close()
                if len(rows) > 2:
                    return False
                return True