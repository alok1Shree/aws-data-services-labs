"""Run an Athena query, wait for completion, print rows and the bytes scanned (what you are billed on)."""
import sys
import time

from common.aws import client

TERMINAL = {"SUCCEEDED", "FAILED", "CANCELLED"}


def wait_for_query(athena, query_id: str, poll_seconds: float = 1.0, timeout_seconds: float = 120) -> dict:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        execution = athena.get_query_execution(QueryExecutionId=query_id)["QueryExecution"]
        if execution["Status"]["State"] in TERMINAL:
            return execution
        time.sleep(poll_seconds)
    raise TimeoutError(f"query {query_id} did not finish in {timeout_seconds}s")


def run_query(sql: str, workgroup: str = "labs", athena=None, poll_seconds: float = 1.0) -> dict:
    athena = athena or client("athena")
    qid = athena.start_query_execution(QueryString=sql, WorkGroup=workgroup)["QueryExecutionId"]
    execution = wait_for_query(athena, qid, poll_seconds)
    state = execution["Status"]["State"]
    if state != "SUCCEEDED":
        raise RuntimeError(f"query {state}: {execution['Status'].get('StateChangeReason', '')}")
    rows = athena.get_paginator("get_query_results").paginate(QueryExecutionId=qid)
    data = [[c.get("VarCharValue") for c in r["Data"]] for page in rows for r in page["ResultSet"]["Rows"]]
    return {"rows": data, "bytes_scanned": execution["Statistics"]["DataScannedInBytes"]}


if __name__ == "__main__":
    result = run_query(open(sys.argv[1]).read())
    for row in result["rows"]:
        print(row)
    print(f"data scanned: {result['bytes_scanned']:,} bytes")
