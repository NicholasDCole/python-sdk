"""Explicit Conductor-managed OCG research-agent tool."""

from __future__ import annotations

from conductor.ai.agents.ocg_config import OcgConfig
from conductor.ai.agents.tool import ToolDef


def ocg_context_search(ocg: OcgConfig) -> ToolDef:
    """Create the server-managed OCG research-agent tool.

    The tool accepts a required ``request`` message. Conductor materializes a
    bounded, server-owned research child and keeps raw OCG graph operations
    internal to that child. ``ocg.memory`` is independent: it applies only
    when the same configuration is assigned to the root :class:`Agent`.
    """
    if not isinstance(ocg, OcgConfig):
        raise TypeError("ocg_context_search requires an OcgConfig")

    return ToolDef(
        name="ocg_research",
        description="Research the OCG knowledge graph for the requested information.",
        input_schema={
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "The issue analysis and specific information to research in OCG.",
                }
            },
            "required": ["request"],
        },
        tool_type="ocg_research",
        config={"ocg_url": ocg.url, "credential": ocg.credential},
        credentials=[ocg.credential],
    )
