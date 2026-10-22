import json
import boto3
from labs.lab02_eventbridge.publish_events import publish_orders


def test_rule_routes_only_high_value_orders(aws):
    ev, sqs = boto3.client("events"), boto3.client("sqs")
    ev.create_event_bus(Name="orders-bus")
    q = sqs.create_queue(QueueName="high-value-orders")["QueueUrl"]
    arn = sqs.get_queue_attributes(QueueUrl=q, AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]
    ev.put_rule(Name="high-value", EventBusName="orders-bus", EventPattern=json.dumps({
        "source": ["app.orders"], "detail-type": ["OrderPlaced"], "detail": {"amount": [{"numeric": [">=", 1000]}]}}))
    ev.put_targets(Rule="high-value", EventBusName="orders-bus", Targets=[{"Id": "q", "Arn": arn}])
    assert publish_orders("orders-bus", [50, 1200, 5000, 999.99], events=ev) == 4
    msgs = sqs.receive_message(QueueUrl=q, MaxNumberOfMessages=10).get("Messages", [])
    amounts = sorted(json.loads(m["Body"])["detail"]["amount"] for m in msgs)
    assert amounts == [1200, 5000]
