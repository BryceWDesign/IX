"""Semantic validation for canonical IX programs."""

from __future__ import annotations

from dataclasses import dataclass

from .ast import AgentBlock, IfStatement, LetStatement, OnBlock, Program, RememberStatement, Statement
from .errors import SourceSpan


@dataclass(frozen=True)
class Diagnostic:
    """A validation finding tied to source code."""

    message: str
    span: SourceSpan
    severity: str = "error"

    def format(self) -> str:
        return f"{self.span.label()}: {self.severity}: {self.message}"


class IXValidator:
    """Validate IX ASTs before execution."""

    def validate(self, program: Program) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        self._validate_statements(program.statements, diagnostics, inside_agent=False)
        return diagnostics

    def _validate_statements(
        self,
        statements: tuple[Statement, ...],
        diagnostics: list[Diagnostic],
        *,
        inside_agent: bool,
    ) -> None:
        seen_agents: set[str] = set()
        seen_events: set[str] = set()

        for statement in statements:
            if isinstance(statement, AgentBlock):
                if inside_agent:
                    diagnostics.append(
                        Diagnostic("Nested agent blocks are not supported", statement.span)
                    )
                if statement.name in seen_agents:
                    diagnostics.append(
                        Diagnostic(f"Duplicate agent name: {statement.name}", statement.span)
                    )
                seen_agents.add(statement.name)
                self._validate_statements(statement.statements, diagnostics, inside_agent=True)
                continue

            if isinstance(statement, OnBlock):
                if not inside_agent:
                    diagnostics.append(
                        Diagnostic("Event blocks must be declared inside an agent", statement.span)
                    )
                if statement.event in seen_events:
                    diagnostics.append(
                        Diagnostic(f"Duplicate event block: {statement.event}", statement.span)
                    )
                seen_events.add(statement.event)
                self._validate_statements(statement.statements, diagnostics, inside_agent=inside_agent)
                continue

            if isinstance(statement, IfStatement):
                self._validate_statements(
                    statement.then_statements,
                    diagnostics,
                    inside_agent=inside_agent,
                )
                self._validate_statements(
                    statement.else_statements,
                    diagnostics,
                    inside_agent=inside_agent,
                )
                continue

            if isinstance(statement, LetStatement | RememberStatement) and not statement.name:
                diagnostics.append(Diagnostic("Assignment target cannot be empty", statement.span))


def validate_ix(program: Program) -> list[Diagnostic]:
    """Validate a parsed IX program and return diagnostics."""

    return IXValidator().validate(program)
