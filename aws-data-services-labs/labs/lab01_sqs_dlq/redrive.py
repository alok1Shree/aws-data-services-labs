"""Move messages from the DLQ back to the source queue after the bug is fixed.
Production alternative: the native API  sqs.start_message_move_task(SourceArn=dlq_arn, DestinationArn=queue_arn)."""
import sys

from common.aws import client


def redrive(dlq_url: str, queue_url: str, sqs=None, max_messages: int = 1000) -> int:
    sqs = sqs or client("sqs")
    moved = 0
    while moved < max_messages:
        msgs = sqs.receive_message(QueueUrl=dlq_url, MaxNumberOfMessages=10, WaitTimeSeconds=1).get("Messages", [])
        if not msgs:
            break
        for m in msgs:
            sqs.send_message(QueueUrl=queue_url, MessageBody=m["Body"])
            sqs.delete_message(QueueUrl=dlq_url, ReceiptHandle=m["ReceiptHandle"])
            moved += 1
    return moved


if __name__ == "__main__":
    print(f"redriven {redrive(sys.argv[1], sys.argv[2])} messages")
