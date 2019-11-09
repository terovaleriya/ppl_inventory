import collections
from datetime import datetime
from decimal import Decimal
from sqlite3 import Connection
from typing import List

from model import Dispatch
from storage.testing import BaseTableTest


class DispatchDocument:
    def __init__(self, connection: Connection):
        super()
        self.connection = connection

    def create_document(self, record: Dispatch) -> Dispatch:
        cur = self.connection.cursor()
        cur.execute('INSERT INTO dispatch_document(customer_id, sku, date, price, amount) VALUES(?, ?, ?, ?, ?)',
                    record[:-1])
        return record._replace(id=cur.lastrowid)

    def list_documents(self) -> List[Dispatch]:
        DispatchRecord = collections.namedtuple('Dispatch', 'cid sku date price amount id')
        self.connection.row_factory = lambda c, row: DispatchRecord(*row)
        cur = self.connection.cursor()
        return cur.execute('SELECT customer_id, sku, date, price, amount, id FROM dispatch_document').fetchall()


class DispatchDocumentTest(BaseTableTest):
    def setUp(self):
        super().setUp()
        self.document = DispatchDocument(self.connection)

    def test(self):
        record = self.document.create_document(Dispatch(1, "F-234", datetime.now(), Decimal('1.2'), 5))
        records = self.document.list_documents()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], record)
