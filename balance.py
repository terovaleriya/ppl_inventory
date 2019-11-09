import collections
import sqlite3
from datetime import datetime
from decimal import Decimal
from sqlite3 import Connection
from typing import List, Optional, Any

from model import Balance, Receive, DocumentID, Amount, SKU, ReportEntry
from storage.testing import BaseTableTest


class BalanceRegister:
    def __init__(self, connection: Connection):
        super()
        self.connection = connection

    def set_rf(self):
        BalanceRecord = collections.namedtuple('Balance', 'id date sku price amount balance')
        self.connection.row_factory = lambda c, row: BalanceRecord(*row)

    def receive(self, receive: Receive) -> None:
        cur = self.connection.cursor()
        cur.execute('INSERT INTO balance_register(id, date, sku, price, amount, balance) VALUES(?, ?, ?, ?, ?, ?)',
                    [receive.id, receive.date, receive.sku, receive.price, receive.amount, receive.amount])

    def dispatch(self, id: DocumentID, delta: Amount) -> None:
        cbal = self.balance(id)
        if cbal is None:
            raise Exception(f'Receive {id} is already depleted')
        nbal = cbal - delta
        if nbal == 0:
            sql, p = 'DELETE FROM balance_register WHERE id = ?', [id]
        else:
            sql, p = 'UPDATE balance_register SET balance = ? WHERE id=?', [nbal, id]
        cur = self.connection.cursor()
        cur.execute(sql, p)

    def list(self) -> List[Balance]:
        self.set_rf()
        cur = self.connection.cursor()
        return cur.execute('SELECT id, date, sku, price, amount, balance FROM balance_register').fetchall()

    def balance(self, id: DocumentID) -> Optional[Amount]:
        self.connection.row_factory = sqlite3.Row
        cur = self.connection.cursor()
        return cur.execute('SELECT balance FROM balance_register WHERE id=?', [id]).fetchone()[0]

    def plan_dispatch(self, sku: SKU, amount: Amount) -> List[Balance]:
        self.set_rf()
        sql = '''SELECT id, date, sku, price, amount, balance 
                FROM (
                         SELECT *,
                                SUM(balance) OVER (ROWS UNBOUNDED PRECEDING ) - balance as rbalance
                         FROM balance_register WHERE sku=?) AS A
                WHERE rbalance < ?
                
                '''
        cur = self.connection.cursor()
        return cur.execute(sql, [sku, amount]).fetchall()

    def report(self) -> List[ReportEntry]:
        ReportEntryRecord = collections.namedtuple('ReportEntry', 'sku cost price amount')
        self.connection.row_factory = lambda c, row: ReportEntryRecord(*row)
        sql = '''SELECT sku, SUM(price * balance) AS cost, SUM(price * balance) / SUM(balance) as price, SUM(balance) as amount
            FROM balance_register
            GROUP BY sku
            '''
        cur = self.connection.cursor()
        return cur.execute(sql).fetchall()


class BalanceRegisterTest(BaseTableTest):
    def setUp(self):
        super().setUp()
        self.register = BalanceRegister(self.connection)

    def test(self):
        now = datetime.now()
        id = 12
        self.register.receive(Receive("F-01", now, Decimal('2'), 100, id))

        ll = self.register.list()
        self.assertEqual(len(ll), 1)
        balance = Balance(id, now, 'F-01', Decimal('2'), 100, 100)
        self.assertEqual(balance, ll[0])

        self.register.dispatch(id, 5)

        ll = self.register.list()
        self.assertEqual(len(ll), 1)
        balance = Balance(id, now, 'F-01', Decimal('2'), 100, 95)
        self.assertEqual(balance, ll[0])

        self.register.dispatch(id, 95)

        ll = self.register.list()
        self.assertEqual(len(ll), 0)
