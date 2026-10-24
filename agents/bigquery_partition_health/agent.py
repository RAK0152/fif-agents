"""BigQuery partition and retention auditor. See usecases.md for the workflow contract."""

from fif_agents.workflow import build_workflow

root_agent = build_workflow("bigquery_partition_health")
