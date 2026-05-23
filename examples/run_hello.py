"""Run the canonical hello.ix example through the IX CLI."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Execute examples/hello.ix from a source checkout."""

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    from ix.cli import main as ix_main

    return ix_main(["run", str(REPO_ROOT / "examples" / "hello.ix")])


if __name__ == "__main__":
    raise SystemExit(main())
