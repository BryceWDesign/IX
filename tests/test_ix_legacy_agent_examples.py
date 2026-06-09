import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ix.cli import main
from ix.parser import parse_ix


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = REPO_ROOT / "agent"


class TestIXLegacyAgentExamples(unittest.TestCase):
    def test_legacy_genesis_files_use_canonical_ix_syntax(self):
        for example_file in sorted(AGENT_DIR.glob("genesis*.ix")):
            with self.subTest(example=example_file.name):
                source = example_file.read_text(encoding="utf-8")
                parse_ix(source, filename=str(example_file))

                check_stdout = io.StringIO()
                with redirect_stdout(check_stdout):
                    check_code = main(["check", str(example_file)])

                self.assertEqual(check_code, 0)
                self.assertIn("OK:", check_stdout.getvalue())

                format_stdout = io.StringIO()
                with redirect_stdout(format_stdout):
                    format_code = main(["format", str(example_file), "--check"])

                self.assertEqual(format_code, 0)
                self.assertIn("OK:", format_stdout.getvalue())

    def test_legacy_genesis_files_run_as_demonstration_only_contracts(self):
        expected_outputs = {
            "genesis1.ix": "IX-GENESIS-I boot contract ready",
            "genesis2.ix": "IX-GENESIS-II mirror contract ready",
        }

        for example_name, expected_output in expected_outputs.items():
            with self.subTest(example=example_name):
                run_stdout = io.StringIO()
                with redirect_stdout(run_stdout):
                    run_code = main(["run", str(AGENT_DIR / example_name)])

                self.assertEqual(run_code, 0)
                self.assertEqual(run_stdout.getvalue().strip(), expected_output)


if __name__ == "__main__":
    unittest.main()
