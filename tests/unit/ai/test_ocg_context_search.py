"""Tests for the typed OCG context-search tool constructor."""

import pytest

from conductor.ai.agents import OcgConfig, ocg_context_search


def test_creates_server_managed_ocg_context_search_capability():
    capability = ocg_context_search(
        OcgConfig(
            url=" https://ocg.example.com/ ",
            credential="OCG_SEARCH_KEY",
        )
    )

    assert capability.name == "ocg_research"
    assert capability.description == (
        "Research the OCG knowledge graph for the requested information."
    )
    assert capability.tool_type == "ocg_research"
    assert capability.config == {
        "ocg_url": "https://ocg.example.com",
        "credential": "OCG_SEARCH_KEY",
    }
    assert capability.credentials == ["OCG_SEARCH_KEY"]
    assert capability.input_schema == {
        "type": "object",
        "properties": {
            "request": {
                "type": "string",
                "description": "The issue analysis and specific information to research in OCG.",
            }
        },
        "required": ["request"],
    }


def test_requires_ocg_configuration():
    with pytest.raises(TypeError, match="OcgConfig"):
        ocg_context_search("https://ocg.example.com")  # type: ignore[arg-type]
