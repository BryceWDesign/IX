# IX Examples

This directory contains canonical `.ix` examples for the current runtime.

All examples are designed to run with the installed `ix` command.

Install from the repository root first:

```
python -m pip install -e .
```

## `hello.ix`

Smallest useful example.

```
ix check examples/hello.ix
ix run examples/hello.ix
ix trace examples/hello.ix
ix test examples/hello.ix
ix assure examples/hello.ix --execute
```

What it shows:

- trace marker,
- variable assignment,
- reply output,
- assertion.

## `branching_review.ix`

Shows conditional decision behavior.

Run approved path:

```
ix run examples/branching_review.ix --input score=91
```

Run review path:

```
ix run examples/branching_review.ix --input score=70
```

Trace branch selection:

```
ix trace examples/branching_review.ix --input score=70
```

What it shows:

- `if` / `else`,
- input variables,
- branch trace records,
- assertion.

## `governed_tool.ix`

Shows explicit policy-gated tool use.

```
ix check examples/governed_tool.ix
ix run examples/governed_tool.ix
ix trace examples/governed_tool.ix
ix assure examples/governed_tool.ix --execute
```

What it shows:

- explicit allow policy,
- deterministic built-in tool call,
- tool result assignment,
- assertion,
- human approval requirement.

The tool call would fail without:

```
allow tool.upper reason "Safe deterministic built-in tool"
```

## `multi_agent_review.ix`

Shows traceable multi-agent handoff.

```
ix orchestrate examples/multi_agent_review.ix --agent Coordinator
```

Full JSON:

```
ix orchestrate examples/multi_agent_review.ix --agent Coordinator --json
```

Evidence bundle:

```
ix evidence examples/multi_agent_review.ix --agent Coordinator --out .tmp/multi-agent-evidence
```

What it shows:

- agent blocks,
- event handlers,
- `send` handoff,
- handoff output assignment,
- reply aggregation,
- assertion,
- human approval requirement,
- evidence export.

## `assurance_ready.ix`

Shows a small file designed to pass bounded assurance checks.

```bash
ix assure examples/assurance_ready.ix --execute --input score=91
```

JSON report:

```
ix assure examples/assurance_ready.ix --execute --input score=91 --json
```

What it shows:

- trace marker,
- branch,
- assertion,
- human approval marker,
- assurance pass.

## Suggested review sequence

For any new example:

```
ix check examples/name.ix
ix format examples/name.ix --check
ix trace examples/name.ix
ix assure examples/name.ix --execute
```

For agent examples:

```
ix check examples/name.ix
ix orchestrate examples/name.ix --agent AgentName
ix assure examples/name.ix --agent AgentName --execute
ix evidence examples/name.ix --agent AgentName --out .tmp/name-evidence
```

## Example design rules

Examples should be:

- small,
- deterministic,
- readable,
- traceable,
- policy-gated when tools are used,
- explicit about human review when downstream use is implied,
- honest about limitations.

Examples should not claim:

- certification,
- production readiness,
- compliance,
- real-world approval,
- autonomous authority.
