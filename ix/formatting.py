"""Canonical source formatter for IX programs."""

from __future__ import annotations

from .ast import (
    AgentBlock,
    AssertStatement,
    LetStatement,
    OnBlock,
    PolicyStatement,
    PrintStatement,
    Program,
    RecallStatement,
    RememberStatement,
    ReplyStatement,
    RequireApprovalStatement,
    Statement,
    ToolCallStatement,
    TraceStatement,
)
from .errors import IXError


class IXFormatError(IXError):
    """Raised when an IX program cannot be formatted."""


class IXFormatter:
    """Render IX AST nodes into stable, human-readable IX source."""

    def __init__(self, *, indent: str = "    ") -> None:
        self.indent = indent

    def format_program(self, program: Program) -> str:
        """Return a normalized source representation for an IX program."""

        lines: list[str] = []
        for index, statement in enumerate(program.statements):
            if index > 0 and isinstance(statement, AgentBlock):
                lines.append("")
            lines.extend(self._format_statement(statement, depth=0))
        return "\n".join(lines).rstrip() + "\n"

    def _format_statement(self, statement: Statement, *, depth: int) -> list[str]:
        prefix = self.indent * depth

        if isinstance(statement, LetStatement):
            return [f"{prefix}let {statement.name} = {statement.expression}"]

        if isinstance(statement, RememberStatement):
            return [f"{prefix}remember {statement.name} = {statement.expression}"]

        if isinstance(statement, PrintStatement):
            return [f"{prefix}print {statement.expression}"]

        if isinstance(statement, ReplyStatement):
            return [f"{prefix}reply {statement.expression}"]

        if isinstance(statement, RecallStatement):
            return [f"{prefix}recall {statement.name}"]

        if isinstance(statement, AssertStatement):
            return [f"{prefix}assert {statement.expression}"]

        if isinstance(statement, TraceStatement):
            return [f"{prefix}trace {statement.message}"]

        if isinstance(statement, RequireApprovalStatement):
            return [f"{prefix}require human_approval reason {statement.reason}"]

        if isinstance(statement, PolicyStatement):
            line = f"{prefix}{statement.effect} {statement.target}"
            if statement.reason is not None:
                line = f"{line} reason {statement.reason}"
            return [line]

        if isinstance(statement, ToolCallStatement):
            line = f"{prefix}call {statement.tool_name}"
            if statement.output_name is not None:
                line = f"{line} as {statement.output_name}"
            if statement.arguments:
                arguments = ", ".join(
                    f"{argument.name} = {argument.expression}" for argument in statement.arguments
                )
                line = f"{line} with {arguments}"
            return [line]

        if isinstance(statement, OnBlock):
            lines = [f"{prefix}on {statement.event} {{"]
            for child in statement.statements:
                lines.extend(self._format_statement(child, depth=depth + 1))
            lines.append(f"{prefix}}}")
            return lines

        if isinstance(statement, AgentBlock):
            lines = [f"{prefix}agent {statement.name} {{"]
            for child_index, child in enumerate(statement.statements):
                if child_index > 0 and isinstance(child, OnBlock):
                    lines.append("")
                lines.extend(self._format_statement(child, depth=depth + 1))
            lines.append(f"{prefix}}}")
            return lines

        raise IXFormatError(f"Unsupported statement for formatting: {type(statement).__name__}")


def format_ix(program: Program) -> str:
    """Format a parsed IX program using the canonical formatter."""

    return IXFormatter().format_program(program)
