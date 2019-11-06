from datetime import date
from decimal import Decimal
from typing import List, Sequence, Tuple

Price = Decimal
Money = Decimal
Amount = int
SKU = str
Unit = str
CustomerID = str
MovementID = str
Product = (SKU, str, Unit)  # sku, name, unit
Customer = (CustomerID, str)  # id, name
Movement = (MovementID, SKU, date, Price, Amount)  # tid, pid, batch, date, price, amount
InventoryRecord = Tuple[SKU, Amount, Money]
