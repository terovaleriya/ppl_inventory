import collections
from sqlite3 import Connection
from typing import List

from model import Customer, CustomerID
from storage.testing import BaseTableTest


class CustomerTable:
    def __init__(self, connection: Connection):
        super()
        self.connection = connection

    def set_rf(self):
        CustomerRecord = collections.namedtuple('Customer', 'name id')
        self.connection.row_factory = lambda c, row: CustomerRecord(*row)

    def create_customer(self, customer: Customer) -> Customer:
        cur = self.connection.cursor()
        cur.execute('INSERT INTO customers(name) VALUES(?)', customer[:-1])
        return customer._replace(id=cur.lastrowid)

    def delete_customer(self, cid: CustomerID) -> None:
        cur = self.connection.cursor()
        cur.execute('DELETE FROM customers WHERE id=?', [cid])

    def find_customer(self, cid: CustomerID) -> Customer:
        self.set_rf()
        cur = self.connection.cursor()
        return cur.execute('SELECT name, id FROM customers WHERE id=?', [cid]).fetchone()

    def list_customers(self) -> List[Customer]:
        self.set_rf()
        cur = self.connection.cursor()
        return cur.execute('SELECT name, id FROM customers').fetchall()


class CustomerTableTest(BaseTableTest):
    def setUp(self):
        super().setUp()
        self.table = CustomerTable(self.connection)

    def test(self):
        bravit = self.table.create_customer(Customer(name="Виталий Брагилевский"))
        cid = bravit.id
        customer = self.table.find_customer(cid)
        self.assertEqual(bravit, customer)
        self.table.delete_customer(cid)
        customer = self.table.find_customer(cid)
        self.assertEqual(None, customer)
