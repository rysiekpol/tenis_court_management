from reservation.reservation_handler import ReservationHandler
from reservation import tools


def main():
    reservation_handler = ReservationHandler()

    while True:
        ask_user()
        choice = 0
        while True:
            try:
                choice = int(input("Enter your choice: "))
            except ValueError:
                print("Invalid number. Please provide a number.")
                continue
            else:
                # choice was successfully parsed
                break

        reservation_handler.execute_option(choice)
        input("Press enter to continue...")


def ask_user():
    tools.terminal_clear()

    print("What do you want to do?")
    print("1. Make a reservation")
    print("2. Cancel a reservation")
    print("3. Print schedule")
    print("4. Save schedule to file")
    print("5. Exit")


if __name__ == "__main__":
    main()
