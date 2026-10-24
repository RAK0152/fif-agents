"""ADC-authenticated REST transport with fixed Google API origins."""

from functools import lru_cache
import json
import os
import re

import google.auth
from google.auth.transport.requests import AuthorizedSession
import requests

from .config import project

# service -> (host, API root, discovery version)
SERVICES = {
    "bigquery": ("bigquery", "/bigquery/v2", "v2"),
    "dataform": ("dataform", "/v1", "v1"),
    "bigqueryreservation": ("bigqueryreservation", "/v1", "v1"),
    "monitoring": ("monitoring", "/v3", "v3"),
    "logging": ("logging", "/v2", "v2"),
    "cloudresourcemanager": ("cloudresourcemanager", "/v3", "v3"),
    "dataflow": ("dataflow", "/v1b3", "v1b3"),
    "pubsub": ("pubsub", "/v1", "v1"),
    "composer": ("composer", "/v1", "v1"),
    "dataproc": ("dataproc", "/v1", "v1"),
    "datastream": ("datastream", "/v1", "v1"),
    "dataplex": ("dataplex", "/v1", "v1"),
    "sqladmin": ("sqladmin", "/sql/v1beta4", "v1beta4"),
    "spanner": ("spanner", "/v1", "v1"),
    "firestore": ("firestore", "/v1", "v1"),
    "storage": ("storage", "/storage/v1", "v1"),
    "run": ("run", "/v2", "v2"),
    "container": ("container", "/v1", "v1"),
    "compute": ("compute", "/compute/v1", "v1"),
    "dns": ("dns", "/dns/v1", "v1"),
    "iam": ("iam", "/v1", "v1"),
    "secretmanager": ("secretmanager", "/v1", "v1"),
    "cloudkms": ("cloudkms", "/v1", "v1"),
    "cloudbuild": ("cloudbuild", "/v1", "v1"),
    "artifactregistry": ("artifactregistry", "/v1", "v1"),
    "cloudscheduler": ("cloudscheduler", "/v1", "v1"),
    "workflows": ("workflows", "/v1", "v1"),
    "workflowexecutions": ("workflowexecutions", "/v1", "v1"),
    "aiplatform": ("aiplatform", "/v1", "v1"),
}


def object_json(value: str) -> dict:
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("Expected a JSON object")
    return parsed


def api_url(service: str, path: str) -> str:
    if service not in SERVICES:
        raise ValueError(f"Unsupported service: {service}")
    if not path.startswith("/") or any(c in path for c in ("?", "#", "%", "\\", "://")):
        raise ValueError("Use an unencoded API-relative path, not a URL; put parameters in query_json")
    if "//" in path or any(segment in {".", ".."} for segment in path.split("/")):
        raise ValueError("Invalid path")
    host, root, _ = SERVICES[service]
    if not path.startswith(root + "/"):
        raise ValueError(f"{service} paths must start with {root}/")
    if service == "aiplatform":
        match = re.search(r"/locations/([a-z0-9-]+)(?:/|$)", path)
        if not match:
            raise ValueError("Vertex AI requests require /locations/REGION/")
        if match[1] != "global":
            host = match[1] + "-aiplatform"
    return f"https://{host}.googleapis.com{path}"


@lru_cache(maxsize=1)
def session() -> AuthorizedSession:
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    return AuthorizedSession(credentials)


def request(service: str, method: str, path: str, query: dict | None = None,
            body: dict | None = None) -> dict:
    response = session().request(method, api_url(service, path), params=query,
                                 json=body, timeout=int(os.getenv("FIF_HTTP_TIMEOUT", "45")),
                                 allow_redirects=False)
    if not 200 <= response.status_code < 300:
        raise RuntimeError(f"GCP {service} HTTP {response.status_code}: {response.text[:2000]}")
    return response.json() if response.content else {"status": "accepted"}


def bounded(data: dict) -> dict:
    text = json.dumps(data, default=str)
    limit = int(os.getenv("FIF_MAX_RESPONSE_CHARS", "40000"))
    if len(text) <= limit:
        return data
    return {"truncated": True, "total_characters": len(text), "preview": text[:limit],
            "nextPageToken": data.get("nextPageToken"),
            "hint": "Narrow filters, fields and page size. Follow nextPageToken when present."}


def runtime_info() -> dict:
    """Return nonsecret runtime settings and supported API roots; no credential values."""
    from .config import enabled
    return {"project": project(), "location": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
            "bigquery_location": os.getenv("FIF_BQ_LOCATION", "US"),
            "writes_enabled": enabled("FIF_ALLOW_WRITES"),
            "query_execution_enabled": enabled("FIF_EXECUTE_QUERIES"),
            "api_roots": {name: item[1] for name, item in SERVICES.items()}}


@lru_cache(maxsize=32)
def discovery(service: str) -> dict:
    host, _, version = SERVICES[service]
    response = requests.get(f"https://{host}.googleapis.com/$discovery/rest",
                            params={"version": version}, timeout=30)
    if response.status_code == 404:
        response = requests.get(f"https://www.googleapis.com/discovery/v1/apis/{service}/{version}/rest",
                                timeout=30)
    response.raise_for_status()
    return response.json()


def describe_gcp_api(service: str, resource: str, method: str) -> dict:
    """Read official API discovery metadata before constructing requests.

    Args:
        service: Supported service, e.g. dataform or compute.
        resource: Dotted resource, e.g. projects.locations.repositories.workspaces.
            Use an empty string to list top-level resources.
        method: Method name, e.g. writeFile or patch; empty lists available methods.
    """
    try:
        document = discovery(service)
        node = document
        for part in resource.split(".") if resource else []:
            node = node["resources"][part]
        if not method:
            return {"resources": list(node.get("resources", {})), "methods": list(node.get("methods", {}))}
        spec = node["methods"][method]
        ref = spec.get("request", {}).get("$ref")
        return bounded({"rootUrl": document.get("rootUrl"), "servicePath": document.get("servicePath"),
                        "method": spec, "request_schema": document.get("schemas", {}).get(ref, {}),
                        "note": "Use full API-relative paths, including the API root from runtime_info."})
    except Exception as exc:
        return {"error": str(exc), "hint": "Do not invent an API method when discovery fails."}


def inspect_gcp(service: str, path: str, query_json: str = "{}") -> dict:
    """GET GCP resource metadata using ADC. Query parameters are a JSON object.

    Example: service=bigquery, path=/bigquery/v2/projects/PROJECT/datasets/DATASET/tables/TABLE.
    Pagination is explicit: follow nextPageToken with pageToken. Secret payload access is excluded.
    """
    try:
        if service == "secretmanager" and path.endswith(":access"):
            raise ValueError("Secret payload access is not supported")
        return bounded(request(service, "GET", path, object_json(query_json)))
    except Exception as exc:
        return {"error": str(exc)}


def describe_gcp_schema(service: str, schema_name: str) -> dict:
    """Resolve a request property's $ref from official discovery, e.g. Run GoogleCloudRunV2Service."""
    try:
        return gcp_schema(service, schema_name)
    except Exception as exc:
        return {"error": str(exc)}


def gcp_schema(service: str, schema_name: str) -> dict:
    return bounded(discovery(service)["schemas"][schema_name])


def inspect_gcp_post(service: str, path: str, body_json: str) -> dict:
    """Read-only POST for Logging entries:list and project/service-account getIamPolicy.

    Logging body example: resourceNames=[projects/PROJECT], filter=..., pageSize=20.
    """
    try:
        allowed = ((service == "logging" and path == "/v2/entries:list") or
                   (service in {"cloudresourcemanager", "iam"} and path.endswith(":getIamPolicy")))
        if not allowed:
            raise ValueError("This POST is not on the read-only allowlist; propose it in an action plan")
        return bounded(request(service, "POST", path, body=object_json(body_json)))
    except Exception as exc:
        return {"error": str(exc)}
