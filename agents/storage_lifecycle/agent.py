"""Cloud Storage lifecycle optimizer. See usecases.md for the workflow contract."""

from fif_agents.workflow import build_workflow

root_agent = build_workflow("storage_lifecycle")
