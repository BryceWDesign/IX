# IX Safety Model

IX is experimental. This document explains what safety boundaries exist today and what is intentionally not claimed.

## Core safety doctrine

IX follows these rules:

1. Human-readable behavior first.
2. Fail closed when uncertain.
3. Tool use must be explicit.
4. Runtime behavior must be traced.
5. Evidence artifacts must be reviewable.
6. Human approval requirements must be visible.
7. No certification or compliance claims without external validation.

## What IX is

IX is a local, deterministic agent contract language and runtime.

It can:

- parse `.ix` files,
- validate structure,
- execute simple deterministic statements,
- run agent event blocks,
- evaluate conditionals,
- enforce policy-gated built-in tool calls,
- perform traceable handoffs,
- emit structured traces,
- export evidence bundles,
- run bounded assurance checks.

## What IX is not

IX is not:

- production-ready,
- certified,
- DoD-approved,
- compliance-approved,
- a safety-critical controller,
- an autonomous weapon system,
- a real-world actuation platform,
- a replacement for human review,
- a replacement for legal review,
- a replacement for security review,
- an LLM agent platform by itself.

## Current tool boundary

The current built-in tools are deterministic and side-effect free:

- `tool.echo`
- `tool.upper`
- `tool.lower`
- `tool.length`
- `tool.sha256`

They do not:

- access the network,
- send email,
- mutate files,
- deploy software,
- call external APIs,
- control devices,
- make purchases,
- approve real-world actions.

This is intentional.

## Tool policy model

Tool calls are denied by default.

This fails:

```
call tool.upper as shouted with text = "hello"
```

This passes:

```
allow tool.upper reason "Safe deterministic built-in tool"
call tool.upper as shouted with text = "hello"
```

Deny overrides allow:

```
allow tool.*
deny tool.upper reason "Disabled for this scenario"
call tool.upper as shouted with text = "hello"
```

The runtime fails closed.

## Human approval markers

IX can record that human approval is required:

```
require human_approval reason "Reviewer must approve before operational use"
```

This does not perform real approval routing. It creates a visible artifact in:

- runtime result,
- trace,
- evidence bundle,
- assurance report.

## Handoff safety

IX supports agent-to-agent handoffs:

```
send Reviewer.review as verdict with item = "request"
```

Safety properties:

- target agent/event must exist or execution fails,
- handoffs are recorded,
- handoff depth is bounded,
- handoff output is explicit when assigned with `as`.

Current limitation:

- There is no identity, access-control, or external authorization system attached to handoffs.

## Branch safety

IX records conditional decisions:

```
if score >= 80 {
    reply "approved"
} else {
    reply "human review required"
}
```

Branch evaluation is recorded in:

- `branches`,
- trace events,
- evidence bundles.

Current limitation:

- IX records the branch taken; it does not prove the branch condition is correct for a real-world domain.

## Expression safety

IX uses a narrow expression evaluator. It does not expose Python builtins.

Supported behavior is intentionally limited.

Unsupported expression types fail at runtime.

## Evidence limitations

Evidence bundles document what the IX runtime observed during one execution.

They do not prove:

- legal compliance,
- operational safety,
- external truth,
- model reliability,
- domain correctness,
- system certification,
- organizational approval.

Evidence bundles are review aids.

## Assurance limitations

`ix assure` checks bounded evidence-readiness.

It does not certify a system.

A passing report means:

- the file passed current IX structural checks,
- known tool calls are policy-gated,
- known handoff targets exist,
- assertions and trace markers may be present,
- optional runtime execution passed if requested.

It does not mean:

- the script is safe for deployment,
- the behavior is correct for a real mission,
- the file is compliant with law or policy,
- a human has actually approved it.

## Recommended safe workflow

Before using an IX file in any serious review:

```
ix check file.ix
ix format file.ix --check
ix trace file.ix
ix assure file.ix --execute
ix evidence file.ix --out .tmp/evidence-review
```

For agent files:

```
ix check file.ix
ix trace file.ix --agent AgentName
ix assure file.ix --agent AgentName --execute
ix evidence file.ix --agent AgentName --out .tmp/evidence-review
```

## Future safety requirements before external tools

Before IX adds external tools such as network, email, filesystem mutation, repository mutation, cloud deployment, or real-world actuation, the project should add:

- explicit tool capability metadata,
- deny-by-default external tool policy,
- test coverage for every external capability,
- structured receipts,
- stronger evidence manifests,
- sandboxing,
- allowlisted paths/resources,
- human approval enforcement,
- replayable run bundles,
- tamper-evident hashes or signatures,
- threat model documentation,
- red-team/adversarial scenario tests.

## Public claim boundaries

Safe to say:

> IX is an experimental evidence-bound agent contract language and local runtime.

Safe to say:

> IX can produce structured traces and evidence bundles for local deterministic agent behavior files.

Not safe to say:

> IX is certified.

Not safe to say:

> IX is DoD-compliant.

Not safe to say:

> IX is production-ready.

Not safe to say:

> IX proves an AI system is safe.

Not safe to say:

> IX lets non-programmers safely deploy autonomous agents.

## Summary

IX improves reviewability. It does not remove the need for review.

IX creates evidence. It does not certify the evidence.

IX can enforce local runtime policy. It does not guarantee real-world safety.
