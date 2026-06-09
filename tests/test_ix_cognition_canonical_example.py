import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ix.assurance import assess_ix
from ix.cli import main
from ix.cognition import cognition_obligation_ids
from ix.evidence import EvidenceBundleWriter
from ix.formatting import format_ix
from ix.parser import parse_ix
from ix.runtime import run_ix


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_FILE = REPO_ROOT / "examples" / "cognitionkernel_wave6_contract.ix"


class TestIXCognitionCanonicalExample(unittest.TestCase):
    def test_canonical_example_parses_and_is_canonically_formatted(self):
        source = EXAMPLE_FILE.read_text(encoding="utf-8")
        program = parse_ix(source, filename=str(EXAMPLE_FILE))

        self.assertEqual(format_ix(program), source)

    def test_canonical_example_passes_cognitionkernel_wave6_profile(self):
        program = parse_ix(
            EXAMPLE_FILE.read_text(encoding="utf-8"),
            filename=str(EXAMPLE_FILE),
        )

        report = assess_ix(program, profile="cognitionkernel-wave6")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "pass")
        self.assertEqual(report.profile, "cognitionkernel-wave6")
        self.assertEqual(report.metrics["attempts"], 1)
        self.assertEqual(report.metrics["obligations"], len(cognition_obligation_ids()))
        self.assertEqual(report.metrics["evidence_requirements"], len(cognition_obligation_ids()))
        self.assertEqual(report.metrics["falsification_gates"], len(cognition_obligation_ids()))
        self.assertIn("cognition_contract.required_obligations.present", check_ids)
        self.assertIn("cognition_contract.obligations.canonical", check_ids)
        self.assertIn("cognition_contract.agi_claim_restriction.present", check_ids)
        self.assertIn("cognition_contract.research_boundary.present", check_ids)
        self.assertIn("cognition_contract.prohibited_claim_language.absent", check_ids)
        self.assertIn("cognition_contract.kernel_handoff.present", check_ids)
        self.assertIn(
            "cognition_contract.obligation_canonical_falsification.present",
            check_ids,
        )

    def test_canonical_example_runtime_exports_metadata_without_execution(self):
        program = parse_ix(
            EXAMPLE_FILE.read_text(encoding="utf-8"),
            filename=str(EXAMPLE_FILE),
        )

        result = run_ix(program)

        self.assertEqual(result.status, "completed")
        self.assertEqual(result.outputs, [])
        self.assertEqual(result.replies, [])
        self.assertEqual(result.approvals_required, [])
        self.assertEqual(
            result.contract_metadata["runtime_semantics"],
            "metadata_only_not_executed",
        )
        self.assertEqual(result.contract_metadata["counts"]["attempts"], 1)
        self.assertEqual(
            result.contract_metadata["counts"]["obligations"],
            len(cognition_obligation_ids()),
        )
        self.assertEqual(
            result.contract_metadata["attempts"][0]["name"],
            "wave6_measured_cognition",
        )
        self.assertEqual(
            [event.kind for event in result.trace],
            ["run.start", "contract.metadata", "run.complete"],
        )

    def test_canonical_example_evidence_bundle_contains_kernel_handoff_and_reports(self):
        program = parse_ix(
            EXAMPLE_FILE.read_text(encoding="utf-8"),
            filename=str(EXAMPLE_FILE),
        )
        result = run_ix(program)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "canonical-cognition-evidence"
            bundle = EvidenceBundleWriter().write_bundle(
                result,
                source_file=EXAMPLE_FILE,
                output_dir=output_dir,
                command="unit-test",
            )

            relative_files = set(bundle.relative_files())
            self.assertIn("contract.json", relative_files)
            self.assertIn("kernel-handoff.json", relative_files)
            self.assertIn("satisfaction-report.json", relative_files)
            self.assertIn("failure-report.json", relative_files)

            summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
            kernel_handoff = json.loads(
                (output_dir / "kernel-handoff.json").read_text(encoding="utf-8")
            )
            satisfaction = json.loads(
                (output_dir / "satisfaction-report.json").read_text(encoding="utf-8")
            )
            failure = json.loads(
                (output_dir / "failure-report.json").read_text(encoding="utf-8")
            )

            self.assertEqual(
                summary["counts"]["contract_obligations"],
                len(cognition_obligation_ids()),
            )
            self.assertEqual(summary["counts"]["kernel_handoff_packages"], 1)
            self.assertEqual(
                summary["counts"]["satisfaction_report_items"],
                len(cognition_obligation_ids()),
            )
            self.assertEqual(
                summary["counts"]["failure_report_gates"],
                len(cognition_obligation_ids()),
            )
            self.assertEqual(kernel_handoff["packages"][0]["target"], "IX-CognitionKernel")
            self.assertFalse(kernel_handoff["packages"][0]["self_certification_allowed"])
            self.assertTrue(kernel_handoff["packages"][0]["human_authority_required"])
            self.assertEqual(
                len(kernel_handoff["packages"][0]["obligations"]),
                len(cognition_obligation_ids()),
            )
            self.assertEqual(satisfaction["status"], "not_evaluated")
            self.assertEqual(failure["status"], "not_evaluated")

    def test_cli_check_format_assure_and_evidence_support_canonical_example(self):
        check_stdout = io.StringIO()
        with redirect_stdout(check_stdout):
            check_code = main(["check", str(EXAMPLE_FILE)])
        self.assertEqual(check_code, 0)
        self.assertIn("OK:", check_stdout.getvalue())

        format_stdout = io.StringIO()
        with redirect_stdout(format_stdout):
            format_code = main(["format", str(EXAMPLE_FILE), "--check"])
        self.assertEqual(format_code, 0)
        self.assertIn("OK:", format_stdout.getvalue())

        assure_stdout = io.StringIO()
        with redirect_stdout(assure_stdout):
            assure_code = main(
                [
                    "assure",
                    str(EXAMPLE_FILE),
                    "--profile",
                    "cognitionkernel-wave6",
                    "--json",
                ]
            )
        self.assertEqual(assure_code, 0)
        assure_payload = json.loads(assure_stdout.getvalue())
        self.assertEqual(assure_payload["status"], "pass")
        self.assertEqual(assure_payload["metrics"]["obligations"], 20)

        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_stdout = io.StringIO()
            output_dir = Path(tmpdir) / "evidence"
            with redirect_stdout(evidence_stdout):
                evidence_code = main(
                    ["evidence", str(EXAMPLE_FILE), "--out", str(output_dir)]
                )

            self.assertEqual(evidence_code, 0)
            self.assertTrue((output_dir / "kernel-handoff.json").exists())
            self.assertTrue((output_dir / "satisfaction-report.json").exists())
            self.assertTrue((output_dir / "failure-report.json").exists())
            self.assertIn("- kernel-handoff.json", evidence_stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
