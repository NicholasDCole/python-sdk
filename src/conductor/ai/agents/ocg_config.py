# Copyright (c) 2025 Agentspan
# Licensed under the MIT License. See LICENSE file in the project root for details.

"""Declarative Open Context Graph configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional


RecallPolicy = Literal["validate", "trust_and_terminate"]


@dataclass(frozen=True)
class OcgConfig:
    """Configure Conductor-managed OCG integration for an agent.

    ``credential`` is the name of a Conductor secret. Raw API keys are not
    accepted or stored by this configuration. ``memory`` enables the
    server-managed long-term-memory recall and capture lifecycle.
    ``context_search`` enables a server-managed OCG research sub-agent. Both
    capabilities can be enabled together.
    """

    url: str
    credential: str = "OCG_PUBLIC_KEY"
    memory: bool = False
    context_search: bool = False
    user: Optional[str] = None
    recall_policy: Optional[RecallPolicy] = None
    recall_instructions: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.url, str):
            raise ValueError("OcgConfig url must be a non-empty string")
        normalized_url = self.url.strip().rstrip("/")
        if not normalized_url:
            raise ValueError("OcgConfig url must be non-empty")

        if not isinstance(self.credential, str):
            raise ValueError("OcgConfig credential must be a non-empty secret name")
        normalized_credential = self.credential.strip()
        if not normalized_credential:
            raise ValueError("OcgConfig credential must be a non-empty secret name")

        if not isinstance(self.memory, bool):
            raise ValueError("OcgConfig memory must be a boolean")

        if not isinstance(self.context_search, bool):
            raise ValueError("OcgConfig context_search must be a boolean")

        if self.recall_policy is not None and self.recall_policy not in (
            "validate",
            "trust_and_terminate",
        ):
            raise ValueError("OcgConfig recall_policy must be 'validate' or 'trust_and_terminate'")

        normalized_instructions = None
        if self.recall_instructions is not None:
            if not isinstance(self.recall_instructions, str):
                raise ValueError("OcgConfig recall_instructions must be a non-empty string")
            normalized_instructions = self.recall_instructions.strip()
            if not normalized_instructions:
                raise ValueError("OcgConfig recall_instructions must be a non-empty string")

        if self.recall_policy is not None and normalized_instructions is not None:
            raise ValueError("OcgConfig accepts only one of recall_policy or recall_instructions")

        if not self.memory and (
            self.user is not None
            or self.recall_policy is not None
            or normalized_instructions is not None
        ):
            raise ValueError("OcgConfig recall options require memory=True")

        if self.memory and self.recall_policy is None and normalized_instructions is None:
            object.__setattr__(self, "recall_policy", "validate")

        object.__setattr__(self, "url", normalized_url)
        object.__setattr__(self, "credential", normalized_credential)
        object.__setattr__(self, "recall_instructions", normalized_instructions)
