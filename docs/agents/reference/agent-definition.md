# Agent definition fields

`Agent` accepts a name, `provider/model`, instructions, tools, sub-agents, and
runtime policy. Important fields include `strategy`, `max_turns`, `max_tokens`,
`temperature`, `timeout_seconds`, `output_type`, `guardrails`, `termination`,
`handoffs`, `credentials`, `stateful`, `enable_planning`, `callbacks`, and
`fallback`.

## Managed OCG

Configure managed OCG context search directly on the agent; it does not need an
OCG tool declaration. `memory=True` enables long-term-memory recall and capture,
while `context_search=True` enables the server-managed OCG research sub-agent.
They can use the same OCG URL and credential together or independently.

```python
from conductor.ai.agents import Agent, OcgConfig

agent = Agent(
    name="incident_agent",
    model="openai/gpt-4o",
    ocg=OcgConfig(
        url="https://ocg.example",
        credential="OCG_PUBLIC_KEY",
        memory=True,
        context_search=True,
    ),
)
```

`ocg_context_search(ocg)` remains available temporarily for backwards
compatibility, but is deprecated. Use `OcgConfig(context_search=True)` for new
agents.

Names must match `^[a-zA-Z_][a-zA-Z0-9_-]*$`. Empty models represent inherited or
external-agent behavior. The complete constructor and serialization semantics are
maintained in [api-reference.md](../api-reference.md) and
`AgentConfigSerializer`; use those sources when adding a newly supported field.
