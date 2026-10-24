"""Run the real ADK event loop with a fake model, without cloud credentials."""

import asyncio
import json

from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import InMemoryRunner
from google.genai import types

from fif_agents.workflow import build_workflow


class FixedModel(BaseLlm):
    model: str = "offline"
    reply: str

    async def generate_content_async(self, llm_request, stream=False):
        yield LlmResponse(content=types.Content(role="model", parts=[types.Part(text=self.reply)]))


def test_real_adk_handoffs_and_repeat_turn(monkeypatch):
    monkeypatch.setenv("FIF_AUTH_MODE", "api_key")
    monkeypatch.setenv("GOOGLE_API_KEY", "offline-test")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    monkeypatch.setenv("FIF_ALLOW_WRITES", "false")
    root = build_workflow("cloudrun_latency")
    plan = {"summary": "Raise minimum instances", "missing_inputs": [], "actions": [
        {"kind": "gcp_api", "description": "Scale", "service": "run", "method": "PATCH",
         "path": "/v2/projects/test-project/locations/us-central1/services/demo",
         "body_json": '{"scaling":{"minInstanceCount":1}}'}],
        "validation_steps": ["Read back service"], "rollback": "Restore previous scaling"}
    replies = ["Observed cold starts.", json.dumps(plan),
               '{"approved":true,"rationale":"Matches request","risks":[]}', "Preview only; no changes applied."]
    for agent, reply in zip([a for a in root.sub_agents if isinstance(a, LlmAgent)], replies):
        agent.model = FixedModel(reply=reply)

    async def run():
        runner = InMemoryRunner(agent=root, app_name="offline_test")
        session = await runner.session_service.create_session(app_name="offline_test", user_id="test")
        for _ in range(2):
            events = [event async for event in runner.run_async(user_id="test", session_id=session.id,
                new_message=types.Content(role="user", parts=[types.Part(text="Investigate demo cold starts")]))]
            current = await runner.session_service.get_session(app_name="offline_test", user_id="test", session_id=session.id)
            assert isinstance(current.state["plan"], dict)
            assert current.state["review"]["approved"] is True
            assert json.loads(current.state["execution"])["status"] == "preview"
            assert current.state["report"] == replies[-1]
            assert {a.name for a in root.sub_agents} <= {event.author for event in events}
        await runner.close()
    asyncio.run(run())
