-- Deterministic seed data for the backup/restore exercise (synthetic, no real customer data).
SET client_min_messages = warning;
CREATE SCHEMA IF NOT EXISTS lab;

CREATE TABLE lab.accounts (
    account_id   integer PRIMARY KEY,
    holder       text    NOT NULL,
    branch_code  char(4) NOT NULL,
    opened_on    date    NOT NULL
);

CREATE TABLE lab.ledger_entries (
    entry_id     bigint  PRIMARY KEY,
    account_id   integer NOT NULL REFERENCES lab.accounts(account_id),
    amount_cents bigint  NOT NULL CHECK (amount_cents <> 0),
    memo         text    NOT NULL,
    posted_on    date    NOT NULL
);

CREATE INDEX ledger_entries_account_idx ON lab.ledger_entries(account_id);

INSERT INTO lab.accounts (account_id, holder, branch_code, opened_on)
SELECT g, 'synthetic-holder-' || g, lpad((g % 7)::text, 4, '0'), date '2020-01-01' + g
FROM generate_series(1, 50) AS g;

INSERT INTO lab.ledger_entries (entry_id, account_id, amount_cents, memo, posted_on)
SELECT g,
       ((g - 1) % 50) + 1,
       CASE WHEN g % 3 = 0 THEN -(g * 17) ELSE g * 101 END,
       'synthetic-entry-' || g,
       date '2024-01-01' + (g % 365)
FROM generate_series(1, 1000) AS g;

CREATE VIEW lab.account_balances AS
SELECT account_id, sum(amount_cents) AS balance_cents, count(*) AS entries
FROM lab.ledger_entries GROUP BY account_id;
