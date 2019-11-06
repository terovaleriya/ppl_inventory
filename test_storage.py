import os
import unittest
import sqlite3
from sqlite3.dbapi2 import Connection
from typing import Tuple

from base_types import Customer
from main import SqlStorage
from storage import Storage


class SqlStorageCase(unittest.TestCase):
    storage: Storage

    def setUp(self) -> None:
        dbfilename = 'test.db'
        if os.path.exists(dbfilename):
            os.remove(dbfilename)
        conn: Connection = sqlite3.connect("test.db")
        self.storage = SqlStorage(conn)
        self.storage.open()

    def tearDown(self) -> None:
        self.storage.close()

    def test_customer(self):
        bravit: Customer = ("1456", "Виталий Брагилевский")
        self.storage.create_customer(bravit)
        customer = self.storage.find_customer("1456")
        self.assertEqual(bravit, customer)
        self.storage.delete_customer("1456")
        customer = self.storage.find_customer("1456")
        self.assertEqual(None, customer)

    def test_product(self):
        noodles = ("F-234", "Макароны", "Упаковка")
        self.storage.create_product(noodles)
        product = self.storage.find_product("F-234")
        self.assertEqual(noodles, product)
        self.storage.delete_product("F-234")
        product = self.storage.find_product("F-234")
        self.assertEqual(None, product)

    def test_overall_cost(self):
        self.storage.add_movement(("U-342", "F-234", "24/12/2018", "109", "3"))
        self.storage.add_movement(("U-343", "F-235", "23/11/2018", "139", "4"))
        overall_cost = self.storage.get_overall_cost()
        self.assertEqual(883, overall_cost)
        overall_cost = self.storage.get_overall_cost("U-342")
        self.assertEqual(327, overall_cost)

    def test_overall_amount(self):
        self.storage.add_movement(("U-342", "F-234", "24/12/2018", "109", "3"))
        self.storage.add_movement(("U-343", "F-235", "23/11/2018", "139", "4"))
        overall_amount = self.storage.get_overall_amount()
        self.assertEqual(7, overall_amount)
        overall_amount = self.storage.get_overall_amount("U-342")
        self.assertEqual(3, overall_amount)

    def test_fifo_price(self):
        self.storage.add_movement(("U-342", "F-234", "24/12/2018", "109", "3"))
        self.storage.add_movement(("U-344", "F-234", "25/12/2018", "112", "5"))
        fifo_price = self.storage.get_fifo_price("F-234", 4)
        self.assertEqual(109.75, fifo_price)
        self.storage.add_movement(("U-345", "F-236", "23/12/2018", "140", "1"))
        self.storage.add_movement(("U-345", "F-236", "20/12/2018", "120", "12"))
        fifo_price = self.storage.get_fifo_price("F-234", 8)
        self.assertEqual(120, fifo_price)

    def test_inventory_records(self):
        self.storage.add_movement(("U-345", "F-236", "20/12/2018", "140", "12"))
        self.storage.add_movement(("U-345", "F-236", "23/12/2018", "140", "-5"))
        self.storage.add_movement(("U-346", "F-236", "20/12/2018", "150", "12"))
        self.storage.add_movement(("U-346", "F-236", "23/12/2018", "150", "-5"))
        inventory_records = self.storage.get_inventory_records()
        self.assertEqual([("U-345", 7, 980), ("U-346", 7, 1050)], inventory_records)

    def test_movement_history_record(self):
        self.storage.add_movement(("U-345", "F-236", "20/12/2018", "140", "12"))
        self.storage.add_movement(("U-345", "F-236", "23/12/2018", "140", "-5"))
        self.storage.add_movement(("U-346", "F-236", "20/12/2018", "150", "12"))
        self.storage.add_movement(("U-346", "F-236", "23/12/2018", "150", "-5"))
        history_record = self.storage.get_movement_history_record()
        self.assertEqual([(1, "U-345", "F-236", "20/12/2018", 140, 12),
                          (2, "U-345", "F-236", "23/12/2018", 140, -5),
                          (3, "U-346", "F-236", "20/12/2018", 150, 12),
                          (4, "U-346", "F-236", "23/12/2018", 150, -5)], history_record)
        history_record = self.storage.get_movement_history_record("U-346")
        self.assertEqual([(3, "U-346", "F-236", "20/12/2018", 150, 12),
                          (4, "U-346", "F-236", "23/12/2018", 150, -5)], history_record)


if __name__ == '__main__':
    unittest.main()
