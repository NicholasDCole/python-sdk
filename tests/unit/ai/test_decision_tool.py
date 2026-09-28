import runpy
from pathlib import Path

import pytest

from conductor.ai.agents import Agent, Strategy, ToolDef
from conductor.ai.agents.config_serializer import AgentConfigSerializer


def test_decision_tool_serializes_as_router_selector():
    selector = ToolDef(
        name="ready",
        tool_type="decision",
        config={
            "model": "jev-1.13",
            "provider": "typesafe",
            "questions": {"ready": {"type": "boolean", "instructions": "Ready?"}},
        },
    )
    agent = Agent(
        name="router",
        strategy=Strategy.ROUTER,
        router=selector,
        agents=[Agent(name="yes", model="configured/chat")],
    )

    assert AgentConfigSerializer().serialize(agent)["router"] == {
        "name": "ready",
        "kind": "decision",
        "model": "jev-1.13",
        "provider": "typesafe",
        "questions": {"ready": {"type": "boolean", "instructions": "Ready?"}},
    }


@pytest.mark.parametrize(
    ("config", "message"),
    [
        ({"questions": {"route": {"type": "choice"}}}, "requires 'model'"),
        ({"model": "jev-1.13"}, "requires 'questions'"),
    ],
)
def test_decision_router_requires_model_and_questions(config, message):
    agent = Agent(
        name="router",
        strategy=Strategy.ROUTER,
        router=ToolDef(name="selector", tool_type="decision", config=config),
        agents=[Agent(name="child", model="configured/chat")],
    )
    with pytest.raises(ValueError, match=message):
        AgentConfigSerializer().serialize(agent)


def test_non_decision_tool_cannot_be_a_router():
    agent = Agent(
        name="router",
        strategy=Strategy.ROUTER,
        router=ToolDef(name="http", tool_type="http"),
        agents=[Agent(name="child", model="configured/chat")],
    )
    with pytest.raises(ValueError, match="Only a decision ToolDef"):
        AgentConfigSerializer().serialize(agent)


def test_decision_router_example_uses_tool_only_as_selector(monkeypatch):
    examples = Path(__file__).resolve().parents[3] / "examples" / "agents"
    monkeypatch.syspath_prepend(str(examples))
    monkeypatch.setenv("CONDUCTOR_AGENT_LLM_MODEL", "configured/chat")

    router = runpy.run_path(str(examples / "decision_router.py"))["support_router"]()
    config = AgentConfigSerializer().serialize(router)

    assert isinstance(router.router, ToolDef)
    assert router.router.tool_type == "decision"
    assert config["router"]["kind"] == "decision"
    assert set(config["router"]["questions"]["agent"]["choices"]) == {
        child["name"] for child in config["agents"]
    }
    assert all(child["model"] == "configured/chat" for child in config["agents"])


def test_decision_tool_example_serializes_as_server_side_tool(monkeypatch):
    examples = Path(__file__).resolve().parents[3] / "examples" / "agents"
    monkeypatch.setenv("CONDUCTOR_AGENT_LLM_MODEL", "configured/chat")
    monkeypatch.delenv("CONDUCTOR_DECISION_PROVIDER", raising=False)
    agent = runpy.run_path(str(examples / "decision_tool.py"))["support_agent"]

    config = AgentConfigSerializer().serialize(agent)
    assert config["model"] == "configured/chat"
    assert len(config["tools"]) == 1
    tool = config["tools"][0]
    assert tool["name"] == "classify_request"
    assert tool["toolType"] == "decision"
    assert tool["config"]["model"] == "jev-1.13"
    assert set(tool["config"]["questions"]["department"]["choices"]) == {
        "billing",
        "technical",
    }
