# AWS Data Services — Hands-On Labs

Six small, runnable labs on the AWS services used to build event-driven and analytical data pipelines.
Each lab has infrastructure as code (CloudFormation), Python (boto3) code, tests, and design notes.

| # | Lab | Services | What it demonstrates |
|---|-----|----------|----------------------|
| 01 | [SQS + DLQ](labs/lab01_sqs_dlq) | SQS, CloudWatch | Retries, poison-message isolation, DLQ alarm, redrive |
| 02 | [EventBridge](labs/lab02_eventbridge) | EventBridge, SQS | Custom bus, content-based routing (numeric filter) |
| 03 | [Step Functions](labs/lab03_step_functions) | Step Functions, Lambda, DynamoDB, SQS | Validate → choice → persist; retry/catch; failures to DLQ |
| 04 | [DynamoDB](labs/lab04_dynamodb) | DynamoDB | Single-table design, GSI, TTL, idempotent writes, optimistic concurrency |
| 05 | [Glue + Athena](labs/lab05_glue_athena) | S3, Glue, Athena | Partitioned lake, crawler, cost-capped workgroup, CSV → Parquet (CTAS) |
| 06 | [Textract](labs/lab06_textract) | Textract, S3 | OCR lines + forms key/values, confidence-based human review |

## How the pieces fit
```
producer ─► EventBridge (02) ─► SQS (01) ─► consumer
                                    │ failures
                                    ▼
                               DLQ (01) ◄── Step Functions (03) ──► DynamoDB (04)
S3 raw CSV ─► Glue crawler ─► Data Catalog ─► Athena (05)            Textract (06) ─► S3 JSON
```
Lab 03 depends on Labs 01 and 04. The others are independent.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
make install        # boto3, pytest, moto, cfn-lint
make test           # 17 tests, no AWS account needed (moto mocks + botocore stubs)
make lint           # cfn-lint on all templates
export AWS_REGION=ap-south-1   # then follow each lab's README to deploy to your own account
```

## What is verified
- **Tested without AWS:** SQS/DLQ behavior, EventBridge routing, DynamoDB access patterns, Lambda validator, Athena polling logic (stubbed), Textract parsing (fixture), sample-data generator — all via `pytest`, run in CI.
- **Linted, not deployed by CI:** the CloudFormation templates pass `cfn-lint`. Deploy them to a sandbox account yourself; Glue crawler, Athena, Step Functions and Textract behavior is only exercised against real AWS when you run the labs.
- Add your own notes/screenshots per lab (e.g. Athena "data scanned" before/after Parquet) in `docs/` once you have run them.

## Cost & safety
Everything is on-demand/pay-per-use and small, but: Textract and Athena bill per page / per byte scanned, Glue crawlers bill per run time.
Use a sandbox account, set an AWS Budget alert, never upload real customer documents, and delete each stack when done
(empty S3 buckets first). Do not commit credentials; `.env` is git-ignored.

## Repository layout
```
common/            shared boto3 client helpers
labs/lab0X_*/      template.yaml + code + README (design notes)
tests/             pytest suites (moto / stubs)
.github/workflows  CI: cfn-lint + pytest
```
