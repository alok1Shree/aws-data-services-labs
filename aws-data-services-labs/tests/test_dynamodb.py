import boto3
import pytest
from labs.lab04_dynamodb.orders_repo import OrdersRepo, DuplicateOrder, InvalidTransition


@pytest.fixture
def repo(aws):
    boto3.client("dynamodb").create_table(
        TableName="orders", BillingMode="PAY_PER_REQUEST",
        AttributeDefinitions=[{"AttributeName": n, "AttributeType": "S"} for n in ("pk", "sk", "gsi1pk", "gsi1sk")],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}, {"AttributeName": "sk", "KeyType": "RANGE"}],
        GlobalSecondaryIndexes=[{"IndexName": "gsi1", "Projection": {"ProjectionType": "ALL"},
                                 "KeySchema": [{"AttributeName": "gsi1pk", "KeyType": "HASH"}, {"AttributeName": "gsi1sk", "KeyType": "RANGE"}]}])
    return OrdersRepo("orders")


def test_put_is_idempotent(repo):
    repo.put_order("O1", "C1", 99.5, "2026-01-01T10:00:00Z")
    with pytest.raises(DuplicateOrder):
        repo.put_order("O1", "C1", 99.5, "2026-01-01T10:00:00Z")
    assert len(repo.orders_for_customer("C1")) == 1


def test_query_patterns(repo):
    repo.put_order("O1", "C1", 10, "2026-01-01T10:00:00Z")
    repo.put_order("O2", "C1", 20, "2026-01-01T09:00:00Z")
    repo.put_order("O3", "C2", 30, "2026-01-01T11:00:00Z")
    assert [o["order_id"] for o in repo.orders_for_customer("C1")] == ["O1", "O2"]
    assert [o["order_id"] for o in repo.orders_by_status("PLACED")] == ["O2", "O1", "O3"]  # oldest first


def test_transition_requires_expected_state_and_moves_gsi(repo):
    repo.put_order("O1", "C1", 10, "2026-01-01T10:00:00Z")
    repo.transition("O1", "C1", "PLACED", "SHIPPED", "2026-01-02T00:00:00Z")
    assert repo.orders_by_status("PLACED") == []
    assert [o["order_id"] for o in repo.orders_by_status("SHIPPED")] == ["O1"]
    with pytest.raises(InvalidTransition):
        repo.transition("O1", "C1", "PLACED", "CANCELLED", "2026-01-03T00:00:00Z")
