import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from ix.cli import main


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"
CANONICAL_EXAMPLE = EXAMPLES_DIR / "cognitionkernel_wave6_contract.ix"

NEGATIVE_EXAMPLE_EXPECTATIONS = {
    "cognitionkernel_wave6_missing_obligations.ix": (
        "cognition_contract.required_obligations.missing",
    ),
    "cognitionkernel_wave6_overclaiming.ix": (
        "cognition_contract.prohibited_claim_language.present",
        "cognition_contract.required_obligations.missing",
    ),
    "cognitionkernel_wave6_wrong_handoff.ix": (
        "cognition_contract.kernel_handoff.missing",
        "cognition_contract.required_obligations.missing",
    ),
    "cognitionkernel_wave6_noncanonical_falsification.ix": (
        "cognition_contract.obligation_canonical_falsification.missing",
        "cognition_contract.required_obligations.missing",
    ),
}

COGNITION_ARTIFACTS = {
    "contract.json",
    "obligations.json",
    "falsification-gates.json",
    "claim-boundaries.json",
    "kernel-handoff.json",
    "satisfaction-report.json",
    "failure-report.json",
}


class TestIXCognitionCliRegression(unittest.TestCase):
    def test_cli_about_and_version_remain_available(self):
        about_stdout = io.StringIO()
        with redirect_stdout(about_stdout):
            about_code = main(["about"])

        self.assertEqual(about_code, 0)
        self.assertIn("IX", about_stdout.getvalue())
        self.assertIn("audit-first", about_stdout.getvalue())

        version_stdout = io.StringIO()
        with redirect_stdout(version_stdout):
            version_code = main(["version"])

        self.assertEqual(version_code, 0)
        self.assertTrue(version_stdout.getvalue().strip())

    def test_cli_run_trace_and_test_keep_cognition_contract_metadata_only(self):
        run_stdout = io.StringIO()
        with redirect_stdout(run_stdout):
            run_code = main(["run", str(CANONICAL_EXAMPLE)])

        self.assertEqual(run_code, 0)
        self.assertEqual(run_stdout.getvalue(), "")

        trace_stdout = io.StringIO()
        with redirect_stdout(trace_stdout):
            trace_code = main(["trace", str(CANONICAL_EXAMPLE)])

        self.assertEqual(trace_code, 0)
        trace_payload = json.loads(trace_stdout.getvalue())
        self.assertEqual(trace_payload["outputs"], [])
        self.assertEqual(trace_payload["replies"], [])
        self.assertEqual(trace_payload["approvals_required"], [])
        self.assertEqual(trace_payload["contract_metadata"]["counts"]["attempts"], 1)
        self.assertEqual(trace_payload["contract_metadata"]["counts"]["obligations"], 20)
        self.assertEqual(
            trace_payload["contract_metadata"]["runtime_semantics"],
            "metadata_only_not_executed",
        )
        self.assertEqual(
            [event["kind"] for event in trace_payload["trace"]],
            ["run.start", "contract.metadata", "run.complete"],
        )

        test_stdout = io.StringIO()
        with redirect_stdout(test_stdout):
            test_code = main(["test", str(CANONICAL_EXAMPLE)])

        self.assertEqual(test_code, 0)
        self.assertIn("PASS: 0 assertion(s), 3 trace event(s)", test_stdout.getvalue())

    def test_cli_assure_text_mode_passes_canonical_cognition_contract(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(
                [
                    "assure",
                    str(CANONICAL_EXAMPLE),
                    "--profile",
                    "cognitionkernel-wave6",
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("ASSURANCE PASS", output)
        self.assertIn("PROFILE: cognitionkernel-wave6", output)
        self.assertIn("cognition_contract.required_obligations.present", output)
        self.assertIn("cognition_contract.obligations.canonical", output)
        self.assertIn("cognition_contract.agi_claim_restriction.present", output)
        self.assertIn("cognition_contract.research_boundary.present", output)
        self.assertIn("cognition_contract.prohibited_claim_language.absent", output)
        self.assertIn(
            "cognition_contract.obligation_canonical_falsification.present",
            output,
        )

    def test_cli_assure_text_mode_fails_negative_cognition_examples(self):
        for example_name, expected_checks in NEGATIVE_EXAMPLE_EXPECTATIONS.items():
            with self.subTest(example=example_name):
                stdout = io.StringIO()
                example_file = EXAMPLES_DIR / example_name

                with redirect_stdout(stdout):
                    code = main(
                        [
                            "assure",
                            str(example_file),
                            "--profile",
                            "cognitionkernel-wave6",
                        ]
                    )

                output = stdout.getvalue()
                self.assertEqual(code, 2)
                self.assertIn("ASSURANCE FAIL", output)
                self.assertIn("PROFILE: cognitionkernel-wave6", output)
                for expected_check in expected_checks:
                    self.assertIn(expected_check, output)

    def test_cli_assure_json_mode_reports_profile_specific_separation(self):
        cognition_stdout = io.StringIO()
        with redirect_stdout(cognition_stdout):
            cognition_code = main(
                [
                    "assure",
                    str(CANONICAL_EXAMPLE),
                    "--profile",
                    "cognitionkernel-wave6",
                    "--json",
                ]
            )

        self.assertEqual(cognition_code, 0)
        cognition_payload = json.loads(cognition_stdout.getvalue())
        cognition_check_ids = {check["id"] for check in cognition_payload["checks"]}
        self.assertEqual(cognition_payload["status"], "pass")
        self.assertIn(
            "cognition_contract.required_obligations.present",
            cognition_check_ids,
        )

        local_stdout = io.StringIO()
        with redirect_stdout(local_stdout):
            local_code = main(
                [
                    "assure",
                    str(CANONICAL_EXAMPLE),
                    "--profile",
                    "experimental-local",
                    "--json",
                ]
            )

        self.assertEqual(local_code, 2)
        local_payload = json.loads(local_stdout.getvalue())
        local_check_ids = {check["id"] for check in local_payload["checks"]}
        self.assertEqual(local_payload["profile"], "experimental-local")
        self.assertEqual(local_payload["status"], "fail")
        self.assertIn("program.no_executable_path", local_check_ids)
        self.assertNotIn(
            "cognition_contract.required_obligations.present",
            local_check_ids,
        )
        self.assertNotIn(
            "cognition_contract.required_obligations.missing",
            local_check_ids,
        )

    def test_cli_evidence_exports_manifested_cognition_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "canonical-cognition-evidence"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                code = main(
                    [
                        "evidence",
                        str(CANONICAL_EXAMPLE),
                        "--out",
                        str(output_dir),
                    ]
                )

            self.assertEqual(code, 0)
            output = stdout.getvalue()
            self.assertIn("EVIDENCE BUNDLE WRITTEN", output)

            for artifact_name in COGNITION_ARTIFACTS:
                with self.subTest(artifact=artifact_name):
                    self.assertIn(f"- {artifact_name}", output)
                    self.assertTrue((output_dir / artifact_name).exists())

            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
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

            self.assertTrue(COGNITION_ARTIFACTS.issubset(set(manifest["artifact_files"])))
            self.assertEqual(summary["counts"]["contract_attempts"], 1)
            self.assertEqual(summary["counts"]["contract_obligations"], 20)
            self.assertEqual(summary["counts"]["kernel_handoff_packages"], 1)
            self.assertEqual(summary["counts"]["satisfaction_report_items"], 20)
            self.assertEqual(summary["counts"]["failure_report_gates"], 20)
            self.assertEqual(kernel_handoff["packages"][0]["target"], "IX-CognitionKernel")
            self.assertEqual(satisfaction["status"], "not_evaluated")
            self.assertEqual(failure["status"], "not_evaluated")

    def test_cli_unknown_cognition_profile_still_fails_closed_on_stderr(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(
                [
                    "assure",
                    str(CANONICAL_EXAMPLE),
                    "--profile",
                    "not-a-profile",
                ]
            )

        self.assertEqual(code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("IX assure failed", stderr.getvalue())
        self.assertIn("Unknown assurance profile", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
