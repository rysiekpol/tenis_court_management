from tennis_scheduler.reservation.reservation_validator import Validator
from tennis_scheduler.reservation.database.db_initializer import DatabaseInitializer
from tennis_scheduler.reservation.database.db_initializer_orm import DatabaseInitializerORM
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
import sqlite3, os

TEST_DB = "test_db.sqlite"


class TestValidator(unittest.TestCase):

    def setUp(self) -> None:
        # create new database for each test
        db = DatabaseInitializer(TEST_DB)
        db.insert("Adam Kowalski", datetime(2050, 1, 1, 12, 0), datetime(2050, 1, 1, 13, 0))
        db.insert("Adam Kowalski", datetime(2050, 1, 2, 12, 0), datetime(2050, 1, 2, 13, 0))
        db.insert("Adam Kowalski", datetime(2049, 12, 30, 16, 0), datetime(2049, 12, 30, 16, 30))
        db.insert("Marcin Marcinowski", datetime(2050, 1, 1, 13, 0), datetime(2050, 1, 1, 14, 0))
        db.insert("Szymon Szymański", datetime(2050, 1, 1, 15, 0), datetime(2050, 1, 1, 16, 30))
        db.insert("Szymon Szymański", datetime(2050, 1, 1, 8, 0), datetime(2050, 1, 1, 9, 0))
        db.insert("Błażej Błażejowski", datetime(2050, 1, 2, 16, 0), datetime(2050, 1, 2, 17, 0))

        self.validator = Validator(TEST_DB)

    @patch('tennis_scheduler.reservation.reservation_validator.Validator._invalid_name',
           return_value='Marek Kowalski')
    def test_invalid_name(self, mock_input):
        self.assertEqual(self.validator._invalid_name(), "Marek Kowalski")

    def test_invalid_name_regex(self):
        self.assertEqual(self.validator._invalid_name_regex("Jacek Żółty"), "Jacek Żółty")
        self.assertIsNone(self.validator._invalid_name_regex(" Jacek Żółty"))
        self.assertIsNone(self.validator._invalid_name_regex("Jacek Żółty "))
        self.assertIsNone(self.validator._invalid_name_regex(""))
        self.assertIsNone(self.validator._invalid_name_regex("Double  Space"))
        self.assertIsNone(self.validator._invalid_name_regex("NoSpace"))

    def test_invalid_option(self):
        self.assertIsNone(self.validator._invalid_option(7))
        self.assertIsNone(self.validator._invalid_option("abc"))

    @patch('tennis_scheduler.reservation.reservation_validator.Validator._invalid_date', return_value='01.01.2050 12:00')
    def test_invalid_date(self, mock_input):
        self.assertEqual(self.validator._invalid_date(), "01.01.2050 12:00")

    def test_invalid_date_format(self):
        actual_time_5h = datetime.now() + timedelta(hours=5)
        actual_time_5h = actual_time_5h.replace(minute=30)
        actual_time_5h_str = datetime.strftime(actual_time_5h, "%d.%m.%Y %H:%M")

        actual_time_minus_5h = datetime.utcnow() - timedelta(hours=5)
        actual_time_minus_5h = actual_time_minus_5h.replace(minute=30)
        actual_time_minus_5h_str = datetime.strftime(actual_time_minus_5h, "%d.%m.%Y %H:%M")

        self.assertEqual(self.validator._invalid_date_format(actual_time_5h_str),
                         datetime.strptime(actual_time_5h_str, "%d.%m.%Y %H:%M"))
        self.assertEqual(self.validator._invalid_date_format(actual_time_minus_5h_str),
                         datetime.strptime(actual_time_minus_5h_str, "%d.%m.%Y %H:%M"))
        self.assertIsNone(self.validator._invalid_date_format("32.01.2050 15:00"))
        self.assertIsNone(self.validator._invalid_date_format("2050.01.01 12:00"))
        self.assertIsNone(self.validator._invalid_date_format("01.01.2050 25:00"))
        self.assertIsNone(self.validator._invalid_date_format("01.01.2050 20:61"))

    def test_invalid_minutes(self):
        self.assertEqual(self.validator._invalid_minutes(datetime(2050, 1, 1, 12, 0)), datetime(2050, 1, 1, 12, 0))
        self.assertEqual(self.validator._invalid_minutes(datetime(2050, 1, 1, 15, 30)), datetime(2050, 1, 1, 15, 30))
        self.assertIsNone(self.validator._invalid_minutes(datetime(2050, 1, 1, 16, 31)))
        self.assertIsNone(self.validator._invalid_minutes(datetime(2050, 1, 1, 8, 1)))

    def test_invalid_booking_format(self):
        self.assertEqual(self.validator._invalid_booking_format(1, datetime(2050, 1, 1, 12, 0)), 30)
        self.assertEqual(self.validator._invalid_booking_format(2, datetime(2050, 1, 1, 12, 0)), 60)
        self.assertEqual(self.validator._invalid_booking_format(3, datetime(2050, 1, 1, 12, 0)), 90)
        self.assertIsNone(self.validator._invalid_booking_format(4, datetime(2050, 1, 1, 12, 0)))
        self.assertIsNone(self.validator._invalid_booking_format(3, datetime(2050, 1, 1, 18, 0)))

    def test_check_too_many_reservations(self):
        self.assertIsNone(self.validator._check_too_many_reservations("Adam Kowalski", datetime(2050, 1, 2, 17, 0)))
        self.assertTrue(self.validator._check_too_many_reservations("Marcin Marcinowski", datetime(2050, 1, 3, 12, 0)))

    def test_check_time_range(self):
        self.assertIsNone(self.validator._check_time_range(datetime(2050, 1, 1, 18, 30)))
        self.assertIsNone(self.validator._check_time_range(datetime(2050, 1, 1, 7, 30)))
        self.assertTrue(self.validator._check_time_range(datetime(2050, 1, 1, 8, 0)))
        self.assertTrue(self.validator._check_time_range(datetime(2050, 1, 1, 18, 0)))

    def test_check_if_not_in_past(self):
        self.assertTrue(self.validator._check_if_not_in_past(datetime(2050, 1, 1, 12, 0)))
        self.assertIsNone(self.validator._check_if_not_in_past(datetime(2101, 1, 1, 12, 0)))
        self.assertIsNone(self.validator._check_if_not_in_past(datetime(2000, 1, 1, 12, 0)))
        self.assertIsNone(self.validator._check_if_not_in_past(datetime.now() + timedelta(minutes=59)))
        self.assertTrue(self.validator._check_if_not_in_past(datetime.now() + timedelta(minutes=61)))
        self.assertTrue(self.validator._check_if_not_in_past(datetime.now() + timedelta(minutes=60, seconds=1)))

    def test_check_availability(self):
        self.assertTrue(self.validator._check_availability(datetime(2050, 1, 2, 14, 0), datetime(2050, 1, 2, 15, 30)))
        self.assertIsNone(self.validator._check_availability(datetime(2050, 1, 1, 13, 30), datetime(2050, 1, 1, 14, 0)))
        self.assertTrue(self.validator._check_availability(datetime(2050, 1, 1, 14, 0), datetime(2050, 1, 1, 15, 0)))

    def test_check_closest_reservation(self):
        self.assertEqual(self.validator._check_closest_reservation
                         (datetime(2050, 1, 1, 12, 0), 60), datetime(2050, 1, 1, 11, 0))
        self.assertEqual(self.validator._check_closest_reservation
                         (datetime(2050, 1, 1, 12, 0), 90), datetime(2050, 1, 1, 10, 30))
        self.assertEqual(self.validator._check_closest_reservation
                         (datetime(2049, 12, 30, 16, 0), 30), datetime(2049, 12, 30, 15, 30))
        self.assertEqual(self.validator._check_closest_reservation(datetime(2050, 1, 1, 14, 30), 90), datetime(2050, 1, 1, 16, 30))
        self.assertEqual(self.validator._check_closest_reservation(datetime(2050, 1, 2, 16, 30), 60),datetime(2050, 1, 2, 17, 0))

    def test_get_base_available_times(self):
        self.assertIsNotNone(self.validator._get_base_available_times(datetime(2050, 1, 1, 16, 0)))
        self.assertIsNotNone(self.validator._get_base_available_times(datetime(2050, 1, 2, 11, 0)))

    def test_check_if_can_cancel(self):
        self.assertEqual(self.validator._check_if_can_cancel
                        ("Adam Kowalski", datetime(2050, 1, 1, 12, 0)), datetime(2050, 1, 1, 12, 0))
        self.assertEqual(self.validator._check_if_can_cancel
                         ("Błażej Błażejowski", datetime(2050, 1, 2, 16, 0)), datetime(2050, 1, 2, 16, 0))
        self.assertIsNone(self.validator._check_if_can_cancel
                          ("Marcin Marcinowski", datetime(2050, 1, 1, 12, 0)))
        self.assertIsNone(self.validator._check_if_can_cancel
                          ("Szymon Szymański", datetime(2050, 1, 1, 15, 30)))

    def test_check_data_range(self):
        self.assertTrue(self.validator._check_data_range(datetime(2050, 1, 1), datetime(2050, 1, 8)))
        self.assertTrue(self.validator._check_data_range(datetime(2100, 12, 25), datetime(2100, 12, 31)))
        self.assertIsNone(self.validator._check_data_range(datetime(2050, 1, 1), datetime(2050, 1, 9)))
        self.assertIsNone(self.validator._check_data_range(datetime(2050, 1, 20), datetime(2050, 1, 19)))
        self.assertIsNone(self.validator._check_data_range(datetime(2101, 1, 1), datetime(2101, 1, 5)))
        self.assertIsNone(self.validator._check_data_range
                          (datetime.now()-timedelta(days=1), datetime.now()+timedelta(days=2)))
        self.assertTrue(self.validator._check_data_range(datetime.now(), datetime.now() + timedelta(days=2)))

    def test_invalid_extension_format(self):
        self.assertIsNone(self.validator._invalid_extension_format("txt"))
        self.assertIsNone(self.validator._invalid_extension_format("docx"))
        self.assertTrue(self.validator._invalid_extension_format("csv"))
        self.assertTrue(self.validator._invalid_extension_format("json"))

    def test_invalid_filename_format(self):
        self.assertIsNone(self.validator._invalid_filename_format("błąd"))
        self.assertIsNone(self.validator._invalid_filename_format(""))
        self.assertIsNone(self.validator._invalid_filename_format("file%file"))
        self.assertTrue(self.validator._invalid_filename_format("01.01-08.01"))

    def test_invalid_choice_json_format(self):
        self.assertFalse(self.validator._invalid_choice_json_format("NO"))
        self.assertFalse(self.validator._invalid_choice_json_format("n"))
        self.assertTrue(self.validator._invalid_choice_json_format("y"))
        self.assertTrue(self.validator._invalid_choice_json_format("yEs"))
        self.assertIsNone(self.validator._invalid_choice_json_format(""))
        self.assertIsNone(self.validator._invalid_choice_json_format("nOpE"))

    @classmethod
    def tearDownClass(cls):
        os.remove(TEST_DB)
