"""Cloud Composer DAG incident investigator. See usecases.md for the workflow contract."""

from fif_agents.workflow import build_workflow

root_agent = build_workflow("composer_dag_failures")
