<p align="center">
  <strong>IX</strong>
</p>

<p align="center">
  <a href="https://github.com/BryceWDesign/IX/actions/workflows/python-tests.yml">
    <img src="https://github.com/BryceWDesign/IX/actions/workflows/python-tests.yml/badge.svg" alt="Python tests">
  </a>
</p>

# IX

**Readable agent behavior. Governed execution. Evidence after every run.**

IX is an experimental evidence-bound agent contract language and local runtime for writing, checking, running, tracing, orchestrating, and reviewing human-readable AI-agent behavior files.

IX uses `.ix` files to describe behavior in a constrained language that is easier to inspect than general-purpose application code.

The core idea:

> Agent behavior should be readable before execution and reviewable after execution.

IX is not production-ready, not certified, not DoD-approved, and not a compliance product. It is a local research prototype for executable, traceable, evidence-producing agent behavior contracts.

## What IX does today

Current IX can:

- parse `.ix` files,
- validate IX syntax and structure,
- run top-level scripts,
- run agent event blocks,
- emit replies and printed outputs,
- evaluate simple expressions,
- execute `if` / `else` branches,
- record branch decisions,
- store and recall local runtime memory,
- enforce deny-by-default built-in tool policies,
- run deterministic built-in tools only when explicitly allowed,
- perform traceable multi-agent handoffs,
- emit structured JSON traces,
- export reviewable evidence bundles,
- run bounded assurance checks,
- run CI smoke tests against the installed CLI and canonical examples.

## What IX does not do today

IX does not currently provide:

- LLM model calls,
- autonomous web browsing,
- external network access,
- email sending,
- file mutation tools,
- deployment tools,
- real-world actuation,
- cryptographic signing,
- sandbox isolation,
- production security controls,
- formal certification,
- legal compliance guarantees,
- autonomous authority.

Those omissions are intentional at this stage. IX proves the language, runtime, trace, policy, handoff, assurance, and evidence model first.

## Why this exists

AI-agent systems are often hard to review because behavior is hidden inside application code, prompts, framework graphs, tool adapters, and runtime side effects.

IX explores a different layer:

> A human-readable contract language for agent behavior, backed by a deterministic runtime and evidence artifacts.

A reviewer should be able to read a file like this:

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

Then run:

```
ix trace examples/branching_review.ix --input score=70
```

And inspect what happened.

## Installation

IX requires Python 3.11 or newer.

From the repository root:

```
python -m pip install -e .
```

Check the installed command:

```
ix version
ix about
```

## Quickstart

Check an IX file:

```
ix check examples/hello.ix
```

Run it:

```
ix run examples/hello.ix
```

Expected output:

```
Hello from IX
```

Trace it:

```
ix trace examples/hello.ix
```

Run assurance checks:

```
ix assure examples/hello.ix --execute
```

## Canonical examples

### Hello example

```
ix check examples/hello.ix
ix run examples/hello.ix
ix trace examples/hello.ix
ix test examples/hello.ix
ix assure examples/hello.ix --execute
```

### Branching review

```
ix run examples/branching_review.ix --input score=91
ix run examples/branching_review.ix --input score=70
ix trace examples/branching_review.ix --input score=70
```

### Governed tool call

```
ix run examples/governed_tool.ix
ix trace examples/governed_tool.ix
ix assure examples/governed_tool.ix --execute
```

Tool calls are denied by default. The example works because it explicitly allows the deterministic built-in tool:

```
allow tool.upper reason "Safe deterministic built-in tool"
call tool.upper as shouted with text = "evidence-bound agent contract"
reply shouted
```

### Multi-agent review

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

### Assurance-ready example

```
ix assure examples/assurance_ready.ix --execute --input score=91
ix assure examples/assurance_ready.ix --execute --input score=91 --json
```

## Command surface

IX currently exposes:

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

## Language overview

### Variables

```
let name = "IX"
reply "Hello from {name}"
```

### Memory

```
remember mission = "traceable behavior"
recall mission
reply "Mission: {mission}"
```

### Assertions

```
assert score >= 0
```

Failed assertions stop execution.

### Trace markers

```
trace "workflow started"
```

Runtime events are always traced, but explicit trace statements make review easier.

### Human approval markers

```
require human_approval reason "Reviewer must approve before operational use"
```

This records a review requirement. It does not perform real external approval routing.

### Branching

```
if score >= 80 {
    reply "approved"
} else {
    reply "human review required"
}
```

Branch decisions are recorded in trace output and evidence bundles.

### Tool policy

Tool calls fail closed unless explicitly allowed.

```
allow tool.upper reason "Safe deterministic built-in tool"
call tool.upper as shouted with text = "hello"
reply shouted
```

Current built-in tools are deterministic and side-effect free:

- `tool.echo`
- `tool.upper`
- `tool.lower`
- `tool.length`
- `tool.sha256`

### Agents

```
agent Greeter {
    on start {
        trace "greeter started"
        reply "Hello. I am ready."
        assert true
    }
}
```

Run it:

```
ix run file.ix --agent Greeter
```

### Multi-agent handoff

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

Handoffs are recorded in runtime results, trace output, and evidence bundles.

## Evidence bundles

Create an evidence bundle:

```
ix evidence examples/multi_agent_review.ix --agent Coordinator --out .tmp/evidence-review
```

IX writes artifacts such as:

```
manifest.json
summary.json
trace.json
policies.json
tool-results.json
handoffs.json
branches.json
approvals-required.json
outputs.txt
replies.txt
assurance-claims.md
limitations.md
```

Evidence bundles are review artifacts, not certifications.

They show what the IX runtime observed during one execution. They do not prove that a script is safe, lawful, compliant, complete, or production-ready.

## Assurance reports

Run static assurance checks:

```
ix assure examples/assurance_ready.ix --input score=91
```

Run static checks plus runtime execution:

```
ix assure examples/assurance_ready.ix --execute --input score=91
```

JSON output:

```
ix assure examples/assurance_ready.ix --execute --input score=91 --json
```

The assurance analyzer can check:

- executable paths,
- validation diagnostics,
- known tool calls,
- explicit allow policies,
- missing handoff targets,
- explicit assertions,
- explicit trace statements,
- human approval markers,
- optional runtime execution success.

A passing assurance report means the file passed the current IX checks. It does not certify safety or compliance.

## Documentation

Start here:

- [Quickstart](docs/QUICKSTART.md)
- [Handbook](docs/HANDBOOK.md)
- [Language Reference](docs/LANGUAGE_REFERENCE.md)
- [Trace Schema](docs/TRACE_SCHEMA.md)
- [Safety Model](docs/SAFETY_MODEL.md)
- [Examples Guide](examples/README.md)

## Recommended review workflow

For a top-level IX script:

```
ix check path/to/file.ix
ix format path/to/file.ix --check
ix trace path/to/file.ix
ix assure path/to/file.ix --execute
ix evidence path/to/file.ix --out .tmp/evidence-review
```

For an agent file:

```
ix check path/to/file.ix
ix format path/to/file.ix --check
ix trace path/to/file.ix --agent AgentName
ix assure path/to/file.ix --agent AgentName --execute
ix evidence path/to/file.ix --agent AgentName --out .tmp/evidence-review
```

## CI

The GitHub Actions workflow installs IX and runs:

- Python unit tests,
- parser/runtime/CLI regression tests,
- canonical example checks,
- formatter checks,
- trace smoke tests,
- orchestration smoke tests,
- evidence bundle smoke tests,
- assurance smoke tests.

The front-page badge reflects the `python-tests.yml` workflow.

## Project status

IX is currently an experimental local prototype.

It is suitable for:

- language/runtime research,
- deterministic local examples,
- trace schema exploration,
- governance-oriented workflow prototyping,
- evidence bundle experimentation,
- human-readable agent behavior contract design.

It is not suitable for:

- production deployment,
- regulated operational use,
- safety-critical control,
- autonomous external actions,
- unreviewed tool execution,
- compliance claims,
- certification claims.

## Public claim boundaries

Accurate:

> IX is an experimental evidence-bound agent contract language and local runtime.

Accurate:

> IX can check, run, trace, orchestrate, and export evidence for deterministic `.ix` files.

Accurate:

> IX explores human-readable, reviewable agent behavior contracts.

Not accurate:

> IX is certified.

Not accurate:

> IX is DoD-compliant.

Not accurate:

> IX proves AI systems are safe.

Not accurate:

> IX lets non-programmers safely deploy autonomous agents.

Not accurate:

> IX is production-ready.

## Design doctrine

IX should remain:

- readable,
- deterministic by default,
- deny-by-default for tools,
- trace-first,
- evidence-producing,
- human-review-friendly,
- honest about limitations.

The long-term direction is an evidence-bound contract layer for AI-agent behavior: a small language where behavior can be read, checked, executed, traced, and reviewed before higher-risk automation is trusted.

## License

See [LICENSE](LICENSE).
