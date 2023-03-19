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
            name = input("What's you Name? {Name Surname} e.g. John Smith\n")
        except ValueError:
            terminal_clear()
            print(f"Invalid name -> {name}. Please provide a valid name.")
            return
        return self.invalid_name_regex(name)

    @staticmethod
    def invalid_name_regex(name):
        # checking if name and surname starts with big letter
        # there is only one whitespace between words
        # rest of the letters must be low
        if re.match("^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+ [A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$", name) \
                is None or len(name) == 0:
            terminal_clear()
            print(f"Invalid name -> {name}. Your name and surname must start with big letters and "
                  "rest must be low letters. There can also be only one whitespace between words.")
            return
        return name

    @staticmethod
    def invalid_option(option):
        terminal_clear()
        print(f"Invalid option -> {option}. Please provide a valid option.")

    def invalid_date(self):
        date = None
        try:
            date = input("When would you like to book? {DD.MM.YYYY HH:MM} e.g. 10.07.2023 15:30\n"
                         "Minutes must be :00 or :30.\n")
        except ValueError:
            terminal_clear()
            print(f"Invalid date -> {date}. Please provide a valid date -> DD.MM.YYYY HH:MM")
            return
        return self.invalid_date_format(date)

    def invalid_date_format(self, date):
        try:
            datetime.strptime(date, "%d.%m.%Y %H:%M")
        except ValueError:
            terminal_clear()
            print(f"Invalid date -> {date}. Please provide a valid date -> DD.MM.YYYY HH:MM")
            return
        return self.invalid_minutes(datetime.strptime(date, "%d.%m.%Y %H:%M"))

    @staticmethod
    def invalid_minutes(date):
        if date.minute not in [0, 30]:
            terminal_clear()
            print("Minutes must be :00 or :30! Please provide a valid minutes.")
            return
        return date

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

    def check_reservation_conditions(self, name, date_start):
        if not self.check_time_range(date_start):
            return
        if not self.check_if_not_in_past(date_start):
            return
        if not self.check_too_many_reservations(name, date_start):
            return
        return True

    def check_too_many_reservations(self, name, date):
        if not self.database.check_too_many_reservations(name, date):
            print("You can't make more than 2 reservations in a week.")
            return
        return True

    @staticmethod
    def check_time_range(date):
        if date.hour < 8 or date.hour > 18 or (date.hour == 18 and date.minute != 0):
            print("You can't make a reservation before 8:00 and after 18:00.")
            return
        return True

    def check_availability(self, date_start, date_end):
        if not self.database.check_availability(date_start, date_end):
            # print("Court is already booked. Please choose another date.")
            return
        return True

    @staticmethod
    def check_if_not_in_past(date):
        if datetime.now() + timedelta(hours=1) > date or date > datetime(2100, 12, 31):
            print("You need to make a reservation at least one hour from now, and at most to 31.12.2100 in the future.")
            return
        return True

    def check_closest_reservation(self, date_start, book_time):
        closest_reservations = self.database.get_reserved_times(date_start)
        if closest_reservations is None:
            return

        available_times = self.get_base_available_times(date_start)
        if len(available_times) == 0:
            print("Court is already booked and cannot be booked for another hour. Please choose another date.")
            return

        available_times = self.get_real_available_times(available_times, closest_reservations)
        if len(available_times) == 0:
            print("Court is already booked and cannot be booked for another hour. Please choose another date.")
            return

        final_times = self.get_final_times(available_times, book_time)
        if len(final_times) == 0:
            print("Court is already booked and cannot be booked for another hour. Please choose another date.")
            return

        return self.get_final_choice(final_times, date_start)


    def get_base_available_times(self, date_start):
        available_times = []
        start_time = date_start.replace(hour=date_start.hour, minute=0, second=0, microsecond=0)
        end_time = date_start.replace(hour=18, minute=30, second=0, microsecond=0)
        while start_time < end_time:
            available_times.append([start_time, start_time + timedelta(minutes=30)])
            # add every time from start hour to 18:00 with delta -> 30 minutes
            start_time += timedelta(minutes=30)
        return available_times

    def get_real_available_times(self, available_times, closest_reservations):
        available_times_copy = available_times.copy()
        for start_time, end_time in closest_reservations:
            for j in range(len(available_times)):
                if start_time <= available_times[j][0] < end_time:
                    if available_times[j] in available_times_copy:
                        available_times_copy.remove(available_times[j])
        return available_times_copy

    def get_final_times(self, available_times, book_time):
        final_times = []
        # book_time//30 means which index of booking time user chose
        for i in range(len(available_times) - book_time // 30 + 1):
            if available_times[i][0] + timedelta(minutes=book_time) == available_times[i + book_time // 30 - 1][1]:
                final_times.append(available_times[i][0])
        return final_times

    def get_final_choice(self, final_times, date_start):
        closest_time = min(final_times, key=lambda x: abs(x - date_start))

        print(f"The time you chose is unavailable, "
              f"would you like to make a reservation for {str(closest_time.time())[:-3]} instead? (yes/no)")
        choice = input()
        if choice.lower() in ["y", "yes"]:
            return True
        elif choice.lower() in ["n", "no"]:
            return False
        print("Invalid choice. Please choose yes or no.")
        return