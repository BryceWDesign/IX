# Developer Validation Guide

This guide documents the validation path for local IX development. It exists to keep the repository reproducible before larger language changes are added.

The canonical package is `ix/`. Local validation should install the package in editable mode before running tests or CLI smoke checks. A raw test run from an uninstalled checkout may fail to import `ix` depending on the caller's environment and Python path.

## Supported Python versions

The GitHub workflow currently validates Python 3.11 and Python 3.12.

Use Python 3.11 or newer for local checks.

## Fresh checkout setup

From the repository root:

    python -m pip install --upgrade pip
    python -m pip install -e .

Optional virtual environment setup on Windows PowerShell:

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    python -m pip install -e .

Optional virtual environment setup on macOS or Linux:

    python -m venv .venv
    . .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -e .

## Unit test validation

Run the package-level test suite from the repository root:

    python -m pytest -q

The GitHub workflow also runs the unittest discovery path:

    python -m unittest discover -s tests -p "test_*.py" -v

Both commands should pass before a language, runtime, assurance, evidence, or CLI change is considered ready.

## CLI smoke validation

After editable install, the `ix` command should be available from the active environment.

Basic CLI checks:

    ix version
    ix about

Validate and format-check all canonical examples:

    ix check examples/hello.ix
    ix format examples/hello.ix --check
    ix check examples/branching_review.ix
    ix format examples/branching_review.ix --check
    ix check examples/governed_tool.ix
    ix format examples/governed_tool.ix --check
    ix check examples/multi_agent_review.ix
    ix format examples/multi_agent_review.ix --check
    ix check examples/assurance_ready.ix
    ix format examples/assurance_ready.ix --check

Run representative examples:

    ix run examples/hello.ix
    ix trace examples/hello.ix
    ix test examples/hello.ix
    ix assure examples/hello.ix --execute

    ix run examples/branching_review.ix --input score=70
    ix trace examples/branching_review.ix --input score=91
    ix test examples/branching_review.ix --input score=91
    ix assure examples/branching_review.ix --execute --input score=91

    ix run examples/governed_tool.ix
    ix trace examples/governed_tool.ix
    ix assure examples/governed_tool.ix --execute

    ix orchestrate examples/multi_agent_review.ix --agent Coordinator
    ix orchestrate examples/multi_agent_review.ix --agent Coordinator --json
    ix assure examples/multi_agent_review.ix --agent Coordinator --execute

    ix assure examples/assurance_ready.ix --execute --input score=91
    ix trace examples/assurance_ready.ix --input score=70

Evidence bundle smoke check:

    ix evidence examples/multi_agent_review.ix --agent Coordinator --out .tmp/ix-evidence-smoke

The generated `.tmp/ix-evidence-smoke` directory is local output and should not be committed.

## Legacy agent example checks

The `agent/genesis1.ix` and `agent/genesis2.ix` files are demonstration-only contracts. They should continue to parse, format-check, and run without unsupported legacy syntax.

Manual checks:

    ix check agent/genesis1.ix
    ix format agent/genesis1.ix --check
    ix run agent/genesis1.ix

    ix check agent/genesis2.ix
    ix format agent/genesis2.ix --check
    ix run agent/genesis2.ix

These examples must not imply autonomous evolution, autonomous learning authority, or AGI-candidate status.

## Formatting and linting note

The project metadata contains Ruff configuration, but the current package dependencies do not install Ruff. Do not claim Ruff validation unless Ruff has been installed in the active environment and the command has actually been run.

If Ruff is available, use:

    python -m ruff check ix tests

Future commits may add explicit development dependency installation if linting becomes part of the required local validation path.

## Pre-delivery rule for language changes

Before delivering a language feature, verify the relevant surfaces together:

- parser behavior,
- AST representation,
- formatter behavior,
- semantic validation,
- runtime compatibility when applicable,
- assurance behavior,
- evidence output when applicable,
- CLI behavior,
- positive tests,
- negative tests,
- regression coverage for existing examples.

A cognition-contract feature is not complete because syntax parses. It is complete only when the repository can prove how the feature is represented, validated, reported, and tested.
