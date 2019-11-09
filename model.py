from datetime import datetime
from decimal import *
from typing import NamedTuple, Optional, List

Price = Decimal
Money = Decimal
Amount = int
SKU = str
Unit = str
CustomerID = int
DocumentID = int
NewID = -1


class Product(NamedTuple):
    sku: SKU
    name: str
    units: Unit


class Customer(NamedTuple):
    name: str
    id: CustomerID = NewID


class Receive(NamedTuple):
    sku: SKU
    date: datetime
    price: Price
    amount: Amount
    id: DocumentID = NewID


class Dispatch(NamedTuple):
    cid: CustomerID
    sku: SKU
    date: datetime
    price: Price
    amount: Amount
    id: DocumentID = NewID


class Movement(NamedTuple):
    sku: SKU
    rid: DocumentID
    did: Optional[DocumentID]
    date: datetime
    price: Price
    amount: Amount
    id: DocumentID = NewID


class Balance(NamedTuple):
    id: DocumentID
    date: datetime
    sku: SKU
    price: Price
    amount: Amount
    balance: Amount


class DispatchPlan(NamedTuple):
    price: Price
    requestAmount: Amount
    stockAmount: Amount
    balances: List[Balance]


class ReportEntry(NamedTuple):
    sku: Optional[SKU]
    cost: Money
    price: Price
    amount: Amount


class Report(NamedTuple):
    totalCost: Money
    entries: List[ReportEntry]
