-- noinspection SqlWithoutWhereForFile

DELETE
FROM product;
DELETE
FROM customers;

INSERT INTO product(sku, name, unit)
VALUES ('F-01', 'Макароны', 'Упаковка'),
       ('F-02', 'Вино', 'Бутылка'),
       ('F-03', 'Пармезан', 'Килограмм'),
       ('F-04', 'Клюква сушеная', 'Упаковка'),
       ('F-05', 'Чай', 'Упаковка'),
       ('F-06', 'Рис', 'Упаковка');

INSERT INTO customers(name)
VALUES ('Виталий Брагилевский'),
       ('Иван Крузенштерн');

