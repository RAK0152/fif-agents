import base64
import hashlib
import json

import pytest

from fif_agents import gcp, tools
from fif_agents.models import Action, Plan, Review


@pytest.fixture(autouse=True)
def environment(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    monkeypatch.setenv("FIF_ALLOW_WRITES", "false")
    monkeypatch.setenv("FIF_EXECUTE_QUERIES", "false")
    monkeypatch.setenv("FIF_BQ_MAX_BYTES", "1000")
    monkeypatch.setenv("FIF_BQ_LOCATION", "US")


def state(*actions, approved=True, missing=None):
    return {"plan": Plan(summary="test", actions=list(actions), rollback="restore previous values",
                         missing_inputs=missing or []).model_dump_json(),
            "review": Review(approved=approved, rationale="test").model_dump_json()}


def action(**kwargs):
    return Action(kind="gcp_api", description="Update Cloud Run", service="run", method="PATCH",
                  path="/v2/projects/test-project/locations/us-central1/services/demo", **kwargs)


def test_default_preview_does_not_call_cloud(monkeypatch):
    monkeypatch.setattr(gcp, "request", lambda *a, **k: pytest.fail("Unexpected cloud call"))
    result = tools.execute_reviewed_plan(state(action()), ("run",))
    assert result["status"] == "preview"


@pytest.mark.parametrize("value", [{}, state(action(), approved=False), state(action(), missing=["resource"])])
def test_missing_invalid_or_rejected_review_blocks(monkeypatch, value):
    monkeypatch.setattr(gcp, "request", lambda *a, **k: pytest.fail("Unexpected cloud call"))
    assert tools.execute_reviewed_plan(value, ("run",))["status"] == "blocked"


def test_preflight_all_actions_before_mutating(monkeypatch):
    monkeypatch.setenv("FIF_ALLOW_WRITES", "true")
    monkeypatch.setattr(gcp, "request", lambda *a, **k: pytest.fail("Should preflight entire plan"))
    invalid = Action(kind="gcp_api", description="out of scope", service="compute", path="/compute/v1/projects/test-project/zones")
    assert tools.execute_reviewed_plan(state(action(), invalid), ("run",))["status"] == "blocked"


def test_pending_operation_stops_dependents(monkeypatch):
    monkeypatch.setenv("FIF_ALLOW_WRITES", "true")
    calls = []
    def request(*args, **kwargs):
        calls.append(args)
        return {"name": "projects/test-project/locations/us-central1/operations/op1", "done": False}
    monkeypatch.setattr(gcp, "request", request)
    result = tools.execute_reviewed_plan(state(action(), action()), ("run",))
    assert result["status"] == "pending_operation"
    assert result["remaining_actions"] == 1
    assert len(calls) == 1


def test_failed_operation_stops_dependents(monkeypatch):
    monkeypatch.setenv("FIF_ALLOW_WRITES", "true")
    monkeypatch.setattr(gcp, "request", lambda *a, **k: {"error": {"message": "failed"}})
    result = tools.execute_reviewed_plan(state(action(), action()), ("run",))
    assert result["status"] == "failed"
    assert result["remaining_actions"] == 1


def test_service_specific_async_envelope_stops_dependents(monkeypatch):
    monkeypatch.setenv("FIF_ALLOW_WRITES", "true")
    monkeypatch.setattr(gcp, "request", lambda *a, **k: {"name": "operation-123", "status": "RUNNING"})
    result = tools.execute_reviewed_plan(state(action(), action()), ("run",))
    assert result["status"] == "submitted"
    assert result["remaining_actions"] == 1


@pytest.mark.parametrize("path", ["https://evil.example", "//evil.example/v1", "/v2/../v1/x", "/v2/x?token=x", "/v2/%2e%2e/x", "/v2/x#y"])
def test_api_origin_and_path_validation(path):
    with pytest.raises(ValueError):
        gcp.api_url("run", path)


def test_vertex_regional_endpoint():
    assert gcp.api_url("aiplatform", "/v1/projects/p/locations/us-central1/pipelineJobs/j").startswith("https://us-central1-aiplatform.googleapis.com/")


def test_read_post_rejects_mutations(monkeypatch):
    monkeypatch.setattr(gcp, "request", lambda *a, **k: pytest.fail("Unexpected request"))
    result = gcp.inspect_gcp_post("cloudresourcemanager", "/v3/projects/p:setIamPolicy", "{}")
    assert "error" in result


def test_secret_payload_is_excluded():
    assert "error" in gcp.inspect_gcp("secretmanager", "/v1/projects/p/secrets/s/versions/latest:access")


@pytest.mark.parametrize("statement,read_enabled,write_enabled,expected", [
    ("SELECT", False, False, "preview"),
    ("SELECT", True, False, "submitted"),
    ("UPDATE", True, False, "preview"),
    ("UPDATE", False, True, "submitted"),
    ("SCRIPT", True, True, "failed"),
    ("UNKNOWN", True, True, "failed"),
])
def test_sql_gates_and_dry_run_first(monkeypatch, statement, read_enabled, write_enabled, expected):
    monkeypatch.setenv("FIF_EXECUTE_QUERIES", str(read_enabled))
    monkeypatch.setenv("FIF_ALLOW_WRITES", str(write_enabled))
    calls = []
    def request(service, method, path, **kwargs):
        body = kwargs["body"]
        calls.append(body)
        assert body["configuration"]["query"]["maximumBytesBilled"] == "1000"
        if body["configuration"]["dryRun"]:
            return {"statistics": {"query": {"statementType": statement, "totalBytesProcessed": "50"}}}
        return {"jobReference": body["jobReference"], "status": {"state": "RUNNING"}}
    monkeypatch.setattr(gcp, "request", request)
    result = tools.execute_reviewed_plan(state(Action(kind="bigquery_sql", description="SQL", sql="SELECT 1")), ("bigquery",))
    assert result["status"] == expected
    assert calls[0]["configuration"]["dryRun"] is True
    assert len(calls) == (2 if expected == "submitted" else 1)


def test_over_budget_sql_never_executes(monkeypatch):
    monkeypatch.setenv("FIF_EXECUTE_QUERIES", "true")
    calls = []
    def request(*args, **kwargs):
        calls.append(kwargs)
        return {"statistics": {"query": {"statementType": "SELECT", "totalBytesProcessed": "1001"}}}
    monkeypatch.setattr(gcp, "request", request)
    assert "error" in tools._execute_sql("SELECT 1")
    assert len(calls) == 1


def test_generic_sql_cannot_bypass_dry_run(monkeypatch):
    monkeypatch.setenv("FIF_ALLOW_WRITES", "true")
    raw = Action(kind="gcp_api", description="bypass", service="bigquery", method="POST",
                 path="/bigquery/v2/projects/test-project/jobs",
                 body_json=json.dumps({"configuration": {"query": {"query": "SELECT 1"}}}))
    assert tools.execute_reviewed_plan(state(raw), ("bigquery",))["status"] == "blocked"


WORKSPACE = "projects/test-project/locations/us-central1/repositories/repo/workspaces/dev"


def test_dataform_changed_file_is_not_overwritten(monkeypatch):
    monkeypatch.setenv("FIF_ALLOW_WRITES", "true")
    calls = []
    def request(service, method, *args, **kwargs):
        calls.append(method)
        return {"fileContents": base64.b64encode(b"changed").decode()}
    monkeypatch.setattr(gcp, "request", request)
    edit = Action(kind="dataform_write", description="edit", workspace=WORKSPACE,
                  file_path="definitions/orders.sqlx", contents="new", expected_sha256=hashlib.sha256(b"original").hexdigest())
    result = tools.execute_reviewed_plan(state(edit), ("dataform",))
    assert result["status"] == "failed"
    assert calls == ["GET"]


def test_dataform_write_encoding_and_hash(monkeypatch):
    monkeypatch.setenv("FIF_ALLOW_WRITES", "true")
    writes = []
    def request(service, method, path, query=None, body=None):
        if method == "GET":
            return {"fileContents": base64.b64encode(b"original").decode()}
        writes.append(body)
        return {}
    monkeypatch.setattr(gcp, "request", request)
    edit = Action(kind="dataform_write", description="edit", workspace=WORKSPACE,
                  file_path="definitions/orders.sqlx", contents="select 1", expected_sha256=hashlib.sha256(b"original").hexdigest())
    assert tools.execute_reviewed_plan(state(edit), ("dataform",))["status"] == "completed"
    assert base64.b64decode(writes[0]["contents"]) == b"select 1"


def test_compilation_failure_stops_invocation(monkeypatch):
    monkeypatch.setenv("FIF_ALLOW_WRITES", "true")
    calls = []
    def request(*args, **kwargs):
        calls.append(args)
        return {"compilationErrors": [{"message": "Invalid SQL"}]}
    monkeypatch.setattr(gcp, "request", request)
    compile_action = Action(kind="gcp_api", description="compile", service="dataform", method="POST",
                            path="/v1/projects/test-project/locations/us-central1/repositories/repo/compilationResults")
    result = tools.execute_reviewed_plan(state(compile_action, compile_action), ("dataform",))
    assert result["status"] == "failed"
    assert len(calls) == 1
