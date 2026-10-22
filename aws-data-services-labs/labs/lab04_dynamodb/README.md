# Lab 04 — DynamoDB single-table design

Table `orders` (on-demand), GSI `gsi1`, TTL on `expires_at`, point-in-time recovery.

| Access pattern | Operation |
|---|---|
| Orders of a customer | `Query pk=CUSTOMER#id, sk begins_with ORDER#` |
| Orders by status, oldest first | `Query gsi1 gsi1pk=STATUS#PLACED` |
| Create exactly once | `PutItem` + `attribute_not_exists` condition |
| Safe status change | `UpdateItem` + `#status = :expected` condition |

## Run
```bash
aws cloudformation deploy --template-file template.yaml --stack-name lab04-dynamodb
```
Run the unit tests (`pytest tests/test_dynamodb.py -v`) to see each pattern, then point `OrdersRepo("orders")` at the real table.

## Design notes
- Model from access patterns, not entities. A `Scan` in production code is a design smell.
- Hot partition risk: `STATUS#PLACED` as a GSI partition key concentrates writes at scale — shard it (`STATUS#PLACED#0..N`) for high volume.
- Conditional writes give idempotency without a separate lock table.
- TTL deletions are eventual (typically within hours of expiry) — filter expired items in reads if exactness matters.
