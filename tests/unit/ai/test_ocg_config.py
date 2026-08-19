"""Tests for declarative OCG configuration."""

import pytest

from conductor.ai.agents import Agent, OcgConfig, ocg_context_search
from conductor.ai.agents.config_serializer import AgentConfigSerializer


def serialize(agent: Agent) -> dict:
    return AgentConfigSerializer().serialize(agent)


def test_ocg_absent_omits_long_term_memory():
    config = serialize(Agent(name="assistant", model="openai/gpt-4o"))

    assert "ocg" not in config
    assert "longTermMemory" not in config


def test_ocg_uses_default_credential_and_generated_agent_identity():
    config = serialize(
        Agent(
            name="assistant",
            model="openai/gpt-4o",
            ocg=OcgConfig(url="https://ocg.example.com", memory=True),
        )
    )

    assert config["longTermMemory"] == {
        "ocgUrl": "https://ocg.example.com",
        "credential": "OCG_PUBLIC_KEY",
        "agent": "conductor-agent:assistant",
        "recallPolicy": "validate",
    }


def test_ocg_serializes_explicit_credential_and_user():
    config = serialize(
        Agent(
            name="assistant",
            model="openai/gpt-4o",
            ocg=OcgConfig(
                url="https://ocg.example.com",
                credential="ASSISTANT_OCG_KEY",
                memory=True,
                user="user:123",
            ),
        )
    )

    assert config["longTermMemory"] == {
        "ocgUrl": "https://ocg.example.com",
        "credential": "ASSISTANT_OCG_KEY",
        "agent": "conductor-agent:assistant",
        "user": "user:123",
        "recallPolicy": "validate",
    }


@pytest.mark.parametrize(
    ("raw_url", "normalized_url"),
    [
        (" https://ocg.example.com/ ", "https://ocg.example.com"),
        ("https://ocg.example.com///", "https://ocg.example.com"),
    ],
)
def test_ocg_normalizes_url(raw_url, normalized_url):
    ocg = OcgConfig(url=raw_url, memory=True)

    assert ocg.url == normalized_url


def test_ocg_serializes_custom_recall_instructions():
    config = serialize(
        Agent(
            name="assistant",
            model="openai/gpt-4o",
            ocg=OcgConfig(
                url="https://ocg.example.com",
                memory=True,
                recall_instructions="Use the recalled answer when it addresses the request.",
            ),
        )
    )

    assert "recallPolicy" not in config["longTermMemory"]
    assert config["longTermMemory"]["recallInstructions"] == (
        "Use the recalled answer when it addresses the request."
    )


@pytest.mark.parametrize("recall_policy", ["", "always", "terminate"])
def test_ocg_rejects_unknown_recall_policy(recall_policy):
    with pytest.raises(ValueError, match="recall_policy"):
        OcgConfig(url="https://ocg.example.com", memory=True, recall_policy=recall_policy)


@pytest.mark.parametrize("url", ["", "   ", "///"])
def test_ocg_rejects_empty_url(url):
    with pytest.raises(ValueError, match="url must be non-empty"):
        OcgConfig(url=url, memory=True)


@pytest.mark.parametrize("credential", ["", "   "])
def test_ocg_rejects_empty_credential(credential):
    with pytest.raises(ValueError, match="credential must be a non-empty secret name"):
        OcgConfig(
            url="https://ocg.example.com",
            credential=credential,
            memory=True,
        )


def test_ocg_does_not_accept_raw_api_key_parameter():
    with pytest.raises(TypeError):
        OcgConfig(url="https://ocg.example.com", memory=True, api_key="raw-secret")


def test_ocg_emits_no_legacy_feedback_worker_or_config():
    config = serialize(
        Agent(
            name="assistant",
            model="openai/gpt-4o",
            ocg=OcgConfig(url="https://ocg.example.com", memory=True),
        )
    )

    assert "feedbackSink" not in config
    assert "feedbackWorker" not in config
    assert "memorySummaryModel" not in config["longTermMemory"]
    assert "tools" not in config


def test_ocg_memory_defaults_to_validate_recall():
    ocg = OcgConfig(url="https://ocg.example.com", memory=True)

    assert ocg.recall_policy == "validate"


def test_memory_disabled_omits_long_term_memory():
    config = serialize(
        Agent(
            name="assistant",
            model="openai/gpt-4o",
            ocg=OcgConfig(url="https://ocg.example.com", memory=False),
        )
    )

    assert "longTermMemory" not in config
    assert "ocg" not in config


def test_explicit_research_without_memory_omits_long_term_memory():
    ocg = OcgConfig(url="https://ocg.example.com")

    config = serialize(
        Agent(
            name="assistant",
            model="openai/gpt-4o",
            ocg=ocg,
            tools=[ocg_context_search(ocg)],
        )
    )

    assert "longTermMemory" not in config
    assert [tool["name"] for tool in config["tools"]] == ["ocg_research"]


def test_memory_and_explicit_research_serialize_independently():
    ocg = OcgConfig(url="https://ocg.example.com", credential="OCG_SEARCH_KEY", memory=True)

    config = serialize(
        Agent(
            name="assistant",
            model="openai/gpt-4o",
            ocg=ocg,
            tools=[ocg_context_search(ocg)],
        )
    )

    assert config["longTermMemory"]["ocgUrl"] == "https://ocg.example.com"
    assert "ocg" not in config
    assert config["tools"] == [
        {
            "name": "ocg_research",
            "description": "Research the OCG knowledge graph for the requested information.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "request": {
                        "type": "string",
                        "description": "The issue analysis and specific information to research in OCG.",
                    }
                },
                "required": ["request"],
            },
            "toolType": "ocg_research",
            "config": {
                "ocg_url": "https://ocg.example.com",
                "credential": "OCG_SEARCH_KEY",
                "credentials": ["OCG_SEARCH_KEY"],
            },
        }
    ]


def test_recall_options_require_memory_to_be_enabled():
    with pytest.raises(ValueError, match="memory=True"):
        OcgConfig(url="https://ocg.example.com", recall_policy="validate")


def test_ocg_rejects_removed_context_search_option():
    with pytest.raises(TypeError, match="context_search"):
        OcgConfig(url="https://ocg.example.com", context_search=True)  # type: ignore[call-arg]


def test_ocg_rejects_both_recall_configurations():
    with pytest.raises(ValueError, match="only one"):
        OcgConfig(
            url="https://ocg.example.com",
            memory=True,
            recall_policy="validate",
            recall_instructions="Use the recalled answer directly.",
        )
