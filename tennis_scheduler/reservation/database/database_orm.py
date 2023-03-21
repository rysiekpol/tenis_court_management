from sqlalchemy import create_engine, insert, cast, Date, select, Table, Column, String, MetaData, DateTime, exc, and_
from datetime import datetime, timedelta


class DatabaseORM(object):
    def __init__(self, db):
        self.__db_file = db
        self.engine = None
        self.__initialize()

    def __initialize(self) -> None:
        try:
            self.engine = create_engine('sqlite:///' + self.__db_file)
        except exc.SQLAlchemyError as e:
            print(e)
        finally:
            if self.engine is None:
                return
            metadata = MetaData()
            self.clients = Table('clients', metadata,
                                 Column('name', String),
                                 Column('start_time', DateTime),
                                 Column('end_time', DateTime)
                                 )
            metadata.create_all(self.engine)
            self.engine.dispose()

    def insert(self, name: str, start_time: datetime, end_time: datetime) -> None:
        with self.engine.connect() as conn:
            conn.execute(insert(self.clients)
            .values(
                name=name,
                start_time=start_time,
                end_time=end_time))
            conn.commit()

    def delete(self, name: str, date: datetime) -> None:
        with self.engine.connect() as conn:
            conn.execute(self.clients.delete()
                         .where(and_(self.clients.c.name == name,
                                     self.clients.c.start_time == date)))
            conn.commit()

    def check_availability(self, date_start: datetime, date_end: datetime) -> bool:
        with self.engine.connect() as conn:
            result = conn.execute(select(self.clients)
                                  .where(and_(date_end > self.clients.c.start_time,
                                              date_start < self.clients.c.end_time))).fetchall()
        return len(result) <= 0

    def get_reservations(self, start_date: datetime, end_date: datetime) -> list:
        with self.engine.connect() as conn:
            result = conn.execute(select(self.clients)
                                  .where(and_(self.clients.c.start_time >= start_date,
                                              self.clients.c.end_time <= end_date))
                                  .order_by(self.clients.c.start_time)).fetchall()
        self.engine.dispose()
        return result

    @staticmethod
    def __is_the_same_day(date_one: datetime, date_two: datetime) -> bool:
        return date_one.isocalendar()[1] == date_two.isocalendar()[1]

    def check_too_many_reservations(self, name: str, date: datetime) -> bool:
        with self.engine.connect() as conn:
            result = conn.execute(select(self.clients.c.end_time)
                                  .where(and_(self.clients.c.name == name)))
            rows = [row for row in result.fetchall() if
                    self.__is_the_same_day(row[0], date)]
        return len(rows) <= 2

    def get_reserved_times(self, start_date: datetime) -> list:
        with self.engine.connect() as conn:
            result = conn.execute(select(self.clients.c.start_time, self.clients.c.end_time)
                                  .where(cast(self.clients.c.end_time, Date) == cast(start_date, Date))
                                  .where(self.clients.c.start_time >= datetime.now() + timedelta(hours=1))).fetchall()
        return result

    def get_user_reserved_times(self, name: str, date: datetime) -> datetime:
        with self.engine.connect() as conn:
            result = conn.execute(select(self.clients.c.start_time)
                                  .where(and_(self.clients.c.start_time == date, self.clients.c.name == name)))
            reserved_date = result.fetchall()
        return reserved_date[0][0] if len(reserved_date) > 0 else reserved_date

    def close_database(self) -> None:
        self.engine.dispose()
