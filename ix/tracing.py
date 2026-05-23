"""Structured execution tracing for IX runtime runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .errors import SourceSpan


@dataclass(frozen=True)
class TraceEvent:
    """One auditable runtime event emitted by IX."""

    step: int
    kind: str
    message: str
    span: SourceSpan
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of this trace event."""

        return {
            "step": self.step,
            "kind": self.kind,
            "message": self.message,
            "source": {
                "filename": self.span.filename,
                "line": self.span.line,
                "column": self.span.column,
            },
            "data": self.data,
        }
