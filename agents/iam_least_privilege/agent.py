"""Project IAM least privilege reviewer. See usecases.md for the workflow contract."""

from fif_agents.workflow import build_workflow

root_agent = build_workflow("iam_least_privilege")
