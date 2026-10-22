"""Validation Lambda used by the state machine."""


def handler(event, context=None):
    errors = []
    order = event if isinstance(event, dict) else {}
    for field in ("order_id", "customer_id"):
        if not order.get(field):
            errors.append(f"missing {field}")
    amount = order.get("amount")
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount <= 0:
        errors.append("amount must be a positive number")
    return {"valid": not errors, "errors": errors, "order": order}
