# Lab 02 — EventBridge routing

**Goal:** decouple producers from consumers with content-based routing.

`publish_events.py` → **orders-bus** → rule (`source=app.orders`, `detail-type=OrderPlaced`, `amount >= 1000`) → SQS `high-value-orders`.

## Run
```bash
aws cloudformation deploy --template-file template.yaml --stack-name lab02-eventbridge
python -m labs.lab02_eventbridge.publish_events orders-bus
aws sqs receive-message --queue-url <QueueUrl> --max-number-of-messages 10   # expect the 1200 and 5000 events only
```
Cleanup: `aws cloudformation delete-stack --stack-name lab02-eventbridge`

## Design notes
- `PutEvents` returns HTTP 200 even when entries fail — always check `FailedEntryCount` (done in the code).
- Filtering in the rule (numeric matching) beats filtering in consumers: fewer invocations, less cost.
- The queue policy is scoped with `aws:SourceArn` to this rule — avoid `Principal: *`.
- EventBridge vs SQS vs Kafka: EventBridge = routing/fan-out on event content; SQS = buffering/work queue; Kafka = ordered replayable log at high throughput.
