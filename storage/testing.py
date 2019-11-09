import sqlite3
import unittest
from decimal import Decimal


class BaseTableTest(unittest.TestCase):
    connection: sqlite3.Connection

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
        sqlite3.register_adapter(Decimal, lambda d: str(d))
        sqlite3.register_converter("DECIMAL", lambda s: Decimal(s.decode("utf-8")))
        with open('tables.sql', 'r') as file:
            data = file.read()
            self.connection.executescript(data)
