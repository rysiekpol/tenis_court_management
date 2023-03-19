from tenis_scheduler.reservation.reservation_validator import Validator
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
import sqlite3, os

TEST_DB = "test_db.sqlite"


class TestValidator(unittest.TestCase):

    def setUp(self) -> None:
        conn = sqlite3.connect(TEST_DB)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS clients (name TEXT, start_time DATE, end_time DATE)''')
        c.execute("SELECT * FROM clients")
        if len(c.fetchall()) == 0:
            c.execute("INSERT INTO clients VALUES (?, ?, ?)",
                      ("Adam Kowalski", datetime(2050, 1, 1, 12, 0), datetime(2050, 1, 1, 13, 0)))
            c.execute("INSERT INTO clients VALUES (?, ?, ?)",
                      ("Adam Kowalski", datetime(2050, 1, 2, 12, 0), datetime(2050, 1, 2, 13, 0)))
            c.execute("INSERT INTO clients VALUES (?, ?, ?)",
                      ("Adam Kowalski", datetime(2049, 12, 30, 16, 0), datetime(2049, 12, 30, 16, 30)))
            c.execute("INSERT INTO clients VALUES (?, ?, ?)",
                      ("Marcin Marcinowski", datetime(2050, 1, 1, 13, 0), datetime(2050, 1, 1, 14, 0)))
            c.execute("INSERT INTO clients VALUES (?, ?, ?)",
                      ("Szymon Szymański", datetime(2050, 1, 1, 15, 0), datetime(2050, 1, 1, 16, 30)))
            c.execute("INSERT INTO clients VALUES (?, ?, ?)",
                      ("Błażej Błażejowski", datetime(2050, 1, 2, 16, 0), datetime(2050, 1, 2, 17, 0)))
            conn.commit()
        conn.close()

        self.validator = Validator(TEST_DB)

    @patch('tenis_scheduler.reservation.reservation_validator.Validator.invalid_name',
           return_value='Marek Kowalski')
    def test_invalid_name(self, mock_input):
        self.assertEqual(self.validator.invalid_name(), "Marek Kowalski")

    def test_invalid_name_regex(self):
        self.assertEqual(self.validator.invalid_name_regex("Jacek Żółty"), "Jacek Żółty")
        self.assertIsNone(self.validator.invalid_name_regex(" Jacek Żółty"))
        self.assertIsNone(self.validator.invalid_name_regex("Jacek Żółty "))
        self.assertIsNone(self.validator.invalid_name_regex(""))
        self.assertIsNone(self.validator.invalid_name_regex("Double  Space"))
        self.assertIsNone(self.validator.invalid_name_regex("NoSpace"))

    def test_invalid_option(self):
        self.assertIsNone(self.validator.invalid_option(7))
        self.assertIsNone(self.validator.invalid_option("abc"))

    @patch('tenis_scheduler.reservation.reservation_validator.Validator.invalid_date', return_value='01.01.2050 12:00')
    def test_invalid_date(self, mock_input):
        self.assertEqual(self.validator.invalid_date(), "01.01.2050 12:00")

    def test_invalid_date_format(self):
        actual_time_5h = datetime.now() + timedelta(hours=5)
        actual_time_5h = actual_time_5h.replace(minute=30)
        actual_time_5h_str = datetime.strftime(actual_time_5h, "%d.%m.%Y %H:%M")

        actual_time_minus_5h = datetime.utcnow() - timedelta(hours=5)
        actual_time_minus_5h = actual_time_minus_5h.replace(minute=30)
        actual_time_minus_5h_str = datetime.strftime(actual_time_minus_5h, "%d.%m.%Y %H:%M")

        self.assertEqual(self.validator.invalid_date_format(actual_time_5h_str),
                         datetime.strptime(actual_time_5h_str, "%d.%m.%Y %H:%M"))
        self.assertEqual(self.validator.invalid_date_format(actual_time_minus_5h_str),
                         datetime.strptime(actual_time_minus_5h_str, "%d.%m.%Y %H:%M"))
        self.assertIsNone(self.validator.invalid_date_format("32.01.2050 15:00"))
        self.assertIsNone(self.validator.invalid_date_format("2050.01.01 12:00"))
        self.assertIsNone(self.validator.invalid_date_format("01.01.2050 25:00"))
        self.assertIsNone(self.validator.invalid_date_format("01.01.2050 20:61"))

    def test_invalid_minutes(self):
        self.assertEqual(self.validator.invalid_minutes(datetime(2050, 1, 1, 12, 0)), datetime(2050, 1, 1, 12, 0))
        self.assertEqual(self.validator.invalid_minutes(datetime(2050, 1, 1, 15, 30)), datetime(2050, 1, 1, 15, 30))
        self.assertIsNone(self.validator.invalid_minutes(datetime(2050, 1, 1, 16, 31)))
        self.assertIsNone(self.validator.invalid_minutes(datetime(2050, 1, 1, 8, 1)))

    def test_invalid_booking_format(self):
        self.assertEqual(self.validator.invalid_booking_format(1, datetime(2050, 1, 1, 12, 0)), 30)
        self.assertEqual(self.validator.invalid_booking_format(2, datetime(2050, 1, 1, 12, 0)), 60)
        self.assertEqual(self.validator.invalid_booking_format(3, datetime(2050, 1, 1, 12, 0)), 90)
        self.assertIsNone(self.validator.invalid_booking_format(4, datetime(2050, 1, 1, 12, 0)))
        self.assertIsNone(self.validator.invalid_booking_format(3, datetime(2050, 1, 1, 18, 0)))

    def test_check_too_many_reservations(self):
        self.assertIsNone(self.validator.check_too_many_reservations("Adam Kowalski", datetime(2050, 1, 2, 17, 0)))
        self.assertTrue(self.validator.check_too_many_reservations("Marcin Marcinowski", datetime(2050, 1, 3, 12, 0)))

    def test_check_time_range(self):
        self.assertIsNone(self.validator.check_time_range(datetime(2050, 1, 1, 18, 30)))
        self.assertIsNone(self.validator.check_time_range(datetime(2050, 1, 1, 7, 30)))
        self.assertTrue(self.validator.check_time_range(datetime(2050, 1, 1, 8, 0)))
        self.assertTrue(self.validator.check_time_range(datetime(2050, 1, 1, 18, 0)))

    def test_check_if_not_in_past(self):
        self.assertTrue(self.validator.check_if_not_in_past(datetime(2050, 1, 1, 12, 0)))
        self.assertIsNone(self.validator.check_if_not_in_past(datetime(2101, 1, 1, 12, 0)))
        self.assertIsNone(self.validator.check_if_not_in_past(datetime(2000, 1, 1, 12, 0)))
        self.assertIsNone(self.validator.check_if_not_in_past(datetime.now() + timedelta(minutes=59)))
        self.assertTrue(self.validator.check_if_not_in_past(datetime.now() + timedelta(minutes=61)))
        self.assertTrue(self.validator.check_if_not_in_past(datetime.now() + timedelta(minutes=60, seconds=1)))

    def test_check_availability(self):
        self.assertTrue(self.validator.check_availability(datetime(2050, 1, 2, 14, 0), datetime(2050, 1, 2, 15, 30)))
        self.assertIsNone(self.validator.check_availability(datetime(2050, 1, 1, 13, 30), datetime(2050, 1, 1, 14, 0)))
        self.assertTrue(self.validator.check_availability(datetime(2050, 1, 1, 14, 0), datetime(2050, 1, 1, 15, 0)))

    def test_check_closest_reservation(self):
        self.assertEqual(self.validator.check_closest_reservation
                         (datetime(2050, 1, 1, 12, 0), 60), datetime(2050, 1, 1, 14, 0))
        self.assertEqual(self.validator.check_closest_reservation
                         (datetime(2050, 1, 1, 12, 0), 90), datetime(2050, 1, 1, 16, 30))
        self.assertEqual(self.validator.check_closest_reservation
                         (datetime(2049, 12, 30, 16, 0), 30), datetime(2049, 12, 30, 16, 30))
        self.assertIsNone(self.validator.check_closest_reservation(datetime(2050, 1, 2, 18, 0), 60))
        self.assertEqual(self.validator.check_closest_reservation(datetime(2050, 1, 2, 16, 30), 60),datetime(2050, 1, 2, 17, 0))

    def test_get_base_available_times(self):
        self.assertIsNotNone(self.validator.get_base_available_times(datetime(2050, 1, 1, 16, 0)))
        self.assertIsNotNone(self.validator.get_base_available_times(datetime(2050, 1, 2, 11, 0)))
        self.assertListEqual(self.validator.get_base_available_times(datetime(2050, 1, 1, 19, 0)), [])

    def test_check_if_can_cancel(self):
        self.assertEqual(self.validator.check_if_can_cancel
                        ("Adam Kowalski", datetime(2050, 1, 1, 12, 0)), datetime(2050, 1, 1, 12, 0))
        self.assertEqual(self.validator.check_if_can_cancel("Błażej Błażejowski", datetime(2050, 1, 2, 16, 0)), datetime(2050, 1, 2, 16, 0))
        self.assertIsNone(self.validator.check_if_can_cancel("Marcin Marcinowski", datetime(2050, 1, 1, 12, 0)))
        self.assertIsNone(self.validator.check_if_can_cancel("Szymon Szymański", datetime(2050, 1, 1, 15, 30)))

    @classmethod
    def tearDownClass(cls):
        os.remove(TEST_DB)
