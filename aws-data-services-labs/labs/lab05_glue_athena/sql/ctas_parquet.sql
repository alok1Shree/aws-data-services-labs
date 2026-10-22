-- Convert raw CSV to partitioned, compressed Parquet. Re-run the same aggregates on this table and
-- compare "Data scanned" in run_athena.py: columnar + compressed typically scans a fraction of the CSV bytes.
-- (Replace <bucket> with your bucket name; the external_location must be empty.)
CREATE TABLE orders_lake.orders_parquet
WITH (
    format = 'PARQUET',
    write_compression = 'SNAPPY',
    external_location = 's3://<bucket>/curated/orders_parquet/',
    partitioned_by = ARRAY['dt']
) AS
SELECT order_id, customer_id, amount, status, dt
FROM orders_lake.orders;
