from .tools import terminal_clear
import re
from datetime import datetime, timedelta
from .database.db_initializer import DatabaseInitializer


class Validator:

    def __init__(self, database_name):
        self.database = DatabaseInitializer(database_name)

    def invalid_name(self):
        name = None
        try:
            name = input("What's you Name?\n")
        except ValueError:
            terminal_clear()
            print(f"Invalid name -> {name}. Please provide a valid name.")
            return
        return self.invalid_name_regex(name)

    @staticmethod
    def invalid_name_regex(name):
        if re.match("^([a-zA-ZąćęłńóśźżĄĘŁŃÓŚŹŻ]+\s)*[a-zA-ZąćęłńóśźżĄĘŁŃÓŚŹŻ]*$", name) is None or len(name) == 0:
            terminal_clear()
            print(f"Invalid name -> {name}. Your name must consists of big and "
                  "low letters with at most one whitespace between words.")
            return
        return name

    @staticmethod
    def invalid_option(option):
        terminal_clear()
        print(f"Invalid option -> {option}. Please provide a valid option.")

    def invalid_date(self):
        date = None
        try:
            date = input("When would you like to book? {DD.MM.YYYY HH:MM}\n")
        except ValueError:
            terminal_clear()
            print(f"Invalid date -> {date}. Please provide a valid date -> DD.MM.YYYY HH:MM")
            return
        return self.invalid_date_format(date)

    @staticmethod
    def invalid_date_format(date):
        try:
            datetime.strptime(date, "%d.%m.%Y %H:%M")
        except ValueError:
            terminal_clear()
            print(f"Invalid date -> {date}. Please provide a valid date -> DD.MM.YYYY HH:MM")
            return
        return datetime.strptime(date, "%d.%m.%Y %H:%M")

    def invalid_booking(self, date):
        booking = None
        print("How long would you like to book court?")
        print("1) 30 Minutes")
        print("2) 60 Minutes")
        if date.hour < 17:
            print("3) 90 Minutes")

        try:
            booking = int(input())
        except ValueError:
            terminal_clear()
            print(f"Invalid booking -> {booking}. ", end="")
            if date.hour < 17:
                print("Please provide a valid booking -> 1, 2, 3")
            else:
                print("Please provide a valid booking -> 1, 2")
            return

        return self.invalid_booking_format(booking, date)

    @staticmethod
    def invalid_booking_format(booking_time, date):
        book_hours = {1: 30, 2: 60, 3: 90}
        if date.hour >= 17 and booking_time == 3:
            terminal_clear()
            print("You can't book court for 90 minutes after 17:00")
            return
        if booking_time not in [1, 2, 3]:
            terminal_clear()
            print(f"Invalid booking -> {booking_time}. ", end="")
            if date.hour < 17:
                print("Please provide a valid booking -> 1, 2, 3")
            else:
                print("Please provide a valid booking -> 1, 2")
            return
        return book_hours[booking_time]

    def check_reservation_conditions(self, name, date_start, date_end):
        if not self.check_time_range(date_start):
            return
        if not self.check_if_not_in_past(date_start):
            return
        if not self.check_too_many_reservations(name, date_start):
            return
        if not self.check_availability(date_start, date_end):
            return
        return True

    def check_too_many_reservations(self, name, date):
        if not self.database.check_too_many_reservations(name, date):
            print("You can't make more than 2 reservations in a week.")
            return
        return True

    @staticmethod
    def check_time_range(date):
        if date.hour < 8 or date.hour >= 18:
            print("You can't make a reservation before 8:00 and after 17:59.")
            return
        return True

    def check_availability(self, date_start, date_end):
        if not self.database.check_availability(date_start, date_end):
            print("Court is already booked. Please choose another date.")
            return
        return True

    @staticmethod
    def check_if_not_in_past(date):
        if datetime.now() + timedelta(hours=1) > date or date > datetime(2100, 12, 31):
            print("You need to make a reservation at least one hour from now, and at most to 31.12.2100 in the future.")
            return
        return True
