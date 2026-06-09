import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from ix.assurance import (
    AssuranceAnalyzer,
    AssuranceProfile,
    AssuranceProfileRegistry,
    assess_ix,
)
from ix.cli import main
from ix.parser import parse_ix


class TestIXAssuranceProfiles(unittest.TestCase):
    def test_default_registry_exposes_experimental_local_profile(self):
        registry = AssuranceProfileRegistry()

        self.assertEqual(registry.names(), ("experimental-local",))
        profile = registry.require("experimental-local")
        self.assertEqual(profile.name, "experimental-local")
        self.assertTrue(profile.require_executable_path)
        self.assertTrue(profile.check_tool_policies)
        self.assertTrue(profile.check_handoff_targets)
        self.assertTrue(profile.allow_runtime_execution)

    def test_assessment_records_selected_profile(self):
        program = parse_ix(
            '''
            trace "domain marker"
            assert true
            require human_approval reason "Review before use"
            '''
        )

        report = assess_ix(program, profile="experimental-local")

        self.assertEqual(report.profile, "experimental-local")
        self.assertEqual(report.checks[0].check_id, "profile.selected")
        self.assertEqual(report.checks[0].data["profile"]["name"], "experimental-local")

    def test_unknown_assurance_profile_fails_closed(self):
        program = parse_ix('trace "x"')

        with self.assertRaisesRegex(ValueError, "Unknown assurance profile"):
            assess_ix(program, profile="unknown-profile")

    def test_custom_profile_can_disable_checks_without_mutating_default_profile(self):
        registry = AssuranceProfileRegistry(
            profiles=(
                AssuranceProfile(
                    name="contract-metadata-only",
                    description="Only validates parser and semantic diagnostics.",
                    require_executable_path=False,
                    check_tool_policies=False,
                    check_handoff_targets=False,
                    check_condition_markers=False,
                    check_assertions=False,
                    check_trace_statements=False,
                    check_human_review=False,
                    allow_runtime_execution=False,
                ),
            )
        )
        analyzer = AssuranceAnalyzer(profile_registry=registry)
        program = parse_ix("agent Empty { on start { } }")

        report = analyzer.assess(program, profile="contract-metadata-only")

        self.assertEqual(report.status, "pass")
        self.assertEqual(report.profile, "contract-metadata-only")
        self.assertEqual([check.check_id for check in report.checks], ["profile.selected"])

    def test_profile_can_disallow_runtime_execution_checks(self):
        registry = AssuranceProfileRegistry(
            profiles=(
                AssuranceProfile(
                    name="no-execute",
                    description="Static-only profile for tests.",
                    allow_runtime_execution=False,
                ),
            )
        )
        analyzer = AssuranceAnalyzer(profile_registry=registry)
        program = parse_ix(
            '''
            trace "domain marker"
            assert true
            require human_approval reason "Review before use"
            '''
        )

        report = analyzer.assess(program, profile="no-execute", execute=True)

        self.assertEqual(report.status, "fail")
        self.assertIn(
            "runtime.execution_not_allowed_by_profile",
            [check.check_id for check in report.checks],
        )

    def test_cli_assure_rejects_unknown_profile(self):
        ix_file = self._write_ix('trace "x"')
        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(["assure", str(ix_file), "--profile", "unknown-profile"])

        self.assertEqual(code, 2)
        self.assertIn("Unknown assurance profile", stderr.getvalue())

    def test_cli_assure_json_includes_profile_selected_check(self):
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
        self.assertEqual(payload["profile"], "experimental-local")
        self.assertEqual(payload["checks"][0]["id"], "profile.selected")

    def _write_ix(self, source: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "program.ix"
        path.write_text(source, encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
