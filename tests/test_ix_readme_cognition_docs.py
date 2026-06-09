import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"


class TestIXReadmeCognitionDocs(unittest.TestCase):
    def test_readme_documents_locked_cognition_contract_framing(self):
        text = README.read_text(encoding="utf-8")

        self.assertIn(
            "IX writes the governed developmental contract for AGI-candidate attempts.",
            text,
        )
        self.assertIn("That does not mean IX is AGI.", text)
        self.assertIn("It does not mean IX creates AGI.", text)
        self.assertIn("metadata_only_not_executed", text)

    def test_readme_documents_cognition_profile_and_canonical_example(self):
        text = README.read_text(encoding="utf-8")

        self.assertIn("cognitionkernel-wave6", text)
        self.assertIn("examples/cognitionkernel_wave6_contract.ix", text)
        self.assertIn("ix assure examples/cognitionkernel_wave6_contract.ix --profile cognitionkernel-wave6", text)
        self.assertIn("ix evidence examples/cognitionkernel_wave6_contract.ix --out .tmp/cognition-evidence", text)

    def test_readme_documents_required_cognition_obligations(self):
        text = README.read_text(encoding="utf-8")
        required_ids = {
            "purpose_discipline",
            "claim_boundary_discipline",
            "human_authority",
            "prediction_before_trial",
            "measured_outcome_capture",
            "reality_delta_comparison",
            "evidence_bound_memory_update",
            "future_reasoning_change",
            "cross_domain_transfer_probe",
            "novelty_generality_pressure",
            "long_horizon_planning_trace",
            "uncertainty_assumption_exposure",
            "contradiction_handling",
            "shortcut_reward_hacking_detection",
            "safe_refusal_path",
            "self_improvement_airlock",
            "no_self_certification",
            "falsification_ledger",
            "independent_replay_review",
            "kernel_handoff_package",
        }

        for obligation_id in required_ids:
            with self.subTest(obligation_id=obligation_id):
                self.assertIn(obligation_id, text)

    def test_readme_documents_cognition_evidence_artifacts(self):
        text = README.read_text(encoding="utf-8")
        artifact_names = {
            "contract.json",
            "obligations.json",
            "falsification-gates.json",
            "claim-boundaries.json",
            "kernel-handoff.json",
            "satisfaction-report.json",
            "failure-report.json",
        }

        for artifact_name in artifact_names:
            with self.subTest(artifact_name=artifact_name):
                self.assertIn(artifact_name, text)

    def test_readme_preserves_anti_overclaim_boundaries(self):
        text = README.read_text(encoding="utf-8")

        self.assertIn("> IX is AGI.", text)
        self.assertIn("> IX creates AGI.", text)
        self.assertIn("> IX proves AGI.", text)
        self.assertIn("> IX certifies AGI-candidate success.", text)
        self.assertIn("> IX executes downstream cognition obligations.", text)
        self.assertIn("> IX lets a model approve itself.", text)


if __name__ == "__main__":
    unittest.main()
