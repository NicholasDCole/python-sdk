"""Route to one of two chat agents with a DecisionAgent selector.

Deployment compiles the router into one decision-backed SWITCH. DecisionAgent is
only the selector and is not deployed as a standalone agent. Pass --run for inference.
"""

import argparse
import json
import os

from conductor.ai.agents import Agent, AgentRuntime, DecisionAgent, Strategy
from conductor.client.configuration.configuration import Configuration

PROMPT = "The customer reports a duplicate charge on the latest invoice."
CHAT_MODEL = os.getenv("CONDUCTOR_AGENT_LLM_MODEL", "openai/gpt-4o-mini")


def support_agent():
    billing = Agent(
        name="billing",
        model=CHAT_MODEL,
        instructions="Help the customer with billing and invoice questions.",
    )
    technical = Agent(
        name="technical",
        model=CHAT_MODEL,
        instructions="Help the customer troubleshoot product issues.",
    )
    return Agent(
        name="decision_support_router",
        strategy=Strategy.ROUTER,
        router=DecisionAgent(
            name="support_selector",
            model="jev-1.13",
            questions={
                "agent": {
                    "type": "choice",
                    "instructions": "Choose the right support team.",
                    "choices": {
                        "billing": "Payments and invoices",
                        "technical": "Product errors and troubleshooting",
                    },
                }
            },
        ),
        agents=[billing, technical],
        max_turns=1,
        synthesize=False,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    config = Configuration(
        server_api_url=os.environ.get("CONDUCTOR_SERVER_URL", "http://localhost:8080/api")
    )
    with AgentRuntime(config) as runtime:
        agent = support_agent()
        if not args.run:
            print(json.dumps(runtime.plan(agent, PROMPT), indent=2))
            return

        runtime.deploy(agent)
        handle = runtime.start(agent, PROMPT)
        print("Execution:", handle.execution_id)
        result = handle.join(timeout=120)
        if not result.is_success:
            raise RuntimeError(f"{result.status}: {result.error}")
        print(json.dumps(result.output, indent=2))


if __name__ == "__main__":
    main()
