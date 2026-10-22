import json
import boto3
from labs.lab01_sqs_dlq.producer import send_orders
from labs.lab01_sqs_dlq.consumer import poll_once
from labs.lab01_sqs_dlq.redrive import redrive


def make_queues(max_receive=2):
    sqs = boto3.client("sqs")
    dlq = sqs.create_queue(QueueName="orders-dlq")["QueueUrl"]
    dlq_arn = sqs.get_queue_attributes(QueueUrl=dlq, AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]
    q = sqs.create_queue(QueueName="orders-queue", Attributes={
        "RedrivePolicy": json.dumps({"deadLetterTargetArn": dlq_arn, "maxReceiveCount": max_receive})})["QueueUrl"]
    return sqs, q, dlq


def depth(sqs, url):
    return int(sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["ApproximateNumberOfMessages"])["Attributes"]["ApproximateNumberOfMessages"])


def test_poison_messages_end_up_in_dlq_and_good_ones_are_deleted(aws):
    sqs, q, dlq = make_queues(max_receive=2)
    assert send_orders(q, count=10, poison_every=5, sqs=sqs) == 10  # 2 poison (5 and 10)
    totals = {"processed": 0, "failed": 0}
    for _ in range(4):  # visibility timeout 0 -> immediate redelivery, simulating retries
        s = poll_once(q, sqs=sqs, wait_seconds=0, visibility_timeout=0)
        totals = {k: totals[k] + s[k] for k in totals}
    assert totals["processed"] == 8
    assert depth(sqs, dlq) == 2
    assert depth(sqs, q) == 0


def test_redrive_moves_messages_back(aws):
    sqs, q, dlq = make_queues()
    for i in range(3):
        sqs.send_message(QueueUrl=dlq, MessageBody=json.dumps({"order_id": str(i), "amount": 1}))
    assert redrive(dlq, q, sqs=sqs) == 3
    assert depth(sqs, dlq) == 0 and depth(sqs, q) == 3
