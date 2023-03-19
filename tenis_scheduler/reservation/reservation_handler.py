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

            if self.check_availability(date, date + timedelta(minutes=book)) is not None:
                break

            # if date is not available, check for closest available time
            closest_time = self.check_closest_reservation(date, book)
            if closest_time is None:
                input("Press enter to continue...")
                return

            choice = self.get_final_choice(closest_time)
            if choice is None:
                return
            elif choice:
                break
            else:
                continue

        self.database.insert(name, date, date + timedelta(minutes=book))
        print("Reservation successful!")
        input("Press Enter to continue...")
        return

    def get_final_choice(self, closest_time):
        print(f"The time you chose is unavailable, "
              f"would you like to make a reservation for {str(closest_time.time())[:-3]} instead? (yes/no)")
        choice = input()
        if choice.lower() in ["y", "yes"]:
            return True
        elif choice.lower() in ["n", "no"]:
            return False
        print("Invalid choice. Please choose yes or no.")
        return

    def cancel(self):
        pass

    def print_reservations(self):
        pass

    def save_reservations(self):
        pass
