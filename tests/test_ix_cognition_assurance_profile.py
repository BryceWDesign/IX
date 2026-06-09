import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ix.assurance import AssuranceProfileRegistry, assess_ix
from ix.cli import main
from ix.parser import parse_ix


class TestIXCognitionAssuranceProfile(unittest.TestCase):
    def test_registry_exposes_cognitionkernel_wave6_profile(self):
        registry = AssuranceProfileRegistry()

        self.assertEqual(
            registry.names(),
            ("cognitionkernel-wave6", "experimental-local"),
        )
        profile = registry.require("cognitionkernel-wave6")
        self.assertEqual(profile.name, "cognitionkernel-wave6")
        self.assertTrue(profile.require_non_empty_program)
        self.assertFalse(profile.require_executable_path)
        self.assertFalse(profile.allow_runtime_execution)
        self.assertFalse(profile.check_tool_policies)
        self.assertFalse(profile.check_handoff_targets)
        self.assertFalse(profile.check_assertions)
        self.assertFalse(profile.check_trace_statements)
        self.assertFalse(profile.check_human_review)
        self.assertIn("does not certify AGI", profile.description)

    def test_cognition_profile_requires_non_empty_program(self):
        report = assess_ix(parse_ix(""), profile="cognitionkernel-wave6")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "fail")
        self.assertEqual(report.profile, "cognitionkernel-wave6")
        self.assertIn("profile.selected", check_ids)
        self.assertIn("program.empty", check_ids)
        self.assertNotIn("program.no_executable_path", check_ids)

    def test_cognition_profile_runs_static_review_without_executable_runtime_checks(self):
        program = parse_ix('trace "static contract marker"')

        report = assess_ix(program, profile="cognitionkernel-wave6")
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "pass")
        self.assertEqual(report.profile, "cognitionkernel-wave6")
        self.assertIn("profile.selected", check_ids)
        self.assertIn("program.non_empty", check_ids)
        self.assertNotIn("program.executable_path", check_ids)
        self.assertNotIn("assertions.missing", check_ids)
        self.assertNotIn("trace_statements.present", check_ids)

    def test_cognition_profile_blocks_runtime_execution(self):
        program = parse_ix('trace "static contract marker"')

        report = assess_ix(program, profile="cognitionkernel-wave6", execute=True)
        check_ids = {check.check_id for check in report.checks}

        self.assertEqual(report.status, "fail")
        self.assertIn("runtime.execution_not_allowed_by_profile", check_ids)

    def test_cli_assure_json_can_select_cognition_profile(self):
        ix_file = self._write_ix('trace "static contract marker"')
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            code = main(
                [
                    "assure",
                    str(ix_file),
                    "--profile",
                    "cognitionkernel-wave6",
                    "--json",
                ]
            )

        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        check_ids = {check["id"] for check in payload["checks"]}
        self.assertEqual(payload["profile"], "cognitionkernel-wave6")
        self.assertEqual(payload["status"], "pass")
        self.assertIn("profile.selected", check_ids)
        self.assertIn("program.non_empty", check_ids)

    def test_cli_assure_execute_fails_closed_for_cognition_profile(self):
        ix_file = self._write_ix('trace "static contract marker"')
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            code = main(
                [
                    "assure",
                    str(ix_file),
                    "--profile",
                    "cognitionkernel-wave6",
                    "--execute",
                ]
            )

        self.assertEqual(code, 2)
        self.assertIn("ASSURANCE FAIL", stdout.getvalue())
        self.assertIn("runtime.execution_not_allowed_by_profile", stdout.getvalue())

    def _write_ix(self, source: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "program.ix"
        path.write_text(source, encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
