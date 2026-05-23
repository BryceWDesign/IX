"""Shared IX exception types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceSpan:
    """Location metadata for a parsed IX construct."""

    filename: str
    line: int
    column: int = 1

    def label(self) -> str:
        return f"{self.filename}:{self.line}:{self.column}"


class IXError(Exception):
    """Base class for all canonical IX errors."""


class IXSyntaxError(IXError):
    """Raised when IX source cannot be parsed."""

    def __init__(self, message: str, span: SourceSpan | None = None) -> None:
        self.message = message
        self.span = span
        if span is None:
            super().__init__(message)
        else:
            super().__init__(f"{span.label()}: {message}")


class IXValidationError(IXError):
    """Raised when parsed IX source violates semantic validation rules."""
