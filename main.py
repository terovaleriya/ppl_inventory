from sqlite3.dbapi2 import Connection
from typing import List

from base_types import Movement, InventoryRecord, SKU, Amount, Money, CustomerID, Customer, Product
from storage import Storage


class SqlStorage(Storage):
    filename = 'tables.sql'

    def __init__(self, connection: Connection) -> None:
        super()
        self.connection = connection

    def open(self) -> None:
        with open(self.filename, 'r') as file:
            data = file.read()
        self.connection.executescript(data)

    def close(self) -> None:
        pass

    def create_product(self, product: Product) -> None:
        sql = 'INSERT INTO product(sku, name, unit) VALUES(?,?, ?)'
        cur = self.connection.cursor()
        cur.execute(sql, product)

    def delete_product(self, sku: SKU) -> None:
        sql = 'DELETE FROM product WHERE sku=?'
        cur = self.connection.cursor()
        cur.execute(sql, [sku])

    def find_product(self, sku: SKU) -> Product:
        sql = 'SELECT sku, name, unit FROM product WHERE sku=?'
        cur = self.connection.cursor()
        return cur.execute(sql, [sku]).fetchone()

    def create_customer(self, customer: Customer) -> None:
        sql = 'INSERT INTO customers(id, name) VALUES(?,?)'
        cur = self.connection.cursor()
        cur.execute(sql, customer)

    def delete_customer(self, cid: CustomerID) -> None:
        sql = 'DELETE FROM customers WHERE id=?'
        cur = self.connection.cursor()
        cur.execute(sql, [cid])

    def find_customer(self, cid: CustomerID) -> Customer:
        sql = 'SELECT id, name FROM customers WHERE id=?'
        cur = self.connection.cursor()
        return cur.execute(sql, [cid]).fetchone()

    def add_movement(self, movement: Movement) -> None:
        sql = 'INSERT INTO movements(sku, batch, date, price, amount) VALUES(?, ?, ?, ?, ?)'
        cur = self.connection.cursor()
        cur.execute(sql, movement)

    def get_overall_cost(self, sku: SKU = None) -> Money:
        if sku is None:
            sql = 'SELECT SUM(amount*price) FROM movements'
            cur = self.connection.cursor().execute(sql)
        else:
            sql = 'SELECT SUM(amount*price) FROM movements WHERE sku=?'
            cur = self.connection.cursor().execute(sql, [sku])
        return cur.fetchone()[0]

    def get_fifo_price(self, sku: SKU, amount: Amount) -> Money:
        pass

    def get_overall_amount(self, sku: SKU = None) -> Amount:
        if sku is None:
            sql = 'SELECT SUM(amount) FROM movements'
            cur = self.connection.cursor().execute(sql)
        else:
            sql = 'SELECT SUM(amount) FROM movements WHERE sku=?'
            cur = self.connection.cursor().execute(sql, [sku])
        return cur.fetchone()[0]

    def get_inventory_records(self) -> List[InventoryRecord]:
        sql = 'SELECT sku, SUM(amount), SUM(amount*price) FROM movements group by sku order by sku'
        cur = self.connection.cursor().execute(sql)
        return cur.fetchall()

    def get_movement_history_record(self, sku: SKU = None) -> Movement:
        if sku is None:
            sql = 'SELECT * FROM movements'
            cur = self.connection.cursor().execute(sql)
        else:
            sql = 'SELECT * FROM movements WHERE sku=?'
            cur = self.connection.cursor().execute(sql, [sku])
        return cur.fetchall()
