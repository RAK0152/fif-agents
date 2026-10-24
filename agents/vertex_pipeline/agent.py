"""Vertex AI pipeline failure investigator. See usecases.md for the workflow contract."""

from fif_agents.workflow import build_workflow

root_agent = build_workflow("vertex_pipeline")
