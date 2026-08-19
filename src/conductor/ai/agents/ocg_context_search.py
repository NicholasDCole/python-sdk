"""Conductor-managed OCG context-search capability."""

from __future__ import annotations

from conductor.ai.agents.ocg_config import OcgConfig
from conductor.ai.agents.tool import ToolDef


def ocg_context_search(ocg: OcgConfig) -> ToolDef:
    """Expose Conductor-managed OCG context and graph search tools.

    ``ocg.memory`` controls long-term memory only when the same configuration
    is assigned to the root ``Agent``.
    """
    if not isinstance(ocg, OcgConfig):
        raise TypeError("ocg_context_search requires an OcgConfig")

    return ToolDef(
        name="ocg",
        description="Server-managed OCG context and graph search tools.",
        tool_type="ocg",
        config={"ocg_url": ocg.url, "credential": ocg.credential},
        credentials=[ocg.credential],
    )
