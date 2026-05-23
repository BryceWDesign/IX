# IX Language Reference

This document describes the canonical IX language surface currently supported by the runtime.

## Comments

Use `#` for comments.

```
# This is a comment
reply "Hello"
```

Comments inside quoted strings are preserved:

```
reply "This # is text, not a comment"
```

## Strings

Strings may use double quotes:

```
reply "Hello"
```

String interpolation uses `{name}`:

```
let name = "IX"
reply "Hello from {name}"
```

## Booleans and null

IX accepts lowercase boolean/null names:

```
assert true
assert false == false
assert null == null
```

## Variables

Use `let` to create a local variable.

```
let name = "IX"
reply "Hello {name}"
```

Variables are available during the current execution path.

## Memory

Use `remember` to store a value in runtime memory.

```
remember mission = "traceable behavior"
```

Use `recall` to pull it into local variables:

```
recall mission
reply "Mission: {mission}"
```

Current memory is local to the runtime execution result.

## Output

Use `print` for printed output:

```
print "Diagnostic output"
```

Use `reply` for agent-style responses:

```
reply "Ready"
```

Both are recorded in the execution result and trace.

## Trace markers

Use `trace` to add domain-specific trace events:

```
trace "review workflow started"
```

Runtime events are always traced, but explicit trace statements make review easier.

## Assertions

Use `assert` to require a condition.

```
assert score >= 0
assert verdict == "approved"
```

Failed assertions stop execution.

## Human approval requirement

Use `require human_approval` to record a review requirement.

```
require human_approval reason "Reviewer must approve before operational use"
```

The reason is recorded in:

- runtime result,
- trace,
- evidence bundle,
- assurance report.

## Policies

Policies control tool access.

Allow one tool:

```
allow tool.upper reason "Safe deterministic built-in tool"
```

Allow a namespace:

```
allow tool.* reason "Allow deterministic built-in tools"
```

Deny one tool:

```
deny tool.upper reason "Uppercase disabled"
```

Deny overrides allow when both match.

## Tool calls

Syntax:

```
call tool.name as output_name with argument = value
```

Example:

```
allow tool.upper reason "Safe deterministic built-in tool"
call tool.upper as shouted with text = "hello"
reply shouted
```

Without an allow policy, tool calls fail closed.

### Built-in tools

Current built-in tools:

| Tool | Purpose | Example argument |
|---|---|---|
| `tool.echo` | Return message/text/value | `message = "hello"` |
| `tool.upper` | Uppercase text | `text = "hello"` |
| `tool.lower` | Lowercase text | `text = "HELLO"` |
| `tool.length` | Return text length | `text = "abcd"` |
| `tool.sha256` | Return SHA-256 hash of text | `text = "hello"` |

## Agents

Agents group event handlers.

```
agent Greeter {
    on start {
        reply "Ready"
    }
}
```

Run the default `start` event:

```
ix run file.ix --agent Greeter
```

Run a named event:

```
ix run file.ix --agent Greeter --event user_message --input input_text=hello
```

## Events

Events are declared inside agents.

```
agent Router {
    on start {
        reply "Ready"
    }

    on user_message {
        reply "You said: {input_text}"
    }
}
```

Top-level `on` blocks are invalid.

## Handoffs

Use `send` to call another agent event.

```
send Reviewer.review as verdict with item = "request"
```

Full example:

```
agent Coordinator {
    on start {
        send Reviewer.review as verdict with item = "request"
        reply "Final: {verdict}"
    }
}

agent Reviewer {
    on review {
        reply "approved: {item}"
    }
}
```

Handoffs are recorded in runtime output, trace output, and evidence bundles.

## Branching

Use `if` / `else`:

```
if score >= 80 {
    reply "approved"
} else {
    reply "human review required"
}
```

The selected branch is recorded.

An `else` block is optional:

```
if ready == true {
    reply "ready"
}
```

## Expressions

IX currently uses a narrow safe expression evaluator.

Supported expression categories include:

- string literals,
- number literals,
- booleans,
- null,
- variables,
- arithmetic operators,
- comparison operators,
- boolean `and`,
- boolean `or`,
- boolean `not`.

Examples:

```
assert score >= 80
assert name == "IX"
assert ready == true
assert score >= 0 and score <= 100
```

Unsupported expression forms fail at runtime.

## File structure

A file can contain top-level statements:

```
trace "started"
reply "Hello"
```

Or agents:

```
agent Name {
    on start {
        reply "Hello"
    }
}
```

A file may contain multiple agents.

## Formatting

Use:

```
ix format file.ix
```

The formatter normalizes indentation and spacing around assignments.

## Command reference

```
ix version
ix about
ix check file.ix
ix run file.ix
ix trace file.ix
ix test file.ix
ix format file.ix
ix orchestrate file.ix --agent AgentName
ix evidence file.ix --out evidence-dir
ix assure file.ix --execute
```

## Reserved direction

The current language intentionally avoids:

- arbitrary Python execution,
- ungoverned network access,
- ungoverned filesystem mutation,
- ungoverned email sending,
- hidden autonomous actions.

Future capability should be added through explicit governed tools, trace events, tests, and evidence artifacts.
