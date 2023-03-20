import os


# check what is the user's os and clear the terminal
def terminal_clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")