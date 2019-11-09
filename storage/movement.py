import collections
from datetime import datetime
from decimal import Decimal
from sqlite3 import Connection
from typing import List

from model import Movement, SKU, Amount, DocumentID
from storage.testing import BaseTableTest


class MovementJournal:
    def __init__(self, connection: Connection):
        super()
        self.connection = connection

    def set_rf(self):
        MovementRecord = collections.namedtuple('Movement', 'sku rid did date price amount id')
        self.connection.row_factory = lambda c, row: MovementRecord(*row)

    def add_movement(self, movement: Movement) -> Movement:
        sql = '''
        INSERT INTO movements_journal(sku, receive_id, dispatch_id, date, price, amount) 
        VALUES(?, ?, ?, ?, ?, ?)'''
        cur = self.connection.cursor()
        cur.execute(sql, movement[:-1])
        return movement._replace(id=cur.lastrowid)

    def get_movement_history_record(self, sku: SKU = None) -> List[Movement]:
        self.set_rf()
        if sku is None:
            sql, p = 'SELECT sku, receive_id, dispatch_id, date, price, amount, id FROM movements_journal', []
        else:
            sql, p = 'SELECT sku, receive_id, dispatch_id, date, price, amount, id FROM movements_journal WHERE sku=?', [
                sku]
        cur = self.connection.cursor().execute(sql, p)
        res = cur.fetchall()
        return res

    def report(self):
        sql = '''SELECT *
                FROM (SELECT '->'                              AS type,
                             strftime('%m-%Y', date)           AS period,
                             sku,
                             SUM(amount * price) / SUM(amount) AS avgPrice,
                             MIN(price)                        AS minPrice,
                             MAX(price)                        AS maxPrice,
                             AVG(amount)                       AS avgAmount,
                             SUM(amount)                       AS amount
                      FROM movements_journal
                      WHERE dispatch_id IS NULL
                      group by strftime('%m-%Y', date), sku
                      UNION
                      SELECT '<-'                              AS type,
                             strftime('%m-%Y', date)           AS period,
                             sku,
                             SUM(amount * price) / SUM(amount) AS avgPrice,
                             MIN(price)                        AS minPrice,
                             MAX(price)                        AS maxPrice,
                             AVG(amount)                       AS avgAmount,
                             SUM(amount)                       AS amount
                      FROM movements_journal
                      WHERE dispatch_id IS NOT NULL
                      GROUP BY strftime('%m-%Y', date), sku)
                ORDER BY type, sku, period
                '''
        cur = self.connection.cursor().execute(sql)
        res = cur.fetchall()
        return res


class MovementJournalTest(BaseTableTest):
    def setUp(self):
        super().setUp()
        self.journal = MovementJournal(self.connection)

    def add_movement(self, sku: SKU, rid: DocumentID, did: DocumentID, ds: str, price: str,
                     amount: Amount) -> Movement:
        movement = Movement(sku, rid, did, datetime.strptime(ds, '%d/%m/%Y'), Decimal(price), amount)
        return self.journal.add_movement(movement)

    def test(self):
        m0 = self.add_movement("U-345", 1, 2, "20/12/2018", '140', 12)
        m1 = self.add_movement("U-345", 3, 4, "23/12/2018", '140', -5)
        m2 = self.add_movement("U-346", 5, 6, "20/12/2018", '150', 12)
        m3 = self.add_movement("U-346", 7, 8, "23/12/2018", '150', -5)
        history_record = self.journal.get_movement_history_record()
        self.assertEqual([m0, m1, m2, m3], history_record)
        history_record = self.journal.get_movement_history_record("U-346")
        self.assertEqual([m2, m3], history_record)
