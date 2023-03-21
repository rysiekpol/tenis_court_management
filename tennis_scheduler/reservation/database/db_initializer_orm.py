from sqlalchemy import create_engine, insert, cast, Date, select, Table, Column, String, MetaData, DateTime, exc, and_
from datetime import datetime, timedelta


class DatabaseInitializerORM(object):
    def __init__(self, db):
        self.__db_file = db
        self.__initialize()

    def __initialize(self):
        engine = None
        try:
            engine = create_engine('sqlite:///' + self.__db_file)
        except exc.SQLAlchemyError as e:
            print(e)
        finally:
            metadata = MetaData()
            self.clients = Table('clients', metadata,
                                 Column('name', String),
                                 Column('start_time', DateTime),
                                 Column('end_time', DateTime)
                                 )
            metadata.create_all(engine)
            engine.dispose()

    def insert(self, name, start_time, end_time):
        engine = create_engine('sqlite:///' + self.__db_file)
        with engine.connect() as conn:
            conn.execute(insert(self.clients)
            .values(
                name=name,
                start_time=start_time,
                end_time=end_time))
            conn.commit()
        engine.dispose()

    def delete(self, name, date):
        engine = create_engine('sqlite:///' + self.__db_file)
        with engine.connect() as conn:
            conn.execute(self.clients.delete()
                         .where(and_(self.clients.c.name == name,
                                     self.clients.c.start_time == date)))
            conn.commit()
        engine.dispose()

    def check_availability(self, date_start, date_end):
        engine = create_engine('sqlite:///' + self.__db_file)
        with engine.connect() as conn:
            result = conn.execute(select(self.clients)
                                  .where(and_(date_end > self.clients.c.start_time,
                                              date_start < self.clients.c.end_time))).fetchall()
        engine.dispose()
        return not len(result) > 0

    def get_reservations(self, start_date, end_date):
        engine = create_engine('sqlite:///' + self.__db_file)
        with engine.connect() as conn:
            result = conn.execute(select(self.clients)
                                  .where(and_(self.clients.c.start_time >= start_date,
                                              self.clients.c.end_time <= end_date))
                                  .order_by(self.clients.c.start_time)).fetchall()
        engine.dispose()
        return result

    def check_too_many_reservations(self, name, date):
        engine = create_engine('sqlite:///' + self.__db_file)
        with engine.connect() as conn:
            result = conn.execute(select(self.clients.c.end_time)
                                  .where(and_(self.clients.c.name == name)))
            rows = [row for row in result.fetchall() if
                    row[0].isocalendar()[1] == date.isocalendar()[1]]
        engine.dispose()
        return not len(rows) > 2

    def get_reserved_times(self, start_date):
        engine = create_engine('sqlite:///' + self.__db_file)
        with engine.connect() as conn:
            result = conn.execute(select(self.clients.c.start_time, self.clients.c.end_time)
                                  .where(cast(self.clients.c.end_time, Date) == cast(start_date, Date))
                                  .where(self.clients.c.start_time >= datetime.now() + timedelta(hours=1))).fetchall()
        return result

    def get_user_reserved_times(self, name, date):
        engine = create_engine('sqlite:///' + self.__db_file)
        with engine.connect() as conn:
            result = conn.execute(select(self.clients.c.start_time)
                                  .where(and_(self.clients.c.start_time == date, self.clients.c.name == name)))
            reserved_date = result.fetchall()
        engine.dispose()
        if len(reserved_date) > 0:
            reserved_date = reserved_date[0][0]
        return reserved_date
