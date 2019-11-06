CREATE TABLE IF NOT EXISTS product
(
    sku  CHAR(10) PRIMARY KEY,
    name TEXT NOT NULL,
    unit CHAR(15)
);

CREATE TABLE IF NOT EXISTS movements
(
    trans_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku      CHAR(10)      NOT NULL,
    batch    CHAR(10)      NOT NULL,
    date     INTEGER       NOT NULL,
    price    NUMERIC(5, 2) NOT NULL CHECK (price > 0),
    amount   INTEGER       NOT NULL,
    FOREIGN KEY (sku)
        REFERENCES product (sku)
);

CREATE TABLE IF NOT EXISTS customers
(
    id   CHAR(10) PRIMARY KEY,
    name TEXT(1) NOT NULL
)
