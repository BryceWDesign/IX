"""Canonical IX runtime.

This runtime executes the conservative IX core created by the canonical parser.
It is intentionally deterministic, dependency-free, and audit-first. Every
meaningful action emits a structured trace event so future commands such as
`ix trace` and `ix evidence` can be built on a real execution ledger instead of
bolted-on logging.
"""

from __future__ import annotations

import ast as py_ast
import operator
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

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
    TraceStatement,
)
from .errors import IXError, SourceSpan
from .tracing import TraceEvent
from .validator import validate_ix

_INTERPOLATION = re.compile(r"\{(?P<name>[A-Za-z_][A-Za-z0-9_]*)\}")

_BINARY_OPERATORS = {
    py_ast.Add: operator.add,
    py_ast.Sub: operator.sub,
    py_ast.Mult: operator.mul,
    py_ast.Div: operator.truediv,
    py_ast.FloorDiv: operator.floordiv,
    py_ast.Mod: operator.mod,
}

_UNARY_OPERATORS = {
    py_ast.UAdd: operator.pos,
    py_ast.USub: operator.neg,
    py_ast.Not: operator.not_,
}

_COMPARISON_OPERATORS = {
    py_ast.Eq: operator.eq,
    py_ast.NotEq: operator.ne,
    py_ast.Lt: operator.lt,
    py_ast.LtE: operator.le,
    py_ast.Gt: operator.gt,
    py_ast.GtE: operator.ge,
}


class IXRuntimeError(IXError):
    """Raised when IX execution fails at runtime."""


@dataclass
class ExecutionResult:
    """Result object returned after running an IX program."""

    status: str
    variables: dict[str, Any] = field(default_factory=dict)
    memory: dict[str, Any] = field(default_factory=dict)
    outputs: list[str] = field(default_factory=list)
    replies: list[str] = field(default_factory=list)
    approvals_required: list[str] = field(default_factory=list)
    policies: list[dict[str, Any]] = field(default_factory=list)
    trace: list[TraceEvent] = field(default_factory=list)

    def trace_as_dicts(self) -> list[dict[str, Any]]:
        """Return the trace ledger in JSON-serializable form."""

        return [event.to_dict() for event in self.trace]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable result summary."""

        return {
            "status": self.status,
            "variables": dict(self.variables),
            "memory": dict(self.memory),
            "outputs": list(self.outputs),
            "replies": list(self.replies),
            "approvals_required": list(self.approvals_required),
            "policies": list(self.policies),
            "trace": self.trace_as_dicts(),
        }


class SafeExpressionEvaluator:
    """Evaluate a narrow, deterministic expression subset for IX."""

    def __init__(self, values: Mapping[str, Any]) -> None:
        self.values = values

    def evaluate(self, expression: str) -> Any:
        """Evaluate an IX expression without exposing Python builtins."""

        try:
            parsed = py_ast.parse(expression, mode="eval")
        except SyntaxError:
            return self._fallback_text(expression)
        return self._evaluate_node(parsed.body)

    def _evaluate_node(self, node: py_ast.AST) -> Any:
        if isinstance(node, py_ast.Constant):
            return node.value

        if isinstance(node, py_ast.Name):
            if node.id in self.values:
                return self.values[node.id]
            if node.id == "true":
                return True
            if node.id == "false":
                return False
            if node.id == "null":
                return None
            raise IXRuntimeError(f"Unknown name: {node.id}")

        if isinstance(node, py_ast.BinOp):
            operator_fn = _BINARY_OPERATORS.get(type(node.op))
            if operator_fn is None:
                raise IXRuntimeError(f"Unsupported binary operator: {type(node.op).__name__}")
            return operator_fn(self._evaluate_node(node.left), self._evaluate_node(node.right))

        if isinstance(node, py_ast.UnaryOp):
            operator_fn = _UNARY_OPERATORS.get(type(node.op))
            if operator_fn is None:
                raise IXRuntimeError(f"Unsupported unary operator: {type(node.op).__name__}")
            return operator_fn(self._evaluate_node(node.operand))

        if isinstance(node, py_ast.BoolOp):
            values = [bool(self._evaluate_node(value)) for value in node.values]
            if isinstance(node.op, py_ast.And):
                return all(values)
            if isinstance(node.op, py_ast.Or):
                return any(values)
            raise IXRuntimeError(f"Unsupported boolean operator: {type(node.op).__name__}")

        if isinstance(node, py_ast.Compare):
            return self._evaluate_compare(node)

        raise IXRuntimeError(f"Unsupported expression: {type(node).__name__}")

    def _evaluate_compare(self, node: py_ast.Compare) -> bool:
        left = self._evaluate_node(node.left)
        for operator_node, comparator in zip(node.ops, node.comparators, strict=True):
            operator_fn = _COMPARISON_OPERATORS.get(type(operator_node))
            if operator_fn is None:
                raise IXRuntimeError(
                    f"Unsupported comparison operator: {type(operator_node).__name__}"
                )
            right = self._evaluate_node(comparator)
            if not operator_fn(left, right):
                return False
            left = right
        return True

    def _fallback_text(self, expression: str) -> str:
        stripped = expression.strip()
        if not stripped:
            return ""
        return stripped


class IXRuntime:
    """Execute canonical IX programs with structured trace output."""

    def run(
        self,
        program: Program,
        *,
        agent: str | None = None,
        event: str | None = None,
        inputs: Mapping[str, Any] | None = None,
    ) -> ExecutionResult:
        diagnostics = validate_ix(program)
        if diagnostics:
            joined = "\n".join(diagnostic.format() for diagnostic in diagnostics)
            raise IXRuntimeError(f"IX validation failed:\n{joined}")

        result = ExecutionResult(status="running")
        values: dict[str, Any] = dict(inputs or {})
        statements = self._select_statements(program, agent=agent, event=event)
        self._emit(result, "run.start", "IX execution started", program.span)

        for statement in statements:
            self._execute_statement(statement, values, result)

        result.variables = dict(values)
        result.status = "completed"
        self._emit(result, "run.complete", "IX execution completed", program.span)
        return result

    def _select_statements(
        self,
        program: Program,
        *,
        agent: str | None,
        event: str | None,
    ) -> tuple[Statement, ...]:
        if agent is None and event is None:
            selected: list[Statement] = []
            for statement in program.statements:
                if not isinstance(statement, AgentBlock):
                    selected.append(statement)
            return tuple(selected)

        if agent is None:
            raise IXRuntimeError("Selecting an event requires an agent name")

        for statement in program.statements:
            if isinstance(statement, AgentBlock) and statement.name == agent:
                return self._select_agent_event(statement, event=event or "start")

        raise IXRuntimeError(f"Agent not found: {agent}")

    def _select_agent_event(self, agent: AgentBlock, *, event: str) -> tuple[Statement, ...]:
        for statement in agent.statements:
            if isinstance(statement, OnBlock) and statement.event == event:
                return statement.statements
        raise IXRuntimeError(f"Event not found for agent {agent.name}: {event}")

    def _execute_statement(
        self,
        statement: Statement,
        values: dict[str, Any],
        result: ExecutionResult,
    ) -> None:
        evaluator = SafeExpressionEvaluator({**result.memory, **values})

        if isinstance(statement, LetStatement):
            value = evaluator.evaluate(statement.expression)
            values[statement.name] = value
            self._emit(result, "let", f"Set variable {statement.name}", statement.span)
            return

        if isinstance(statement, RememberStatement):
            value = evaluator.evaluate(statement.expression)
            result.memory[statement.name] = value
            self._emit(result, "memory.remember", f"Remembered {statement.name}", statement.span)
            return

        if isinstance(statement, RecallStatement):
            if statement.name not in result.memory:
                raise IXRuntimeError(f"Memory value not found: {statement.name}")
            values[statement.name] = result.memory[statement.name]
            self._emit(result, "memory.recall", f"Recalled {statement.name}", statement.span)
            return

        if isinstance(statement, PrintStatement):
            rendered = self._render(statement.expression, evaluator)
            result.outputs.append(rendered)
            self._emit(result, "print", "Printed output", statement.span, text=rendered)
            return

        if isinstance(statement, ReplyStatement):
            rendered = self._render(statement.expression, evaluator)
            result.replies.append(rendered)
            self._emit(result, "reply", "Emitted reply", statement.span, text=rendered)
            return

        if isinstance(statement, AssertStatement):
            passed = bool(evaluator.evaluate(statement.expression))
            self._emit(
                result,
                "assert",
                "Assertion passed" if passed else "Assertion failed",
                statement.span,
                expression=statement.expression,
                passed=passed,
            )
            if not passed:
                raise IXRuntimeError(f"Assertion failed: {statement.expression}")
            return

        if isinstance(statement, TraceStatement):
            message = self._render(statement.message, evaluator)
            self._emit(result, "trace", message, statement.span)
            return

        if isinstance(statement, RequireApprovalStatement):
            reason = self._render(statement.reason, evaluator)
            result.approvals_required.append(reason)
            self._emit(result, "approval.required", reason, statement.span)
            return

        if isinstance(statement, PolicyStatement):
            policy = {
                "effect": statement.effect,
                "target": statement.target,
                "reason": self._render(statement.reason, evaluator) if statement.reason else None,
            }
            result.policies.append(policy)
            self._emit(result, "policy.recorded", f"Policy recorded: {statement.effect}", statement.span)
            return

        raise IXRuntimeError(f"Unsupported runtime statement: {type(statement).__name__}")

    def _render(self, expression: str | None, evaluator: SafeExpressionEvaluator) -> str:
        if expression is None:
            return ""
        value = evaluator.evaluate(expression)
        if isinstance(value, str):
            return self._interpolate(value, evaluator.values)
        return str(value)

    def _interpolate(self, text: str, values: Mapping[str, Any]) -> str:
        def replace(match: re.Match[str]) -> str:
            name = match.group("name")
            if name not in values:
                raise IXRuntimeError(f"Unknown interpolation name: {name}")
            return str(values[name])

        return _INTERPOLATION.sub(replace, text)

    def _emit(
        self,
        result: ExecutionResult,
        kind: str,
        message: str,
        span: SourceSpan,
        **data: Any,
    ) -> None:
        result.trace.append(
            TraceEvent(
                step=len(result.trace) + 1,
                kind=kind,
                message=message,
                span=span,
                data=data,
            )
        )


def run_ix(
    program: Program,
    *,
    agent: str | None = None,
    event: str | None = None,
    inputs: Mapping[str, Any] | None = None,
) -> ExecutionResult:
    """Run a parsed IX program using the canonical runtime."""

    return IXRuntime().run(program, agent=agent, event=event, inputs=inputs)
