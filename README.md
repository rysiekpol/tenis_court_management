
# Tenis Scheduler 

@@ author -> Maciej Szefler - ma.szefler@gmail.com / maciek20022010@gmail.com

This script was made for the backend internship task at Profil Software for managing the tennis court. You can make reservations, delete, print, and save them to a file.

While writing to JSON, you can choose so the script can save it with empty days or without them.

The standard path for writing files depends from your "position" in your os. 

Script uses sqlite as a database with ORM or clean SQL (you can choose which option you like).

I used SQLAlchemy for "speaking" with database in ORM.
## Packages
If you want to use database with ORM, you need to install sqlalchemy.

On Windows:

```bash
$ cd Downloads/internship_task # most probably
$ python -m venv venv
$ venv\Scripts\activate
$ pip install sqlalchemy

```

On macOS/Linux:

```bash
$ cd Downloads/internship_task # most probably
$ python -m venv venv
$ source venv/bin/activate
$ pip install sqlalchemy
```

Then in ```internship_task/reservation/reservation_validator.py```  comment the line 
```py
self._database = Database(database_name)
# and uncomment the line
self._database = DatabaseORM(database_name)
```

If you want to use tests while using ORM database, in ```internship_task/test/test_reservations.py``` change
```python
self.db = Database(TEST_DB)
# to 
self.db = DatabaseORM(TEST_DB)
```

If you don't want to use ORM database, then delete it, and remove lines from above. You will also need to remove importing packages from the files above.

## Usage/Examples

To start a script, type in the terminal:

```bash
$ cd Downloads/internship_task # most probably
$ python tennis_scheduler

# depending on your os distribution you may need to type in
$ python3 tennis_scheduler 
```

To run unit tests, type in:

```bash
$ python -m unittest discover  

# or same as above
$ python3 -m unittest discover
```

Make a reservation e.g.

```
What do you want to do? {1, 2, 3, 4, 5}
1. Make a reservation
2. Cancel a reservation
3. Print schedule
4. Save schedule to file
5. Exit
$ 1

What's your Name? {Name Surname} e.g. John Smith
$ John Smith

When would you like to book? {DD.MM.YYYY HH:MM} e.g. 10.07.2023 15:30
Minutes must be :00 or :30.
$ 27.03.2023 15:30

For how long would you like to book court?
1) 30 Minutes
2) 60 Minutes
3) 90 Minutes
$ 3

The time you chose is unavailable, would you like to make a reservation for 14:00 instead? (yes/no)
$ yes

Reservation successful!
Press enter to continue...
```

Cancel a reservation e.g.

```
What do you want to do? {1, 2, 3, 4, 5}
1. Make a reservation
2. Cancel a reservation
3. Print schedule
4. Save schedule to file
5. Exit
$ 2

What's your Name? {Name Surname} e.g. John Smith
$ John Smith

What date would you like to cancel? {DD.MM.YYYY HH:MM} e.g. 10.07.2023 15:30
Minutes must be :00 or :30.
$ 27.03.2023 14:00

Reservation cancelled!
Press enter to continue...
```

Print schedule e.g.

```
What do you want to do? {1, 2, 3, 4, 5}
1. Make a reservation
2. Cancel a reservation
3. Print schedule
4. Save schedule to file
5. Exit
$ 3

From what date would you like to get schedule? {DD.MM.YYYY} e.g. 10.07.2023
$ 20.03.2023

Till what date would you like to get schedule? {DD.MM.YYYY} e.g. 10.07.2023
$ 24.03.2023

Today:
No reservations
Tomorrow:
* Szymon Szymański 21.03.2023 14:30 - 21.03.2023 15:30
* Andrzej Zapasnik 21.03.2023 15:30 - 21.03.2023 17:00
Wednesday:
* John Smith 22.03.2023 12:00 - 22.03.2023 13:00
Thursday:
No reservations
Friday:
No reservations
Press enter to continue...
```

Save schedule to file e.g.

```
What do you want to do? {1, 2, 3, 4, 5}
1. Make a reservation
2. Cancel a reservation
3. Print schedule
4. Save schedule to file
5. Exit
Enter your choice:
$ 4

From what date would you like to get schedule? {DD.MM.YYYY} e.g. 10.07.2023
$ 20.03.2023

Till what date would you like to get schedule? {DD.MM.YYYY} e.g. 10.07.2023
$ 24.03.2023

What extension would you like the file to be saved in? {csv/json}
$ json

What would you like the file to be named?
$ 20.03-24.03

Do you want empty dates in your file? {yes/no}
$ no

Reservations saved!
Press enter to continue...
```


## Few Rules

    1. While saving or canceling a reservation, the date must be at least today,
    2. Date must be at most 31.12.2100,
    3. Tenis court works from 8:00 to 19:30, so you can only make a reservation till 18:00
    4. You can choose only full hours and half past,
    5. Name and Surname must start with a big letter, the rest must be low. There also must be one whitespace between,
    6. Datetime must be in format DD.MM.YYYY HH:MM, date in format DD.MM.YYYY,
    7. In the event of failure, you will be provided with the cause of failure and brought back to the main menu,
    8. Script treats {"yes", "no", "csv", "json"} as an insensitive case. You can also type shortcut {"y", "n"}.

Enjoy using the script!

