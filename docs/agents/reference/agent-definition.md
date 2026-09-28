# Agent definition fields

`Agent` accepts a name, `provider/model`, instructions, tools, sub-agents, and
runtime policy. Important fields include `strategy`, `max_turns`, `max_tokens`,
`temperature`, `timeout_seconds`, `output_type`, `guardrails`, `termination`,
`handoffs`, `credentials`, `stateful`, `enable_planning`, `callbacks`, and
`fallback`.

Names must match `^[a-zA-Z_][a-zA-Z0-9_-]*$`. Empty models represent inherited or
external-agent behavior. The complete constructor and serialization semantics are
maintained in [api-reference.md](../api-reference.md) and
`AgentConfigSerializer`; use those sources when adding a newly supported field.

## Decision routers

Create a `ToolDef(tool_type="decision", config={...})` and use it as the
`router` of an `Agent(strategy="router", ...)`. The same decision tool primitive
can instead be included in a normal agent's `tools` list. It is never compiled,
deployed, or run as a standalone agent, and it needs no Python worker.
Set `config["provider"]` to override the server's default decision provider.
Questions are dictionaries with `instructions` and a `type`:
`choice` uses a `choices` map, `score` uses an ordered `scale`, and `boolean`
returns a probability. Decision routers require exactly one fixed `choice`
question whose keys match the executable child-agent names.

[Router example](../../../examples/agents/decision_router.py) ·
[Tool example](../../../examples/agents/decision_tool.py)

The parent router needs no chat model or Python worker. The selected child is a
normal executable agent and may use its own chat model and tools. Routing runs
one child and preserves its result. For structured decision inference without a
child agent, use a `SwitchTask` with `evaluator_type="decision"` in a workflow or
a decision tool.
