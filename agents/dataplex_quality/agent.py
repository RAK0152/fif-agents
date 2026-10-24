"""Dataplex data quality scan manager. See usecases.md for the workflow contract."""

from fif_agents.workflow import build_workflow

root_agent = build_workflow("dataplex_quality")
