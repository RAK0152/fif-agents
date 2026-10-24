"""Cloud Load Balancing error investigator. See usecases.md for the workflow contract."""

from fif_agents.workflow import build_workflow

root_agent = build_workflow("load_balancer_errors")
