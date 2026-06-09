<p align="center">
  <strong>IX</strong>
</p>

<p align="center">
  <a href="https://github.com/BryceWDesign/IX/actions/workflows/python-tests.yml">
    <img src="https://github.com/BryceWDesign/IX/actions/workflows/python-tests.yml/badge.svg" alt="Python tests">
  </a>
</p>

# IX

**Readable agent behavior. Governed execution. Evidence after every run. Cognition contracts without AGI overclaim.**

IX is an experimental evidence-bound agent contract language and local runtime for writing, checking, running, tracing, orchestrating, assuring, and reviewing human-readable `.ix` behavior files.

The core idea:

> Agent behavior should be readable before execution and reviewable after execution.

The new cognition-contract framing is:

> IX writes the governed developmental contract for AGI-candidate attempts.

That does not mean IX is AGI. It does not mean IX creates AGI. It means IX can now express, validate, assure, and export a governed contract that tells a downstream system such as IX-CognitionKernel what must be attempted, evidenced, falsified, reviewed, and bounded.

IX remains a local, deterministic, audit-first research prototype.

## Current status

IX currently supports two related layers:

1. **IX Core**  
   A deterministic local language/runtime for governed agent behavior, trace output, bounded tools, multi-agent handoffs, and evidence bundles.

2. **IX Cognition Contracts**  
   A declarative profile for writing reviewable IX-CognitionKernel Wave 6 contracts with purpose, non-goals, claim boundaries, required obligations, evidence requirements, falsification gates, human review, Kernel handoff packages, satisfaction report schemas, and failure report schemas.

The cognition-contract layer is declarative metadata. IX does not execute cognition obligations. IX does not certify downstream results. IX does not grant self-approval or AGI-claim authority.

## What IX does today

IX can currently:

- parse `.ix` files,
- validate IX syntax and structure,
- format IX files,
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
- expose assurance profiles,
- parse cognition `attempt` blocks,
- validate cognition-contract structure,
- enforce canonical cognition-obligation coverage,
- enforce AGI-claim restriction and research-candidate boundaries,
- enforce canonical falsification gates,
- export cognition contract evidence artifacts,
- export IX-CognitionKernel handoff packages,
- export satisfaction and failure report schemas,
- preserve plain IX behavior separately from cognition-contract review.

## What IX does not do today

IX does not provide:

- AGI,
- AGI certification,
- AGI-candidate certification,
- autonomous web browsing,
- uncontrolled LLM calls,
- external network access,
- email sending,
- filesystem mutation tools,
- deployment tools,
- real-world actuation,
- cryptographic signing,
- sandbox isolation,
- production security controls,
- formal certification,
- legal compliance guarantees,
- autonomous authority,
- model self-approval,
- downstream cognition execution.

Those omissions are intentional. IX is designed to make contracts, traces, evidence, and review boundaries explicit before higher-risk automation is trusted.

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

Write an evidence bundle:

```
ix evidence examples/hello.ix --out .tmp/hello-evidence
```

## Cognition-contract quickstart

The canonical cognition-contract example is:

```
examples/cognitionkernel_wave6_contract.ix
```

Check and format it:

```
ix check examples/cognitionkernel_wave6_contract.ix
ix format examples/cognitionkernel_wave6_contract.ix --check
```

Run the cognition assurance profile:

```
ix assure examples/cognitionkernel_wave6_contract.ix --profile cognitionkernel-wave6
```

JSON output:

```
ix assure examples/cognitionkernel_wave6_contract.ix --profile cognitionkernel-wave6 --json
```

Trace metadata extraction:

```
ix trace examples/cognitionkernel_wave6_contract.ix
```

Export cognition evidence artifacts:

```
ix evidence examples/cognitionkernel_wave6_contract.ix --out .tmp/cognition-evidence
```

The canonical cognition example does not emit replies, outputs, or approvals during runtime. IX extracts contract metadata only and records that the contract was not executed as cognition.

Expected runtime semantics:

```
metadata_only_not_executed
```

## Assurance profiles

IX currently includes two built-in assurance profiles.

### `experimental-local`

The default local profile for deterministic IX runtime checks. It is intended for ordinary executable IX files.

It checks:

- validation diagnostics,
- executable paths,
- tool policy gates,
- handoff targets,
- condition markers,
- assertions,
- trace statements,
- human approval markers,
- optional runtime execution.

Example:

```
ix assure examples/assurance_ready.ix --profile experimental-local --execute --input score=91
```

### `cognitionkernel-wave6`

A static cognition-contract review profile for governed IX-CognitionKernel Wave 6 attempts.

It checks:

- top-level `attempt` presence,
- purpose declaration,
- non-goal declaration,
- claim-boundary declaration,
- human approval requirement,
- IX-CognitionKernel handoff contract,
- AGI-claim restriction,
- research-candidate boundary,
- absence of prohibited AGI-certification language,
- all canonical cognition obligations,
- canonical obligation identifiers,
- evidence requirements,
- falsification gates,
- canonical falsification gate coverage,
- runtime execution blocked for this profile.

Example:

```
ix assure examples/cognitionkernel_wave6_contract.ix --profile cognitionkernel-wave6
```

This profile is intentionally static. It does not execute cognition. It does not certify AGI. It does not certify downstream success.

## Cognition-contract language

A cognition contract uses an `attempt` block:

```
attempt wave6_measured_cognition {
    purpose "Define a governed IX-CognitionKernel Wave 6 contract for measured reality correction"
    non_goal "Do not claim AGI, certify AGI, or allow system self-approval"
    claim_boundary "Research candidate only, evaluation use only, not deployment"
    require human_approval reason "Human review required before any advancement or public claim"
    handoff_contract IX-CognitionKernel schema ix.cognition.contract.v1

    obligation prediction_before_trial {
        evidence_required prediction_record
        falsify_if prediction_missing
    }
}
```

The cognition-contract constructs are:

- `attempt`
- `purpose`
- `non_goal`
- `claim_boundary`
- `require human_approval`
- `handoff_contract`
- `obligation`
- `evidence_required`
- `falsify_if`

These constructs are declarative. They define a contract and evidence expectations for downstream review.

## Canonical cognition obligations

The `cognitionkernel-wave6` profile requires all canonical obligation families:

1. `purpose_discipline`
2. `claim_boundary_discipline`
3. `human_authority`
4. `prediction_before_trial`
5. `measured_outcome_capture`
6. `reality_delta_comparison`
7. `evidence_bound_memory_update`
8. `future_reasoning_change`
9. `cross_domain_transfer_probe`
10. `novelty_generality_pressure`
11. `long_horizon_planning_trace`
12. `uncertainty_assumption_exposure`
13. `contradiction_handling`
14. `shortcut_reward_hacking_detection`
15. `safe_refusal_path`
16. `self_improvement_airlock`
17. `no_self_certification`
18. `falsification_ledger`
19. `independent_replay_review`
20. `kernel_handoff_package`

A contract that omits required obligations fails the cognition profile.

A contract that uses unknown obligation IDs fails the cognition profile.

A contract that uses arbitrary falsification labels instead of canonical falsification gates fails the cognition profile.

## Negative cognition examples

The repository includes intentional failure examples:

```
examples/cognitionkernel_wave6_missing_obligations.ix
examples/cognitionkernel_wave6_overclaiming.ix
examples/cognitionkernel_wave6_wrong_handoff.ix
examples/cognitionkernel_wave6_noncanonical_falsification.ix
```

These examples should parse and format cleanly, but fail under:

```
ix assure <example-file> --profile cognitionkernel-wave6
```

They prove the profile is not a decorative happy-path check. It rejects incomplete, overclaiming, wrongly handed-off, or noncanonical contracts.

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

Assurance profiles can be selected with:

```
ix assure file.ix --profile experimental-local
ix assure file.ix --profile cognitionkernel-wave6
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

This records a review requirement. It does not perform external approval routing.

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

### Multi-agent review

```
ix orchestrate examples/multi_agent_review.ix --agent Coordinator
ix orchestrate examples/multi_agent_review.ix --agent Coordinator --json
ix evidence examples/multi_agent_review.ix --agent Coordinator --out .tmp/multi-agent-evidence
```

### Assurance-ready example

```
ix assure examples/assurance_ready.ix --execute --input score=91
ix assure examples/assurance_ready.ix --execute --input score=91 --json
```

### IX-CognitionKernel Wave 6 contract

```
ix check examples/cognitionkernel_wave6_contract.ix
ix format examples/cognitionkernel_wave6_contract.ix --check
ix assure examples/cognitionkernel_wave6_contract.ix --profile cognitionkernel-wave6
ix evidence examples/cognitionkernel_wave6_contract.ix --out .tmp/cognition-evidence
```

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

For cognition contracts, IX also writes:

```
contract.json
obligations.json
falsification-gates.json
claim-boundaries.json
kernel-handoff.json
satisfaction-report.json
failure-report.json
```

These cognition artifacts are review artifacts. They record the contract, required obligations, evidence requirements, falsification gates, claim boundaries, and Kernel handoff package.

They do not execute cognition. They do not mark obligations satisfied. They do not decide whether falsification gates were triggered. They do not certify AGI or deployment readiness.

## IX-CognitionKernel handoff package

When a cognition contract declares:

```
handoff_contract IX-CognitionKernel schema ix.cognition.contract.v1
```

IX evidence export includes:

```
kernel-handoff.json
```

The handoff package contains:

- attempt name,
- target,
- schema,
- runtime semantics,
- execution authority set to `none`,
- self-certification blocked,
- human authority requirement,
- purpose,
- non-goals,
- claim boundaries,
- human approval requirements,
- obligations,
- canonical obligation definitions when available,
- evidence requirements,
- falsification gates.

This is a handoff package, not an execution grant.

## Satisfaction and failure reports

Cognition evidence bundles include:

```
satisfaction-report.json
failure-report.json
```

These reports start in:

```
not_evaluated
```

They are schemas for downstream evidence review.

The satisfaction report lists obligations and required evidence, but does not mark them satisfied.

The failure report lists falsification gates and claim-blocking semantics, but does not decide whether the gates were triggered.

Downstream measured evidence and human review are required.

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

For a cognition contract:

```
ix check path/to/file.ix
ix format path/to/file.ix --check
ix assure path/to/file.ix --profile cognitionkernel-wave6
ix trace path/to/file.ix
ix evidence path/to/file.ix --out .tmp/cognition-evidence
```

## Documentation

Start here:

- [Developer Validation Guide](docs/DEVELOPER_VALIDATION.md)
- [Cognition Contract Upgrade Doctrine](docs/COGNITION_CONTRACT_UPGRADE.md)
- [Quickstart](docs/QUICKSTART.md)
- [Handbook](docs/HANDBOOK.md)
- [Language Reference](docs/LANGUAGE_REFERENCE.md)
- [Trace Schema](docs/TRACE_SCHEMA.md)
- [Safety Model](docs/SAFETY_MODEL.md)
- [Examples Guide](examples/README.md)
- [Roadmap](docs/roadmap.md)

## CI

The GitHub Actions workflow installs IX and runs:

- Python unit tests,
- parser/runtime/CLI regression tests,
- canonical example checks,
- formatter checks,
- trace smoke tests,
- orchestration smoke tests,
- evidence bundle smoke tests,
- assurance smoke tests,
- cognition-contract parser, validator, formatter, profile, evidence, CLI, and negative-example tests.

The front-page badge reflects the `python-tests.yml` workflow.

## Project status

IX is currently an experimental local prototype.

It is suitable for:

- language/runtime research,
- deterministic local examples,
- trace schema exploration,
- governance-oriented workflow prototyping,
- evidence bundle experimentation,
- human-readable agent behavior contract design,
- cognition-contract declaration and review,
- IX-CognitionKernel handoff package generation,
- falsification-gate and claim-boundary contract testing.

It is not suitable for:

- production deployment,
- regulated operational use,
- safety-critical control,
- autonomous external actions,
- unreviewed tool execution,
- compliance claims,
- certification claims,
- AGI claims,
- self-approval claims,
- downstream cognition execution.

## Public claim boundaries

Accurate:

> IX is an experimental evidence-bound agent contract language and local runtime.

Accurate:

> IX can check, run, trace, orchestrate, assure, and export evidence for deterministic `.ix` files.

Accurate:

> IX writes the governed developmental contract for AGI-candidate attempts.

Accurate:

> IX can express, validate, assure, and export IX-CognitionKernel Wave 6 cognition contracts with obligations, evidence requirements, falsification gates, claim boundaries, human review, and handoff packages.

Accurate:

> IX cognition contracts are declarative and metadata-only at runtime.

Not accurate:

> IX is AGI.

Not accurate:

> IX creates AGI.

Not accurate:

> IX proves AGI.

Not accurate:

> IX certifies AGI-candidate success.

Not accurate:

> IX executes downstream cognition obligations.

Not accurate:

> IX lets a model approve itself.

Not accurate:

> IX is certified.

Not accurate:

> IX is DoD-compliant.

Not accurate:

> IX proves AI systems are safe.

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
- profile-capable,
- falsification-aware,
- honest about limitations,
- strict about claim boundaries.

The long-term direction is an evidence-bound contract layer for AI-agent behavior and governed cognition-candidate attempts: a small language where behavior, obligations, evidence, falsification gates, and handoffs can be read, checked, traced, exported, and reviewed before higher-risk automation is trusted.

## License

See [LICENSE](LICENSE).
