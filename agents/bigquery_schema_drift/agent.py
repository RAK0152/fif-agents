"""BigQuery schema drift and SQL repair. See usecases.md for the workflow contract."""

from fif_agents.workflow import build_workflow

root_agent = build_workflow("bigquery_schema_drift")
