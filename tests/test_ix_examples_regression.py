import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from ix.cli import main
from ix.parser import parse_ix


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"


class TestIXExamplesRegression(unittest.TestCase):
    def test_all_canonical_examples_parse_check_and_format(self):
        example_files = sorted(EXAMPLES_DIR.glob("*.ix"))

        self.assertGreaterEqual(len(example_files), 5)

        for example_file in example_files:
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

    def test_hello_example_runs_traces_tests_and_assures(self):
        example_file = EXAMPLES_DIR / "hello.ix"

        run_stdout = io.StringIO()
        with redirect_stdout(run_stdout):
            run_code = main(["run", str(example_file)])

        self.assertEqual(run_code, 0)
        self.assertEqual(run_stdout.getvalue().strip(), "Hello from IX")

        trace_stdout = io.StringIO()
        with redirect_stdout(trace_stdout):
            trace_code = main(["trace", str(example_file)])

        self.assertEqual(trace_code, 0)
        trace_payload = json.loads(trace_stdout.getvalue())
        self.assertEqual(trace_payload["status"], "completed")
        self.assertEqual(trace_payload["replies"], ["Hello from IX"])
        self.assertIn("run.complete", [event["kind"] for event in trace_payload["trace"]])

        test_stdout = io.StringIO()
        with redirect_stdout(test_stdout):
            test_code = main(["test", str(example_file)])

        self.assertEqual(test_code, 0)
        self.assertIn("PASS: 1 assertion", test_stdout.getvalue())

        assure_stdout = io.StringIO()
        with redirect_stdout(assure_stdout):
            assure_code = main(["assure", str(example_file), "--execute"])

        self.assertEqual(assure_code, 0)
        self.assertIn("ASSURANCE PASS", assure_stdout.getvalue())

    def test_branching_example_records_selected_branch(self):
        example_file = EXAMPLES_DIR / "branching_review.ix"

        approved_stdout = io.StringIO()
        with redirect_stdout(approved_stdout):
            approved_code = main(["run", str(example_file), "--input", "score=91"])

        self.assertEqual(approved_code, 0)
        self.assertEqual(approved_stdout.getvalue().strip(), "approved")

        review_stdout = io.StringIO()
        with redirect_stdout(review_stdout):
            review_code = main(["run", str(example_file), "--input", "score=70"])

        self.assertEqual(review_code, 0)
        self.assertEqual(review_stdout.getvalue().strip(), "human review required")

        trace_stdout = io.StringIO()
        with redirect_stdout(trace_stdout):
            trace_code = main(["trace", str(example_file), "--input", "score=70"])

        self.assertEqual(trace_code, 0)
        trace_payload = json.loads(trace_stdout.getvalue())
        self.assertEqual(trace_payload["branches"][0]["selected_branch"], "else")
        self.assertEqual(trace_payload["replies"], ["human review required"])

    def test_governed_tool_example_records_policy_and_tool_result(self):
        example_file = EXAMPLES_DIR / "governed_tool.ix"

        run_stdout = io.StringIO()
        with redirect_stdout(run_stdout):
            run_code = main(["run", str(example_file)])

        self.assertEqual(run_code, 0)
        self.assertEqual(run_stdout.getvalue().strip(), "EVIDENCE-BOUND AGENT CONTRACT")

        trace_stdout = io.StringIO()
        with redirect_stdout(trace_stdout):
            trace_code = main(["trace", str(example_file)])

        self.assertEqual(trace_code, 0)
        trace_payload = json.loads(trace_stdout.getvalue())
        self.assertEqual(trace_payload["tool_results"][0]["tool"], "tool.upper")
        self.assertEqual(trace_payload["tool_results"][0]["result"], "EVIDENCE-BOUND AGENT CONTRACT")
        self.assertEqual(
            trace_payload["approvals_required"],
            ["Reviewer must approve downstream use"],
        )

        assure_stdout = io.StringIO()
        with redirect_stdout(assure_stdout):
            assure_code = main(["assure", str(example_file), "--execute"])

        self.assertEqual(assure_code, 0)
        self.assertIn("ASSURANCE PASS", assure_stdout.getvalue())

    def test_multi_agent_example_orchestrates_and_exports_evidence(self):
        example_file = EXAMPLES_DIR / "multi_agent_review.ix"

        orchestrate_stdout = io.StringIO()
        with redirect_stdout(orchestrate_stdout):
            orchestrate_code = main(["orchestrate", str(example_file), "--agent", "Coordinator"])

        self.assertEqual(orchestrate_code, 0)
        orchestrate_text = orchestrate_stdout.getvalue()
        self.assertIn("ORCHESTRATION COMPLETE: 1 handoff", orchestrate_text)
        self.assertIn(
            "HANDOFF Reviewer.review -> verdict: approved: agent behavior contract",
            orchestrate_text,
        )
        self.assertIn("Final verdict: approved: agent behavior contract", orchestrate_text)

        json_stdout = io.StringIO()
        with redirect_stdout(json_stdout):
            json_code = main(
                [
                    "orchestrate",
                    str(example_file),
                    "--agent",
                    "Coordinator",
                    "--json",
                ]
            )

        self.assertEqual(json_code, 0)
        payload = json.loads(json_stdout.getvalue())
        self.assertEqual(payload["handoffs"][0]["target_agent"], "Reviewer")
        self.assertEqual(payload["handoffs"][0]["target_event"], "review")
        self.assertEqual(payload["variables"]["verdict"], "approved: agent behavior contract")

        with tempfile.TemporaryDirectory() as tempdir:
            bundle_dir = Path(tempdir) / "evidence"

            evidence_stdout = io.StringIO()
            with redirect_stdout(evidence_stdout):
                evidence_code = main(
                    [
                        "evidence",
                        str(example_file),
                        "--agent",
                        "Coordinator",
                        "--out",
                        str(bundle_dir),
                    ]
                )

            self.assertEqual(evidence_code, 0)
            self.assertTrue((bundle_dir / "manifest.json").exists())
            self.assertTrue((bundle_dir / "trace.json").exists())
            self.assertTrue((bundle_dir / "handoffs.json").exists())
            self.assertTrue((bundle_dir / "approvals-required.json").exists())

            manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
            handoffs = json.loads((bundle_dir / "handoffs.json").read_text(encoding="utf-8"))

            self.assertEqual(manifest["bundle_type"], "ix.execution.evidence")
            self.assertEqual(handoffs[0]["output_value"], "approved: agent behavior contract")

    def test_assurance_ready_example_passes_and_handles_both_branches(self):
        example_file = EXAMPLES_DIR / "assurance_ready.ix"

        high_score_stdout = io.StringIO()
        with redirect_stdout(high_score_stdout):
            high_score_code = main(["run", str(example_file), "--input", "score=91"])

        self.assertEqual(high_score_code, 0)
        self.assertEqual(high_score_stdout.getvalue().strip(), "score accepted")

        low_score_stdout = io.StringIO()
        with redirect_stdout(low_score_stdout):
            low_score_code = main(["run", str(example_file), "--input", "score=70"])

        self.assertEqual(low_score_code, 0)
        self.assertEqual(low_score_stdout.getvalue().strip(), "score requires review")

        json_stdout = io.StringIO()
        with redirect_stdout(json_stdout):
            assure_code = main(
                [
                    "assure",
                    str(example_file),
                    "--execute",
                    "--input",
                    "score=91",
                    "--json",
                ]
            )

        self.assertEqual(assure_code, 0)
        report = json.loads(json_stdout.getvalue())
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["metrics"]["conditions"], 1)
        self.assertEqual(report["metrics"]["assertions"], 1)
        self.assertEqual(report["metrics"]["approvals_required"], 1)

    def test_denied_tool_still_fails_closed(self):
        with tempfile.TemporaryDirectory() as tempdir:
            denied_file = Path(tempdir) / "denied.ix"
            denied_file.write_text(
                'call tool.upper as shouted with text = "hello"\n',
                encoding="utf-8",
            )

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = main(["run", str(denied_file)])

        self.assertEqual(code, 2)
        self.assertIn("Tool call denied by policy", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
