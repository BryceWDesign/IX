# IX Cognition Contract Upgrade Doctrine

## Purpose

This document records the baseline audit and governing doctrine for evolving IX from an evidence-bound agent contract language into a profile-capable language that can also write governed developmental contracts for AGI-candidate attempts.

The upgrade objective is narrow and explicit:

> IX writes the governed developmental contract for AGI-candidate attempts.

IX is not being converted into an AGI system. IX is not being converted into an autonomous agent runtime. IX is not being granted model authority, external side effects, or self-approval power. The upgrade adds a contract layer that can declare purpose, boundaries, obligations, evidence requirements, falsification gates, and handoff expectations for cognition systems such as IX-CognitionKernel.

## Current baseline

The canonical implementation is the `ix/` package. It currently provides the language parser, AST, validator, formatter, runtime, tool policy model, tracing model, assurance checks, evidence bundle export, and CLI.

The repository also contains older or adjacent directories such as `core/`, `engine/`, `src/`, and `interpreter/`. Those directories must not be treated as the canonical runtime for this upgrade unless a future commit explicitly audits, updates, or quarantines them. The cognition-contract work must build on the canonical `ix/` package first.

The current shipped language can already describe and execute bounded local behavior, including traces, replies, conditionals, local memory, deterministic tool calls, agent event blocks, bounded handoffs, assertions, and human-approval markers. Evidence bundles can already export review artifacts for runs.

This baseline matters because the upgrade must preserve IX's strongest properties:

- human-readable behavior before execution,
- reviewable evidence after execution,
- deterministic local runtime behavior,
- deny-by-default tool policy,
- explicit human-approval markers,
- bounded multi-agent handoffs,
- structured traces,
- bounded assurance checks,
- no hidden network access,
- no uncontrolled file mutation,
- no autonomous authority.

## Non-goals

The cognition-contract upgrade must not introduce any of the following:

- a claim that IX is AGI,
- a claim that IX creates AGI,
- a claim that IX guarantees AGI emergence,
- autonomous web access,
- uncontrolled LLM calls,
- uncontrolled shell execution,
- production deployment authority,
- cryptographic claims without implemented signing,
- formal certification claims,
- self-certification by a model or runtime,
- donor-code merges from related repositories,
- decorative syntax that has no parser, AST, validator, assurance, evidence, and test support.

These exclusions are not limitations to hide. They are the guardrails that keep IX useful, auditable, and defensible.

## Upgrade principle

The upgrade must be profile-based. IX Core remains the general governed agent contract language. Cognition-contract capability is added through explicit language constructs, validation rules, assurance profiles, evidence artifacts, and handoff schemas.

The intended stack relationship is:

    IX
    writes the governed developmental contract.

    IX-CognitionKernel
    attempts the cognition loop under that contract.

    IX-IntentRealityLoop
    checks intent against measured reality and outcome deltas.

    IX-BlackFox
    governs execution, policy, review, CI evidence, sandboxing, receipts, and human approval.

    Human reviewers
    decide what the evidence means.

The upgraded IX language must therefore support contract authorship and evidence expectations, not AGI self-assertion.

## Required cognition-contract concepts

The language evolution should add only concepts that can be parsed, validated, assured, exported, and tested.

The required concept set is:

- `attempt`: a named governed cognition attempt,
- `purpose`: the reason the attempt exists,
- `non_goal`: a declared boundary the attempt must not cross,
- `claim_boundary`: a statement limiting what may be claimed from the run,
- `obligation`: a required property the downstream cognition system must satisfy,
- `evidence_required`: an evidence artifact or record required for an obligation to count,
- `falsify_if`: a condition that blocks or falsifies a claim if triggered,
- `require human_approval`: the existing human authority marker, preserved and strengthened by profile checks,
- `handoff_contract`: a structured export target for downstream systems such as IX-CognitionKernel.

These constructs must remain declarative until the runtime has a legitimate action to perform. IX should not pretend to execute cognition internally when its responsibility is to define, validate, and export the contract.

## Required AGI-candidate obligation families

The cognition profile should be able to require obligations that map known AGI-candidate gaps into testable engineering pressure. The initial obligation families are:

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

The profile must not treat these as slogans. A required obligation must have a stable identifier, validation behavior, evidence expectations, and failure semantics.

## Falsification doctrine

A cognition contract is only serious if it can fail.

The upgrade must make failure visible and claim-blocking. If a contract requires prediction, outcome, delta comparison, memory correction, transfer, human review, or independent replay, then absence of the required evidence must not be recorded as success. It must produce a failed assurance check, a falsification record, or a review-required result depending on the phase and evidence available.

Failure must be treated as useful evidence, not hidden theater.

## Human authority doctrine

No model, contract, runtime, evaluator, or downstream cognition system may approve its own AGI-candidate status.

IX may declare that human review is required. IX may export the evidence expected for review. IX may fail a contract that lacks human authority. IX may produce handoff artifacts for downstream execution. IX must not certify that AGI has been achieved.

## Backward compatibility doctrine

Existing `.ix` files must continue to parse, validate, format, execute, trace, and export evidence unless a future commit explicitly documents a breaking change. The cognition-contract constructs must be additive.

The existing `experimental-local` assurance behavior must remain available. A new cognition-focused profile may be added, but it must not silently change the result of existing examples under the existing profile.

## Evidence doctrine

Every cognition-contract feature must be connected to evidence output. The minimum expected evidence additions are:

- contract metadata,
- attempt purpose,
- non-goals,
- claim boundaries,
- obligations,
- evidence requirements,
- falsification gates,
- human-review requirements,
- handoff target metadata,
- profile-check results.

If a feature cannot be represented in evidence, it should not be added yet.

## Test doctrine

Each implementation commit after this doctrine must be backed by tests appropriate to its behavior. The required test surfaces include:

- parser acceptance tests,
- parser rejection tests,
- AST representation tests,
- formatter tests,
- validator tests,
- assurance-profile tests,
- evidence-bundle tests,
- CLI smoke tests,
- regression tests for existing examples.

A feature is not complete because syntax exists. A feature is complete only when the parser, data model, validator, assurance behavior, evidence export, documentation, and tests agree.

## Delivery doctrine

The upgrade must be delivered incrementally. Each commit should preserve a green repository state to the greatest extent possible. README changes should be deferred until the end so public-facing claims reflect implemented behavior rather than plans.

The intended completion state is a repository where IX can:

1. parse a cognition-attempt contract,
2. represent it in the canonical AST,
3. validate it structurally,
4. run profile-specific assurance checks,
5. export reviewable contract evidence,
6. produce a Kernel handoff package,
7. reject weak or overclaiming AGI-candidate contracts,
8. preserve existing IX behavior,
9. remain locally testable,
10. avoid AGI overclaiming.

## Implementation sequence lock

The implementation sequence should follow this order unless a concrete repo finding forces a safer adjustment:

1. document the doctrine and baseline,
2. refresh stale roadmap language,
3. clean or quarantine legacy examples,
4. document developer validation commands,
5. add cognition-contract AST nodes,
6. add parser support,
7. add formatter support,
8. add semantic validation,
9. add profile registry,
10. preserve the existing local assurance profile,
11. add the cognition profile,
12. add core cognition-profile checks,
13. add canonical obligation taxonomy,
14. add missing-obligation failures,
15. add claim-boundary checks,
16. add falsification-gate checks,
17. extend result metadata,
18. add contract evidence artifacts,
19. add Kernel handoff export,
20. add satisfaction and failure report schemas,
21. add canonical cognition example,
22. add negative examples and failure tests,
23. expand CLI and regression coverage,
24. update public documentation and README last.

This sequence is intentionally conservative. It keeps the base language intact while adding cognition-contract capability only when the supporting validation and evidence surfaces exist.
