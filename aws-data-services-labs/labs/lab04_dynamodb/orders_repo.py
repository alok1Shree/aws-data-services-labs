"""Single-table access patterns for orders.

  pk = CUSTOMER#<customer_id>   sk = ORDER#<order_id>
  gsi1pk = STATUS#<status>      gsi1sk = <created_at ISO8601>

Access patterns: (1) get/list a customer's orders, (2) list orders by status in time order,
(3) idempotent create, (4) status transition with optimistic concurrency.
"""
from decimal import Decimal

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from common.aws import resource


class DuplicateOrder(Exception):
    pass


class InvalidTransition(Exception):
    pass


class OrdersRepo:
    def __init__(self, table_name: str = "orders", ddb=None):
        self.table = (ddb or resource("dynamodb")).Table(table_name)

    def put_order(self, order_id: str, customer_id: str, amount, created_at: str, ttl_epoch: int | None = None) -> dict:
        item = {
            "pk": f"CUSTOMER#{customer_id}",
            "sk": f"ORDER#{order_id}",
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": Decimal(str(amount)),  # boto3 rejects float
            "status": "PLACED",
            "created_at": created_at,
            "gsi1pk": "STATUS#PLACED",
            "gsi1sk": created_at,
        }
        if ttl_epoch:
            item["expires_at"] = ttl_epoch
        try:
            # Idempotency: a redelivered SQS message / retried Step Functions task cannot create a second order.
            self.table.put_item(Item=item, ConditionExpression="attribute_not_exists(pk) AND attribute_not_exists(sk)")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise DuplicateOrder(order_id) from e
            raise
        return item

    def orders_for_customer(self, customer_id: str) -> list[dict]:
        resp = self.table.query(
            KeyConditionExpression=Key("pk").eq(f"CUSTOMER#{customer_id}") & Key("sk").begins_with("ORDER#")
        )
        return resp["Items"]

    def orders_by_status(self, status: str, limit: int = 50) -> list[dict]:
        resp = self.table.query(
            IndexName="gsi1", KeyConditionExpression=Key("gsi1pk").eq(f"STATUS#{status}"), Limit=limit, ScanIndexForward=True
        )
        return resp["Items"]

    def transition(self, order_id: str, customer_id: str, from_status: str, to_status: str, at: str) -> None:
        try:
            self.table.update_item(
                Key={"pk": f"CUSTOMER#{customer_id}", "sk": f"ORDER#{order_id}"},
                UpdateExpression="SET #s = :to, gsi1pk = :gpk, gsi1sk = :at",
                ConditionExpression="#s = :from",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={":to": to_status, ":from": from_status, ":gpk": f"STATUS#{to_status}", ":at": at},
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise InvalidTransition(f"{order_id} is not in {from_status}") from e
            raise
