import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from ix.cli import main


class TestIXCliCommands(unittest.TestCase):
    def test_check_command_accepts_valid_file(self):
        ix_file = self._write_ix('reply "Ready"')

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["check", str(ix_file)])

        self.assertEqual(code, 0)
        self.assertIn("OK:", stdout.getvalue())

    def test_check_command_rejects_invalid_file(self):
        ix_file = self._write_ix("teleport now")

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["check", str(ix_file)])

        self.assertEqual(code, 2)
        self.assertIn("Unsupported IX statement", stderr.getvalue())

    def test_run_command_executes_top_level_program(self):
        ix_file = self._write_ix(
            '''
            let name = "Bryce"
            print "Hello {name}"
            reply "Ready"
            '''
        )

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["run", str(ix_file)])

        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().splitlines(), ["Hello Bryce", "Ready"])

    def test_run_command_executes_agent_event_with_input(self):
        ix_file = self._write_ix(
            '''
            agent Router {
                on user_message {
                    reply "You said: {input_text}"
                }
            }
            '''
        )

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(
                [
                    "run",
                    str(ix_file),
                    "--agent",
                    "Router",
                    "--event",
                    "user_message",
                    "--input",
                    "input_text=hello",
                ]
            )

        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), "You said: hello")

    def test_trace_command_emits_json_result(self):
        ix_file = self._write_ix(
            '''
            reply "Ready"
            trace "done"
            '''
        )

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["trace", str(ix_file)])

        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["status"], "completed")
        self.assertEqual(payload["replies"], ["Ready"])
        self.assertEqual(payload["trace"][0]["kind"], "run.start")

    def _write_ix(self, source: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "program.ix"
        path.write_text(source, encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
