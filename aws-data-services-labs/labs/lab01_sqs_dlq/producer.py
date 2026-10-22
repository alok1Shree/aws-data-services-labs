"""Send sample order messages; every Nth message is deliberately malformed (a 'poison' message)."""
import json
import sys

from common.aws import client


def send_orders(queue_url: str, count: int = 10, poison_every: int = 5, sqs=None) -> int:
    sqs = sqs or client("sqs")
    sent = 0
    for i in range(1, count + 1):
        poison = poison_every and i % poison_every == 0
        body = {"order_id": f"ORD-{i:04d}", "customer_id": f"C{i % 3}", "amount": "not-a-number" if poison else 100 + i}
        sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(body))
        sent += 1
    return sent


if __name__ == "__main__":
    print(f"sent {send_orders(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 10)} messages")
