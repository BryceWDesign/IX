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
class IfStatement(Statement):
    condition: str
    then_statements: tuple[Statement, ...] = field(default_factory=tuple)
    else_statements: tuple[Statement, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class OnBlock(Statement):
    event: str
    statements: tuple[Statement, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AgentBlock(Statement):
    name: str
    statements: tuple[Statement, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CognitionContractStatement(Statement):
    """Base class for declarative cognition-contract statements."""


@dataclass(frozen=True)
class AttemptBlock(CognitionContractStatement):
    """A named governed cognition attempt contract."""

    name: str
    statements: tuple[Statement, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PurposeStatement(CognitionContractStatement):
    """The declared reason a cognition attempt exists."""

    text: str


@dataclass(frozen=True)
class NonGoalStatement(CognitionContractStatement):
    """A declared boundary that a cognition attempt must not cross."""

    text: str


@dataclass(frozen=True)
class ClaimBoundaryStatement(CognitionContractStatement):
    """A statement limiting what may be claimed from a cognition attempt."""

    text: str


@dataclass(frozen=True)
class ObligationBlock(CognitionContractStatement):
    """A required property that a downstream cognition system must satisfy."""

    identifier: str
    statements: tuple[Statement, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EvidenceRequirementStatement(CognitionContractStatement):
    """An evidence artifact or record required for an obligation to count."""

    artifact: str


@dataclass(frozen=True)
class FalsifyIfStatement(CognitionContractStatement):
    """A condition that blocks or falsifies a claim if triggered."""

    condition: str


@dataclass(frozen=True)
class HandoffContractStatement(CognitionContractStatement):
    """A structured downstream handoff target for a governed contract."""

    target: str
    schema_name: str | None = None
