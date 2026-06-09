"""Semantic validation for canonical IX programs."""

from __future__ import annotations

import ast as py_ast
import re
from dataclasses import dataclass

from .ast import (
    AgentBlock,
    AttemptBlock,
    ClaimBoundaryStatement,
    EvidenceRequirementStatement,
    FalsifyIfStatement,
    HandoffContractStatement,
    IfStatement,
    LetStatement,
    NonGoalStatement,
    ObligationBlock,
    OnBlock,
    Program,
    PurposeStatement,
    RememberStatement,
    RequireApprovalStatement,
    Statement,
)
from .errors import SourceSpan

_CONTRACT_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_.:-]*$")


@dataclass(frozen=True)
class Diagnostic:
    """A validation finding tied to source code."""

    message: str
    span: SourceSpan
    severity: str = "error"

    def format(self) -> str:
        return f"{self.span.label()}: {self.severity}: {self.message}"


@dataclass(frozen=True)
class _ValidationContext:
    inside_agent: bool = False
    inside_attempt: bool = False
    inside_obligation: bool = False
    inside_if: bool = False


class IXValidator:
    """Validate IX ASTs before execution."""

    def validate(self, program: Program) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        self._validate_statements(
            program.statements,
            diagnostics,
            context=_ValidationContext(),
        )
        return diagnostics

    def _validate_statements(
        self,
        statements: tuple[Statement, ...],
        diagnostics: list[Diagnostic],
        *,
        context: _ValidationContext,
    ) -> None:
        seen_agents: set[str] = set()
        seen_events: set[str] = set()
        seen_attempts: set[str] = set()

        for statement in statements:
            if isinstance(statement, AgentBlock):
                if context.inside_agent:
                    diagnostics.append(
                        Diagnostic("Nested agent blocks are not supported", statement.span)
                    )
                if context.inside_attempt or context.inside_obligation:
                    diagnostics.append(
                        Diagnostic(
                            "Agent blocks are not supported inside cognition contracts",
                            statement.span,
                        )
                    )
                if statement.name in seen_agents:
                    diagnostics.append(
                        Diagnostic(f"Duplicate agent name: {statement.name}", statement.span)
                    )
                seen_agents.add(statement.name)
                self._validate_statements(
                    statement.statements,
                    diagnostics,
                    context=_ValidationContext(inside_agent=True),
                )
                continue

            if isinstance(statement, AttemptBlock):
                self._validate_attempt_block(statement, diagnostics, context, seen_attempts)
                continue

            if isinstance(statement, OnBlock):
                if not context.inside_agent:
                    diagnostics.append(
                        Diagnostic("Event blocks must be declared inside an agent", statement.span)
                    )
                if context.inside_attempt or context.inside_obligation:
                    diagnostics.append(
                        Diagnostic(
                            "Event blocks are not supported inside cognition contracts",
                            statement.span,
                        )
                    )
                if statement.event in seen_events:
                    diagnostics.append(
                        Diagnostic(f"Duplicate event block: {statement.event}", statement.span)
                    )
                seen_events.add(statement.event)
                self._validate_statements(
                    statement.statements,
                    diagnostics,
                    context=_ValidationContext(inside_agent=context.inside_agent),
                )
                continue

            if isinstance(statement, ObligationBlock):
                self._validate_obligation_block(statement, diagnostics, context, set())
                continue

            if isinstance(statement, IfStatement):
                if context.inside_attempt or context.inside_obligation:
                    diagnostics.append(
                        Diagnostic(
                            "If blocks are not supported inside cognition contracts",
                            statement.span,
                        )
                    )
                self._validate_statements(
                    statement.then_statements,
                    diagnostics,
                    context=_ValidationContext(
                        inside_agent=context.inside_agent,
                        inside_attempt=context.inside_attempt,
                        inside_obligation=context.inside_obligation,
                        inside_if=True,
                    ),
                )
                self._validate_statements(
                    statement.else_statements,
                    diagnostics,
                    context=_ValidationContext(
                        inside_agent=context.inside_agent,
                        inside_attempt=context.inside_attempt,
                        inside_obligation=context.inside_obligation,
                        inside_if=True,
                    ),
                )
                continue

            self._validate_leaf_statement(statement, diagnostics, context)

    def _validate_attempt_block(
        self,
        statement: AttemptBlock,
        diagnostics: list[Diagnostic],
        context: _ValidationContext,
        seen_attempts: set[str],
    ) -> None:
        if (
            context.inside_agent
            or context.inside_attempt
            or context.inside_obligation
            or context.inside_if
        ):
            diagnostics.append(
                Diagnostic("Attempt blocks must be declared at top level", statement.span)
            )
        if not self._valid_contract_identifier(statement.name):
            diagnostics.append(Diagnostic("Attempt name cannot be empty or malformed", statement.span))
        if statement.name in seen_attempts:
            diagnostics.append(Diagnostic(f"Duplicate attempt name: {statement.name}", statement.span))
        seen_attempts.add(statement.name)
        if not statement.statements:
            diagnostics.append(Diagnostic("Attempt block cannot be empty", statement.span))

        seen_obligations: set[str] = set()
        for child in statement.statements:
            if isinstance(child, ObligationBlock):
                self._validate_obligation_block(
                    child,
                    diagnostics,
                    _ValidationContext(inside_attempt=True),
                    seen_obligations,
                )
                continue
            self._validate_attempt_child(child, diagnostics)

    def _validate_obligation_block(
        self,
        statement: ObligationBlock,
        diagnostics: list[Diagnostic],
        context: _ValidationContext,
        seen_obligations: set[str],
    ) -> None:
        if not context.inside_attempt or context.inside_obligation:
            diagnostics.append(
                Diagnostic("Obligation blocks must be direct children of an attempt", statement.span)
            )
        if not self._valid_contract_identifier(statement.identifier):
            diagnostics.append(
                Diagnostic("Obligation identifier cannot be empty or malformed", statement.span)
            )
        if statement.identifier in seen_obligations:
            diagnostics.append(
                Diagnostic(f"Duplicate obligation identifier: {statement.identifier}", statement.span)
            )
        seen_obligations.add(statement.identifier)
        if not statement.statements:
            diagnostics.append(Diagnostic("Obligation block cannot be empty", statement.span))

        seen_evidence: set[str] = set()
        for child in statement.statements:
            if isinstance(child, EvidenceRequirementStatement):
                self._validate_evidence_requirement(child, diagnostics, seen_evidence)
                continue
            if isinstance(child, FalsifyIfStatement):
                self._validate_falsification(child, diagnostics)
                continue
            diagnostics.append(
                Diagnostic(
                    "Only evidence_required and falsify_if are supported inside obligations",
                    child.span,
                )
            )

    def _validate_attempt_child(
        self,
        statement: Statement,
        diagnostics: list[Diagnostic],
    ) -> None:
        if isinstance(statement, AttemptBlock):
            self._validate_attempt_block(
                statement,
                diagnostics,
                _ValidationContext(inside_attempt=True),
                set(),
            )
            return
        if isinstance(statement, PurposeStatement):
            if self._blank_text(statement.text):
                diagnostics.append(Diagnostic("Purpose text cannot be empty", statement.span))
            return
        if isinstance(statement, NonGoalStatement):
            if self._blank_text(statement.text):
                diagnostics.append(Diagnostic("Non-goal text cannot be empty", statement.span))
            return
        if isinstance(statement, ClaimBoundaryStatement):
            if self._blank_text(statement.text):
                diagnostics.append(Diagnostic("Claim boundary text cannot be empty", statement.span))
            return
        if isinstance(statement, HandoffContractStatement):
            if not self._valid_contract_identifier(statement.target):
                diagnostics.append(
                    Diagnostic("Handoff contract target cannot be empty or malformed", statement.span)
                )
            if statement.schema_name is not None and not self._valid_contract_identifier(
                statement.schema_name
            ):
                diagnostics.append(
                    Diagnostic("Handoff contract schema cannot be malformed", statement.span)
                )
            return
        if isinstance(statement, RequireApprovalStatement):
            if self._blank_text(statement.reason):
                diagnostics.append(
                    Diagnostic("Human approval reason cannot be empty", statement.span)
                )
            return

        diagnostics.append(
            Diagnostic(
                "Unsupported statement inside attempt block: "
                f"{type(statement).__name__}",
                statement.span,
            )
        )

    def _validate_leaf_statement(
        self,
        statement: Statement,
        diagnostics: list[Diagnostic],
        context: _ValidationContext,
    ) -> None:
        if isinstance(
            statement,
            PurposeStatement
            | NonGoalStatement
            | ClaimBoundaryStatement
            | HandoffContractStatement,
        ):
            diagnostics.append(
                Diagnostic(
                    f"{type(statement).__name__} must be declared inside an attempt",
                    statement.span,
                )
            )
            return

        if isinstance(statement, EvidenceRequirementStatement | FalsifyIfStatement):
            diagnostics.append(
                Diagnostic(
                    f"{type(statement).__name__} must be declared inside an obligation",
                    statement.span,
                )
            )
            return

        if context.inside_attempt or context.inside_obligation:
            diagnostics.append(
                Diagnostic(
                    "Executable statements are not supported inside cognition contracts",
                    statement.span,
                )
            )
            return

        if isinstance(statement, LetStatement | RememberStatement) and not statement.name:
            diagnostics.append(Diagnostic("Assignment target cannot be empty", statement.span))

    def _validate_evidence_requirement(
        self,
        statement: EvidenceRequirementStatement,
        diagnostics: list[Diagnostic],
        seen_evidence: set[str],
    ) -> None:
        if not self._valid_contract_identifier(statement.artifact):
            diagnostics.append(
                Diagnostic("Evidence requirement cannot be empty or malformed", statement.span)
            )
        if statement.artifact in seen_evidence:
            diagnostics.append(
                Diagnostic(f"Duplicate evidence requirement: {statement.artifact}", statement.span)
            )
        seen_evidence.add(statement.artifact)

    def _validate_falsification(
        self,
        statement: FalsifyIfStatement,
        diagnostics: list[Diagnostic],
    ) -> None:
        if self._blank_text(statement.condition):
            diagnostics.append(Diagnostic("Falsification condition cannot be empty", statement.span))

    def _valid_contract_identifier(self, value: str) -> bool:
        return bool(_CONTRACT_IDENTIFIER.match(value.strip()))

    def _blank_text(self, value: str) -> bool:
        text = value.strip()
        if not text:
            return True
        try:
            parsed = py_ast.literal_eval(text)
        except (SyntaxError, ValueError):
            return False
        return isinstance(parsed, str) and not parsed.strip()


def validate_ix(program: Program) -> list[Diagnostic]:
    """Validate a parsed IX program and return diagnostics."""

    return IXValidator().validate(program)
