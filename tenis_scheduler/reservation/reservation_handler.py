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
            self.__print_reservations()
        elif option == 4:
            self.__save_reservations()
        elif option == 5:
            exit()
        else:
            self.invalid_option(option)
        return

    def __reserve(self):
        name = self.invalid_name()
        if name is None:
            return
        date = None
        book = None
        while True:
            date = self.invalid_date("reservation")
            if date is None:
                return

            book = self.invalid_booking(date)
            if book is None:
                return

            if self.check_reservation_conditions(name, date) is None:
                return

            if self.check_availability(date, date + timedelta(minutes=book)) is not None:
                break

            # if date is not available, check for closest available time
            closest_time = self.check_closest_reservation(date, book)
            if closest_time is None:
                return

            choice = self.__get_final_choice(closest_time)
            if choice is None:
                return
            elif choice:
                # user chose "yes" to the closest time, so we can book it
                break
            else:
                # user chose "no" to the closest time, so we need to ask for new date
                continue

        self.__database.insert(name, date, date + timedelta(minutes=book))
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
        name = self.invalid_name()
        if name is None:
            return

        date = self.invalid_date("cancellation")
        if date is None:
            return

        other_date = self.check_cancellation_conditions(name, date)
        # if there are no reservations for the given name and date, return
        if other_date is None:
            return

        self.__database.delete(name, other_date)
        print("Reservation cancelled!")
        return

    def __print_reservations(self):
        pass

    def __save_reservations(self):
        pass
