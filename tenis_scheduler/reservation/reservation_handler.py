from .reservation_validator import Validator
from datetime import timedelta, datetime

MAIN_DB = "tenis_scheduler.sqlite"


class ReservationHandler(Validator):
    def __init__(self):
        super().__init__(MAIN_DB)

    def execute_option(self, option):
        if option == 1:
            self.reserve()
        elif option == 2:
            self.cancel()
        elif option == 3:
            self.print_reservations()
        elif option == 4:
            self.save_reservations()
        elif option == 5:
            exit()
        else:
            self.invalid_option(option)
            input("Press enter to continue...")

    def reserve(self):
        name = self.invalid_name()
        if name is None:
            input("Press enter to continue...")
            return
        date = None
        book = None
        while True:
            date = self.invalid_date()
            if date is None:
                input("Press enter to continue...")
                return

            book = self.invalid_booking(date)
            if book is None:
                input("Press enter to continue...")
                return

            if self.check_reservation_conditions(name, date) is None:
                input("Press enter to continue...")
                return

            if self.check_availability(date, date + timedelta(minutes=book)) is None:
                choice = self.check_closest_reservation(date, book)
                if choice is None:
                    input("Press enter to continue...")
                    return
                elif choice:
                    break
                else:
                    continue

        self.database.insert(name, date, date + timedelta(minutes=book))
        print("Reservation successful!")
        input("Press Enter to continue...")
        return

    def cancel(self):
        pass

    def print_reservations(self):
        pass

    def save_reservations(self):
        pass
