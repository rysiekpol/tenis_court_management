from .tools import terminal_clear
import re
from datetime import datetime, timedelta
from .database.db_initializer import DatabaseInitializer

INFORMATION = {"reservation": "When would you like to book?",
               "cancellation": "What date would you like to cancel?",
               "printing_start": "From what date would you like to get schedule?",
               "printing_end": "Till what date would you like to get schedule?"}

DATE_FORMAT = {"reservation": "{DD.MM.YYYY HH:MM} e.g. 10.07.2023 15:30\nMinutes must be :00 or :30.",
               "cancellation": "{DD.MM.YYYY HH:MM} e.g. 10.07.2023 15:30\nMinutes must be :00 or :30.",
               "printing_start": "{DD.MM.YYYY} e.g. 10.07.2023",
               "printing_end": "{DD.MM.YYYY} e.g. 10.07.2023"}


class Validator:

    def __init__(self, database_name):
        self._database = DatabaseInitializer(database_name)

    def _invalid_name(self):
        name = None
        try:
            name = input("What's your Name? {Name Surname} e.g. John Smith\n")
        except ValueError:
            terminal_clear()
            print(f"Invalid name -> {name}. Please provide a valid name.")
            return
        return self._invalid_name_regex(name)

    @staticmethod
    def _invalid_name_regex(name):
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
    def _invalid_option(option):
        terminal_clear()
        print(f"Invalid option -> {option}. Please provide a valid option.")
        return

    def _invalid_date(self, type_of_usage="reservation"):
        date = None
        try:
            # type of usage means which function called,
            # "reservation" -> reserve, "cancellation" -> cancel
            # "printing_start" -> print_reservations, "printing_end" -> print_reservations
            date = input(f"{INFORMATION[type_of_usage]} {DATE_FORMAT[type_of_usage]}\n")
        except ValueError:
            terminal_clear()
            print(f"Invalid date -> {date}. Please provide a valid date {DATE_FORMAT[type_of_usage]}")
            return
        return self._invalid_date_format(date, type_of_usage)

    def _invalid_date_format(self, date, type_of_usage="reservation"):
        try:
            # date must be in format DD.MM.YYYY HH:MM for reservation and cancellation
            # date must be in format DD.MM.YYYY for printing and saving
            if type_of_usage in ["reservation", "cancellation"]:
                datetime.strptime(date, "%d.%m.%Y %H:%M")
            else:
                datetime.strptime(date, "%d.%m.%Y")

        except ValueError:
            terminal_clear()
            print(f"Invalid date -> {date}. Please provide a valid date {DATE_FORMAT[type_of_usage]}")
            return
        if type_of_usage in ["reservation", "cancellation"]:
            return self._invalid_minutes(datetime.strptime(date, "%d.%m.%Y %H:%M"))
        return datetime.strptime(date, "%d.%m.%Y")

    @staticmethod
    def _invalid_minutes(date):
        if date.minute not in [0, 30]:
            terminal_clear()
            print("Minutes must be :00 or :30! Please provide a valid minutes.")
            return
        return date

    def _invalid_booking(self, date):
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

        return self._invalid_booking_format(booking, date)

    @staticmethod
    def _invalid_booking_format(booking_time, date):
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

    def _check_reservation_conditions(self, name, date_start):
        if not self._check_time_range(date_start):
            return
        if not self._check_if_not_in_past(date_start):
            return
        if not self._check_too_many_reservations(name, date_start):
            return
        return True

    def _check_too_many_reservations(self, name, date):
        if not self._database.check_too_many_reservations(name, date):
            print("You can't make more than 2 reservations in a week.")
            return
        return True

    @staticmethod
    def _check_time_range(date):
        if date.hour < 8 or date.hour > 18 or (date.hour == 18 and date.minute != 0):
            print("Your time must be before 8:00 and after 18:00. Please provide a valid time.")
            return
        return True

    def _check_availability(self, date_start, date_end):
        if not self._database.check_availability(date_start, date_end):
            # print("Court is already booked. Please choose another date.")
            return
        return True

    @staticmethod
    def _check_if_not_in_past(date):
        if datetime.now() + timedelta(hours=1) > date or date > datetime(2100, 12, 31):
            print("Your date needs to be at least one hour from now, and at most to 31.12.2100 in the future.")
            return
        return True

    def _check_closest_reservation(self, date_start, book_time):
        closest_reservations = self._database.get_reserved_times(date_start)
        if closest_reservations is None:
            return

        available_times = self._get_base_available_times(date_start)
        if len(available_times) == 0:
            print("Court is already booked and cannot be booked for another hour. Please choose another date.")
            return

        available_times = self._get_real_available_times(available_times, closest_reservations)
        if len(available_times) == 0:
            print("Court is already booked and cannot be booked for another hour. Please choose another date.")
            return

        final_times = self._get_final_times(available_times, book_time)
        if len(final_times) == 0:
            print("Court is already booked and cannot be booked for another hour. Please choose another date.")
            return

        return min(final_times, key=lambda x: abs(x - date_start))

    @staticmethod
    def _get_base_available_times(date_start):
        available_times = []
        start_time = date_start.replace(hour=date_start.hour, minute=0, second=0, microsecond=0)
        end_time = date_start.replace(hour=18, minute=30, second=0, microsecond=0)
        while start_time < end_time:
            available_times.append([start_time, start_time + timedelta(minutes=30)])
            # add every time from start hour to 18:00 with delta -> 30 minutes
            start_time += timedelta(minutes=30)
        return available_times

    @staticmethod
    def _get_real_available_times(available_times, closest_reservations):
        available_times_copy = available_times.copy()
        for start_time, end_time in closest_reservations:
            for j in range(len(available_times)):
                if start_time <= available_times[j][0] < end_time:
                    if available_times[j] in available_times_copy:
                        available_times_copy.remove(available_times[j])
        return available_times_copy

    @staticmethod
    def _get_final_times(available_times, book_time):
        final_times = []
        # book_time//30 means which index of booking time user chose
        for i in range(len(available_times) - book_time // 30 + 1):
            if available_times[i][0] + timedelta(minutes=book_time) == available_times[i + book_time // 30 - 1][1]:
                final_times.append(available_times[i][0])
        return final_times

    def _check_if_can_cancel(self, name, date_start):
        user_date = self._database.get_user_reserved_times(name, date_start)
        if not user_date:
            print("You can't cancel reservation, because there is no reservation on specified date.")
            return
        return user_date

    def _check_cancellation_conditions(self, name, date_start):
        if not self._check_time_range(date_start):
            return
        if not self._check_if_not_in_past(date_start):
            return
        if not self._check_too_many_reservations(name, date_start):
            return

        return self._check_if_can_cancel(name, date_start)

    @staticmethod
    def _check_data_range(date_start, date_end, operation="printing"):
        # date is provided in format -> DD.MM.YYYY
        if operation == "printing":
            if date_start.date() < datetime.now().date():
                print("Start date must be today or after.")
                return
            if date_end - date_start > timedelta(days=7):
                print("You can check only 7 days in a row.")
                return

        if date_start > date_end:
            print("Start date must be before end date.")
            return
        if date_end > datetime(2100, 12, 31):
            print("Your date needs to be and at most to 31.12.2100 in the future.")
            return
        return True

    def _invalid_extension(self):
        extension = None
        try:
            extension = input("What extension would you like the file to be saved in? {csv/json}\n")
        except ValueError:
            terminal_clear()
            print(f"Invalid extension -> {extension}. Please provide a valid extension -> {{csv/json}}.")
            return
        return self._invalid_extension_format(extension)

    @staticmethod
    def _invalid_extension_format(extension):
        if extension.lower() not in ["csv", "json"]:
            terminal_clear()
            print(f"Invalid extension -> {extension}. Please provide a valid extension -> {{csv/json}}.")
            return
        return extension.lower()

    def _invalid_filename(self):
        filename = None
        try:
            filename = input("What would you like the file to be named?\n")
        except ValueError:
            terminal_clear()
            print(f"Invalid filename -> {filename}. Please provide a valid filename.")
            return
        return self._invalid_filename_format(filename)

    @staticmethod
    def _invalid_filename_format(filename):
        # filename can contain only letters, numbers, underscores and dashes
        if re.match(r"^[a-zA-Z0-9_.-]*$", filename) is None:
            terminal_clear()
            print(f"Invalid filename -> {filename}. Please provide a valid filename.")
            return
        return filename

    def _invalid_choice_json(self):
        choice = None
        try:
            choice = input("Do you want empty dates in your file? {yes/no}\n")
        except ValueError:
            terminal_clear()
            print(f"Invalid option -> {choice}. Please provide a valid option {{yes/no}}.")
            return
        return self._invalid_choice_json_format(choice)

    @staticmethod
    def _invalid_choice_json_format(choice: str):
        if choice.lower() in ["yes", "y"]:
            return True
        return False


