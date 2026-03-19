"""Canonical IX command-line entry point.

This CLI intentionally starts small. In the current migration phase it gives the
repository one stable, testable entry point while legacy prototypes continue to
coexist. Runtime execution, formatting, checking, and tracing commands will be
wired in as later commits land.
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from .version import __version__

_ABOUT_TEXT = (
    "IX is becoming a canonical agent language and runtime platform.\n"
    "This initial CLI commit establishes one stable package boundary so the repo\n"
    "can evolve from scattered prototypes into a single coherent system."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ix",
        description="IX command-line interface",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("version", help="Print the IX package version")
    subparsers.add_parser("about", help="Explain the current canonical IX package")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "version":
        print(__version__)
        return 0

    if args.command == "about":
        print(_ABOUT_TEXT)
        return 0

    parser.print_help(sys.stderr)
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
