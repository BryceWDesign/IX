# IX Quickstart

IX is an experimental human-readable agent contract language.

The short version:

- You write behavior in `.ix` files.
- IX checks the file.
- IX runs the file.
- IX can produce trace JSON and evidence bundles showing what happened.

IX is not production-certified, not a safety-critical automation system, and not a replacement for human review.

## 1. Requirements

You need:

- Python 3.11 or newer
- A terminal
- This repository downloaded or cloned

Check Python:

```
python --version
```

If your system uses `python3` instead:

```
python3 --version
```

## 2. Install IX locally

From the repository root:

```bash
python -m pip install -e .
```

Then check the installed command:

```
ix version
ix about
```

## 3. Run the first example

Check the file first:

```
ix check examples/hello.ix
```

Expected result:

```
OK: examples/hello.ix
```

Run it:

```
ix run examples/hello.ix
```

Expected output:

```
Hello from IX
```

## 4. See the trace

A trace is structured JSON showing what the IX runtime did.

```
ix trace examples/hello.ix
```

The trace includes events such as:

- `run.start`
- `trace`
- `let`
- `reply`
- `assert`
- `run.complete`

## 5. Run a branching example

This example makes a decision based on an input value.

```
ix run examples/branching_review.ix --input score=91
```

Expected output:

```
approved
```

Try a lower score:

```
ix run examples/branching_review.ix --input score=70
```

Expected output:

```
human review required
```

To see which branch ran:

```
ix trace examples/branching_review.ix --input score=70
```

Look for the `branches` section and the `branch.evaluate` trace event.

## 6. Run a governed tool example

IX built-in tools are deterministic and side-effect free. Tool calls are denied unless an IX file explicitly allows them.

```
ix run examples/governed_tool.ix
```

Expected output:

```
EVIDENCE-BOUND AGENT CONTRACT
```

The example contains this policy:

```
allow tool.upper reason "Safe deterministic built-in tool"
```

Without that allow policy, the tool call fails closed.

## 7. Run a multi-agent example

```
ix orchestrate examples/multi_agent_review.ix --agent Coordinator
```

This runs the `Coordinator.start` event. The Coordinator sends work to `Reviewer.review`, receives a verdict, and records the handoff.

To see full JSON:

```
ix orchestrate examples/multi_agent_review.ix --agent Coordinator --json
```

## 8. Create an evidence bundle

```
ix evidence examples/multi_agent_review.ix --agent Coordinator --out .tmp/demo-evidence
```

This writes review artifacts such as:

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

These files are review artifacts, not certifications.

## 9. Run an assurance report

```
ix assure examples/assurance_ready.ix --execute --input score=91
```

Expected result:

```
ASSURANCE PASS: examples/assurance_ready.ix
```

The assurance command checks for things such as:

- whether the file has executable paths,
- whether tool calls are explicitly allowed,
- whether handoff targets exist,
- whether assertions are present,
- whether explicit trace markers are present,
- whether human approval requirements are declared,
- and optionally whether the selected entry point can execute.

## 10. Format an IX file

Print formatted source:

```
ix format examples/hello.ix
```

Check formatting:

```
ix format examples/hello.ix --check
```

Rewrite a file in place:

```
ix format path/to/file.ix --write
```

## 11. Small IX file you can copy

Create a file named `my_first_agent.ix`:

```
agent Greeter {
    on start {
        trace "greeter started"
        reply "Hello. I am ready."
        assert true
        require human_approval reason "Review before operational use"
    }
}
```

Run it:

```
ix run my_first_agent.ix --agent Greeter
```

Trace it:

```
ix trace my_first_agent.ix --agent Greeter
```

Assess it:

```
ix assure my_first_agent.ix --agent Greeter --execute
```

## 12. What IX can do right now

Current supported capabilities include:

- parse `.ix` files,
- check syntax and validation,
- run top-level scripts,
- run agent event blocks,
- emit replies and printed outputs,
- remember and recall values during execution,
- evaluate simple expressions,
- enforce explicit allow policies for built-in tools,
- deny tool calls by default,
- run deterministic built-in tools,
- send traceable handoffs between agents,
- execute `if` / `else` branches,
- export evidence bundles,
- produce bounded assurance reports.

## 13. What IX does not do yet

IX does not currently provide:

- LLM model calls,
- network access,
- email sending,
- file mutation tools,
- browser automation,
- production deployment,
- real-world actuation,
- certification,
- compliance guarantees,
- autonomous authority.

Those omissions are intentional for the current phase. IX is proving the contract-language, trace, policy, handoff, and evidence model first.
