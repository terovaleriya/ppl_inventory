import unittest
from decimal import Decimal

from model import Product, CustomerID, DispatchPlan, Balance, ReportEntry
from warehouse import Warehouse


class SqlStorageCase(unittest.TestCase):
    warehouse: Warehouse
    cid: CustomerID

    def setUp(self) -> None:
        super().setUp()
        self.warehouse = Warehouse(":memory:", create_tables=True)
        self.warehouse.create_product(Product("W1", "Вино", "Бутылка"))
        self.warehouse.create_product(Product("P1", "Пармезан", "Килограмм"))
        self.warehouse.create_product(Product("C1", "Колбаса", "Килограмм"))
        customer = self.warehouse.create_customer("Виталий Брагилевский")
        self.cid = customer.id

    def test_dispatch(self):
        # Основной тестовый сценарий
        self.warehouse.receive("W1", Decimal(100), 10)
        self.warehouse.receive("W1", Decimal(150), 6)
        self.warehouse.receive("W1", Decimal(70), 9)

        plan = self.warehouse.plan_dispatch("W1", 12)
        self.assertEqual(len(plan.balances), 2)
        self.assertEqual(plan.requestAmount, 12)
        self.assertEqual(plan.stockAmount, 12)
        self.assertEqual(plan.balances[0].price, Decimal('100'))
        self.assertEqual(plan.balances[0].amount, 10)
        self.assertEqual(plan.balances[0].balance, 10)
        self.assertEqual(plan.balances[1].price, Decimal('150'))
        self.assertEqual(plan.balances[1].amount, 2)
        self.assertEqual(plan.balances[1].balance, 6)

        self.warehouse.dispatch(self.cid, "W1", 12)
        report = self.warehouse.report()
        self.assertEqual(report.totalCost, Decimal('1230'))
        self.assertEqual(report.entries, [ReportEntry(sku='W1', cost=Decimal(1230), price=Decimal(94), amount=13)])

        movements = self.warehouse.list_movements('W1')
        self.assertEqual(len(movements), 5)

    def test_dispatch_ex(self):
        # Мы теестируем попытку взять больше чем есть
        self.warehouse.receive("P1", Decimal(100), 10)
        self.warehouse.receive("P1", Decimal(150), 6)
        self.warehouse.receive("P1", Decimal(70), 9)

        plan = self.warehouse.plan_dispatch("P1", 26)  # Больше, чем у нас есть
        self.assertEqual(len(plan.balances), 3)
        self.assertEqual(plan.requestAmount, 26)
        self.assertEqual(plan.stockAmount, 25)
        self.assertEqual(plan.balances[0].price, Decimal('100'))
        self.assertEqual(plan.balances[0].amount, 10)
        self.assertEqual(plan.balances[0].balance, 10)
        self.assertEqual(plan.balances[1].price, Decimal('150'))
        self.assertEqual(plan.balances[1].amount, 6)
        self.assertEqual(plan.balances[1].balance, 6)

        self.assertRaises(Exception, lambda: self.warehouse.dispatch(self.cid, "P1", 26))


if __name__ == '__main__':
    unittest.main()
