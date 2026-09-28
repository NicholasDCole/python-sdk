import runpy
from pathlib import Path

from conductor.ai.agents import AgentDef, DecisionAgent
from conductor.ai.agents.config_serializer import AgentConfigSerializer

QUESTIONS = {"ready": {"type": "boolean", "instructions": "Ready?"}}


def test_agent_def_and_convenience_class_serialize_identically():
    questions = QUESTIONS
    definition = AgentDef(name="ready", kind="decision", model="jev-1.13", questions=questions)
    expected = {
        "name": "ready",
        "kind": "decision",
        "model": "jev-1.13",
        "questions": {"ready": {"type": "boolean", "instructions": "Ready?"}},
    }
    assert AgentConfigSerializer().serialize(definition) == expected
    assert (
        AgentConfigSerializer().serialize(
            DecisionAgent("ready", model="jev-1.13", questions=questions)
        )
        == expected
    )


def test_decision_agent_serializes_provider_and_metadata():
    expected = {
        "name": "ready",
        "kind": "decision",
        "model": "jev-1.13",
        "provider": "typesafe",
        "questions": QUESTIONS,
        "metadata": {"owner": "support"},
    }
    serializer = AgentConfigSerializer()
    assert (
        serializer.serialize(
            DecisionAgent(
                "ready",
                model="jev-1.13",
                provider="typesafe",
                questions=QUESTIONS,
                metadata={"owner": "support"},
            )
        )
        == expected
    )
    assert (
        serializer.serialize(
            AgentDef(
                name="ready",
                kind="decision",
                model="jev-1.13",
                provider="typesafe",
                questions=QUESTIONS,
                metadata={"owner": "support"},
            )
        )
        == expected
    )


def test_decision_router_example_uses_decision_only_as_selector(monkeypatch):
    examples = Path(__file__).resolve().parents[3] / "examples" / "agents"
    monkeypatch.syspath_prepend(str(examples))
    monkeypatch.setenv("CONDUCTOR_AGENT_LLM_MODEL", "configured/chat")
    serializer = AgentConfigSerializer()

    simple = runpy.run_path(str(examples / "decision_agent.py"))["support_agent"]()
    config = serializer.serialize(simple)
    assert config["router"]["kind"] == "decision"
    assert set(config["router"]["questions"]["agent"]["choices"]) == {
        child["name"] for child in config["agents"]
    }
    assert all(child.get("kind") != "decision" for child in config["agents"])
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
