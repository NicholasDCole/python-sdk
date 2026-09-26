"""Compatibility import; new code should use DecisionAgent."""

from conductor.ai.agents.decision import DecisionAgent


class JevAgent(DecisionAgent):
    """Deprecated name for DecisionAgent; serializes kind="decision"."""
