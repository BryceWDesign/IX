import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ix.assurance import assess_ix
from ix.ast import IfStatement
from ix.cli import main
from ix.formatting import format_ix
from ix.parser import parse_ix
from ix.runtime import run_ix


class TestIXConditionals(unittest.TestCase):
    def test_parser_accepts_if_else_statement(self):
        program = parse_ix(
            '''
            if score >= 80 {
                reply "approved"
            } else {
                reply "review"
            }
            '''
        )

        statement = program.statements[0]
        self.assertIsInstance(statement, IfStatement)
        self.assertEqual(statement.condition, "score >= 80")
        self.assertEqual(len(statement.then_statements), 1)
        self.assertEqual(len(statement.else_statements), 1)

    def test_runtime_executes_then_branch(self):
        program = parse_ix(
            '''
            if score >= 80 {
                trace "score accepted"
                reply "approved"
            } else {
                reply "review"
            }
            '''
        )

        result = run_ix(program, inputs={"score": 91})

        self.assertEqual(result.replies, ["approved"])
        self.assertEqual(result.branches[0]["selected_branch"], "then")
        self.assertIn("branch.evaluate", [event.kind for event in result.trace])

    def test_runtime_executes_else_branch(self):
        program = parse_ix(
            '''
            if score >= 80 {
                reply "approved"
            } else {
                trace "score needs review"
                reply "review"
            }
            '''
        )

        result = run_ix(program, inputs={"score": 70})

        self.assertEqual(result.replies, ["review"])
        self.assertEqual(result.branches[0]["selected_branch"], "else")

    def test_branch_inherits_outer_tool_policy(self):
        program = parse_ix(
            '''
            allow tool.upper reason "Safe deterministic built-in tool"
            if should_transform == true {
                call tool.upper as shouted with text = "hello"
                reply shouted
            } else {
                reply "unchanged"
            }
            '''
        )

        result = run_ix(program, inputs={"should_transform": True})

        self.assertEqual(result.replies, ["HELLO"])
        self.assertEqual(result.tool_results[0]["result"], "HELLO")

    def test_formatter_outputs_stable_if_else_source(self):
        program = parse_ix(
            '''
            if score>=80 { reply "approved" } else { reply "review" }
            '''
        )

        self.assertEqual(
            format_ix(program),
            'if score>=80 {\n'
            '    reply "approved"\n'
            '} else {\n'
            '    reply "review"\n'
            '}\n',
        )

    def test_assurance_counts_conditionals(self):
        program = parse_ix(
            '''
            trace "start"
            assert true
            if ready == true {
                reply "ready"
            } else {
                reply "hold"
            }
            '''
        )

        report = assess_ix(program)

        self.assertEqual(report.metrics["conditions"], 1)
        self.assertIn("conditions.present", [check.check_id for check in report.checks])

    def test_cli_trace_includes_branch_record(self):
        ix_file = self._write_ix(
            '''
            if ready == true {
                reply "ready"
            } else {
                reply "hold"
            }
            '''
        )

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["trace", str(ix_file), "--input", "ready=true"])

        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["branches"][0]["selected_branch"], "then")
        self.assertEqual(payload["replies"], ["ready"])

    def _write_ix(self, source: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "program.ix"
        path.write_text(source, encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
