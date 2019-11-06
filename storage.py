from abc import ABC, abstractmethod
from typing import List

from base_types import Money, Amount, SKU, CustomerID, Product, Customer, Movement, InventoryRecord


class Storage(ABC):
    @abstractmethod
    def open(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def create_product(self, product: Product) -> None:
        pass

    @abstractmethod
    def delete_product(self, sku: SKU) -> None:
        pass

    @abstractmethod
    def find_product(self, sku: SKU) -> Product:
        pass

    @abstractmethod
    def create_customer(self, customer: Customer) -> None:
        pass

    @abstractmethod
    def delete_customer(self, cid: CustomerID) -> None:
        pass

    @abstractmethod
    def find_customer(self, cid: CustomerID) -> Customer:
        pass

    @abstractmethod
    def add_movement(self, movement: Movement) -> None:
        pass

    # общая стоимость всех находящихся на складе товаров
    @abstractmethod
    def get_overall_cost(self, sku: SKU = None) -> Money:
        pass

    # стоимость требуемых к расходу единиц товара
    @abstractmethod
    def get_fifo_price(self, sku: SKU, amount: Amount) -> Money:
        pass

    @abstractmethod
    def get_overall_amount(self, sku: SKU = None) -> Amount:
        pass

    @abstractmethod
    def get_inventory_records(self) -> List[InventoryRecord]:
        pass

    @abstractmethod
    def get_movement_history_record(self) -> Movement:
        pass
