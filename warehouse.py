import sqlite3
from datetime import datetime
from decimal import Decimal
from functools import reduce
from sqlite3 import Connection
from typing import List, Optional

from model import Customer, CustomerID, Product, SKU, Receive, Dispatch, Movement, Amount, DispatchPlan, Money, \
    Report, Balance
from storage.balance import BalanceRegister
from storage.customer import CustomerTable
from storage.dispatch import DispatchDocument
from storage.movement import MovementJournal
from storage.product import ProductTable
from storage.receive import ReceiveDocument


class Warehouse:
    receive_document: ReceiveDocument
    dispatch_document: DispatchDocument
    customer_table: CustomerTable
    product_table: ProductTable
    balance_registry: BalanceRegister

    def __init__(self, db: str = "main.db", create_tables: bool = False):
        self.connection: Connection = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
        self.connection.execute("PRAGMA foreign_keys = 1")
        sqlite3.register_adapter(Decimal, lambda d: str(d))
        sqlite3.register_converter("DECIMAL", lambda s: Decimal(s.decode("utf-8")))
        if create_tables:
            self.create_table()
        self.customer_table = CustomerTable(self.connection)
        self.product_table = ProductTable(self.connection)
        self.receive_document = ReceiveDocument(self.connection)
        self.movementJournal = MovementJournal(self.connection)
        self.dispatch_document = DispatchDocument(self.connection)
        self.balance_registry = BalanceRegister(self.connection)

    def create_table(self):
        with open('tables.sql', 'r') as file:
            data = file.read()
            self.connection.executescript(data)

    # Работа с клиентом
    def create_customer(self, name: str) -> Customer:
        customer = self.customer_table.create_customer(Customer(name))
        self.connection.commit()
        return customer

    def delete_customer(self, cid: CustomerID) -> None:
        self.customer_table.delete_customer(cid)
        self.connection.commit()

    def find_customer(self, cid: CustomerID) -> Customer:
        return self.customer_table.find_customer(cid)

    def list_customers(self) -> List[Customer]:
        return self.customer_table.list_customers()

    # Работа с товаром
    def create_product(self, product: Product) -> None:
        self.product_table.create_product(product)
        self.connection.commit()

    def delete_product(self, sku: SKU) -> None:
        self.delete_product(sku)
        self.connection.commit()

    def find_product(self, sku: SKU) -> Product:
        return self.product_table.find_product(sku)

    def list_products(self) -> List[Product]:
        return self.product_table.list_products()

    # Поступление товаров на склад
    def receive(self, sku: str, price: Decimal, amount: int) -> None:
        receive = self.receive_document.create_document(Receive(sku, datetime.now(), price, amount))
        self.movementJournal.add_movement(
            Movement(receive.sku, receive.id, None, receive.date, receive.price, receive.amount))
        self.balance_registry.receive(receive)
        self.connection.commit()

    def list_receives(self) -> List[Receive]:
        return self.receive_document.list_documents()

    # Списание товаров со склада
    def dispatch(self, cid: CustomerID, sku: SKU, amount: Amount) -> None:
        plan = self.plan_dispatch(sku, amount)
        if plan.requestAmount > plan.stockAmount:
            raise Exception(f"Недостаточно товара: {plan.requestAmount} > s{plan.stockAmount}")
        acc = amount
        now = datetime.now()
        dispatch = self.dispatch_document.create_document(Dispatch(cid, sku, now, plan.price, plan.stockAmount))
        for balance in plan.balances:
            ia = min(acc, balance.amount)
            self.movementJournal.add_movement(
                Movement(sku, balance.id, dispatch.id, now, balance.price, ia))
            self.balance_registry.dispatch(balance.id, ia)
        self.connection.commit()

    def list_dispatches(self) -> List[Dispatch]:
        return self.dispatch_document.list_documents()

    def list_movements(self, sku: Optional[SKU] = None) -> List[Movement]:
        return self.movementJournal.get_movement_history_record(sku)

    def plan_dispatch(self, sku: SKU, amount: Amount) -> DispatchPlan:
        balances: List[Balance] = self.balance_registry.plan_dispatch(sku, amount)
        if not balances:
            return DispatchPlan(Decimal(0), amount, 0, [])
        acc = amount
        for i, balance in enumerate(balances):
            ia = min(acc, balance.amount)
            acc = acc - ia
            balances[i] = balance._replace(amount=ia)
        stock_amount: Amount = reduce(lambda b0, b1: b0 + b1.amount, balances, 0)
        cost: Money = reduce(lambda b0, b1: b0 + b1.amount * b1.price, balances, Decimal(0))
        return DispatchPlan(cost / stock_amount, amount, stock_amount, balances)

    def report(self) -> Report:
        entries = self.balance_registry.report()
        cost: Money = reduce(lambda f, s: f + s.cost, entries, Decimal(0))
        return Report(cost, entries)

    def report_by_month(self):
        return self.movementJournal.report()
