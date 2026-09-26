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

## Decision agents

Use `DecisionAgent(name, model="jev-1.13", questions=questions)` as the
`router` of an `Agent(strategy="router", ...)`. A Decision configuration is a
selector marker; it cannot be compiled, deployed, or run as a standalone agent.
Pass `provider="typesafe"` (or another configured provider) to override the
server's default decision provider. Arbitrary agent metadata may be supplied with
`metadata={...}`.
Questions are dictionaries with `instructions` and a `type`:
`choice` uses a `choices` map, `score` uses an ordered `scale`, and `boolean`
returns a probability. Decision routers require exactly one fixed `choice`
question whose keys match the executable child-agent names.

[Example](../../../examples/agents/decision_agent.py)

The parent router needs no chat model or Python worker. The selected child is a
normal executable agent and may use its own chat model and tools. Routing runs
one child and preserves its result. For structured decision inference without a
child agent, use an `AiDecisionTask` in a workflow or a decision tool.
