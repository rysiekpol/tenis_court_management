import sqlite3
from sqlite3 import Error
from datetime import datetime


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

    def check_availability(self, date_start, date_end):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                cur = conn.cursor()
                # dates overlap when => (StartA < EndB) and (EndA > StartB)
                cur.execute("SELECT * FROM clients WHERE ? < end_time AND ? > start_time", (date_start ,date_end,))
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
                print(rows)
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
                cur.execute("SELECT end_time FROM clients WHERE name == ?", (name,))
                rows = [row for row in cur.fetchall() if
                        datetime.strptime(row[0],"%Y-%m-%d %H:%M:%S").isocalendar()[1]== date.isocalendar()[1]]
                conn.close()
                print(rows)
                if len(rows) > 2:
                    return False
                return True