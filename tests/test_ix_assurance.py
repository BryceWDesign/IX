import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ix.assurance import AssuranceAnalyzer, assess_ix
from ix.cli import main
from ix.parser import parse_ix


class TestIXAssurance(unittest.TestCase):
    def test_assurance_passes_policy_gated_traceable_assertive_program(self):
        program = parse_ix(
            '''
            allow tool.upper reason "Safe deterministic built-in tool"
            call tool.upper as shouted with text = "hello"
            assert shouted == "HELLO"
            trace "tool result checked"
            require human_approval reason "Reviewer must approve downstream use"
            '''
        )

        report = assess_ix(program)

        self.assertEqual(report.status, "pass")
        self.assertEqual(report.metrics["tool_calls"], 1)
        self.assertEqual(report.metrics["assertions"], 1)
        self.assertEqual(report.metrics["trace_statements"], 1)
        self.assertIn("tool_policy.allowed", [check.check_id for check in report.checks])

    def test_assurance_fails_tool_without_explicit_allow_policy(self):
        program = parse_ix('call tool.upper as shouted with text = "hello"')

        report = AssuranceAnalyzer().assess(program)

        self.assertEqual(report.status, "fail")
        self.assertIn("tool_policy.not_allowed", [check.check_id for check in report.checks])

    def test_assurance_fails_unknown_tool(self):
        program = parse_ix(
            '''
            allow tool.fake reason "Test policy"
            call tool.fake as value with text = "hello"
            '''
        )

        report = assess_ix(program)

        self.assertEqual(report.status, "fail")
        self.assertIn("tool_policy.unknown_tool", [check.check_id for check in report.checks])

    def test_assurance_fails_missing_handoff_target(self):
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

        report = assess_ix(program)

        self.assertEqual(report.status, "fail")
        self.assertIn("handoff.target_missing", [check.check_id for check in report.checks])

    def test_assurance_can_include_runtime_execution_check(self):
        program = parse_ix(
            '''
            agent Coordinator {
                on start {
                    trace "begin"
                    assert true
                    require human_approval reason "Review before deployment"
                    reply "Ready"
                }
            }
            '''
        )

        report = AssuranceAnalyzer().assess(program, execute=True, agent="Coordinator")

        self.assertEqual(report.status, "pass")
        self.assertIn("runtime.execution_passed", [check.check_id for check in report.checks])

    def test_cli_assure_outputs_json_report(self):
        ix_file = self._write_ix(
            '''
            trace "domain marker"
            assert true
            require human_approval reason "Review before use"
            '''
        )

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["assure", str(ix_file), "--json"])

        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["metrics"]["assertions"], 1)

    def test_cli_assure_returns_nonzero_for_failed_assurance(self):
        ix_file = self._write_ix('call tool.upper as shouted with text = "hello"')

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["assure", str(ix_file)])

        self.assertEqual(code, 2)
        self.assertIn("ASSURANCE FAIL", stdout.getvalue())

    def _write_ix(self, source: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "program.ix"
        path.write_text(source, encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
