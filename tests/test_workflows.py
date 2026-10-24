import importlib.util
from pathlib import Path

import pytest
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool

from fif_agents.catalog import CASES
from fif_agents.config import configure
from fif_agents.gcp import SERVICES
from fif_agents.workflow import PlanExecutor, build_workflow, reset_turn


@pytest.fixture(autouse=True)
def environment(monkeypatch):
    monkeypatch.setenv("FIF_AUTH_MODE", "api_key")
    monkeypatch.setenv("GOOGLE_API_KEY", "offline-test-key")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")


def test_fifty_independent_adk_apps_and_valid_tool_declarations():
    assert len(CASES) == len({case.slug for case in CASES}) == 50
    root_dir = Path(__file__).resolve().parents[1]
    assert len(list((root_dir / "agents").glob("*/agent.py"))) == 50
    names = set()
    for case in CASES:
        assert set(case.services) <= SERVICES.keys()
        spec = importlib.util.spec_from_file_location(case.slug, root_dir / "agents" / case.slug / "agent.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        root = module.root_agent
        assert isinstance(root, SequentialAgent)
        assert len(root.sub_agents) == 5
        assert isinstance(root.sub_agents[3], PlanExecutor)
        assert [agent.output_key for agent in root.sub_agents if isinstance(agent, LlmAgent)] == ["evidence", "plan", "review", "report"]
        for agent in root.sub_agents:
            assert agent.parent_agent is root
            assert agent.name not in names
            names.add(agent.name)
            if isinstance(agent, LlmAgent):
                for tool in agent.tools:
                    declaration = FunctionTool(tool)._get_declaration()
                    assert declaration.name == tool.__name__
    assert len(names) == 250


@pytest.mark.parametrize("mode,expected", [("vertex", "TRUE"), ("api_key", "FALSE")])
def test_backend_selection(monkeypatch, mode, expected):
    import os
    monkeypatch.setenv("FIF_AUTH_MODE", mode)
    configure()
    assert os.environ["GOOGLE_GENAI_USE_VERTEXAI"] == expected
    root = build_workflow("bigquery_schema_drift")
    kwargs = root.sub_agents[0].model.client_kwargs
    assert kwargs["vertexai"] is (mode == "vertex")
    if mode == "vertex":
        assert kwargs["project"] == "test-project"
        assert "api_key" not in kwargs
    else:
        assert kwargs["api_key"] == "offline-test-key"
        assert "project" not in kwargs


def test_invalid_backend(monkeypatch):
    monkeypatch.setenv("FIF_AUTH_MODE", "invalid")
    with pytest.raises(ValueError):
        configure()


def test_turn_reset_prevents_stale_plan():
    from types import SimpleNamespace
    context = SimpleNamespace(state={"plan": "old", "review": "approved", "other": "keep"})
    reset_turn(context)
    assert context.state["plan"] == context.state["review"] == ""
    assert context.state["other"] == "keep"
