"""BigQuery expensive query optimizer. See usecases.md for the workflow contract."""

from fif_agents.workflow import build_workflow

root_agent = build_workflow("bigquery_query_cost")
