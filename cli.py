#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from decimal import Decimal, InvalidOperation
from typing import Optional

import click
from tabulate import tabulate

from model import CustomerID, SKU, Amount
from warehouse import Warehouse

warehouse = Warehouse()


# noinspection PyUnusedLocal
def validate_price(ctx, param, value):
    try:
        return Decimal(value)
    except InvalidOperation:
        raise click.UsageError(f'{value} is not a valid price')


# noinspection PyUnusedLocal
def validate_sku(ctx, param, value):
    if value is None:
        return value
    product = warehouse.find_product(value)
    if product is None:
        raise click.UsageError(f"Товар '{value}' не найден")
    return value


# noinspection PyUnusedLocal
def validate_customer(ctx, param, value):
    customer = warehouse.find_customer(value)
    if customer is None:
        raise click.UsageError(f"Покупатель '{value}' не найден")
    return value


@click.group()
def main():
    """
    Простой CLI для нашего складского учета
    """
    pass


@main.command("list-products", help='Вывести список всех товаров')
def list_products():
    products = warehouse.list_products()
    from tabulate import tabulate
    print(tabulate(products, numalign="right", headers=["Артикул", "Наименованиее", "Ед. измерения"], tablefmt="psql"))


@main.command("list-customers", help='Вывести список всех покупателей')
def list_customers():
    products = warehouse.list_customers()
    print(tabulate(products, numalign="right", headers=["ФИО", "№"], tablefmt="psql"))


@main.command("add-customer", help='Зарегистрировать нового покупателя')
@click.option('--name', prompt='Имя клиента', help='Имя клиента')
def add_customers(name: str):
    warehouse.create_customer(name)


@main.command("delete-customer", help='Удалить покупателя')
@click.option('--id', prompt='ID клиента', type=click.INT, help='ID клиента', callback=validate_customer)
def delete_customers(id: CustomerID):
    warehouse.delete_customer(id)


@main.command("receive", help='Ввести поступление товара')
@click.option('--sku', prompt='Артикул', help='Артикул товара', callback=validate_sku)
@click.option('--price', prompt='Цена', help='Цена товара', callback=validate_price)
@click.option('--amount', type=click.IntRange(1), prompt='Количеество', help='Количество товара')
def receive(sku: str, price: Decimal, amount: int):
    warehouse.receive(sku, price, amount)


@main.command("dispatch", help='Ввести убытие товара')
@click.option('--cid', prompt='ID покупателя', help='ID покупателя товара', callback=validate_customer)
@click.option('--sku', prompt='Артикул', help='Артикул товара', callback=validate_sku)
@click.option('--amount', type=click.IntRange(1), prompt='Количеество', help='Количество товара')
def dispatch(cid: CustomerID, sku: SKU, amount: Amount):
    warehouse.dispatch(cid, sku, amount)


@main.command("list-receives", help='Вывести список всех поступлений')
def list_receives():
    products = warehouse.list_receives()
    print(tabulate(products, numalign="right", headers=["Артикул", "Дата", "Цена", "Количество", "№"], tablefmt="psql"))


@main.command("list-dispatches", help='Вывести список всех убытий')
def list_dispatch():
    products = warehouse.list_dispatches()
    print(tabulate(products, numalign="right", headers=["Артикул", "Дата", "Цена", "Количество", "№"], tablefmt="psql"))


@main.command("report", help='Вывести отчет по стоимости и количеству товаров')
def report():
    report = warehouse.report()
    print(f"Общая стоимость всех находящихся на складе товаров: {report.totalCost}")
    print(f"Количество различных артикулов: {len(report)}")
    print(
        tabulate(report.entries, numalign="right", headers=["Артикул", "Общая стоимость", "Средняя Цена", "Количество"],
                 tablefmt="psql"))


@main.command("month-report", help='Вывести отчет с группировкой по месяцам')
def report():
    report = warehouse.report_by_month()
    print(
        tabulate(report, numalign="right",
                 headers=["П/У", "Период", "Артикул", "Ср. цена", "Мин. цена", "Макс. цена", "Среднее кол-во",
                          "Кол-во"],
                 tablefmt="psql"))


@main.command("list-movements", help='Вывести все передвижеия товаров')
@click.option('--sku', help='Артикул товара', callback=validate_sku)
def list_movements(sku: Optional[SKU] = None):
    movements = warehouse.list_movements(sku)
    print(tabulate(movements, numalign="right",
                   headers=["Артикул", "Приход №", "Расход №", "Дата", "Цена", "Количество", "№"],
                   tablefmt="psql"))


@main.command("plan-dispatch", help='Спланировать открузку товара')
@click.option('--sku', prompt='Артикул', help='Артикул товара', callback=validate_sku)
@click.option('--amount', type=click.IntRange(1), prompt='Количеество', help='Количество товара')
def plan_dispatch(sku, amount):
    plan = warehouse.plan_dispatch(sku, amount)
    print(f"Доступно для заказа: {plan.stockAmount} из {plan.requestAmount}")
    print(f"Цена на единицу продукции: {plan.price}")
    print(f"Стоимость всей партии: {plan.price * plan.stockAmount}")
    print(tabulate(plan.balances, numalign="right", headers=["№", "Дата", "", "Цена", "Количество", "Остаток"],
                   tablefmt="psql"))


if __name__ == "__main__":
    main()
