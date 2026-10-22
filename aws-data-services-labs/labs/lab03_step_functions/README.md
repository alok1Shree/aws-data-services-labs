# Lab 03 — Step Functions orchestration

```
ValidateOrder (Lambda, retry w/ backoff) ──► IsValid? ──yes──► PersistOrder (DynamoDB putItem) ──► Done
        │ any error                            └──no────┐
        └───────────────────────────────────────────────┴──► SendToDlq (SQS) ──► Rejected (Fail)
```
Depends on **Lab 01** (DLQ) and **Lab 04** (table).

## Run
```bash
cd labs/03_step_functions/lambdas && zip validate.zip validate.py && aws s3 cp validate.zip s3://<your-bucket>/validate.zip && cd ..
aws cloudformation deploy --template-file template.yaml --stack-name lab03-sfn --capabilities CAPABILITY_IAM \
  --parameter-overrides CodeBucket=<your-bucket> DlqQueueUrl=<DlqUrl> DlqQueueArn=<DlqArn>
aws stepfunctions start-execution --state-machine-arn <StateMachineArn> \
  --input '{"order_id":"ORD-1","customer_id":"C1","amount":250}'
aws stepfunctions start-execution --state-machine-arn <StateMachineArn> --input '{"order_id":"ORD-2","amount":-5}'
```
First execution lands in DynamoDB; the second ends in `Rejected` and appears in the DLQ.

## Design notes
- Direct service integrations (DynamoDB, SQS) avoid glue Lambdas — fewer things to patch, pay for and monitor.
- Retry only transient Lambda errors; business-rule failures are routed (Choice), not retried.
- `ConditionExpression` makes the persist step idempotent if an execution is retried.
- Standard vs Express workflows: Standard = exactly-once, long-running, audit history; Express = at-least-once, high-volume, short.
