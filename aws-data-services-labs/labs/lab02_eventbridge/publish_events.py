"""Publish OrderPlaced events to the custom bus. Only amount >= 1000 matches the rule and reaches SQS."""
import json
import sys

from common.aws import client


def publish_orders(bus_name: str, amounts: list[float], events=None) -> int:
    events = events or client("events")
    entries = [
        {
            "EventBusName": bus_name,
            "Source": "app.orders",
            "DetailType": "OrderPlaced",
            "Detail": json.dumps({"order_id": f"ORD-{i:04d}", "amount": amt}),
        }
        for i, amt in enumerate(amounts, 1)
    ]
    failed = 0
    for i in range(0, len(entries), 10):  # PutEvents accepts max 10 entries per call
        resp = events.put_events(Entries=entries[i : i + 10])
        failed += resp["FailedEntryCount"]
    if failed:
        raise RuntimeError(f"{failed} events failed to publish")  # PutEvents can partially fail with HTTP 200
    return len(entries)


if __name__ == "__main__":
    print(publish_orders(sys.argv[1], [50, 250, 1200, 5000, 999.99]), "events published")
