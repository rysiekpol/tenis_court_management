from .reservation_validator import Validator
from datetime import timedelta


class ReservationHandler(Validator):
    def __init__(self):
        super().__init__()

    def execute_option(self, option):
        if option == 1:
            self.reserve()
        elif option == 2:
            self.cancel()
        elif option == 3:
            self.get_reservations()
        elif option == 4:
            self.save_reservations()
        elif option == 5:
            exit()
        else:
            self.invalid_option(option)

    def reserve(self):
        name = self.invalid_name()
        if name is None:
            return

        date = self.invalid_date()
        if date is None:
            return

        if self.check_reservation_conditions(name, date) is None:
            return

        book = self.invalid_booking(date)
        if book is None:
            print("This date is not available")
            return

        super().insert(name, date, date + timedelta(minutes=book))
        print("Reservation successful!")
        input("Press Enter to continue...")

    def cancel(self):
        pass

    def get_reservations(self):
        pass

    def save_reservations(self):
        pass
