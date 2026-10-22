# Lab 01 — SQS and Dead-Letter Queues

**Goal:** show how a pipeline isolates poison messages instead of blocking on them.

```
producer ──► orders-queue ──► consumer
                 │  (receive count > maxReceiveCount)
                 ▼
             orders-dlq ──► CloudWatch alarm ──► redrive after fix
```

## Run
```bash
aws cloudformation deploy --template-file template.yaml --stack-name lab01-sqs
aws cloudformation describe-stacks --stack-name lab01-sqs --query "Stacks[0].Outputs"
python -m labs.lab01_sqs_dlq.producer <QueueUrl> 10   # (run from repo root; use `python -m labs.lab01_sqs_dlq.producer` if the module path complains)
python -m labs.lab01_sqs_dlq.consumer <QueueUrl>      # watch bad messages fail, then land in the DLQ
python -m labs.lab01_sqs_dlq.redrive <DlqUrl> <QueueUrl>
```
Cleanup: `aws cloudformation delete-stack --stack-name lab01-sqs`

## Design notes (interview-ready)
- Standard queues are **at-least-once**: consumers must be idempotent (see Lab 04's conditional writes).
- `VisibilityTimeout` must exceed worst-case processing time, or healthy messages get redelivered.
- `maxReceiveCount` too low sends transient failures to the DLQ; too high delays isolation of true poison messages.
- DLQ retention (14 days) is longer than the source queue so nothing expires before someone investigates.
- Alarm on `ApproximateNumberOfMessagesVisible > 0` for the DLQ — an unwatched DLQ is just a silent data-loss bucket.
