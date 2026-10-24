"""Cloud Monitoring noisy alert tuner. See usecases.md for the workflow contract."""

from fif_agents.workflow import build_workflow

root_agent = build_workflow("monitoring_alerts")
