import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ix.cli import main
from ix.evidence import EvidenceBundleWriter
from ix.parser import parse_ix
from ix.runtime import run_ix


class TestIXEvidenceBundle(unittest.TestCase):
    def test_evidence_writer_creates_reviewable_bundle_files(self):
        source_file = self._write_ix(
            '''
            allow tool.upper reason "Safe deterministic built-in tool"
            call tool.upper as shouted with text = "hello"
            reply shouted
            require human_approval reason "Reviewer must approve final use"
            '''
        )
        program = parse_ix(source_file.read_text(encoding="utf-8"), filename=str(source_file))
        result = run_ix(program)
        output_dir = Path(self._tempdir.name) / "bundle"

        bundle = EvidenceBundleWriter().write_bundle(
            result,
            source_file=source_file,
            output_dir=output_dir,
            command="unit-test",
        )

        relative_files = set(bundle.relative_files())
        self.assertIn("manifest.json", relative_files)
        self.assertIn("summary.json", relative_files)
        self.assertIn("trace.json", relative_files)
        self.assertIn("policies.json", relative_files)
        self.assertIn("tool-results.json", relative_files)
        self.assertIn("approvals-required.json", relative_files)
        self.assertIn("assurance-claims.md", relative_files)
        self.assertIn("limitations.md", relative_files)

        manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
        summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        tool_results = json.loads((output_dir / "tool-results.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["bundle_type"], "ix.execution.evidence")
        self.assertEqual(summary["status"], "completed")
        self.assertEqual(summary["counts"]["tool_results"], 1)
        self.assertEqual(tool_results[0]["result"], "HELLO")
        self.assertIn(
            "does not certify",
            (output_dir / "assurance-claims.md").read_text(encoding="utf-8"),
        )

    def test_cli_evidence_command_writes_bundle(self):
        source_file = self._write_ix(
            '''
            agent Coordinator {
                on start {
                    send Reviewer.review as verdict with item = "request"
                    reply "Final: {verdict}"
                }
            }

            agent Reviewer {
                on review {
                    reply "approved {item}"
                }
            }
            '''
        )
        output_dir = Path(self._tempdir.name) / "cli-bundle"

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(
                [
                    "evidence",
                    str(source_file),
                    "--agent",
                    "Coordinator",
                    "--out",
                    str(output_dir),
                ]
            )

        self.assertEqual(code, 0)
        self.assertIn("EVIDENCE BUNDLE WRITTEN:", stdout.getvalue())
        self.assertTrue((output_dir / "manifest.json").exists())
        self.assertTrue((output_dir / "handoffs.json").exists())

        handoffs = json.loads((output_dir / "handoffs.json").read_text(encoding="utf-8"))
        self.assertEqual(handoffs[0]["target_agent"], "Reviewer")
        self.assertEqual(handoffs[0]["output_value"], "approved request")

    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tempdir.cleanup()

    def _write_ix(self, source: str) -> Path:
        path = Path(self._tempdir.name) / f"program_{len(list(Path(self._tempdir.name).glob('*.ix')))}.ix"
        path.write_text(source, encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
