import csv
import pytest
from botocore.stub import Stubber
import boto3
from labs.lab05_glue_athena.generate_sample_data import generate
from labs.lab05_glue_athena.run_athena import run_query


def test_sample_data_is_hive_partitioned(tmp_path):
    assert generate(str(tmp_path), days=3, rows_per_day=5) == 15
    files = sorted((tmp_path / "orders").glob("dt=*/part-0.csv"))
    assert [f.parent.name for f in files] == ["dt=2026-01-01", "dt=2026-01-02", "dt=2026-01-03"]
    assert next(csv.reader(open(files[0]))) == ["order_id", "customer_id", "amount", "status"]


def _athena_stub(final_state, reason=""):
    athena = boto3.client("athena", region_name="ap-south-1", aws_access_key_id="x", aws_secret_access_key="x")
    st = Stubber(athena)
    st.add_response("start_query_execution", {"QueryExecutionId": "q1"})
    st.add_response("get_query_execution", {"QueryExecution": {"Status": {"State": "RUNNING"}}})
    st.add_response("get_query_execution", {"QueryExecution": {
        "Status": {"State": final_state, "StateChangeReason": reason}, "Statistics": {"DataScannedInBytes": 2048}}})
    return athena, st


def test_run_query_success_returns_rows_and_bytes():
    athena, st = _athena_stub("SUCCEEDED")
    st.add_response("get_query_results", {"ResultSet": {"Rows": [
        {"Data": [{"VarCharValue": "dt"}, {"VarCharValue": "revenue"}]}, {"Data": [{"VarCharValue": "2026-01-01"}, {"VarCharValue": "10.5"}]}]}})
    with st:
        out = run_query("select 1", athena=athena, poll_seconds=0)
    assert out["bytes_scanned"] == 2048 and out["rows"][1] == ["2026-01-01", "10.5"]


def test_run_query_failure_raises():
    athena, st = _athena_stub("FAILED", "SYNTAX_ERROR")
    with st, pytest.raises(RuntimeError, match="SYNTAX_ERROR"):
        run_query("selec", athena=athena, poll_seconds=0)
