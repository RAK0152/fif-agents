"""Compute Engine managed instance group healer. See usecases.md for the workflow contract."""

from fif_agents.workflow import build_workflow

root_agent = build_workflow("compute_mig_health")
