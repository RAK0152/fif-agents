"""Cloud Build failure and trigger repair. See usecases.md for the workflow contract."""

from fif_agents.workflow import build_workflow

root_agent = build_workflow("cloudbuild_failures")
