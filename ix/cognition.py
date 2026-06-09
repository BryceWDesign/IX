"""Canonical cognition-contract obligation taxonomy for IX."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Iterable, Mapping


@dataclass(frozen=True)
class CognitionObligation:
    """Stable requirement family for governed cognition-candidate contracts."""

    identifier: str
    title: str
    purpose: str
    evidence_artifacts: tuple[str, ...]
    falsification_conditions: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable obligation definition."""

        return {
            "id": self.identifier,
            "title": self.title,
            "purpose": self.purpose,
            "evidence_artifacts": list(self.evidence_artifacts),
            "falsification_conditions": list(self.falsification_conditions),
        }


CANONICAL_COGNITION_OBLIGATIONS: Final[tuple[CognitionObligation, ...]] = (
    CognitionObligation(
        identifier="purpose_discipline",
        title="Purpose discipline",
        purpose="Declare the measured reason the cognition attempt exists before it runs.",
        evidence_artifacts=("attempt_purpose_record",),
        falsification_conditions=("purpose_missing", "purpose_changes_after_result"),
    ),
    CognitionObligation(
        identifier="claim_boundary_discipline",
        title="Claim-boundary discipline",
        purpose="Declare what the attempt may and may not claim from its evidence.",
        evidence_artifacts=("claim_boundary_record", "non_goal_record"),
        falsification_conditions=("claim_boundary_missing", "agi_claim_without_review"),
    ),
    CognitionObligation(
        identifier="human_authority",
        title="Human authority",
        purpose="Require human review for advancement or interpretation of candidate results.",
        evidence_artifacts=("human_review_record",),
        falsification_conditions=("human_review_missing", "system_self_approved"),
    ),
    CognitionObligation(
        identifier="prediction_before_trial",
        title="Prediction before trial",
        purpose="Record a testable prediction before action, trial, or evaluation output is known.",
        evidence_artifacts=("prediction_record",),
        falsification_conditions=("prediction_missing", "prediction_recorded_after_outcome"),
    ),
    CognitionObligation(
        identifier="measured_outcome_capture",
        title="Measured outcome capture",
        purpose="Record the observed result used to judge whether the attempt met reality.",
        evidence_artifacts=("outcome_record",),
        falsification_conditions=("outcome_missing", "outcome_not_measured"),
    ),
    CognitionObligation(
        identifier="reality_delta_comparison",
        title="Reality-delta comparison",
        purpose="Compare prediction against measured outcome and record the delta.",
        evidence_artifacts=("delta_record", "prediction_outcome_comparison"),
        falsification_conditions=("delta_missing", "prediction_outcome_not_compared"),
    ),
    CognitionObligation(
        identifier="evidence_bound_memory_update",
        title="Evidence-bound memory update",
        purpose="Allow memory updates only when tied to measured evidence and reviewable rationale.",
        evidence_artifacts=("memory_update_record", "memory_evidence_link"),
        falsification_conditions=("memory_update_without_evidence", "memory_claim_not_traceable"),
    ),
    CognitionObligation(
        identifier="future_reasoning_change",
        title="Future-reasoning change",
        purpose="Show that measured reality changed later reasoning rather than only being logged.",
        evidence_artifacts=("before_after_reasoning_record",),
        falsification_conditions=("future_reasoning_unchanged", "change_is_cosmetic"),
    ),
    CognitionObligation(
        identifier="cross_domain_transfer_probe",
        title="Cross-domain transfer probe",
        purpose="Test whether learned structure transfers outside the source task or domain.",
        evidence_artifacts=("transfer_probe_record", "source_target_domain_record"),
        falsification_conditions=("transfer_probe_missing", "transfer_failed"),
    ),
    CognitionObligation(
        identifier="novelty_generality_pressure",
        title="Novelty and generality pressure",
        purpose="Expose the attempt to non-identical tasks so success cannot be pure memorization.",
        evidence_artifacts=("novelty_record", "generality_pressure_record"),
        falsification_conditions=("novelty_missing", "task_replay_only"),
    ),
    CognitionObligation(
        identifier="long_horizon_planning_trace",
        title="Long-horizon planning trace",
        purpose="Record multi-step planning state, progress, revisions, and stop conditions.",
        evidence_artifacts=("plan_trace", "planning_revision_record"),
        falsification_conditions=("plan_trace_missing", "plan_abandoned_without_record"),
    ),
    CognitionObligation(
        identifier="uncertainty_assumption_exposure",
        title="Uncertainty and assumption exposure",
        purpose="Expose confidence, uncertainty, and assumptions instead of hiding unknowns.",
        evidence_artifacts=("uncertainty_record", "assumption_ledger"),
        falsification_conditions=("uncertainty_hidden", "assumption_not_recorded"),
    ),
    CognitionObligation(
        identifier="contradiction_handling",
        title="Contradiction handling",
        purpose="Detect contradictions and route them to correction, quarantine, or review.",
        evidence_artifacts=("contradiction_record", "resolution_record"),
        falsification_conditions=("contradiction_ignored", "conflict_used_as_truth"),
    ),
    CognitionObligation(
        identifier="shortcut_reward_hacking_detection",
        title="Shortcut and reward-hacking detection",
        purpose="Detect apparent success caused by metric gaming, shortcuts, or proxy exploitation.",
        evidence_artifacts=("shortcut_audit_record", "reward_audit_record"),
        falsification_conditions=("reward_hacking_detected", "shortcut_not_audited"),
    ),
    CognitionObligation(
        identifier="safe_refusal_path",
        title="Safe refusal path",
        purpose="Permit refusal, deferment, or safe halt when obligations cannot be satisfied.",
        evidence_artifacts=("refusal_record", "safe_halt_record"),
        falsification_conditions=("unsafe_continuation", "required_refusal_missing"),
    ),
    CognitionObligation(
        identifier="self_improvement_airlock",
        title="Self-improvement airlock",
        purpose="Separate proposed self-change from approval, execution, and promotion authority.",
        evidence_artifacts=("self_change_proposal", "approval_separation_record"),
        falsification_conditions=("self_change_self_approved", "unreviewed_self_modification"),
    ),
    CognitionObligation(
        identifier="no_self_certification",
        title="No self-certification",
        purpose="Prevent the system or model from certifying its own AGI-candidate success.",
        evidence_artifacts=("self_certification_guard_record",),
        falsification_conditions=("system_self_certifies", "model_claims_final_authority"),
    ),
    CognitionObligation(
        identifier="falsification_ledger",
        title="Falsification ledger",
        purpose="Record failure conditions and use them to block unsupported advancement claims.",
        evidence_artifacts=("falsification_ledger",),
        falsification_conditions=("falsification_record_missing", "failed_gate_ignored"),
    ),
    CognitionObligation(
        identifier="independent_replay_review",
        title="Independent replay and review readiness",
        purpose="Produce enough evidence for independent replay, audit, or human review.",
        evidence_artifacts=("replay_manifest", "review_packet"),
        falsification_conditions=("replay_not_possible", "review_packet_missing"),
    ),
    CognitionObligation(
        identifier="kernel_handoff_package",
        title="Kernel handoff package",
        purpose="Export a structured obligation package for IX-CognitionKernel to attempt.",
        evidence_artifacts=("kernel_handoff_package",),
        falsification_conditions=("kernel_handoff_missing", "handoff_schema_invalid"),
    ),
)

CANONICAL_COGNITION_OBLIGATION_IDS: Final[tuple[str, ...]] = tuple(
    obligation.identifier for obligation in CANONICAL_COGNITION_OBLIGATIONS
)

_CANONICAL_COGNITION_OBLIGATION_MAP: Final[dict[str, CognitionObligation]] = {
    obligation.identifier: obligation for obligation in CANONICAL_COGNITION_OBLIGATIONS
}

CANONICAL_COGNITION_OBLIGATION_MAP: Final[Mapping[str, CognitionObligation]] = MappingProxyType(
    _CANONICAL_COGNITION_OBLIGATION_MAP
)


def get_cognition_obligation(identifier: str) -> CognitionObligation | None:
    """Return a canonical cognition obligation by identifier, if known."""

    return CANONICAL_COGNITION_OBLIGATION_MAP.get(identifier)


def require_cognition_obligation(identifier: str) -> CognitionObligation:
    """Return a canonical cognition obligation or raise ValueError."""

    obligation = get_cognition_obligation(identifier)
    if obligation is None:
        known = ", ".join(CANONICAL_COGNITION_OBLIGATION_IDS)
        raise ValueError(f"Unknown cognition obligation `{identifier}`. Known obligations: {known}")
    return obligation


def cognition_obligation_ids() -> tuple[str, ...]:
    """Return canonical cognition obligation identifiers in stable order."""

    return CANONICAL_COGNITION_OBLIGATION_IDS


def cognition_obligations() -> tuple[CognitionObligation, ...]:
    """Return canonical cognition obligations in stable order."""

    return CANONICAL_COGNITION_OBLIGATIONS


def cognition_obligation_payloads(
    identifiers: Iterable[str] | None = None,
) -> list[dict[str, object]]:
    """Return JSON-serializable obligation definitions for selected identifiers."""

    selected_ids = tuple(identifiers) if identifiers is not None else CANONICAL_COGNITION_OBLIGATION_IDS
    return [require_cognition_obligation(identifier).to_dict() for identifier in selected_ids]
