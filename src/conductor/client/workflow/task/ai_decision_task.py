from typing import Any, Dict, Optional

from conductor.client.workflow.task.task import TaskInterface
from conductor.client.workflow.task.task_type import TaskType


class AiDecisionTask(TaskInterface):
    """Run one choice decision using server-managed inference credentials.

    The server returns the structured decision and ``selectedCase``. Compose
    this task with :class:`SwitchTask` in the workflow definition to run the
    selected branch.
    """

    def __init__(
        self,
        task_ref_name: str,
        model: str,
        state: str,
        questions: Dict[str, Any],
        task_name: Optional[str] = None,
        *,
        provider: Optional[str] = None,
    ) -> None:
        super().__init__(
            task_reference_name=task_ref_name,
            task_type=TaskType.AI_DECISION,
            task_name=task_name or "ai_decision",
            input_parameters={
                "model": model,
                **({"provider": provider} if provider is not None else {}),
                "state": state,
                "questions": questions,
            },
        )
