import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from ix.ast import ToolCallStatement
from ix.cli import main
from ix.formatting import format_ix
from ix.parser import parse_ix
from ix.runtime import IXRuntimeError, run_ix
from ix.tools import BuiltInToolRegistry


class TestIXGovernedTools(unittest.TestCase):
    def test_parser_accepts_tool_call(self):
        program = parse_ix('call tool.echo as echoed with message = "Hello"')

        self.assertIsInstance(program.statements[0], ToolCallStatement)
        self.assertEqual(program.statements[0].tool_name, "tool.echo")
        self.assertEqual(program.statements[0].output_name, "echoed")
        self.assertEqual(program.statements[0].arguments[0].name, "message")

    def test_runtime_requires_explicit_allow_policy_for_tool_calls(self):
        program = parse_ix('call tool.echo as echoed with message = "Hello"')

        with self.assertRaises(IXRuntimeError):
            run_ix(program)

    def test_runtime_executes_allowed_tool_and_records_trace(self):
        program = parse_ix(
            '''
            allow tool.echo reason "Safe deterministic built-in tool"
            call tool.echo as echoed with message = "Hello {name}"
            reply echoed
            '''
        )

        result = run_ix(program, inputs={"name": "Bryce"})

        self.assertEqual(result.variables["echoed"], "Hello Bryce")
        self.assertEqual(result.replies, ["Hello Bryce"])
        self.assertEqual(result.tool_results[0]["tool"], "tool.echo")
        self.assertIn("tool.call", [event.kind for event in result.trace])

    def test_deny_policy_overrides_allow_policy(self):
        program = parse_ix(
            '''
            allow tool.* reason "Allow safe tools"
            deny tool.echo reason "Echo disabled in this scenario"
            call tool.echo as echoed with message = "Hello"
            '''
        )

        with self.assertRaises(IXRuntimeError):
            run_ix(program)

    def test_format_supports_tool_calls(self):
        program = parse_ix('call tool.upper as shouted with text="hello"')

        self.assertEqual(
            format_ix(program),
            'call tool.upper as shouted with text = "hello"\n',
        )

    def test_cli_trace_includes_tool_results(self):
        ix_file = self._write_ix(
            '''
            allow tool.upper reason "Safe deterministic built-in tool"
            call tool.upper as shouted with text = "hello"
            reply shouted
            '''
        )

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["trace", str(ix_file)])

        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["tool_results"][0]["result"], "HELLO")
        self.assertEqual(payload["replies"], ["HELLO"])

    def test_cli_run_fails_closed_on_denied_tool(self):
        ix_file = self._write_ix('call tool.echo as echoed with message = "Hello"')

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["run", str(ix_file)])

        self.assertEqual(code, 2)
        self.assertIn("Tool call denied by policy", stderr.getvalue())

    def test_registry_exposes_deterministic_builtin_tools(self):
        registry = BuiltInToolRegistry()

        self.assertIn("tool.sha256", registry.names())
        self.assertEqual(registry.invoke("tool.length", {"text": "abcd"}), 4)

    def _write_ix(self, source: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "program.ix"
        path.write_text(source, encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
