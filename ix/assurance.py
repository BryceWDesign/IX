"""Static and optional runtime assurance checks for IX programs."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

from .ast import (
    AgentBlock,
    AssertStatement,
    IfStatement,
    OnBlock,
    PolicyStatement,
    Program,
    RequireApprovalStatement,
    SendStatement,
    Statement,
    ToolCallStatement,
    TraceStatement,
)
from .runtime import IXRuntime, IXRuntimeError
from .tools import BuiltInToolRegistry
from .validator import validate_ix

AssuranceSeverity = Literal["pass", "warn", "fail"]


@dataclass(frozen=True)
class AssuranceProfile:
    """Configured assurance behavior for one named review profile."""

    name: str
    description: str
    require_executable_path: bool = True
    check_tool_policies: bool = True
    check_handoff_targets: bool = True
    check_condition_markers: bool = True
    check_assertions: bool = True
    check_trace_statements: bool = True
    check_human_review: bool = True
    allow_runtime_execution: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable profile representation."""

        return {
            "name": self.name,
            "description": self.description,
            "require_executable_path": self.require_executable_path,
            "check_tool_policies": self.check_tool_policies,
            "check_handoff_targets": self.check_handoff_targets,
            "check_condition_markers": self.check_condition_markers,
            "check_assertions": self.check_assertions,
            "check_trace_statements": self.check_trace_statements,
            "check_human_review": self.check_human_review,
            "allow_runtime_execution": self.allow_runtime_execution,
        }


class AssuranceProfileRegistry:
    """Registry of supported assurance profiles."""

    def __init__(self, profiles: tuple[AssuranceProfile, ...] | None = None) -> None:
        configured_profiles = profiles or (
            AssuranceProfile(
                name="experimental-local",
                description=(
                    "Default local IX assurance profile for deterministic, "
                    "evidence-bound development checks."
                ),
            ),
        )
        self._profiles = {profile.name: profile for profile in configured_profiles}

    def get(self, name: str) -> AssuranceProfile | None:
        """Return a profile by name, or None when it is not registered."""

        return self._profiles.get(name)

    def require(self, name: str) -> AssuranceProfile:
        """Return a profile by name or raise a clear error for unsupported names."""

        profile = self.get(name)
        if profile is None:
            available = ", ".join(sorted(self._profiles))
            raise ValueError(f"Unknown assurance profile `{name}`. Available profiles: {available}")
        return profile

    def names(self) -> tuple[str, ...]:
        """Return registered profile names in stable order."""

        return tuple(sorted(self._profiles))

    def profiles(self) -> tuple[AssuranceProfile, ...]:
        """Return registered profiles in stable order."""

        return tuple(self._profiles[name] for name in self.names())


@dataclass(frozen=True)
class AssuranceCheck:
    """One assurance finding for an IX program."""

    check_id: str
    severity: AssuranceSeverity
    message: str
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable check representation."""

        return {
            "id": self.check_id,
            "severity": self.severity,
            "message": self.message,
            "data": self.data,
        }


@dataclass(frozen=True)
class AssuranceReport:
    """Assurance report for one IX program."""

    status: AssuranceSeverity
    profile: str
    metrics: dict[str, int]
    checks: tuple[AssuranceCheck, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable report representation."""

        return {
            "status": self.status,
            "profile": self.profile,
            "metrics": self.metrics,
            "checks": [check.to_dict() for check in self.checks],
        }


class AssuranceAnalyzer:
    """Analyze IX programs for bounded evidence-readiness checks."""

    def __init__(
        self,
        *,
        tool_registry: BuiltInToolRegistry | None = None,
        profile_registry: AssuranceProfileRegistry | None = None,
    ) -> None:
        self.tool_registry = tool_registry or BuiltInToolRegistry()
        self.profile_registry = profile_registry or AssuranceProfileRegistry()

    def assess(
        self,
        program: Program,
        *,
        profile: str = "experimental-local",
        execute: bool = False,
        agent: str | None = None,
        event: str | None = None,
        inputs: Mapping[str, Any] | None = None,
    ) -> AssuranceReport:
        """Assess a parsed IX program and return an assurance report."""

        active_profile = self.profile_registry.require(profile)
        checks: list[AssuranceCheck] = [
            AssuranceCheck(
                "profile.selected",
                "pass",
                f"Using assurance profile `{active_profile.name}`.",
                {"profile": active_profile.to_dict()},
            )
        ]
        metrics = self._metrics(program)

        diagnostics = validate_ix(program)
        for diagnostic in diagnostics:
            checks.append(
                AssuranceCheck(
                    "validation.diagnostic",
                    "fail",
                    diagnostic.format(),
                    {
                        "line": diagnostic.span.line,
                        "column": diagnostic.span.column,
                    },
                )
            )

        if active_profile.require_executable_path:
            if metrics["executable_paths"] == 0:
                checks.append(
                    AssuranceCheck(
                        "program.no_executable_path",
                        "fail",
                        "Program has no top-level statements and no agent event blocks to execute.",
                    )
                )
            else:
                checks.append(
                    AssuranceCheck(
                        "program.executable_path",
                        "pass",
                        "Program exposes at least one executable path.",
                        {"executable_paths": metrics["executable_paths"]},
                    )
                )

        if active_profile.check_tool_policies:
            checks.extend(self._check_tool_policies(program))
        if active_profile.check_handoff_targets:
            checks.extend(self._check_handoff_targets(program))

        if active_profile.check_condition_markers and metrics["conditions"] > 0:
            checks.append(
                AssuranceCheck(
                    "conditions.present",
                    "pass",
                    "Program contains explicit conditional decision logic.",
                    {"conditions": metrics["conditions"]},
                )
            )

        if active_profile.check_assertions:
            if metrics["assertions"] == 0:
                checks.append(
                    AssuranceCheck(
                        "assertions.missing",
                        "warn",
                        "Program has no explicit IX assertions. Add assertions for "
                        "stronger testability.",
                    )
                )
            else:
                checks.append(
                    AssuranceCheck(
                        "assertions.present",
                        "pass",
                        "Program contains explicit IX assertions.",
                        {"assertions": metrics["assertions"]},
                    )
                )

        if active_profile.check_trace_statements:
            if metrics["trace_statements"] == 0:
                checks.append(
                    AssuranceCheck(
                        "trace_statements.missing",
                        "warn",
                        "Program has no explicit trace statements. Runtime trace still exists, "
                        "but domain trace markers improve reviewability.",
                    )
                )
            else:
                checks.append(
                    AssuranceCheck(
                        "trace_statements.present",
                        "pass",
                        "Program contains explicit trace statements.",
                        {"trace_statements": metrics["trace_statements"]},
                    )
                )

        if active_profile.check_human_review:
            if metrics["approvals_required"] > 0:
                checks.append(
                    AssuranceCheck(
                        "human_review.present",
                        "pass",
                        "Program declares human approval requirements.",
                        {"approvals_required": metrics["approvals_required"]},
                    )
                )
            elif metrics["tool_calls"] > 0 or metrics["handoffs"] > 0:
                checks.append(
                    AssuranceCheck(
                        "human_review.missing_for_automation",
                        "warn",
                        "Program uses tools or agent handoffs without an explicit human "
                        "approval checkpoint.",
                    )
                )

        if execute:
            if active_profile.allow_runtime_execution:
                checks.append(self._runtime_check(program, agent=agent, event=event, inputs=inputs))
            else:
                checks.append(
                    AssuranceCheck(
                        "runtime.execution_not_allowed_by_profile",
                        "fail",
                        "Assurance profile "
                        f"`{active_profile.name}` does not allow runtime execution checks.",
                    )
                )

        return AssuranceReport(
            status=self._status(checks),
            profile=active_profile.name,
            metrics=metrics,
            checks=tuple(checks),
        )

    def _metrics(self, program: Program) -> dict[str, int]:
        metrics = {
            "agents": 0,
            "events": 0,
            "top_level_statements": 0,
            "executable_paths": 0,
            "policies": 0,
            "tool_calls": 0,
            "handoffs": 0,
            "approvals_required": 0,
            "assertions": 0,
            "trace_statements": 0,
            "conditions": 0,
        }
        self._collect_metrics(program.statements, metrics, top_level=True)
        metrics["executable_paths"] = metrics["events"] + metrics["top_level_statements"]
        return metrics

    def _collect_metrics(
        self,
        statements: tuple[Statement, ...],
        metrics: dict[str, int],
        *,
        top_level: bool,
    ) -> None:
        for statement in statements:
            if isinstance(statement, AgentBlock):
                metrics["agents"] += 1
                self._collect_metrics(statement.statements, metrics, top_level=False)
                continue

            if isinstance(statement, OnBlock):
                metrics["events"] += 1
                self._collect_metrics(statement.statements, metrics, top_level=False)
                continue

            if top_level:
                metrics["top_level_statements"] += 1

            if isinstance(statement, PolicyStatement):
                metrics["policies"] += 1
            elif isinstance(statement, ToolCallStatement):
                metrics["tool_calls"] += 1
            elif isinstance(statement, SendStatement):
                metrics["handoffs"] += 1
            elif isinstance(statement, RequireApprovalStatement):
                metrics["approvals_required"] += 1
            elif isinstance(statement, AssertStatement):
                metrics["assertions"] += 1
            elif isinstance(statement, TraceStatement):
                metrics["trace_statements"] += 1
            elif isinstance(statement, IfStatement):
                metrics["conditions"] += 1
                self._collect_metrics(statement.then_statements, metrics, top_level=False)
                self._collect_metrics(statement.else_statements, metrics, top_level=False)

    def _check_tool_policies(self, program: Program) -> list[AssuranceCheck]:
        checks: list[AssuranceCheck] = []
        self._check_tool_policies_in_scope(
            program.statements,
            "top-level",
            checks,
            inherited_policies=(),
        )

        for statement in program.statements:
            if isinstance(statement, AgentBlock):
                for child in statement.statements:
                    if isinstance(child, OnBlock):
                        scope = f"{statement.name}.{child.event}"
                        self._check_tool_policies_in_scope(
                            child.statements,
                            scope,
                            checks,
                            inherited_policies=(),
                        )

        if not any(check.check_id.startswith("tool_policy") for check in checks):
            checks.append(
                AssuranceCheck(
                    "tool_policy.no_tool_calls",
                    "pass",
                    "No tool calls require policy gating in this program.",
                )
            )

        return checks

    def _check_tool_policies_in_scope(
        self,
        statements: tuple[Statement, ...],
        scope: str,
        checks: list[AssuranceCheck],
        *,
        inherited_policies: tuple[PolicyStatement, ...],
    ) -> None:
        local_policies = tuple(
            statement for statement in statements if isinstance(statement, PolicyStatement)
        )
        policies = inherited_policies + local_policies

        for statement in statements:
            if isinstance(statement, ToolCallStatement):
                self._check_one_tool_policy(statement, policies, scope, checks)
                continue

            if isinstance(statement, IfStatement):
                self._check_tool_policies_in_scope(
                    statement.then_statements,
                    f"{scope}.if_then",
                    checks,
                    inherited_policies=policies,
                )
                self._check_tool_policies_in_scope(
                    statement.else_statements,
                    f"{scope}.if_else",
                    checks,
                    inherited_policies=policies,
                )

    def _check_one_tool_policy(
        self,
        statement: ToolCallStatement,
        policies: tuple[PolicyStatement, ...],
        scope: str,
        checks: list[AssuranceCheck],
    ) -> None:
        if statement.tool_name not in self.tool_registry.names():
            checks.append(
                AssuranceCheck(
                    "tool_policy.unknown_tool",
                    "fail",
                    f"Unknown tool `{statement.tool_name}` in scope `{scope}`.",
                    {"scope": scope, "tool": statement.tool_name},
                )
            )
            return

        decision = self._tool_policy_decision(statement.tool_name, policies)
        if decision["effect"] != "allow":
            checks.append(
                AssuranceCheck(
                    "tool_policy.not_allowed",
                    "fail",
                    f"Tool `{statement.tool_name}` is not explicitly allowed in scope `{scope}`.",
                    {"scope": scope, "tool": statement.tool_name, "decision": decision},
                )
            )
        else:
            checks.append(
                AssuranceCheck(
                    "tool_policy.allowed",
                    "pass",
                    f"Tool `{statement.tool_name}` is explicitly allowed in scope `{scope}`.",
                    {"scope": scope, "tool": statement.tool_name, "decision": decision},
                )
            )

    def _check_handoff_targets(self, program: Program) -> list[AssuranceCheck]:
        checks: list[AssuranceCheck] = []
        targets = self._agent_events(program)
        handoffs = self._send_statements(program.statements)

        if not handoffs:
            checks.append(
                AssuranceCheck(
                    "handoff.no_handoffs",
                    "pass",
                    "No agent handoffs require target validation in this program.",
                )
            )
            return checks

        for handoff in handoffs:
            target = (handoff.target_agent, handoff.target_event)
            if target in targets:
                checks.append(
                    AssuranceCheck(
                        "handoff.target_found",
                        "pass",
                        f"Handoff target `{handoff.target_agent}.{handoff.target_event}` exists.",
                        {
                            "target_agent": handoff.target_agent,
                            "target_event": handoff.target_event,
                        },
                    )
                )
            else:
                checks.append(
                    AssuranceCheck(
                        "handoff.target_missing",
                        "fail",
                        "Handoff target "
                        f"`{handoff.target_agent}.{handoff.target_event}` does not exist.",
                        {
                            "target_agent": handoff.target_agent,
                            "target_event": handoff.target_event,
                        },
                    )
                )

        return checks

    def _agent_events(self, program: Program) -> set[tuple[str, str]]:
        targets: set[tuple[str, str]] = set()

        for statement in program.statements:
            if isinstance(statement, AgentBlock):
                for child in statement.statements:
                    if isinstance(child, OnBlock):
                        targets.add((statement.name, child.event))

        return targets

    def _send_statements(self, statements: tuple[Statement, ...]) -> list[SendStatement]:
        found: list[SendStatement] = []

        for statement in statements:
            if isinstance(statement, SendStatement):
                found.append(statement)
            elif isinstance(statement, AgentBlock | OnBlock):
                found.extend(self._send_statements(statement.statements))
            elif isinstance(statement, IfStatement):
                found.extend(self._send_statements(statement.then_statements))
                found.extend(self._send_statements(statement.else_statements))

        return found

    def _runtime_check(
        self,
        program: Program,
        *,
        agent: str | None,
        event: str | None,
        inputs: Mapping[str, Any] | None,
    ) -> AssuranceCheck:
        try:
            result = IXRuntime(tool_registry=self.tool_registry).run(
                program,
                agent=agent,
                event=event,
                inputs=inputs,
            )
        except IXRuntimeError as error:
            return AssuranceCheck(
                "runtime.execution_failed",
                "fail",
                f"Runtime execution failed: {error}",
            )

        return AssuranceCheck(
            "runtime.execution_passed",
            "pass",
            "Runtime execution completed under the selected entry point.",
            {
                "trace_events": len(result.trace),
                "outputs": len(result.outputs),
                "replies": len(result.replies),
                "handoffs": len(result.handoffs),
                "tool_results": len(result.tool_results),
                "branches": len(result.branches),
            },
        )

    def _tool_policy_decision(
        self,
        tool_name: str,
        policies: tuple[PolicyStatement, ...],
    ) -> dict[str, Any]:
        matching = [policy for policy in policies if self._policy_matches(policy.target, tool_name)]
        denying = [policy for policy in matching if policy.effect == "deny"]

        if denying:
            return {
                "effect": "deny",
                "target": denying[-1].target,
                "reason": denying[-1].reason,
            }

        allowing = [policy for policy in matching if policy.effect == "allow"]
        if allowing:
            return {
                "effect": "allow",
                "target": allowing[-1].target,
                "reason": allowing[-1].reason,
            }

        return {
            "effect": "deny",
            "target": tool_name,
            "reason": "No explicit allow policy matched this tool call.",
        }

    def _policy_matches(self, target: str, tool_name: str) -> bool:
        if target == tool_name:
            return True

        if target.endswith(".*"):
            return tool_name.startswith(target[:-1])

        return False

    def _status(self, checks: list[AssuranceCheck]) -> AssuranceSeverity:
        if any(check.severity == "fail" for check in checks):
            return "fail"

        if any(check.severity == "warn" for check in checks):
            return "warn"

        return "pass"


def assess_ix(
    program: Program,
    *,
    profile: str = "experimental-local",
    execute: bool = False,
    agent: str | None = None,
    event: str | None = None,
    inputs: Mapping[str, Any] | None = None,
) -> AssuranceReport:
    """Assess a parsed IX program with the default assurance analyzer."""

    return AssuranceAnalyzer().assess(
        program,
        profile=profile,
        execute=execute,
        agent=agent,
        event=event,
        inputs=inputs,
    )
