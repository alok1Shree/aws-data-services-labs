# Lab 05 — Glue Data Catalog + Athena over S3

```
generate_sample_data.py ─► s3://<bucket>/raw/orders/dt=…/*.csv ─► Glue crawler ─► Data Catalog (orders_lake.orders)
                                                                              └► Athena (workgroup "labs", 1 GB scan cap)
```

## Run
```bash
aws cloudformation deploy --template-file template.yaml --stack-name lab05-lake --capabilities CAPABILITY_IAM
python -m labs.lab05_glue_athena.generate_sample_data
aws s3 sync labs/lab05_glue_athena/sample_data/orders s3://<BucketName>/raw/orders/
aws glue start-crawler --name orders-raw-crawler          # wait until READY
python -m labs.lab05_glue_athena.run_athena labs/lab05_glue_athena/sql/daily_revenue.sql
```
Then run `sql/ctas_parquet.sql` (edit the bucket) and repeat the aggregate on `orders_parquet`; record both "data scanned" numbers in your notes.
Cleanup: empty the bucket (`aws s3 rm s3://<BucketName> --recursive`), then delete the stack.

## Design notes
- Athena bills per **byte scanned**: partition by the column you filter on, store Parquet, select only the columns you need.
- A crawler is convenient for exploration; for production prefer explicit table DDL / `MSCK REPAIR` or partition projection so schema changes are reviewed, not discovered.
- Workgroup with `EnforceWorkGroupConfiguration` + scan cutoff protects against a runaway `SELECT *`.
- Small files hurt: many tiny objects per partition slow queries — compact during ETL.
