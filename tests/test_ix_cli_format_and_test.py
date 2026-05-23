import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from ix.cli import main


class TestIXCliFormatAndTest(unittest.TestCase):
    def test_format_command_prints_normalized_source(self):
        ix_file = self._write_ix('let name="Bryce"\nreply "Hello {name}"')

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["format", str(ix_file)])

        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue(), 'let name = "Bryce"\nreply "Hello {name}"\n')

    def test_format_check_fails_when_file_is_not_formatted(self):
        ix_file = self._write_ix('let name="Bryce"\n')

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["format", str(ix_file), "--check"])

        self.assertEqual(code, 2)
        self.assertIn("is not formatted", stderr.getvalue())

    def test_format_write_rewrites_file(self):
        ix_file = self._write_ix('let name="Bryce"\n')

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["format", str(ix_file), "--write"])

        self.assertEqual(code, 0)
        self.assertEqual(ix_file.read_text(encoding="utf-8"), 'let name = "Bryce"\n')
        self.assertIn("Formatted:", stdout.getvalue())

    def test_test_command_reports_assertions(self):
        ix_file = self._write_ix(
            '''
            let name = "Bryce"
            assert name == "Bryce"
            '''
        )

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["test", str(ix_file)])

        self.assertEqual(code, 0)
        self.assertIn("PASS: 1 assertion", stdout.getvalue())

    def test_test_command_fails_on_failed_assertion(self):
        ix_file = self._write_ix('assert "safe" == "unsafe"')

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["test", str(ix_file)])

        self.assertEqual(code, 2)
        self.assertIn("Assertion failed", stderr.getvalue())

    def _write_ix(self, source: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "program.ix"
        path.write_text(source, encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
