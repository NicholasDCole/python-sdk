from typing import Any, Dict, Optional

from conductor.client.workflow.task.task import (
    TaskInterface,
    get_task_interface_list_as_workflow_task_list,
)
from conductor.client.workflow.task.task_type import TaskType


class AiDecisionTask(TaskInterface):
    """Describe a model decision and its branches for server-side routing.

    Each choice contains a description and a list of SDK tasks. The server
    constructs the decision and switch and exposes the selected branch result
    through output("result"). Requires server support for this routing contract.
    """

    def __init__(
        self,
        task_ref_name: str,
        model: str,
        state: str,
        instructions: str,
        choices: Dict[str, Any],
        *,
        task_name: Optional[str] = None,
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
                "instructions": instructions,
                "choices": {
                    key: {
                        "description": choice["description"],
                        "tasks": get_task_interface_list_as_workflow_task_list(*choice["tasks"]),
                    }
                    for key, choice in choices.items()
                },
            },
        )
