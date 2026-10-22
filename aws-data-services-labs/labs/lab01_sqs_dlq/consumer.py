"""Long-polling consumer. Failed messages are NOT deleted: they reappear after the visibility timeout
and, after maxReceiveCount receives, SQS moves them to the dead-letter queue."""
import json
import sys

from common.aws import client


def process(body: dict) -> None:
    """Business logic. Raises on bad input, which is what triggers the retry/DLQ path."""
    if not isinstance(body.get("amount"), (int, float)):
        raise ValueError(f"invalid amount for {body.get('order_id')}: {body.get('amount')!r}")


def poll_once(queue_url: str, sqs=None, wait_seconds: int = 1, visibility_timeout: int | None = None) -> dict:
    sqs = sqs or client("sqs")
    kwargs = {"QueueUrl": queue_url, "MaxNumberOfMessages": 10, "WaitTimeSeconds": wait_seconds}
    if visibility_timeout is not None:
        kwargs["VisibilityTimeout"] = visibility_timeout
    stats = {"processed": 0, "failed": 0}
    for msg in sqs.receive_message(**kwargs).get("Messages", []):
        try:
            process(json.loads(msg["Body"]))
        except (ValueError, json.JSONDecodeError) as exc:
            stats["failed"] += 1
            print(f"FAILED (will retry / DLQ): {exc}")
            continue
        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg["ReceiptHandle"])
        stats["processed"] += 1
    return stats


if __name__ == "__main__":
    url = sys.argv[1]
    while True:
        print(poll_once(url, wait_seconds=20))
