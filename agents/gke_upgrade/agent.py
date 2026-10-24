"""GKE upgrade readiness planner. See usecases.md for the workflow contract."""

from fif_agents.workflow import build_workflow

root_agent = build_workflow("gke_upgrade")
