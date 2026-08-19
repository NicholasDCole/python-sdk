"""Explicit managed OCG research agent tool.

Set ``OCG_INSTANCE_URL`` to your managed OCG endpoint before running.
The credential is the name of a Conductor secret, not a raw API key.
"""

from __future__ import annotations

import os

from conductor.ai.agents import Agent, OcgConfig, ocg_context_search


ocg = OcgConfig(
    url=os.environ["OCG_INSTANCE_URL"],
    credential="OCG_PUBLIC_KEY",
    memory=True,
)

agent = Agent(
    name="incident_agent",
    model="openai/gpt-4o",
    instructions="Use ocg_research only after narrowing the incident question.",
    ocg=ocg,
    tools=[ocg_context_search(ocg)],
)
