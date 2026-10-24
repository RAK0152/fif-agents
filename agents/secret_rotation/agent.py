"""Secret Manager rotation readiness auditor. See usecases.md for the workflow contract."""

from fif_agents.workflow import build_workflow

root_agent = build_workflow("secret_rotation")
