"""Decision agent definitions. Inference and credentials stay on Conductor."""

from copy import deepcopy
from typing import Any, Dict, Optional

from conductor.ai.agents.agent import Agent


class DecisionAgent(Agent):
    """Supply questions here or through context.questions at runtime."""

    kind = "decision"

    def __init__(
        self,
        name: str,
        *,
        model: str,
        provider: Optional[str] = None,
        questions: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name=name, model=model, metadata=metadata)
        self.provider = provider
        self.questions = deepcopy(questions)
