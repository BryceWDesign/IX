import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ix.assurance import AssuranceProfileRegistry, assess_ix
from ix.cli import main
from ix.cognition import cognition_obligation_ids, require_cognition_obligation
from ix.parser import parse_ix


def build_cognition_contract(
    obligation_ids: tuple[str, ...] | None = None,
    *,
    purpose: str = "Test whether measured reality corrects future reasoning",
    non_goal: str = "Do not claim AGI",
    claim_boundary: str = "Research candidate only",
    human_review: str = "Human review required before advancement",
    handoff_target: str = "IX-CognitionKernel",
    falsification_overrides: dict[str, str] | None = None,
) -> str:
    selected_obligations = obligation_ids or cognition_obligation_ids()
    overrides = falsification_overrides or {}
    lines = [
        "attempt wave6_measured_cognition {",
        f'    purpose "{purpose}"',
        f'    non_goal "{non_goal}"',
        f'    claim_boundary "{claim_boundary}"',
        f'    require human_approval reason "{human_review}"',
        f"    handoff_contract {handoff_target} schema ix.cognition.contract.v1",
        "",
    ]

    for obligation_id in selected_obligations:
        definition = require_cognition_obligation(obligation_id)
        falsification_condition = overrides.get(
            obligation_id,
            definition.falsification_conditions[0],
        )
        lines.extend(
            [
                f"    obligation {obligation_id} {{",
                f"        evidence_required {definition.evidence_artifacts[0]}",
                f"        falsify_if {falsification_condition}",
                "    }",
                "",
            ]
        )

    lines.append("}")
    return "\n".join(lines)


VALID_COGNITION_CONTRACT = build_cognition_contract()


class TestIXCognitionAssuranceProfile(unittest.TestCase):
    def test_registry_exposes_cognitionkernel_wave6_profile(self):
        registry = AssuranceProfileRegistry()

        self.assertEqual(
            registry.names(),
            ("cognitionkernel-wave6", "experimental-local"),
        )
        profile = registry.require("cognitionkernel-wave6")
        self.assertEqual(profile.name, "cognitionkernel-wave6")
        self.assertTrue(profile.require_non_empty_program)
        self.assertFalse(profile.require_executable_path)
        self.assertFalse(profile.allow_runtime_execution)
        self.assertFalse(profile.check_tool_policies)
        self.assertFalse(profile.check_handoff_targets)
        self.assertFalse(profile.check_assertions)
        self.assertFalse(profile.check_trace_statements)
        self.assertFalse(profile.check_human_review)
        self.assertTrue(profile.check_cognition_contract)
        self.assertIn("does not certify AGI", profile.description)

    def test_cognition_profile_requires_non_empty_program(self):
        report = assess_ix(parse_ix(""), profile="cognitionkernel-wave6")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "fail")
        self.assertEqual(report.profile, "cognitionkernel-wave6")
        self.assertIn("profile.selected", check_ids)
        self.assertIn("program.empty", check_ids)
        self.assertIn("cognition_contract.attempt_missing", check_ids)
        self.assertNotIn("program.no_executable_path", check_ids)

    def test_cognition_profile_requires_attempt_contract_not_loose_statements(self):
        report = assess_ix(parse_ix('trace "static contract marker"'), profile="cognitionkernel-wave6")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "fail")
        self.assertIn("program.non_empty", check_ids)
        self.assertIn("cognition_contract.attempt_missing", check_ids)
        self.assertNotIn("program.executable_path", check_ids)
        self.assertNotIn("assertions.missing", check_ids)
        self.assertNotIn("trace_statements.present", check_ids)

    def test_cognition_profile_accepts_complete_canonical_contract(self):
        program = parse_ix(VALID_COGNITION_CONTRACT)

        report = assess_ix(program, profile="cognitionkernel-wave6")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "pass")
        self.assertEqual(report.metrics["attempts"], 1)
        self.assertEqual(report.metrics["obligations"], 20)
        self.assertEqual(report.metrics["purposes"], 1)
        self.assertEqual(report.metrics["non_goals"], 1)
        self.assertEqual(report.metrics["claim_boundaries"], 1)
        self.assertEqual(report.metrics["approvals_required"], 1)
        self.assertEqual(report.metrics["handoff_contracts"], 1)
        self.assertEqual(report.metrics["evidence_requirements"], 20)
        self.assertEqual(report.metrics["falsification_gates"], 20)
        self.assertIn("cognition_contract.attempt_present", check_ids)
        self.assertIn("cognition_contract.purpose.present", check_ids)
        self.assertIn("cognition_contract.non_goal.present", check_ids)
        self.assertIn("cognition_contract.claim_boundary.present", check_ids)
        self.assertIn("cognition_contract.human_review.present", check_ids)
        self.assertIn("cognition_contract.agi_claim_restriction.present", check_ids)
        self.assertIn("cognition_contract.research_boundary.present", check_ids)
        self.assertIn("cognition_contract.prohibited_claim_language.absent", check_ids)
        self.assertIn("cognition_contract.handoff_contract.present", check_ids)
        self.assertIn("cognition_contract.kernel_handoff.present", check_ids)
        self.assertIn("cognition_contract.obligations.present", check_ids)
        self.assertIn("cognition_contract.required_obligations.present", check_ids)
        self.assertIn("cognition_contract.obligations.canonical", check_ids)
        self.assertIn("cognition_contract.obligation_evidence.present", check_ids)
        self.assertIn("cognition_contract.obligation_falsification.present", check_ids)
        self.assertIn(
            "cognition_contract.obligation_canonical_falsification.present",
            check_ids,
        )

    def test_cognition_profile_fails_missing_core_contract_parts(self):
        program = parse_ix(
            '''
            attempt wave6_measured_cognition {
                purpose "Test measured correction"
                obligation prediction_before_trial {
                    evidence_required prediction_record
                }
            }
            '''
        )

        report = assess_ix(program, profile="cognitionkernel-wave6")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "fail")
        self.assertIn("cognition_contract.non_goal.missing", check_ids)
        self.assertIn("cognition_contract.claim_boundary.missing", check_ids)
        self.assertIn("cognition_contract.human_review.missing", check_ids)
        self.assertIn("cognition_contract.agi_claim_restriction.missing", check_ids)
        self.assertIn("cognition_contract.research_boundary.missing", check_ids)
        self.assertIn("cognition_contract.handoff_contract.missing", check_ids)
        self.assertIn("cognition_contract.required_obligations.missing", check_ids)
        self.assertIn("cognition_contract.obligation_falsification.missing", check_ids)
        self.assertIn(
            "cognition_contract.obligation_canonical_falsification.missing",
            check_ids,
        )

    def test_cognition_profile_fails_missing_required_obligations(self):
        incomplete_ids = tuple(
            obligation_id
            for obligation_id in cognition_obligation_ids()
            if obligation_id != "future_reasoning_change"
        )
        program = parse_ix(build_cognition_contract(incomplete_ids))

        report = assess_ix(program, profile="cognitionkernel-wave6")
        check_ids = {check.check_id for check in report.checks}
        missing_checks = [
            check
            for check in report.checks
            if check.check_id == "cognition_contract.required_obligations.missing"
        ]

        self.assertEqual(report.status, "fail")
        self.assertIn("cognition_contract.required_obligations.missing", check_ids)
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("future_reasoning_change", missing_checks[0].data["missing_obligations"])

    def test_cognition_profile_fails_unknown_obligation_ids(self):
        program = parse_ix(
            build_cognition_contract(cognition_obligation_ids() + ("custom_gap_label",))
        )

        report = assess_ix(program, profile="cognitionkernel-wave6")
        check_ids = {check.check_id for check in report.checks}
        unknown_checks = [
            check
            for check in report.checks
            if check.check_id == "cognition_contract.obligations.unknown"
        ]

        self.assertEqual(report.status, "fail")
        self.assertIn("cognition_contract.obligations.unknown", check_ids)
        self.assertEqual(len(unknown_checks), 1)
        self.assertIn("custom_gap_label", unknown_checks[0].data["unknown_obligations"])

    def test_cognition_profile_fails_noncanonical_falsification_gate(self):
        program = parse_ix(
            build_cognition_contract(
                falsification_overrides={
                    "prediction_before_trial": "arbitrary_failure_label",
                }
            )
        )

        report = assess_ix(program, profile="cognitionkernel-wave6")
        check_ids = {check.check_id for check in report.checks}
        missing_checks = [
            check
            for check in report.checks
            if check.check_id
            == "cognition_contract.obligation_canonical_falsification.missing"
        ]

        self.assertEqual(report.status, "fail")
        self.assertIn(
            "cognition_contract.obligation_canonical_falsification.missing",
            check_ids,
        )
        self.assertEqual(len(missing_checks), 1)
        self.assertEqual(missing_checks[0].data["obligation"], "prediction_before_trial")
        self.assertEqual(
            missing_checks[0].data["declared_conditions"],
            ["arbitrary_failure_label"],
        )
        self.assertIn("prediction_missing", missing_checks[0].data["canonical_conditions"])

    def test_cognition_profile_fails_missing_agi_claim_restriction(self):
        program = parse_ix(
            build_cognition_contract(
                non_goal="Do not skip review",
            )
        )

        report = assess_ix(program, profile="cognitionkernel-wave6")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "fail")
        self.assertIn("cognition_contract.agi_claim_restriction.missing", check_ids)
        self.assertIn("cognition_contract.research_boundary.present", check_ids)

    def test_cognition_profile_fails_missing_research_candidate_boundary(self):
        program = parse_ix(
            build_cognition_contract(
                claim_boundary="Operational deployment allowed",
            )
        )

        report = assess_ix(program, profile="cognitionkernel-wave6")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "fail")
        self.assertIn("cognition_contract.agi_claim_restriction.present", check_ids)
        self.assertIn("cognition_contract.research_boundary.missing", check_ids)

    def test_cognition_profile_fails_prohibited_agi_certification_language(self):
        program = parse_ix(
            build_cognition_contract(
                purpose="This contract proves AGI achieved",
                claim_boundary="Research candidate only",
            )
        )

        report = assess_ix(program, profile="cognitionkernel-wave6")
        check_ids = {check.check_id for check in report.checks}
        prohibited_checks = [
            check
            for check in report.checks
            if check.check_id == "cognition_contract.prohibited_claim_language.present"
        ]

        self.assertEqual(report.status, "fail")
        self.assertIn("cognition_contract.prohibited_claim_language.present", check_ids)
        self.assertEqual(len(prohibited_checks), 1)
        self.assertIn(
            "this contract proves agi achieved",
            prohibited_checks[0].data["matched_text"],
        )

    def test_cognition_profile_allows_negative_agi_language(self):
        program = parse_ix(
            build_cognition_contract(
                purpose="This is not AGI and does not certify AGI",
                non_goal="Do not certify AGI",
                claim_boundary="Research candidate only",
            )
        )

        report = assess_ix(program, profile="cognitionkernel-wave6")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "pass")
        self.assertIn("cognition_contract.agi_claim_restriction.present", check_ids)
        self.assertIn("cognition_contract.prohibited_claim_language.absent", check_ids)

    def test_cognition_profile_fails_wrong_handoff_target(self):
        program = parse_ix(build_cognition_contract(handoff_target="OtherKernel"))

        report = assess_ix(program, profile="cognitionkernel-wave6")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "fail")
        self.assertIn("cognition_contract.handoff_contract.present", check_ids)
        self.assertIn("cognition_contract.kernel_handoff.missing", check_ids)

    def test_cognition_profile_blocks_runtime_execution(self):
        program = parse_ix(VALID_COGNITION_CONTRACT)

        report = assess_ix(program, profile="cognitionkernel-wave6", execute=True)
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "fail")
        self.assertIn("runtime.execution_not_allowed_by_profile", check_ids)

    def test_cli_assure_json_can_select_cognition_profile(self):
        ix_file = self._write_ix(VALID_COGNITION_CONTRACT)
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            code = main(
                [
                    "assure",
                    str(ix_file),
                    "--profile",
                    "cognitionkernel-wave6",
                    "--json",
                ]
            )

        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        check_ids = {check["id"] for check in payload["checks"]}
        self.assertEqual(payload["profile"], "cognitionkernel-wave6")
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["metrics"]["attempts"], 1)
        self.assertEqual(payload["metrics"]["obligations"], 20)
        self.assertIn("profile.selected", check_ids)
        self.assertIn("program.non_empty", check_ids)
        self.assertIn("cognition_contract.attempt_present", check_ids)
        self.assertIn("cognition_contract.required_obligations.present", check_ids)
        self.assertIn("cognition_contract.prohibited_claim_language.absent", check_ids)
        self.assertIn(
            "cognition_contract.obligation_canonical_falsification.present",
            check_ids,
        )

    def test_cli_assure_execute_fails_closed_for_cognition_profile(self):
        ix_file = self._write_ix(VALID_COGNITION_CONTRACT)
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            code = main(
                [
                    "assure",
                    str(ix_file),
                    "--profile",
                    "cognitionkernel-wave6",
                    "--execute",
                ]
            )

        self.assertEqual(code, 2)
        self.assertIn("ASSURANCE FAIL", stdout.getvalue())
        self.assertIn("runtime.execution_not_allowed_by_profile", stdout.getvalue())

    def _write_ix(self, source: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "program.ix"
        path.write_text(source, encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
