import pytest
from labs.lab03_step_functions.lambdas.validate import handler


def test_valid_order():
    out = handler({"order_id": "O1", "customer_id": "C1", "amount": 10})
    assert out["valid"] and out["errors"] == []


@pytest.mark.parametrize("event", [{"order_id": "O1", "amount": 5}, {"order_id": "O1", "customer_id": "C", "amount": -1},
                                    {"order_id": "O1", "customer_id": "C", "amount": "10"}, {"customer_id": "C", "amount": True}, None])
def test_invalid_orders(event):
    assert handler(event)["valid"] is False
