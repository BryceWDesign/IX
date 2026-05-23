# IX Handbook

## Purpose

IX is an experimental evidence-bound agent contract language.

It is designed around a simple idea:

> Agent behavior should be readable before execution and reviewable after execution.

A normal software system often hides behavior inside general-purpose code. IX instead gives you a small language for describing agent behavior in a way that can be checked, run, traced, and reviewed.

IX is not trying to be Python. It is not trying to be a full no-code platform. It is a constrained language for agent behavior contracts.

## Mental model

Think of IX as four layers:

1. **Contract** — the `.ix` file says what behavior is allowed or expected.
2. **Runtime** — IX executes that behavior.
3. **Trace** — IX records what happened.
4. **Evidence** — IX exports reviewable artifacts.

The `.ix` file is not just a diagram. It is executable.

## Who IX is for

IX is meant for several audiences:

### Non-programmer reviewer

A program manager, policy reviewer, legal reviewer, technical evaluator, or operations lead should be able to read an IX file and understand the intended behavior.

They may not write production software, but they can review:

```
require human_approval reason "Reviewer must approve downstream use"
```

That line is intentionally plain.

### Developer

A developer can use IX to define narrow agent behaviors, test them, trace them, and later connect them to larger systems.

### Governance or assurance reviewer

A reviewer can inspect traces, policies, handoffs, tool results, and evidence bundles.

IX does not claim to solve governance by itself. It creates structured artifacts that make review easier.

## What an IX file looks like

A small top-level script:

```
trace "hello example started"
let name = "IX"
reply "Hello from {name}"
assert name == "IX"
```

An agent:

```
agent Greeter {
    on start {
        trace "greeter started"
        reply "Hello. I am ready."
        assert true
    }
}
```

A multi-agent workflow:

```
agent Coordinator {
    on start {
        send Reviewer.review as verdict with item = "request"
        reply "Final verdict: {verdict}"
    }
}

agent Reviewer {
    on review {
        reply "approved: {item}"
    }
}
```

A governed tool call:

```
allow tool.upper reason "Safe deterministic built-in tool"
call tool.upper as shouted with text = "hello"
reply shouted
```

A branch:

```
if score >= 80 {
    reply "approved"
} else {
    reply "human review required"
}
```

## Core commands

### `ix version`

Prints the IX package version.

```
ix version
```

### `ix about`

Prints a short description of the current IX runtime.

```
ix about
```

### `ix check`

Parses and validates an IX file.

```
ix check examples/hello.ix
```

Use this before running unknown or newly edited IX files.

### `ix run`

Runs an IX file.

```
ix run examples/hello.ix
```

Run an agent event:

```
ix run examples/multi_agent_review.ix --agent Coordinator
```

Run a specific event:

```
ix run examples/multi_agent_review.ix --agent Reviewer --event review --input item=request
```

### `ix trace`

Runs an IX file and prints JSON trace output.

```
ix trace examples/hello.ix
```

Trace with input:

```
ix trace examples/branching_review.ix --input score=70
```

### `ix test`

Runs an IX file and reports assertion count.

```
ix test examples/assurance_ready.ix --input score=91
```

This is not a replacement for Python unit tests. It checks IX assertions inside IX behavior files.

### `ix format`

Formats IX source.

```
ix format examples/hello.ix
```

Check formatting:

```
ix format examples/hello.ix --check
```

Write formatting changes:

```
ix format examples/hello.ix --write
```

### `ix orchestrate`

Runs a multi-agent workflow and summarizes handoffs.

```
ix orchestrate examples/multi_agent_review.ix --agent Coordinator
```

Full JSON output:

```
ix orchestrate examples/multi_agent_review.ix --agent Coordinator --json
```

### `ix evidence`

Runs an IX file and writes a reviewable evidence bundle.

```
ix evidence examples/multi_agent_review.ix --agent Coordinator --out .tmp/demo-evidence
```

### `ix assure`

Runs static assurance checks, and optionally runtime checks.

```
ix assure examples/assurance_ready.ix --execute --input score=91
```

JSON report:

```
ix assure examples/assurance_ready.ix --execute --input score=91 --json
```

## Inputs

Use `--input name=value`.

Examples:

```
ix run examples/branching_review.ix --input score=91
ix run examples/branching_review.ix --input score=70
ix trace examples/branching_review.ix --input score=91
```

Boolean inputs:

```
ix trace file.ix --input ready=true
ix trace file.ix --input ready=false
```

String inputs:

```
ix run file.ix --input item=request
```

Quoted strings are also accepted:

```
ix run file.ix --input 'item="agent behavior contract"'
```

## Writing useful IX files

A useful IX file should usually contain:

- a clear trace marker,
- explicit assertions,
- explicit human approval requirements for downstream use,
- explicit allow policies before tool calls,
- simple branches instead of hidden logic,
- clear agent/event names.

A stronger IX file:

```
trace "review workflow started"

if score >= 80 {
    reply "approved"
} else {
    reply "human review required"
}

assert score >= 0
require human_approval reason "Reviewer must approve before operational use"
```

A weak IX file:

```
reply "approved"
```

The weak file runs, but it does not explain much. It has no trace marker, no assertion, and no human review marker.

## Tool calls

IX currently includes deterministic built-in tools only:

- `tool.echo`
- `tool.upper`
- `tool.lower`
- `tool.length`
- `tool.sha256`

Tool calls are denied by default.

This fails:

```
call tool.upper as shouted with text = "hello"
reply shouted
```

This passes:

```
allow tool.upper reason "Safe deterministic built-in tool"
call tool.upper as shouted with text = "hello"
reply shouted
```

Wildcard policies are supported:

```
allow tool.* reason "Allow deterministic built-in tools for this example"
```

Deny overrides allow:

```
allow tool.*
deny tool.upper reason "Uppercase transform disabled in this scenario"
call tool.upper as shouted with text = "hello"
```

That fails closed.

## Agent handoffs

Agents can send scoped work to other agent events:

```
agent Coordinator {
    on start {
        send Reviewer.review as verdict with item = "request"
        reply "Final verdict: {verdict}"
    }
}

agent Reviewer {
    on review {
        reply "approved: {item}"
    }
}
```

The handoff is recorded in:

- `handoffs`,
- `trace`,
- evidence bundle handoff artifacts.

IX also limits recursive handoff depth to prevent unbounded loops.

## Branching

IX supports `if` and `else`:

```
if score >= 80 {
    reply "approved"
} else {
    reply "human review required"
}
```

Branch execution is recorded in:

- `branches`,
- `trace`,
- evidence bundles.

## Assertions

Assertions help make behavior testable:

```
assert score >= 0
assert verdict == "approved: request"
```

If an assertion fails, execution fails.

## Human approval markers

Human approval requirements are explicit review markers:

```
require human_approval reason "Reviewer must approve before operational use"
```

This does not magically route approval to a real human. It records the requirement in the execution result, trace, evidence bundle, and assurance output.

## Evidence bundles

Evidence bundles are meant for review.

They include:

- manifest,
- summary,
- trace,
- policies,
- tool results,
- handoffs,
- branches,
- approval requirements,
- outputs,
- replies,
- assurance claim notes,
- limitations.

They do not certify anything.

## Assurance reports

`ix assure` checks for bounded evidence-readiness.

It can flag:

- invalid IX structure,
- missing executable paths,
- unknown tools,
- tool calls without explicit allow policies,
- missing handoff targets,
- missing assertions,
- missing explicit trace statements,
- missing human approval markers when automation features are used,
- optional runtime execution failure.

A pass means the file passed the current IX assurance checks. It does not mean the file is safe for production or compliant with any external standard.

## Recommended review workflow

For a new `.ix` file:

```
ix check path/to/file.ix
ix format path/to/file.ix --check
ix trace path/to/file.ix
ix assure path/to/file.ix --execute
ix evidence path/to/file.ix --out .tmp/evidence-review
```

For an agent:

```
ix check path/to/file.ix
ix trace path/to/file.ix --agent AgentName
ix assure path/to/file.ix --agent AgentName --execute
ix evidence path/to/file.ix --agent AgentName --out .tmp/evidence-review
```

## Honest limitations

IX is experimental.

Current IX does not include:

- LLM model calls,
- autonomous browsing,
- email sending,
- external network tools,
- file mutation tools,
- deployment tools,
- real-world actuation,
- access control integration,
- identity management,
- cryptographic signing,
- sandbox isolation,
- certification or compliance guarantees.

IX is currently a local, deterministic runtime proving the language, trace, policy, handoff, and evidence concepts.

## Good public positioning

Accurate:

> IX is an experimental evidence-bound agent contract language and runtime for human-readable, traceable agent behavior.

Accurate:

> IX can check, run, trace, orchestrate, and export evidence for local deterministic `.ix` scripts.

Not accurate:

> IX is DoD-compliant.

Not accurate:

> IX certifies agent safety.

Not accurate:

> IX lets non-programmers safely deploy autonomous agents.

Not accurate:

> IX is production-ready.

## Design doctrine

IX should follow these rules:

1. Fail closed when uncertain.
2. Tool use must be explicit.
3. Human review markers must be visible.
4. Runtime behavior must be traceable.
5. Evidence must be reviewable.
6. Capabilities must not be overstated.
7. The language should stay readable.
8. The runtime should stay deterministic unless future external tools are explicitly governed.
