CREATE TABLE IF NOT EXISTS product
(
    sku  CHAR(10) PRIMARY KEY,
    name TEXT NOT NULL,
    unit CHAR(15)
);

CREATE TABLE IF NOT EXISTS receive_document
(
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    sku    CHAR(10)  NOT NULL REFERENCES product (sku),
    date   TIMESTAMP NOT NULL,
    price  DECIMAL   NOT NULL CHECK (price > 0),
    amount INTEGER   NOT NULL
);

CREATE TABLE IF NOT EXISTS dispatch_document
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER   NOT NULL REFERENCES customers (id),
    sku         CHAR(10)  NOT NULL REFERENCES product (sku),
    date        TIMESTAMP NOT NULL,
    price       DECIMAL   NOT NULL CHECK (price > 0),
    amount      INTEGER   NOT NULL
);

CREATE TABLE IF NOT EXISTS movements_journal
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    sku         CHAR(10)                                  NOT NULL REFERENCES product (sku),
    receive_id  INTEGER REFERENCES receive_document (id)  NOT NULL,
    dispatch_id INTEGER REFERENCES dispatch_document (id) NULL,
    date        TIMESTAMP                                 NOT NULL,
    price       DECIMAL                                   NOT NULL CHECK (price > 0),
    amount      INTEGER                                   NOT NULL
);

CREATE INDEX IF NOT EXISTS movements_journal_sku ON movements_journal (sku);

CREATE TABLE IF NOT EXISTS balance_register
(
    id      INTEGER PRIMARY KEY REFERENCES receive_document,
    date    TIMESTAMP NOT NULL,
    sku     CHAR(10)  NOT NULL REFERENCES product (sku),
    price   DECIMAL   NOT NULL CHECK (price > 0),
    amount  INTEGER   NOT NULL,
    balance INTEGER   NOT NULL CHECK (balance > 0)
);

CREATE TABLE IF NOT EXISTS customers
(
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT(1) NOT NULL UNIQUE
)
