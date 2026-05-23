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
                    "artifact_files": [
                        "summary.json",
                        "trace.json",
                        "policies.json",
                        "tool-results.json",
                        "handoffs.json",
                        "branches.json",
                        "approvals-required.json",
                        "outputs.txt",
                        "replies.txt",
                        "assurance-claims.md",
                        "limitations.md",
                    ],
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
        files.append(self._write_json(output_dir / "approvals-required.json", result.approvals_required))
        files.append(self._write_text(output_dir / "outputs.txt", "\n".join(result.outputs) + "\n"))
        files.append(self._write_text(output_dir / "replies.txt", "\n".join(result.replies) + "\n"))
        files.append(self._write_text(output_dir / "assurance-claims.md", self._claims_text(result)))
        files.append(self._write_text(output_dir / "limitations.md", self._limitations_text()))

        return EvidenceBundle(output_dir=output_dir, files=tuple(files))

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
            f"- Human approval requirements captured: {len(result.approvals_required)}.\n\n"
            "## Not claimed\n\n"
            "- This bundle does not certify the script as safe, complete, lawful, or production-ready.\n"
            "- This bundle does not prove external system behavior beyond the deterministic IX runtime output.\n"
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
            "are intentionally not part of this bundle model.\n"
        )
