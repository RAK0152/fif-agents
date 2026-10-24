"""Google Cloud Workflows execution debugger. See usecases.md for the workflow contract."""

from fif_agents.workflow import build_workflow

root_agent = build_workflow("workflows_failures")
