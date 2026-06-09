import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ix.assurance import assess_ix
from ix.cli import main
from ix.formatting import format_ix
from ix.parser import parse_ix


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"

NEGATIVE_EXAMPLES = {
    "cognitionkernel_wave6_missing_obligations.ix": {
        "expected_checks": {
            "cognition_contract.required_obligations.missing",
        },
        "expected_missing": {
            "purpose_discipline",
            "claim_boundary_discipline",
            "human_authority",
            "reality_delta_comparison",
            "evidence_bound_memory_update",
            "future_reasoning_change",
            "cross_domain_transfer_probe",
            "novelty_generality_pressure",
            "long_horizon_planning_trace",
            "uncertainty_assumption_exposure",
            "contradiction_handling",
            "shortcut_reward_hacking_detection",
            "safe_refusal_path",
            "self_improvement_airlock",
            "no_self_certification",
            "falsification_ledger",
            "independent_replay_review",
            "kernel_handoff_package",
        },
    },
    "cognitionkernel_wave6_overclaiming.ix": {
        "expected_checks": {
            "cognition_contract.prohibited_claim_language.present",
            "cognition_contract.required_obligations.missing",
        },
        "expected_missing": {
            "purpose_discipline",
            "claim_boundary_discipline",
            "human_authority",
            "measured_outcome_capture",
            "reality_delta_comparison",
            "evidence_bound_memory_update",
            "future_reasoning_change",
            "cross_domain_transfer_probe",
            "novelty_generality_pressure",
            "long_horizon_planning_trace",
            "uncertainty_assumption_exposure",
            "contradiction_handling",
            "shortcut_reward_hacking_detection",
            "safe_refusal_path",
            "self_improvement_airlock",
            "no_self_certification",
            "falsification_ledger",
            "independent_replay_review",
            "kernel_handoff_package",
        },
    },
    "cognitionkernel_wave6_wrong_handoff.ix": {
        "expected_checks": {
            "cognition_contract.kernel_handoff.missing",
            "cognition_contract.required_obligations.missing",
        },
        "expected_missing": {
            "purpose_discipline",
            "claim_boundary_discipline",
            "human_authority",
            "measured_outcome_capture",
            "reality_delta_comparison",
            "evidence_bound_memory_update",
            "future_reasoning_change",
            "cross_domain_transfer_probe",
            "novelty_generality_pressure",
            "long_horizon_planning_trace",
            "uncertainty_assumption_exposure",
            "contradiction_handling",
            "shortcut_reward_hacking_detection",
            "safe_refusal_path",
            "self_improvement_airlock",
            "no_self_certification",
            "falsification_ledger",
            "independent_replay_review",
            "kernel_handoff_package",
        },
    },
    "cognitionkernel_wave6_noncanonical_falsification.ix": {
        "expected_checks": {
            "cognition_contract.obligation_canonical_falsification.missing",
            "cognition_contract.required_obligations.missing",
        },
        "expected_missing": {
            "purpose_discipline",
            "claim_boundary_discipline",
            "human_authority",
            "measured_outcome_capture",
            "reality_delta_comparison",
            "evidence_bound_memory_update",
            "future_reasoning_change",
            "cross_domain_transfer_probe",
            "novelty_generality_pressure",
            "long_horizon_planning_trace",
            "uncertainty_assumption_exposure",
            "contradiction_handling",
            "shortcut_reward_hacking_detection",
            "safe_refusal_path",
            "self_improvement_airlock",
            "no_self_certification",
            "falsification_ledger",
            "independent_replay_review",
            "kernel_handoff_package",
        },
    },
}


class TestIXCognitionNegativeExamples(unittest.TestCase):
    def test_negative_examples_parse_and_format_cleanly(self):
        for example_name in NEGATIVE_EXAMPLES:
            with self.subTest(example=example_name):
                example_file = EXAMPLES_DIR / example_name
                source = example_file.read_text(encoding="utf-8")
                program = parse_ix(source, filename=str(example_file))

                self.assertEqual(format_ix(program), source)

    def test_negative_examples_fail_cognitionkernel_wave6_profile(self):
        for example_name, expectation in NEGATIVE_EXAMPLES.items():
            with self.subTest(example=example_name):
                example_file = EXAMPLES_DIR / example_name
                program = parse_ix(
                    example_file.read_text(encoding="utf-8"),
                    filename=str(example_file),
                )

                report = assess_ix(program, profile="cognitionkernel-wave6")
                check_ids = {check.check_id for check in report.checks}

                self.assertEqual(report.status, "fail")
                self.assertTrue(expectation["expected_checks"].issubset(check_ids))

    def test_negative_examples_report_expected_missing_obligations(self):
        for example_name, expectation in NEGATIVE_EXAMPLES.items():
            with self.subTest(example=example_name):
                example_file = EXAMPLES_DIR / example_name
                program = parse_ix(
                    example_file.read_text(encoding="utf-8"),
                    filename=str(example_file),
                )

                report = assess_ix(program, profile="cognitionkernel-wave6")
                missing_checks = [
                    check
                    for check in report.checks
                    if check.check_id
                    == "cognition_contract.required_obligations.missing"
                ]

                self.assertEqual(len(missing_checks), 1)
                self.assertEqual(
                    set(missing_checks[0].data["missing_obligations"]),
                    expectation["expected_missing"],
                )

    def test_overclaiming_example_reports_prohibited_claim_text(self):
        example_file = EXAMPLES_DIR / "cognitionkernel_wave6_overclaiming.ix"
        program = parse_ix(
            example_file.read_text(encoding="utf-8"),
            filename=str(example_file),
        )

        report = assess_ix(program, profile="cognitionkernel-wave6")
        prohibited_checks = [
            check
            for check in report.checks
            if check.check_id == "cognition_contract.prohibited_claim_language.present"
        ]

        self.assertEqual(len(prohibited_checks), 1)
        self.assertIn(
            "this contract proves agi achieved",
            prohibited_checks[0].data["matched_text"],
        )

    def test_noncanonical_falsification_example_reports_gate_mismatch(self):
        example_file = EXAMPLES_DIR / "cognitionkernel_wave6_noncanonical_falsification.ix"
        program = parse_ix(
            example_file.read_text(encoding="utf-8"),
            filename=str(example_file),
        )

        report = assess_ix(program, profile="cognitionkernel-wave6")
        missing_checks = [
            check
            for check in report.checks
            if check.check_id
            == "cognition_contract.obligation_canonical_falsification.missing"
        ]

        self.assertEqual(len(missing_checks), 1)
        self.assertEqual(missing_checks[0].data["obligation"], "prediction_before_trial")
        self.assertEqual(
            missing_checks[0].data["declared_conditions"],
            ["arbitrary_failure_label"],
        )
        self.assertIn("prediction_missing", missing_checks[0].data["canonical_conditions"])

    def test_negative_examples_fail_closed_through_cli_assure(self):
        for example_name, expectation in NEGATIVE_EXAMPLES.items():
            with self.subTest(example=example_name):
                example_file = EXAMPLES_DIR / example_name
                stdout = io.StringIO()

                with redirect_stdout(stdout):
                    code = main(
                        [
                            "assure",
                            str(example_file),
                            "--profile",
                            "cognitionkernel-wave6",
                            "--json",
                        ]
                    )

                self.assertEqual(code, 2)
                payload = json.loads(stdout.getvalue())
                check_ids = {check["id"] for check in payload["checks"]}

                self.assertEqual(payload["status"], "fail")
                self.assertTrue(expectation["expected_checks"].issubset(check_ids))


if __name__ == "__main__":
    unittest.main()
