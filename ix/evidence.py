"""Evidence bundle export for IX executions."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .runtime import ExecutionResult


@dataclass(frozen=True)
class EvidenceBundle:
    """Metadata for a written IX evidence bundle."""

    output_dir: Path
    files: tuple[Path, ...]

    def relative_files(self) -> tuple[str, ...]:
        """Return bundle file paths relative to the bundle directory."""

        return tuple(path.relative_to(self.output_dir).as_posix() for path in self.files)


class EvidenceBundleWriter:
    """Write reviewable evidence artifacts for an IX execution result."""

    def write_bundle(
        self,
        result: ExecutionResult,
        *,
        source_file: Path,
        output_dir: Path,
        command: str,
    ) -> EvidenceBundle:
        """Write an evidence bundle and return its metadata."""

        output_dir.mkdir(parents=True, exist_ok=True)
        generated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        source_hash = self._sha256_file(source_file)
        result_payload = result.to_dict()
        contract_metadata = self._contract_metadata(result)
        contract_counts = self._contract_counts(contract_metadata)

        artifact_files = [
            "summary.json",
            "trace.json",
            "policies.json",
            "tool-results.json",
            "handoffs.json",
            "branches.json",
            "approvals-required.json",
            "contract.json",
            "obligations.json",
            "falsification-gates.json",
            "claim-boundaries.json",
            "outputs.txt",
            "replies.txt",
            "assurance-claims.md",
            "limitations.md",
        ]

        files: list[Path] = []
        files.append(
            self._write_json(
                output_dir / "manifest.json",
                {
                    "bundle_type": "ix.execution.evidence",
                    "schema_version": "1.0",
                    "generated_at": generated_at,
                    "command": command,
                    "source_file": str(source_file),
                    "source_sha256": source_hash,
                    "status": result.status,
                    "artifact_files": artifact_files,
                },
            )
        )
        files.append(
            self._write_json(
                output_dir / "summary.json",
                {
                    "status": result.status,
                    "source_file": str(source_file),
                    "source_sha256": source_hash,
                    "generated_at": generated_at,
                    "counts": {
                        "trace_events": len(result.trace),
                        "outputs": len(result.outputs),
                        "replies": len(result.replies),
                        "policies": len(result.policies),
                        "tool_results": len(result.tool_results),
                        "handoffs": len(result.handoffs),
                        "branches": len(result.branches),
                        "approvals_required": len(result.approvals_required),
                        "contract_attempts": contract_counts["attempts"],
                        "contract_obligations": contract_counts["obligations"],
                        "contract_evidence_requirements": contract_counts[
                            "evidence_requirements"
                        ],
                        "contract_falsification_gates": contract_counts[
                            "falsification_gates"
                        ],
                    },
                    "variables": result_payload["variables"],
                    "memory": result_payload["memory"],
                },
            )
        )
        files.append(self._write_json(output_dir / "trace.json", result.trace_as_dicts()))
        files.append(self._write_json(output_dir / "policies.json", result.policies))
        files.append(self._write_json(output_dir / "tool-results.json", result.tool_results))
        files.append(self._write_json(output_dir / "handoffs.json", result.handoffs))
        files.append(self._write_json(output_dir / "branches.json", result.branches))
        files.append(
            self._write_json(output_dir / "approvals-required.json", result.approvals_required)
        )
        files.append(self._write_json(output_dir / "contract.json", contract_metadata))
        files.append(
            self._write_json(
                output_dir / "obligations.json",
                self._obligations_payload(contract_metadata),
            )
        )
        files.append(
            self._write_json(
                output_dir / "falsification-gates.json",
                self._falsification_payload(contract_metadata),
            )
        )
        files.append(
            self._write_json(
                output_dir / "claim-boundaries.json",
                self._claim_boundaries_payload(contract_metadata),
            )
        )
        files.append(self._write_text(output_dir / "outputs.txt", "\n".join(result.outputs) + "\n"))
        files.append(self._write_text(output_dir / "replies.txt", "\n".join(result.replies) + "\n"))
        files.append(self._write_text(output_dir / "assurance-claims.md", self._claims_text(result)))
        files.append(self._write_text(output_dir / "limitations.md", self._limitations_text()))

        return EvidenceBundle(output_dir=output_dir, files=tuple(files))

    def _contract_metadata(self, result: ExecutionResult) -> dict[str, Any]:
        metadata = getattr(result, "contract_metadata", None)
        if isinstance(metadata, dict):
            return metadata
        return {
            "contract_type": "ix.cognition.contracts",
            "schema_version": "1.0",
            "runtime_semantics": "metadata_only_not_executed",
            "counts": {
                "attempts": 0,
                "obligations": 0,
                "evidence_requirements": 0,
                "falsification_gates": 0,
            },
            "attempts": [],
        }

    def _contract_counts(self, metadata: dict[str, Any]) -> dict[str, int]:
        counts = metadata.get("counts", {})
        if not isinstance(counts, dict):
            counts = {}
        return {
            "attempts": int(counts.get("attempts", 0)),
            "obligations": int(counts.get("obligations", 0)),
            "evidence_requirements": int(counts.get("evidence_requirements", 0)),
            "falsification_gates": int(counts.get("falsification_gates", 0)),
        }

    def _obligations_payload(self, metadata: dict[str, Any]) -> dict[str, Any]:
        obligations: list[dict[str, Any]] = []
        for attempt in self._attempts(metadata):
            attempt_name = str(attempt.get("name", ""))
            for obligation in self._obligations(attempt):
                obligations.append(
                    {
                        "attempt": attempt_name,
                        "id": obligation.get("id"),
                        "source": obligation.get("source"),
                        "evidence_required": list(obligation.get("evidence_required", [])),
                        "falsify_if": list(obligation.get("falsify_if", [])),
                    }
                )
        return {
            "schema_version": "1.0",
            "runtime_semantics": metadata.get("runtime_semantics"),
            "obligations": obligations,
        }

    def _falsification_payload(self, metadata: dict[str, Any]) -> dict[str, Any]:
        gates: list[dict[str, Any]] = []
        for attempt in self._attempts(metadata):
            attempt_name = str(attempt.get("name", ""))
            for obligation in self._obligations(attempt):
                obligation_id = obligation.get("id")
                for condition in obligation.get("falsify_if", []):
                    gates.append(
                        {
                            "attempt": attempt_name,
                            "obligation": obligation_id,
                            "condition": condition,
                        }
                    )
        return {
            "schema_version": "1.0",
            "runtime_semantics": metadata.get("runtime_semantics"),
            "falsification_gates": gates,
        }

    def _claim_boundaries_payload(self, metadata: dict[str, Any]) -> dict[str, Any]:
        attempts: list[dict[str, Any]] = []
        for attempt in self._attempts(metadata):
            attempts.append(
                {
                    "attempt": attempt.get("name"),
                    "purpose": list(attempt.get("purpose", [])),
                    "non_goals": list(attempt.get("non_goals", [])),
                    "claim_boundaries": list(attempt.get("claim_boundaries", [])),
                    "human_approval_required": list(
                        attempt.get("human_approval_required", [])
                    ),
                    "handoff_contracts": list(attempt.get("handoff_contracts", [])),
                }
            )
        return {
            "schema_version": "1.0",
            "runtime_semantics": metadata.get("runtime_semantics"),
            "attempts": attempts,
        }

    def _attempts(self, metadata: dict[str, Any]) -> list[dict[str, Any]]:
        attempts = metadata.get("attempts", [])
        if not isinstance(attempts, list):
            return []
        return [attempt for attempt in attempts if isinstance(attempt, dict)]

    def _obligations(self, attempt: dict[str, Any]) -> list[dict[str, Any]]:
        obligations = attempt.get("obligations", [])
        if not isinstance(obligations, list):
            return []
        return [obligation for obligation in obligations if isinstance(obligation, dict)]

    def _write_json(self, path: Path, payload: Any) -> Path:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def _write_text(self, path: Path, text: str) -> Path:
        path.write_text(text, encoding="utf-8")
        return path

    def _sha256_file(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _claims_text(self, result: ExecutionResult) -> str:
        contract_metadata = self._contract_metadata(result)
        contract_counts = self._contract_counts(contract_metadata)
        return (
            "# IX Assurance Claims\n\n"
            "This evidence bundle supports only bounded, runtime-observed claims.\n\n"
            "## Supported by this bundle\n\n"
            f"- Execution status recorded as `{result.status}`.\n"
            f"- Trace event count: {len(result.trace)}.\n"
            f"- Policy records captured: {len(result.policies)}.\n"
            f"- Tool results captured: {len(result.tool_results)}.\n"
            f"- Agent handoffs captured: {len(result.handoffs)}.\n"
            f"- Conditional branches captured: {len(result.branches)}.\n"
            f"- Human approval requirements captured: {len(result.approvals_required)}.\n"
            f"- Cognition attempt contracts captured: {contract_counts['attempts']}.\n"
            f"- Cognition obligations captured: {contract_counts['obligations']}.\n\n"
            "## Not claimed\n\n"
            "- This bundle does not certify the script as safe, complete, lawful, or production-ready.\n"
            "- This bundle does not prove external system behavior beyond the deterministic IX runtime output.\n"
            "- This bundle does not execute or certify cognition-contract obligations.\n"
            "- This bundle does not certify AGI, AGI-candidate status, or deployment readiness.\n"
            "- This bundle does not replace human review.\n"
        )

    def _limitations_text(self) -> str:
        return (
            "# IX Evidence Bundle Limitations\n\n"
            "IX evidence bundles are review artifacts, not certifications. They document what the "
            "current IX runtime observed and emitted during one execution. They do not prove that "
            "the script is appropriate for operational deployment, regulated use, safety-critical "
            "automation, or legal compliance.\n\n"
            "Current IX built-in tools are deterministic and side-effect free. External network, "
            "email, filesystem mutation, procurement, deployment, and real-world actuation tools "
            "are intentionally not part of this bundle model.\n\n"
            "Cognition-contract artifacts are declarative metadata. They record the contract, "
            "obligations, claim boundaries, and falsification gates that a downstream cognition "
            "system may later attempt. They do not execute cognition, prove learning, prove "
            "transfer, certify AGI, or authorize self-approval.\n"
        )
