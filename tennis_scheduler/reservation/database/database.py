import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta


class Database(object):
    def __init__(self, db):
        self.__db_file = db
        self.__initialize()

    def __initialize(self):
        """ create a database connection to a SQLite database """
        conn = None
        try:
            conn = sqlite3.connect(self.__db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                c = conn.cursor()
                # by default table will have a key based on the rowid value
                c.execute('''CREATE TABLE IF NOT EXISTS clients (name TEXT, start_time DATE, end_time DATE)''')
                conn.close()

    def insert(self, name: str, start_time: datetime, end_time: datetime) -> None:
        conn = None
        try:
            conn = sqlite3.connect(self.__db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                c = conn.cursor()
                c.execute("INSERT INTO clients VALUES (?, ?, ?)", (name, start_time, end_time))
                conn.commit()
                conn.close()

    def delete(self, name: str, date: datetime) -> None:
        conn = None
        try:
            conn = sqlite3.connect(self.__db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                c = conn.cursor()
                c.execute("DELETE FROM clients WHERE name == ? AND start_time == ?", (name, date))
                conn.commit()
                conn.close()

    def check_availability(self, date_start: datetime, date_end: datetime) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.__db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                cur = conn.cursor()
                # dates overlap when => (StartA < EndB) and (EndA > StartB)
                cur.execute("SELECT * FROM clients WHERE ? < end_time AND ? > start_time", (date_start, date_end,))
                rows = cur.fetchall()
                conn.close()
                return len(rows) <= 0

    def get_reservations(self, start_date: datetime, end_date: datetime) -> list:
        conn = None
        try:
            conn = sqlite3.connect(self.__db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT name, start_time, end_time FROM clients "
                            "WHERE start_time >= ? AND end_time <= ? ORDER BY start_time ASC", (start_date, end_date,))
                rows = [(name_, (datetime.strptime(start_date_, '%Y-%m-%d %H:%M:%S')),
                         (datetime.strptime(end_date_, '%Y-%m-%d %H:%M:%S')))
                        for name_, start_date_, end_date_ in cur.fetchall()]
                conn.close()
                return rows

    def check_too_many_reservations(self, name: str, date: datetime) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.__db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT end_time FROM clients WHERE name == ?", (name,))
                rows = [row for row in cur.fetchall() if
                        datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").isocalendar()[1] == date.isocalendar()[1]]
                conn.close()
                return len(rows) <= 2

    def get_reserved_times(self, start_date: datetime) -> list:
        conn = None
        try:
            conn = sqlite3.connect(self.__db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT start_time, end_time FROM clients WHERE date(end_time) == date(?)", (start_date,))

                rows = [((datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')),
                         (datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')))
                        for start_date, end_date in cur.fetchall()
                        if datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S') >= datetime.now() + timedelta(hours=1)]

                conn.close()
                return rows

    def get_user_reserved_times(self, name: str, date: datetime) -> datetime:
        conn = None
        try:
            conn = sqlite3.connect(self.__db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT start_time FROM clients WHERE start_time == ? AND name = ?", (date, name))
                reserved_date = cur.fetchall()
                if len(reserved_date) > 0:
                    reserved_date = datetime.strptime(reserved_date[0][0], '%Y-%m-%d %H:%M:%S')
                conn.close()
                return reserved_date


