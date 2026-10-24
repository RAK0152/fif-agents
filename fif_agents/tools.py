"""BigQuery, Dataform and deterministic reviewed-plan execution."""

import base64
import hashlib
import json
import os
from pathlib import PurePosixPath
import re
import uuid

from . import gcp
from .config import enabled, project
from .models import Action, Plan, Review


def _bq_body(sql: str, dry_run: bool) -> dict:
    if not sql.strip():
        raise ValueError("SQL must not be empty")
    return {"jobReference": {"projectId": project(), "location": os.getenv("FIF_BQ_LOCATION", "US"),
                             "jobId": "fif_" + uuid.uuid4().hex},
            "configuration": {"dryRun": dry_run,
                              "query": {"query": sql, "useLegacySql": False,
                                        "maximumBytesBilled": os.getenv("FIF_BQ_MAX_BYTES", "1000000000")}}}


def bigquery_dry_run(sql: str) -> dict:
    """Validate GoogleSQL and estimate bytes without running it. Never pass SQLX."""
    try:
        body = _bq_body(sql, True)
        result = gcp.request("bigquery", "POST", f"/bigquery/v2/projects/{project()}/jobs", body=body)
        if result.get("status", {}).get("errorResult"):
            return {"error": result["status"]["errorResult"]}
        return {"valid": True, "statistics": result.get("statistics", {}),
                "status": result.get("status", {})}
    except Exception as exc:
        return {"error": str(exc)}


def _execute_sql(sql: str) -> dict:
    checked = bigquery_dry_run(sql)
    if "error" in checked:
        return checked
    query_stats = checked.get("statistics", {}).get("query", {})
    statement = query_stats.get("statementType", "UNKNOWN")
    bytes_processed = int(query_stats.get("totalBytesProcessed", checked.get("statistics", {}).get("totalBytesProcessed", 0)))
    if bytes_processed > int(os.getenv("FIF_BQ_MAX_BYTES", "1000000000")):
        return {"error": "Dry-run scan exceeds FIF_BQ_MAX_BYTES", "dry_run": checked}
    if statement == "SCRIPT" or statement == "UNKNOWN":
        return {"error": "Only a single classified SQL statement can execute; split scripts into reviewed actions", "dry_run": checked}
    allowed = enabled("FIF_EXECUTE_QUERIES") if statement == "SELECT" else enabled("FIF_ALLOW_WRITES")
    if not allowed:
        return {"status": "preview", "sql": sql, "dry_run": checked,
                "required_setting": "FIF_EXECUTE_QUERIES" if statement == "SELECT" else "FIF_ALLOW_WRITES"}
    result = gcp.request("bigquery", "POST", f"/bigquery/v2/projects/{project()}/jobs", body=_bq_body(sql, False))
    if result.get("status", {}).get("errorResult"):
        return {"error": result["status"]["errorResult"], "job": result}
    ref = result.get("jobReference", {})
    return {"status": "submitted", "job": result,
            "verification_path": f"/bigquery/v2/projects/{project()}/jobs/{ref.get('jobId', '')}",
            "results_path": f"/bigquery/v2/projects/{project()}/queries/{ref.get('jobId', '')}",
            "location": ref.get("location", os.getenv("FIF_BQ_LOCATION", "US"))}


def _workspace_path(workspace: str, file_path: str) -> str:
    if not re.fullmatch(r"projects/[^/]+/locations/[^/]+/repositories/[^/]+/workspaces/[^/]+", workspace):
        raise ValueError("Supply a complete Dataform workspace resource name")
    if not file_path or PurePosixPath(file_path).is_absolute() or ".." in PurePosixPath(file_path).parts or "\\" in file_path:
        raise ValueError("File path must be relative to the Dataform workspace")
    return "/v1/" + workspace


def dataform_read_file(workspace: str, file_path: str) -> dict:
    """Read a Dataform workspace file and SHA-256 for an optimistic concurrency check."""
    try:
        path = _workspace_path(workspace, file_path)
        response = gcp.request("dataform", "GET", path + ":readFile", {"path": file_path})
        raw = base64.b64decode(response.get("fileContents", ""), validate=True)
        return gcp.bounded({"file_path": file_path, "contents": raw.decode("utf-8"),
                            "sha256": hashlib.sha256(raw).hexdigest()})
    except Exception as exc:
        return {"error": str(exc)}


def _write_dataform(action: Action) -> dict:
    path = _workspace_path(action.workspace, action.file_path)
    if not re.fullmatch(r"[0-9a-f]{64}|NEW", action.expected_sha256):
        raise ValueError("Use the original file SHA-256, or NEW for an explicitly new file")
    if not enabled("FIF_ALLOW_WRITES"):
        return {"status": "preview", "action": action.model_dump()}
    if action.expected_sha256 == "NEW":
        # Only an actual 404 permits creation; permission/network failures do not.
        try:
            gcp.request("dataform", "GET", path + ":readFile", {"path": action.file_path})
        except RuntimeError as exc:
            if "HTTP 404:" not in str(exc):
                raise
        else:
            raise ValueError("File already exists; read it and supply its hash")
    else:
        original = dataform_read_file(action.workspace, action.file_path)
        if "error" in original or original.get("sha256") != action.expected_sha256:
            raise ValueError("File unavailable or changed since review; read and replan")
    result = gcp.request("dataform", "POST", path + ":writeFile", body={
        "path": action.file_path, "contents": base64.b64encode(action.contents.encode()).decode()})
    return {"status": "written", "result": result,
            "next_step": "Create a workspace compilationResult and inspect compilationErrors before any invocation"}


def _preflight(action: Action, allowed_services: tuple[str, ...]) -> None:
    service = {"bigquery_sql": "bigquery", "dataform_write": "dataform"}.get(action.kind, action.service)
    if service not in allowed_services:
        raise ValueError(f"Service {service} is outside this workflow's scope")
    if action.kind == "gcp_api":
        gcp.api_url(action.service, action.path)
        gcp.object_json(action.query_json)
        gcp.object_json(action.body_json)
        # Dedicated paths carry validation that the generic transport cannot bypass.
        if action.service == "bigquery" and action.method != "GET":
            if "/jobs" in action.path or "/queries" in action.path:
                body = gcp.object_json(action.body_json)
                if "/queries" in action.path or body.get("configuration", {}).get("query"):
                    raise ValueError("Use bigquery_sql for SQL jobs, including dry runs")
        if action.service == "dataform" and action.path.endswith(":writeFile"):
            raise ValueError("Use dataform_write for workspace writes")
        if action.service == "secretmanager" and action.path.endswith(":access"):
            raise ValueError("Secret payload access is not supported")
    elif action.kind == "bigquery_sql":
        if not action.sql.strip():
            raise ValueError("SQL is required")
    else:
        _workspace_path(action.workspace, action.file_path)
        if not re.fullmatch(r"[0-9a-f]{64}|NEW", action.expected_sha256):
            raise ValueError("Dataform writes require original SHA-256 or NEW")


def execute_reviewed_plan(state: dict, allowed_services: tuple[str, ...]) -> dict:
    """Execute exactly the structured plan after review; stop at first error/preview.

    This is called by a deterministic ADK agent, never exposed as a model tool.
    """
    try:
        # ADK structured output is stored as a dict; JSON strings also support
        # restored sessions and direct offline callers.
        raw_plan, raw_review = state.get("plan", ""), state.get("review", "")
        plan = Plan.model_validate_json(raw_plan) if isinstance(raw_plan, str) else Plan.model_validate(raw_plan)
        review = Review.model_validate_json(raw_review) if isinstance(raw_review, str) else Review.model_validate(raw_review)
        if not review.approved or plan.missing_inputs:
            return {"status": "blocked", "review": review.model_dump(), "missing_inputs": plan.missing_inputs}
        if len(plan.actions) > 20:
            raise ValueError("Split plans larger than 20 actions into smaller runs")
        for action in plan.actions:
            _preflight(action, allowed_services)
        results = []
        for action in plan.actions:
            try:
                if action.kind == "bigquery_sql":
                    result = _execute_sql(action.sql)
                elif action.kind == "dataform_write":
                    result = _write_dataform(action)
                elif action.method != "GET" and not enabled("FIF_ALLOW_WRITES"):
                    result = {"status": "preview", "action": action.model_dump()}
                else:
                    result = {"status": "returned", "response": gcp.request(
                        action.service, action.method, action.path,
                        gcp.object_json(action.query_json),
                        gcp.object_json(action.body_json) if action.method != "GET" else None)}
                    payload = result["response"]
                    if payload.get("error") or payload.get("compilationErrors"):
                        result["error"] = payload.get("error", payload.get("compilationErrors"))
                    elif payload.get("name") and "/operations/" in payload["name"] and not payload.get("done"):
                        result["status"] = "pending_operation"
                    elif action.method != "GET" and not (
                        action.service == "dataform" and action.method == "POST"
                        and action.path.endswith("/compilationResults")
                    ):
                        # Compute, Cloud SQL, Dataflow and other APIs have different
                        # operation envelopes. Do not infer completion from HTTP 200.
                        result["status"] = "submitted"
                results.append({"description": action.description, "result": gcp.bounded(result)})
                # A later action must not assume asynchronous work has completed.
                if "error" in result or result.get("status") in {"preview", "submitted", "pending_operation"}:
                    return {"status": result.get("status", "failed") if "error" not in result else "failed",
                            "results": results, "remaining_actions": len(plan.actions) - len(results),
                            "note": "Verify pending work before replanning remaining actions. Preview stops at the first gated action."}
            except Exception as exc:
                results.append({"description": action.description, "error": str(exc)})
                return {"status": "failed", "results": results, "remaining_actions": len(plan.actions) - len(results)}
        return {"status": "completed" if results else "no_actions", "results": results}
    except Exception as exc:
        return {"status": "blocked", "error": str(exc)}
