import collections
from datetime import datetime
from decimal import Decimal
from sqlite3 import Connection
from typing import List

from model import Receive
from storage.testing import BaseTableTest


class ReceiveDocument:
    def __init__(self, connection: Connection):
        super()
        self.connection = connection

    def create_document(self, record: Receive) -> Receive:
        cur = self.connection.cursor()
        cur.execute('INSERT INTO receive_document(sku, date, price, amount) VALUES(?, ?, ?, ?)', record[:-1])
        return record._replace(id=cur.lastrowid)

    def list_documents(self) -> List[Receive]:
        ReceiveRecord = collections.namedtuple('Receive', 'sku date price amount id')
        self.connection.row_factory = lambda c, row: ReceiveRecord(*row)
        cur = self.connection.cursor()
        return cur.execute('SELECT sku, date, price, amount, id FROM receive_document').fetchall()


class ReceiveDocumentTest(BaseTableTest):
    def setUp(self):
        super().setUp()
        self.document = ReceiveDocument(self.connection)

    def test(self):
        record = self.document.create_document(Receive("F-234", datetime.now(), Decimal('1.2'), 5))
        records = self.document.list_documents()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], record)
