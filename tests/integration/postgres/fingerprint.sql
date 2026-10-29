-- Prints one line per table: <table>|<row_count>|<md5 of ordered rows>. Used to compare source vs restored DB.
SELECT 'lab.accounts|' || count(*) || '|' || md5(coalesce(string_agg(t::text, ',' ORDER BY account_id), ''))
FROM lab.accounts t;
SELECT 'lab.ledger_entries|' || count(*) || '|' || md5(coalesce(string_agg(t::text, ',' ORDER BY entry_id), ''))
FROM lab.ledger_entries t;
SELECT 'lab.account_balances|' || count(*) || '|' || md5(coalesce(string_agg(t::text, ',' ORDER BY account_id), ''))
FROM lab.account_balances t;
