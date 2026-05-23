# IX Trace Schema

IX trace output is JSON produced by:

```
ix trace file.ix
```

or embedded inside evidence bundles produced by:

```
ix evidence file.ix --out evidence-dir
```

The trace is meant to show what the IX runtime did during one execution.

## Top-level trace result

`ix trace` emits a JSON object with this general shape:

```
{
  "status": "completed",
  "variables": {},
  "memory": {},
  "outputs": [],
  "replies": [],
  "approvals_required": [],
  "policies": [],
  "tool_results": [],
  "handoffs": [],
  "branches": [],
  "trace": []
}
```

## `status`

Current expected success status:

```
"completed"
```

If execution fails, the CLI returns non-zero and prints the error to stderr instead of producing a completed JSON payload.

## `variables`

Local variables visible at the end of execution.

Example:

```
{
  "name": "IX"
}
```

## `memory`

Runtime memory values recorded through `remember`.

Example:

```
{
  "mission": "traceable behavior"
}
```

## `outputs`

Values emitted through `print`.

```
[
  "Diagnostic output"
]
```

## `replies`

Values emitted through `reply`.

```
[
  "Hello from IX"
]
```

## `approvals_required`

Human approval markers created by:

```
require human_approval reason "Reviewer must approve before use"
```

Example:

```
[
  "Reviewer must approve before use"
]
```

## `policies`

Policies recorded during execution.

Example:

```
[
  {
    "effect": "allow",
    "target": "tool.upper",
    "reason": "Safe deterministic built-in tool"
  }
]
```

## `tool_results`

Tool execution records.

Example:

```
[
  {
    "tool": "tool.upper",
    "output_name": "shouted",
    "result": "HELLO",
    "arguments": {
      "text": "hello"
    },
    "policy": {
      "effect": "allow",
      "target": "tool.upper",
      "reason": "\"Safe deterministic built-in tool\""
    }
  }
]
```

Tool calls are denied unless an explicit allow policy matches.

## `handoffs`

Agent-to-agent handoff records.

Example:

```
[
  {
    "target_agent": "Reviewer",
    "target_event": "review",
    "arguments": {
      "item": "request"
    },
    "output_name": "verdict",
    "output_value": "approved: request",
    "replies": [
      "approved: request"
    ],
    "outputs": []
  }
]
```

## `branches`

Conditional branch records.

Example:

```
[
  {
    "condition": "score >= 80",
    "selected_branch": "then",
    "condition_value": true,
    "statement_count": 1
  }
]
```

## `trace`

A list of ordered trace events.

Each event has this shape:

```
{
  "step": 1,
  "kind": "run.start",
  "message": "IX execution started",
  "source": {
    "filename": "examples/hello.ix",
    "line": 1,
    "column": 1
  },
  "data": {}
}
```

## Trace event fields

### `step`

Sequential event number starting at 1.

### `kind`

Machine-readable event kind.

### `message`

Human-readable event message.

### `source`

Source location for the construct that produced the event.

### `data`

Event-specific payload.

## Current event kinds

### `run.start`

Runtime execution started.

### `run.complete`

Runtime execution completed.

### `let`

A variable was set.

### `memory.remember`

A memory value was stored.

### `memory.recall`

A memory value was recalled.

### `print`

A printed output was emitted.

### `reply`

A reply was emitted.

### `assert`

An assertion was evaluated.

Data includes:

```
{
  "expression": "score >= 0",
  "passed": true
}
```

### `trace`

A domain-specific trace marker from an IX `trace` statement.

### `approval.required`

A human approval requirement was recorded.

### `policy.recorded`

A policy statement was recorded during execution.

### `tool.denied`

A tool call was denied by policy.

This event is emitted before the runtime fails closed.

### `tool.call`

A tool call executed.

Data includes:

```
{
  "tool": "tool.upper",
  "output_name": "shouted",
  "tool_result": "HELLO",
  "arguments": {
    "text": "hello"
  },
  "policy": {
    "effect": "allow",
    "target": "tool.upper",
    "reason": "\"Safe deterministic built-in tool\""
  }
}
```

### `handoff.start`

An agent handoff started.

### `handoff.complete`

An agent handoff completed.

### `branch.evaluate`

A conditional branch was evaluated.

Data includes:

```
{
  "condition": "score >= 80",
  "selected_branch": "then",
  "condition_value": true,
  "statement_count": 1
}
```

## Stability note

This schema is stable enough for local review and tests, but the project is still experimental. Treat this as the current canonical trace schema, not a formal external standard.
