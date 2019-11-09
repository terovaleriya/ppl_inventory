import collections
from sqlite3 import Connection
from typing import List

from model import Product, SKU
from storage.testing import BaseTableTest


class ProductTable:
    def __init__(self, connection: Connection):
        super()
        self.connection = connection

    def set_rf(self):
        CustomerRecord = collections.namedtuple('Product', 'sku name units')
        self.connection.row_factory = lambda c, row: CustomerRecord(*row)

    def create_product(self, product: Product) -> Product:
        cur = self.connection.cursor()
        cur.execute('INSERT INTO product(sku, name, unit) VALUES(?, ?, ?)', product)
        return product

    def delete_product(self, sku: SKU) -> None:
        sql = 'DELETE FROM product WHERE sku=?'
        cur = self.connection.cursor()
        cur.execute(sql, [sku])

    def find_product(self, sku: SKU) -> Product:
        self.set_rf()
        cur = self.connection.cursor()
        return cur.execute('SELECT sku, name, unit FROM product WHERE sku=?', [sku]).fetchone()

    def list_products(self) -> List[Product]:
        self.set_rf()
        cur = self.connection.cursor()
        return cur.execute('SELECT sku, name, unit FROM product').fetchall()


class ProductTableTest(BaseTableTest):
    def setUp(self):
        super().setUp()
        self.table = ProductTable(self.connection)

    def test(self):
        noodles = self.table.create_product(Product(sku="F-234", name="Макароны", units="Упаковка"))
        product = self.table.find_product("F-234")
        self.assertEqual(noodles, product)
        self.table.delete_product("F-234")
        product = self.table.find_product("F-234")
        self.assertEqual(None, product)
