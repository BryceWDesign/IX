"""Canonical abstract syntax tree nodes for IX."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .errors import SourceSpan


@dataclass(frozen=True)
class Node:
    """Base AST node."""

    span: SourceSpan


@dataclass(frozen=True)
class Statement(Node):
    """Base class for executable IX statements."""


@dataclass(frozen=True)
class Program(Node):
    """A complete IX source file."""

    statements: tuple[Statement, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class LetStatement(Statement):
    name: str
    expression: str


@dataclass(frozen=True)
class PrintStatement(Statement):
    expression: str


@dataclass(frozen=True)
class ReplyStatement(Statement):
    expression: str


@dataclass(frozen=True)
class RememberStatement(Statement):
    name: str
    expression: str


@dataclass(frozen=True)
class RecallStatement(Statement):
    name: str


@dataclass(frozen=True)
class AssertStatement(Statement):
    expression: str


@dataclass(frozen=True)
class TraceStatement(Statement):
    message: str


@dataclass(frozen=True)
class RequireApprovalStatement(Statement):
    reason: str


PolicyEffect = Literal["allow", "deny"]


@dataclass(frozen=True)
class PolicyStatement(Statement):
    effect: PolicyEffect
    target: str
    reason: str | None = None


@dataclass(frozen=True)
class ToolArgument:
    name: str
    expression: str


@dataclass(frozen=True)
class ToolCallStatement(Statement):
    tool_name: str
    output_name: str | None = None
    arguments: tuple[ToolArgument, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SendStatement(Statement):
    target_agent: str
    target_event: str
    output_name: str | None = None
    arguments: tuple[ToolArgument, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class OnBlock(Statement):
    event: str
    statements: tuple[Statement, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AgentBlock(Statement):
    name: str
    statements: tuple[Statement, ...] = field(default_factory=tuple)
