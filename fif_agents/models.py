"""Structured contracts passed between the specialist agents."""

from typing import Literal
from pydantic import BaseModel, Field


class Action(BaseModel):
    kind: Literal["gcp_api", "bigquery_sql", "dataform_write"]
    description: str
    service: str = ""
    method: Literal["GET", "POST", "PATCH", "PUT", "DELETE"] = "GET"
    path: str = ""
    query_json: str = "{}"
    body_json: str = "{}"
    sql: str = ""
    workspace: str = ""
    file_path: str = ""
    contents: str = ""
    expected_sha256: str = ""


class Plan(BaseModel):
    summary: str
    missing_inputs: list[str] = Field(default_factory=list)
    actions: list[Action] = Field(default_factory=list)
    validation_steps: list[str] = Field(default_factory=list)
    rollback: str


class Review(BaseModel):
    approved: bool
    rationale: str
    risks: list[str] = Field(default_factory=list)
