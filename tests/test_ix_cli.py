import io
import unittest
from contextlib import redirect_stdout, redirect_stderr

from ix import __version__
from ix.cli import main


class TestIXCli(unittest.TestCase):
    def test_version_command(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["version"])

        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), __version__)

    def test_about_command(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["about"])

        self.assertEqual(code, 0)
        self.assertIn("canonical agent language", stdout.getvalue())

    def test_no_command_returns_nonzero(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main([])

        self.assertEqual(code, 1)
        self.assertIn("usage:", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
