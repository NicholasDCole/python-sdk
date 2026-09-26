from conductor.client.http.api_client import ApiClient
from conductor.client.workflow.task.ai_decision_task import AiDecisionTask
from conductor.client.workflow.task.inline import InlineTask
from conductor.client.workflow.task.switch_task import SwitchTask
from conductor.client.workflow.task.task_type import TaskType
from examples.agentic_workflows.ai_decision_routing import create_workflow


def test_ai_decision_references_and_serialization():
    choices = {
        "billing": {"description": "Payments", "tasks": [InlineTask("billing", "'billing'")]},
        "technical": {"description": "Errors", "tasks": [InlineTask("technical", "'technical'")]},
    }
    task = AiDecisionTask(
        "decision", "jev-1.13", "${workflow.input.request}", "Choose a team.", choices
    )
    serialized = ApiClient().sanitize_for_serialization(task.to_workflow_task())
    assert task.task_type == TaskType.AI_DECISION
    assert serialized["type"] == "AI_DECISION"
    assert serialized["name"] == "ai_decision"
    assert serialized["taskReferenceName"] == "decision"
    assert serialized["inputParameters"] == {
        "model": "jev-1.13",
        "state": "${workflow.input.request}",
        "instructions": "Choose a team.",
        "choices": {
            key: {
                "description": choice["description"],
                "tasks": [
                    ApiClient().sanitize_for_serialization(choice["tasks"][0].to_workflow_task())
                ],
            }
            for key, choice in choices.items()
        },
    }
    assert task.input("state") == "${decision.input.state}"
    assert task.output() == "${decision.output}"
    assert task.output("answers") == "${decision.output.answers}"
    assert task.output("result") == "${decision.output.result}"
    assert task.output("selectedCase") == "${decision.output.selectedCase}"


def test_custom_name_and_input_reference():
    task = AiDecisionTask(
        "decision", "jev-1.13", "request", "Choose a team.", {}, task_name="choose_team"
    )
    task.input_parameter("state", "${workflow.input.request}")
    definition = task.to_workflow_task()
    assert definition.name == "choose_team"
    assert definition.input_parameters["state"] == "${workflow.input.request}"


def test_routing_example_serializes_one_task_with_branches():
    definition = ApiClient().sanitize_for_serialization(create_workflow(None).to_workflow_def())
    assert len(definition["tasks"]) == 1
    decision = definition["tasks"][0]
    assert decision["type"] == "AI_DECISION"
    assert decision["inputParameters"]["state"] == "${workflow.input.request}"
    assert decision["taskReferenceName"] == "route_request"
    choices = decision["inputParameters"]["choices"]
    assert set(choices) == {"billing", "technical"}
    for team, choice in choices.items():
        assert choice["description"]
        tasks = choice["tasks"]
        assert len(tasks) == 1
        assert tasks[0]["type"] == "INLINE"
        assert tasks[0]["taskReferenceName"] == f"handle_{team}"
        assert tasks[0]["inputParameters"]["request"] == "${workflow.input.request}"
    assert definition["outputParameters"] == {
        "result": "${route_request.output.result}",
    }


def test_nested_branch_serialization_preserves_task_references():
    branch = SwitchTask("nested", "${workflow.input.priority}")
    branch.switch_case(
        "high", [InlineTask("urgent", "$.request", {"request": "${workflow.input.request}"})]
    )
    task = AiDecisionTask(
        "route",
        "jev-1.13",
        "request",
        "Choose a team.",
        {
            "billing": {"description": "Payments", "tasks": [branch]},
            "technical": {
                "description": "Errors",
                "tasks": [InlineTask("technical", "'technical'")],
            },
        },
    )
    serialized = ApiClient().sanitize_for_serialization(task.to_workflow_task())
    nested = serialized["inputParameters"]["choices"]["billing"]["tasks"][0]
    assert nested["type"] == "SWITCH"
    assert nested["inputParameters"]["switchCaseValue"] == "${workflow.input.priority}"
    urgent = nested["decisionCases"]["high"][0]
    assert urgent["taskReferenceName"] == "urgent"
    assert urgent["inputParameters"]["request"] == "${workflow.input.request}"
