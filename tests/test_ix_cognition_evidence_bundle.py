import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ix.cli import main
from ix.evidence import EvidenceBundleWriter
from ix.parser import parse_ix
from ix.runtime import run_ix


COGNITION_CONTRACT = '''
attempt wave6_measured_cognition {
    purpose "Test measured correction"
    non_goal "Do not claim AGI"
    claim_boundary "Research candidate only"
    require human_approval reason "Human review required"
    handoff_contract IX-CognitionKernel schema ix.cognition.contract.v1

    obligation prediction_before_trial {
        evidence_required prediction_record
        falsify_if prediction_missing
    }
}
'''

NON_KERNEL_CONTRACT = '''
attempt wave6_measured_cognition {
    purpose "Test measured correction"
    non_goal "Do not claim AGI"
    claim_boundary "Research candidate only"
    require human_approval reason "Human review required"
    handoff_contract OtherKernel schema ix.cognition.contract.v1

    obligation prediction_before_trial {
        evidence_required prediction_record
        falsify_if prediction_missing
    }
}
'''


class TestIXCognitionEvidenceBundle(unittest.TestCase):
    def test_evidence_writer_exports_cognition_contract_artifacts(self):
        source_file = self._write_ix(COGNITION_CONTRACT)
        program = parse_ix(source_file.read_text(encoding="utf-8"), filename=str(source_file))
        result = run_ix(program)
        output_dir = Path(self._tempdir.name) / "cognition-bundle"

        bundle = EvidenceBundleWriter().write_bundle(
            result,
            source_file=source_file,
            output_dir=output_dir,
            command="unit-test",
        )

        relative_files = set(bundle.relative_files())
        self.assertIn("contract.json", relative_files)
        self.assertIn("obligations.json", relative_files)
        self.assertIn("falsification-gates.json", relative_files)
        self.assertIn("claim-boundaries.json", relative_files)
        self.assertIn("kernel-handoff.json", relative_files)
        self.assertIn("satisfaction-report.json", relative_files)
        self.assertIn("failure-report.json", relative_files)

        manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
        summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        contract = json.loads((output_dir / "contract.json").read_text(encoding="utf-8"))
        obligations = json.loads((output_dir / "obligations.json").read_text(encoding="utf-8"))
        gates = json.loads((output_dir / "falsification-gates.json").read_text(encoding="utf-8"))
        boundaries = json.loads((output_dir / "claim-boundaries.json").read_text(encoding="utf-8"))
        kernel_handoff = json.loads((output_dir / "kernel-handoff.json").read_text(encoding="utf-8"))
        satisfaction = json.loads((output_dir / "satisfaction-report.json").read_text(encoding="utf-8"))
        failure = json.loads((output_dir / "failure-report.json").read_text(encoding="utf-8"))

        self.assertIn("contract.json", manifest["artifact_files"])
        self.assertIn("kernel-handoff.json", manifest["artifact_files"])
        self.assertIn("satisfaction-report.json", manifest["artifact_files"])
        self.assertIn("failure-report.json", manifest["artifact_files"])
        self.assertEqual(summary["counts"]["contract_attempts"], 1)
        self.assertEqual(summary["counts"]["contract_obligations"], 1)
        self.assertEqual(summary["counts"]["contract_evidence_requirements"], 1)
        self.assertEqual(summary["counts"]["contract_falsification_gates"], 1)
        self.assertEqual(summary["counts"]["kernel_handoff_packages"], 1)
        self.assertEqual(summary["counts"]["satisfaction_report_items"], 1)
        self.assertEqual(summary["counts"]["failure_report_gates"], 1)
        self.assertEqual(contract["runtime_semantics"], "metadata_only_not_executed")
        self.assertEqual(contract["attempts"][0]["name"], "wave6_measured_cognition")
        self.assertEqual(obligations["obligations"][0]["id"], "prediction_before_trial")
        self.assertEqual(
            obligations["obligations"][0]["evidence_required"],
            ["prediction_record"],
        )
        self.assertEqual(
            gates["falsification_gates"],
            [
                {
                    "attempt": "wave6_measured_cognition",
                    "obligation": "prediction_before_trial",
                    "condition": "prediction_missing",
                }
            ],
        )
        self.assertEqual(boundaries["attempts"][0]["purpose"], ["Test measured correction"])
        self.assertEqual(boundaries["attempts"][0]["non_goals"], ["Do not claim AGI"])
        self.assertEqual(
            boundaries["attempts"][0]["claim_boundaries"],
            ["Research candidate only"],
        )
        self.assertEqual(kernel_handoff["handoff_type"], "ix.cognitionkernel.handoff")
        self.assertEqual(len(kernel_handoff["packages"]), 1)
        self.assertEqual(kernel_handoff["packages"][0]["target"], "IX-CognitionKernel")
        self.assertEqual(kernel_handoff["packages"][0]["schema"], "ix.cognition.contract.v1")
        self.assertEqual(kernel_handoff["packages"][0]["execution_authority"], "none")
        self.assertFalse(kernel_handoff["packages"][0]["self_certification_allowed"])
        self.assertTrue(kernel_handoff["packages"][0]["human_authority_required"])
        self.assertEqual(
            kernel_handoff["packages"][0]["obligations"][0]["id"],
            "prediction_before_trial",
        )
        self.assertTrue(kernel_handoff["packages"][0]["obligations"][0]["canonical"])
        self.assertEqual(
            kernel_handoff["packages"][0]["obligations"][0]["canonical_definition"]["id"],
            "prediction_before_trial",
        )

        self.assertEqual(satisfaction["report_type"], "ix.cognition.satisfaction_report")
        self.assertEqual(satisfaction["status"], "not_evaluated")
        self.assertEqual(
            satisfaction["attempts"][0]["evaluation_state"],
            "pending_downstream_evidence",
        )
        self.assertEqual(
            satisfaction["attempts"][0]["obligations"][0]["status"],
            "pending_downstream_evidence",
        )
        self.assertIsNone(satisfaction["attempts"][0]["obligations"][0]["satisfied"])
        self.assertEqual(
            satisfaction["attempts"][0]["obligations"][0]["required_evidence"],
            ["prediction_record"],
        )
        self.assertEqual(
            satisfaction["attempts"][0]["obligations"][0]["received_evidence"],
            [],
        )

        self.assertEqual(failure["report_type"], "ix.cognition.failure_report")
        self.assertEqual(failure["status"], "not_evaluated")
        self.assertEqual(
            failure["attempts"][0]["failure_conditions"][0]["obligation"],
            "prediction_before_trial",
        )
        self.assertEqual(
            failure["attempts"][0]["failure_conditions"][0]["condition"],
            "prediction_missing",
        )
        self.assertIsNone(failure["attempts"][0]["failure_conditions"][0]["triggered"])
        self.assertTrue(failure["attempts"][0]["failure_conditions"][0]["claim_blocking"])
        self.assertEqual(
            failure["attempts"][0]["failure_conditions"][0]["required_resolution"],
            "human_review",
        )

        claims_text = (output_dir / "assurance-claims.md").read_text(encoding="utf-8")
        self.assertIn("IX-CognitionKernel handoff packages captured: 1", claims_text)
        self.assertIn("Satisfaction report obligations listed: 1", claims_text)
        self.assertIn("Failure report gates listed: 1", claims_text)
        self.assertIn("does not mark cognition obligations as satisfied", claims_text)

    def test_kernel_handoff_payload_is_empty_without_kernel_target(self):
        source_file = self._write_ix(NON_KERNEL_CONTRACT)
        program = parse_ix(source_file.read_text(encoding="utf-8"), filename=str(source_file))
        result = run_ix(program)
        output_dir = Path(self._tempdir.name) / "non-kernel-bundle"

        EvidenceBundleWriter().write_bundle(
            result,
            source_file=source_file,
            output_dir=output_dir,
            command="unit-test",
        )

        summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        kernel_handoff = json.loads((output_dir / "kernel-handoff.json").read_text(encoding="utf-8"))

        self.assertEqual(summary["counts"]["kernel_handoff_packages"], 0)
        self.assertEqual(kernel_handoff["packages"], [])

    def test_plain_ix_bundle_exports_empty_cognition_contract_artifacts(self):
        source_file = self._write_ix('reply "Plain IX"')
        program = parse_ix(source_file.read_text(encoding="utf-8"), filename=str(source_file))
        result = run_ix(program)
        output_dir = Path(self._tempdir.name) / "plain-bundle"

        EvidenceBundleWriter().write_bundle(
            result,
            source_file=source_file,
            output_dir=output_dir,
            command="unit-test",
        )

        summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        contract = json.loads((output_dir / "contract.json").read_text(encoding="utf-8"))
        obligations = json.loads((output_dir / "obligations.json").read_text(encoding="utf-8"))
        gates = json.loads((output_dir / "falsification-gates.json").read_text(encoding="utf-8"))
        boundaries = json.loads((output_dir / "claim-boundaries.json").read_text(encoding="utf-8"))
        kernel_handoff = json.loads((output_dir / "kernel-handoff.json").read_text(encoding="utf-8"))
        satisfaction = json.loads((output_dir / "satisfaction-report.json").read_text(encoding="utf-8"))
        failure = json.loads((output_dir / "failure-report.json").read_text(encoding="utf-8"))

        self.assertEqual(summary["counts"]["contract_attempts"], 0)
        self.assertEqual(summary["counts"]["contract_obligations"], 0)
        self.assertEqual(summary["counts"]["kernel_handoff_packages"], 0)
        self.assertEqual(summary["counts"]["satisfaction_report_items"], 0)
        self.assertEqual(summary["counts"]["failure_report_gates"], 0)
        self.assertEqual(contract["attempts"], [])
        self.assertEqual(obligations["obligations"], [])
        self.assertEqual(gates["falsification_gates"], [])
        self.assertEqual(boundaries["attempts"], [])
        self.assertEqual(kernel_handoff["packages"], [])
        self.assertEqual(satisfaction["attempts"], [])
        self.assertEqual(failure["attempts"], [])

    def test_cli_evidence_command_lists_cognition_artifacts(self):
        source_file = self._write_ix(COGNITION_CONTRACT)
        output_dir = Path(self._tempdir.name) / "cli-cognition-bundle"

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["evidence", str(source_file), "--out", str(output_dir)])

        self.assertEqual(code, 0)
        output = stdout.getvalue()
        self.assertIn("- contract.json", output)
        self.assertIn("- obligations.json", output)
        self.assertIn("- falsification-gates.json", output)
        self.assertIn("- claim-boundaries.json", output)
        self.assertIn("- kernel-handoff.json", output)
        self.assertIn("- satisfaction-report.json", output)
        self.assertIn("- failure-report.json", output)
        self.assertTrue((output_dir / "kernel-handoff.json").exists())
        self.assertTrue((output_dir / "satisfaction-report.json").exists())
        self.assertTrue((output_dir / "failure-report.json").exists())

    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tempdir.cleanup()

    def _write_ix(self, source: str) -> Path:
        count = len(list(Path(self._tempdir.name).glob("*.ix")))
        path = Path(self._tempdir.name) / f"program_{count}.ix"
        path.write_text(source, encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
