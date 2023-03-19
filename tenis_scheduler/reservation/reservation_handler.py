from .reservation_validator import Validator
from datetime import timedelta, datetime

MAIN_DB = "tenis_scheduler.sqlite"

class ReservationHandler(Validator):
    def __init__(self):
        super().__init__(MAIN_DB)

    def execute_option(self, option):
        if option == 1:
            self.__reserve()
        elif option == 2:
            self.__cancel()
        elif option == 3:
            self.__print_option()
        elif option == 4:
            self.__save_reservations()
        elif option == 5:
            exit()
        else:
            self._invalid_option(option)
        return

    def __reserve(self):
        name = self._invalid_name()
        if name is None:
            return
        date = None
        book = None
        while True:
            date = self._invalid_date("reservation")
            if date is None:
                return

            book = self._invalid_booking(date)
            if book is None:
                return

            if self._check_reservation_conditions(name, date) is None:
                return

            if self._check_availability(date, date + timedelta(minutes=book)) is not None:
                break

            # if date is not available, check for closest available time
            closest_time = self._check_closest_reservation(date, book)
            if closest_time is None:
                return

            choice = self.__get_final_choice(closest_time)
            if choice is None:
                return
            elif choice:
                # user chose "yes" to the closest time, so we can book it
                date = closest_time
                break
            else:
                # user chose "no" to the closest time, so we need to ask for new date
                continue

        self._database.insert(name, date, date + timedelta(minutes=book))
        print("Reservation successful!")
        return

    @staticmethod
    def __get_final_choice(closest_time):
        print(f"The time you chose is unavailable, "
              f"would you like to make a reservation for {str(closest_time.time())[:-3]} instead? (yes/no)")
        choice = input()
        if choice.lower() in ["y", "yes"]:
            return True
        elif choice.lower() in ["n", "no"]:
            return False
        print("Invalid choice. Please choose yes or no.")
        return

    def __cancel(self):
        name = self._invalid_name()
        if name is None:
            return

        date = self._invalid_date("cancellation")
        if date is None:
            return

        date = self._check_cancellation_conditions(name, date)
        # if there are no reservations for the given name and date, return
        if date is None:
            return

        self._database.delete(name, date)
        print("Reservation cancelled!")
        return

    def __print_option(self):
        start_date = self._invalid_date("printing_start")
        if start_date is None:
            return

        end_date = self._invalid_date("printing_end")
        if end_date is None:
            return

        if self._check_data_range(start_date, end_date) is None:
            return

        # reservations are sorted by start date
        # reservations = (name, start_date, end_date)*n
        reservations = self._database.get_reservations(start_date, end_date)
        # if len(reservations) == 0:
        #     print("No reservations in the given range.")
        #     return

        self.__print_schedule(start_date, end_date, reservations)

    @staticmethod
    def __print_schedule(start_date, end_date, reservations):
        days = (end_date - start_date).days

        reservation_number = 0
        for i in range(days):
            if i == 0 and start_date.date() == datetime.now().date():
                print("Today:")
            elif i == 1 and (start_date + timedelta(days=1)).date() == (datetime.now() + timedelta(days=1)).date():
                print("Tomorrow:")
            else:
                print((start_date.date() + timedelta(days=i)).strftime("%A") + ":")
            reservation_number_copy = reservation_number

            while reservation_number < len(reservations) \
                    and reservations[reservation_number][1].date() == start_date.date() + timedelta(days=i):
                print(
                    f"* {reservations[reservation_number][0]} "
                    f"{reservations[reservation_number][1].strftime('%d.%m.%Y %H:%M')} - "
                    f"{reservations[reservation_number][2].strftime('%d.%m.%Y %H:%M')}")
                reservation_number += 1

            if reservation_number_copy == reservation_number:
                print("No reservations")

    def __save_reservations(self):
        pass
