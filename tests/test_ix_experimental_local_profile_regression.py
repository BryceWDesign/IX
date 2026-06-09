import unittest

from ix.assurance import AssuranceAnalyzer, assess_ix
from ix.parser import parse_ix


class TestIXExperimentalLocalProfileRegression(unittest.TestCase):
    def test_experimental_local_preserves_pass_for_policy_gated_program(self):
        program = parse_ix(
            '''
            allow tool.upper reason "Safe deterministic built-in tool"
            call tool.upper as shouted with text = "hello"
            assert shouted == "HELLO"
            trace "tool result checked"
            require human_approval reason "Reviewer must approve downstream use"
            '''
        )

        report = assess_ix(program, profile="experimental-local")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "pass")
        self.assertEqual(report.profile, "experimental-local")
        self.assertEqual(report.metrics["executable_paths"], 5)
        self.assertEqual(report.metrics["tool_calls"], 1)
        self.assertEqual(report.metrics["assertions"], 1)
        self.assertEqual(report.metrics["trace_statements"], 1)
        self.assertEqual(report.metrics["approvals_required"], 1)
        self.assertIn("profile.selected", check_ids)
        self.assertIn("program.executable_path", check_ids)
        self.assertIn("tool_policy.allowed", check_ids)
        self.assertIn("handoff.no_handoffs", check_ids)
        self.assertIn("assertions.present", check_ids)
        self.assertIn("trace_statements.present", check_ids)
        self.assertIn("human_review.present", check_ids)

    def test_experimental_local_preserves_fail_for_ungated_tool_call(self):
        program = parse_ix('call tool.upper as shouted with text = "hello"')

        report = assess_ix(program, profile="experimental-local")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "fail")
        self.assertEqual(report.metrics["tool_calls"], 1)
        self.assertIn("profile.selected", check_ids)
        self.assertIn("program.executable_path", check_ids)
        self.assertIn("tool_policy.not_allowed", check_ids)

    def test_experimental_local_preserves_fail_for_unknown_tool(self):
        program = parse_ix(
            '''
            allow tool.fake reason "Test policy"
            call tool.fake as value with text = "hello"
            trace "tool checked"
            assert true
            '''
        )

        report = assess_ix(program, profile="experimental-local")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "fail")
        self.assertEqual(report.metrics["tool_calls"], 1)
        self.assertIn("profile.selected", check_ids)
        self.assertIn("tool_policy.unknown_tool", check_ids)

    def test_experimental_local_preserves_fail_for_missing_handoff_target(self):
        program = parse_ix(
            '''
            agent Coordinator {
                on start {
                    send Missing.review as verdict with item = "request"
                    trace "sent"
                    assert true
                }
            }
            '''
        )

        report = assess_ix(program, profile="experimental-local")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "fail")
        self.assertEqual(report.metrics["agents"], 1)
        self.assertEqual(report.metrics["events"], 1)
        self.assertEqual(report.metrics["handoffs"], 1)
        self.assertIn("profile.selected", check_ids)
        self.assertIn("program.executable_path", check_ids)
        self.assertIn("handoff.target_missing", check_ids)

    def test_experimental_local_preserves_warn_for_minimal_executable_program(self):
        program = parse_ix('reply "Ready"')

        report = assess_ix(program, profile="experimental-local")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "warn")
        self.assertEqual(report.metrics["executable_paths"], 1)
        self.assertIn("profile.selected", check_ids)
        self.assertIn("program.executable_path", check_ids)
        self.assertIn("tool_policy.no_tool_calls", check_ids)
        self.assertIn("handoff.no_handoffs", check_ids)
        self.assertIn("assertions.missing", check_ids)
        self.assertIn("trace_statements.missing", check_ids)

    def test_experimental_local_preserves_runtime_execution_when_requested(self):
        program = parse_ix(
            '''
            trace "begin"
            assert true
            require human_approval reason "Review before deployment"
            reply "Ready"
            '''
        )

        report = AssuranceAnalyzer().assess(
            program,
            profile="experimental-local",
            execute=True,
        )
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "pass")
        self.assertIn("profile.selected", check_ids)
        self.assertIn("runtime.execution_passed", check_ids)

    def test_profile_selected_check_is_pass_metadata_not_a_warning_or_failure(self):
        program = parse_ix(
            '''
            trace "domain marker"
            assert true
            require human_approval reason "Review before use"
            '''
        )

        report = assess_ix(program, profile="experimental-local")
        selected_checks = [
            check for check in report.checks if check.check_id == "profile.selected"
        ]

        self.assertEqual(len(selected_checks), 1)
        self.assertEqual(selected_checks[0].severity, "pass")
        self.assertEqual(selected_checks[0].data["profile"]["name"], "experimental-local")
        self.assertTrue(selected_checks[0].data["profile"]["allow_runtime_execution"])


if __name__ == "__main__":
    unittest.main()
