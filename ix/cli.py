"""Canonical IX command-line entry point."""

from __future__ import annotations

import argparse
import ast as py_ast
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .errors import IXError
from .parser import parse_ix
from .runtime import IXRuntime
from .validator import validate_ix
from .version import __version__

_ABOUT_TEXT = (
    "IX is becoming a canonical agent language and runtime platform.\n"
    "This CLI exposes the first executable contract-language commands: check, run, and trace.\n"
    "The current scope is experimental, audit-first, and intentionally conservative."
)


def build_parser() -> argparse.ArgumentParser:
    """Build the IX CLI argument parser."""

    parser = argparse.ArgumentParser(
        prog="ix",
        description="IX command-line interface",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("version", help="Print the IX package version")
    subparsers.add_parser("about", help="Explain the current canonical IX package")

    check_parser = subparsers.add_parser("check", help="Parse and validate an IX file")
    check_parser.add_argument("file", help="Path to the .ix file to check")

    run_parser = subparsers.add_parser("run", help="Run an IX file")
    _add_execution_arguments(run_parser)

    trace_parser = subparsers.add_parser("trace", help="Run an IX file and emit JSON trace output")
    _add_execution_arguments(trace_parser)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the IX command-line interface."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "version":
        print(__version__)
        return 0

    if args.command == "about":
        print(_ABOUT_TEXT)
        return 0

    if args.command == "check":
        return _check_command(args.file)

    if args.command == "run":
        return _run_command(args)

    if args.command == "trace":
        return _trace_command(args)

    parser.print_help(sys.stderr)
    return 1


def _add_execution_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("file", help="Path to the .ix file to execute")
    parser.add_argument("--agent", help="Agent name to execute")
    parser.add_argument("--event", help="Agent event to execute, default: start")
    parser.add_argument(
        "--input",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="Input variable passed into the run. May be used more than once.",
    )


def _check_command(file_path: str) -> int:
    try:
        source_path, program = _load_program(file_path)
        diagnostics = validate_ix(program)
    except (OSError, IXError) as error:
        print(f"IX check failed: {error}", file=sys.stderr)
        return 2

    if diagnostics:
        for diagnostic in diagnostics:
            print(diagnostic.format(), file=sys.stderr)
        return 2

    print(f"OK: {source_path}")
    return 0


def _run_command(args: argparse.Namespace) -> int:
    try:
        _, result = _execute(args)
    except (OSError, IXError, ValueError) as error:
        print(f"IX run failed: {error}", file=sys.stderr)
        return 2

    for output in result.outputs:
        print(output)
    for reply in result.replies:
        print(reply)
    return 0


def _trace_command(args: argparse.Namespace) -> int:
    try:
        _, result = _execute(args)
    except (OSError, IXError, ValueError) as error:
        print(f"IX trace failed: {error}", file=sys.stderr)
        return 2

    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0


def _execute(args: argparse.Namespace):
    _, program = _load_program(args.file)
    inputs = _parse_inputs(args.input)
    result = IXRuntime().run(
        program,
        agent=args.agent,
        event=args.event,
        inputs=inputs,
    )
    return program, result


def _load_program(file_path: str):
    source_path = Path(file_path)
    source = source_path.read_text(encoding="utf-8")
    return source_path, parse_ix(source, filename=str(source_path))


def _parse_inputs(raw_inputs: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}

    for raw_input in raw_inputs:
        if "=" not in raw_input:
            raise ValueError(f"Expected input in NAME=VALUE form: {raw_input!r}")
        name, raw_value = raw_input.split("=", 1)
        name = name.strip()
        if not name:
            raise ValueError("Input name cannot be empty")
        if not name.replace("_", "a").isalnum() or name[0].isdigit():
            raise ValueError(f"Invalid input name: {name!r}")
        parsed[name] = _parse_input_value(raw_value.strip())

    return parsed


def _parse_input_value(raw_value: str) -> Any:
    lowered = raw_value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None

    try:
        return py_ast.literal_eval(raw_value)
    except (SyntaxError, ValueError):
        return raw_value


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
