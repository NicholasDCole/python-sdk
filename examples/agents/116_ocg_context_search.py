"""Managed OCG context search configured directly on an agent.

Set ``OCG_INSTANCE_URL`` to your managed OCG endpoint before running.
The credential is the name of a Conductor secret, not a raw API key.
"""

from __future__ import annotations

import os

from conductor.ai.agents import Agent, OcgConfig

agent = Agent(
    name="incident_agent",
    model="openai/gpt-4o",
    instructions="Research incidents and summarize the relevant evidence.",
    ocg=OcgConfig(
        url=os.environ["OCG_INSTANCE_URL"],
        credential="OCG_PUBLIC_KEY",
        memory=True,
        context_search=True,
    ),
)
