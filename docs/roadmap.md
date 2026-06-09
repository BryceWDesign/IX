# IX Language Roadmap

This roadmap tracks the current shipped state of IX and the next upgrade path. It is intentionally conservative: IX is an evidence-bound agent contract language and deterministic local runtime, not an AGI system, production deployment authority, or uncontrolled autonomous agent framework.

## Shipped baseline

The canonical implementation lives in the `ix/` package. Current shipped capabilities include:

- canonical parser and AST for `.ix` programs,
- deterministic local runtime execution,
- command-line entry point through `ix`,
- `run`, `check`, `format`, `test`, `assure`, and `evidence` CLI flows,
- local variables and memory through `set`, `remember`, and `get`,
- conditionals with deterministic expression evaluation,
- bounded multi-agent event handlers,
- bounded handoffs through `send Agent.event`,
- deny-by-default tool policy with explicit `allow` and `deny` declarations,
- deterministic built-in tools such as `echo`, `upper`, `lower`, `length`, and `sha256`,
- human-approval markers through `require human_approval`,
- assertion handling,
- structured runtime traces,
- assurance reports,
- evidence bundle generation,
- canonical examples and regression tests.

## Current guardrails

IX should remain narrow enough to audit. The current runtime deliberately avoids hidden side effects and does not provide uncontrolled network access, uncontrolled file mutation, autonomous shell execution, unrestricted LLM calls, production authority, or self-certification.

These guardrails are part of the value of IX. Future expansion should preserve them unless a specific capability is added with explicit policy gating, trace events, evidence output, tests, and documentation.

## Near-term cleanup

The next cleanup work should reduce ambiguity before larger language evolution:

- keep shipped documentation aligned with actual runtime behavior,
- clarify the developer validation path for editable installs and test runs,
- quarantine or modernize legacy examples that predate the canonical runtime,
- clearly distinguish the canonical `ix/` package from older prototype directories,
- keep README changes until the end of major feature work so public claims do not outrun implementation.

## Cognition-contract upgrade path

The next major language direction is profile-based cognition-contract support. The locked framing is:

> IX writes the governed developmental contract for AGI-candidate attempts.

This does not mean IX becomes AGI or creates AGI. It means IX gains the ability to declare, validate, assure, and export contracts that define the purpose, boundaries, obligations, evidence requirements, falsification gates, and handoff expectations for a downstream cognition system such as IX-CognitionKernel.

The initial cognition-contract language concepts should include:

- `attempt`,
- `purpose`,
- `non_goal`,
- `claim_boundary`,
- `obligation`,
- `evidence_required`,
- `falsify_if`,
- profile-strengthened `require human_approval`,
- a structured Kernel handoff contract.

These concepts must be additive and must not break existing `.ix` files.

## Cognition profile obligations

A future cognition profile should be able to require stable obligation families such as:

- purpose discipline,
- claim-boundary discipline,
- human authority,
- prediction before trial or action,
- measured outcome capture,
- prediction-versus-outcome delta comparison,
- evidence-bound memory update,
- future-reasoning change after measured correction,
- cross-domain transfer probe,
- novelty or generality pressure,
- long-horizon planning trace,
- uncertainty and assumption exposure,
- contradiction handling,
- shortcut or reward-hacking detection,
- safe refusal path,
- self-improvement airlock,
- no self-certification,
- falsification ledger,
- independent replay or review readiness,
- Kernel handoff package.

A listed obligation is not complete because it appears in documentation. It is complete only when the parser, AST, validator, assurance profile, evidence export, tests, and examples agree.

## Evidence and assurance milestones

Future milestones should add evidence and assurance in this order:

1. profile registry with backward-compatible `experimental-local` behavior,
2. cognition profile checks,
3. canonical obligation taxonomy,
4. missing-obligation failures,
5. claim-boundary validation,
6. falsification-gate validation,
7. cognition contract evidence artifacts,
8. Kernel handoff package export,
9. satisfaction and failure report schema,
10. positive and negative cognition-contract examples.

## Long-range possibilities

These are possible future directions, not current claims:

- typed agent and event schemas,
- VS Code syntax support,
- web-based local playground,
- OpenTelemetry trace export,
- signed evidence bundles,
- differential trace auditing,
- policy conflict detection,
- cross-compilation to JSON or workflow DSLs,
- governed external adapters for files, HTTP, databases, subprocesses, and LLM calls.

Any external adapter must remain deny-by-default and must include explicit policy, trace, evidence, and tests before it is treated as supported.

## Vision

IX should make governed AI behavior readable before execution and reviewable after execution. Its highest-value path is to become a profile-capable contract language for agent workflows, evidence-bound automation, and governed cognition-candidate attempts while preserving its deterministic, local, auditable core.
