"""Let the server select and run an inline branch using decision inference.

Requires server-side AI_DECISION support and inference credentials. No worker needed.
The server compiles instructions/choices into inference and a SWITCH.
Run: CONDUCTOR_SERVER_URL=http://localhost:8080/api python -m examples.agentic_workflows.ai_decision_routing
"""

import argparse
import json
import time

from conductor.client.configuration.configuration import Configuration
from conductor.client.orkes_clients import OrkesClients
from conductor.client.workflow.conductor_workflow import ConductorWorkflow
from conductor.client.workflow.task.ai_decision_task import AiDecisionTask
from conductor.client.workflow.task.inline import InlineTask


def create_workflow(executor, model="jev-1.13", provider=None) -> ConductorWorkflow:
    workflow = ConductorWorkflow(executor=executor, name="ai_decision_routing", version=1)
    billing = InlineTask(
        "handle_billing",
        script='({team: "billing", nextAction: "review_invoice", '
        'message: "Check invoice line items and payment records.", request: $.request})',
        bindings={"request": workflow.input("request")},
    )
    technical = InlineTask(
        "handle_technical",
        script='({team: "technical", nextAction: "collect_diagnostics", '
        'message: "Collect error logs and steps to reproduce.", request: $.request})',
        bindings={"request": workflow.input("request")},
    )
    route = AiDecisionTask(
        task_ref_name="route_request",
        model=model,
        provider=provider,
        state=workflow.input("request"),
        instructions="Choose the team best suited to handle this request.",
        choices={
            "billing": {
                "description": "Payments, invoices, refunds, or subscriptions.",
                "tasks": [billing],
            },
            "technical": {
                "description": "Errors, outages, or product troubleshooting.",
                "tasks": [technical],
            },
        },
    )
    workflow.add(route)
    workflow.output_parameters({"result": route.output("result")})
    return workflow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", default="I was charged twice on my latest invoice.")
    parser.add_argument("--model", default="jev-1.13")
    parser.add_argument("--provider")
    args = parser.parse_args()
    clients = OrkesClients(configuration=Configuration())
    workflow = create_workflow(clients.get_workflow_executor(), args.model, args.provider)
    workflow.register(overwrite=True)
    workflow_id = workflow.start_workflow_with_input({"request": args.request})
    print(f"Workflow: {workflow_id}")
    client = clients.get_workflow_client()
    while True:
        result = client.get_workflow(workflow_id=workflow_id, include_tasks=False)
        if result.is_completed():
            break
        time.sleep(1)
    if result.status != "COMPLETED":
        raise SystemExit(f"{result.status}: {result.reason_for_incompletion}")
    print(json.dumps(result.output, indent=2))


if __name__ == "__main__":
    main()
