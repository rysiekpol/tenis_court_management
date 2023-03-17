from .database.db_initializer import DatabaseInitializer
from .reservation_validator import Validator


class ReservationHandler(Validator):
    def __init__(self):
        self.database = DatabaseInitializer("tennis_scheduler.sqlite")

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
        date = self.invalid_date()
        book = None
        if date != None:
            if self.database.check_availability(date):
                book = self.invalid_booking(date)
            else:
                print("This date is not available")
                return

        if book != None:
            self.database.insert(name, date, book)
            print("Reservation successful!")
            input("Press Enter to continue...")

    def cancel(self):
        pass

    def get_reservations(self):
        pass

    def save_reservations(self):
        pass
