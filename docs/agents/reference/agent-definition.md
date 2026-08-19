# Agent definition fields

`Agent` accepts a name, `provider/model`, instructions, tools, sub-agents, and
runtime policy. Important fields include `strategy`, `max_turns`, `max_tokens`,
`temperature`, `timeout_seconds`, `output_type`, `guardrails`, `termination`,
`handoffs`, `credentials`, `stateful`, `enable_planning`, `callbacks`, and
`fallback`.

## Managed OCG

`memory=True` enables long-term-memory recall and capture. To make OCG research
available to an agent, explicitly add `ocg_context_search(ocg)` to its tools.
The resulting `ocg_research` tool is a server-managed research sub-agent, not a
raw graph or MCP tool. This lets application instructions control when research
runs and what request it receives.

```python
from conductor.ai.agents import Agent, OcgConfig, ocg_context_search

ocg = OcgConfig(
    url="https://ocg.example",
    credential="OCG_PUBLIC_KEY",
    memory=True,
)

agent = Agent(
    name="incident_agent",
    model="openai/gpt-4o",
    ocg=ocg,
    tools=[ocg_context_search(ocg)],
)
```

Names must match `^[a-zA-Z_][a-zA-Z0-9_-]*$`. Empty models represent inherited or
external-agent behavior. The complete constructor and serialization semantics are
maintained in [api-reference.md](../api-reference.md) and
`AgentConfigSerializer`; use those sources when adding a newly supported field.
