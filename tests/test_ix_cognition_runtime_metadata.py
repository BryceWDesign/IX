import unittest

from ix.parser import parse_ix
from ix.runtime import run_ix


class TestIXCognitionRuntimeMetadata(unittest.TestCase):
    def test_runtime_extracts_cognition_contract_metadata_without_execution(self):
        program = parse_ix(
            '''
            attempt wave6_measured_cognition {
                purpose "Test measured correction"
                non_goal "Do not claim AGI"
                claim_boundary "Research candidate only"
                require human_approval reason "Human review required"
                handoff_contract IX-CognitionKernel schema ix.cognition.contract.v1

                obligation prediction_before_trial {
                    evidence_required prediction_record
                    falsify_if prediction_missing
                }
            }
            '''
        )

        result = run_ix(program)

        self.assertEqual(result.status, "completed")
        self.assertEqual(result.outputs, [])
        self.assertEqual(result.replies, [])
        self.assertEqual(result.approvals_required, [])
        self.assertEqual(result.contract_metadata["runtime_semantics"], "metadata_only_not_executed")
        self.assertEqual(result.contract_metadata["counts"]["attempts"], 1)
        self.assertEqual(result.contract_metadata["counts"]["obligations"], 1)
        self.assertEqual(result.contract_metadata["counts"]["evidence_requirements"], 1)
        self.assertEqual(result.contract_metadata["counts"]["falsification_gates"], 1)

        attempt = result.contract_metadata["attempts"][0]
        self.assertEqual(attempt["name"], "wave6_measured_cognition")
        self.assertEqual(attempt["purpose"], ["Test measured correction"])
        self.assertEqual(attempt["non_goals"], ["Do not claim AGI"])
        self.assertEqual(attempt["claim_boundaries"], ["Research candidate only"])
        self.assertEqual(attempt["human_approval_required"], ["Human review required"])
        self.assertEqual(
            attempt["handoff_contracts"],
            [
                {
                    "target": "IX-CognitionKernel",
                    "schema": "ix.cognition.contract.v1",
                    "source": {
                        "filename": "<memory>",
                        "line": 7,
                        "column": 17,
                    },
                }
            ],
        )
        self.assertEqual(
            attempt["obligations"],
            [
                {
                    "id": "prediction_before_trial",
                    "source": {
                        "filename": "<memory>",
                        "line": 9,
                        "column": 17,
                    },
                    "evidence_required": ["prediction_record"],
                    "falsify_if": ["prediction_missing"],
                }
            ],
        )

        trace_kinds = [event.kind for event in result.trace]
        self.assertEqual(trace_kinds, ["run.start", "contract.metadata", "run.complete"])

    def test_runtime_keeps_contract_metadata_separate_from_executable_behavior(self):
        program = parse_ix(
            '''
            attempt wave6_measured_cognition {
                purpose "Test measured correction"
                non_goal "Do not claim AGI"
                claim_boundary "Research candidate only"
                require human_approval reason "Human review required"
                handoff_contract IX-CognitionKernel schema ix.cognition.contract.v1

                obligation prediction_before_trial {
                    evidence_required prediction_record
                    falsify_if prediction_missing
                }
            }

            reply "Executable path still works"
            '''
        )

        result = run_ix(program)

        self.assertEqual(result.replies, ["Executable path still works"])
        self.assertEqual(result.approvals_required, [])
        self.assertEqual(result.contract_metadata["counts"]["attempts"], 1)
        self.assertIn("contract_metadata", result.to_dict())
        self.assertEqual(
            [event.kind for event in result.trace],
            ["run.start", "contract.metadata", "reply", "run.complete"],
        )

    def test_runtime_reports_empty_contract_metadata_for_plain_ix_programs(self):
        program = parse_ix(
            '''
            reply "Plain IX"
            assert true
            '''
        )

        result = run_ix(program)

        self.assertEqual(result.replies, ["Plain IX"])
        self.assertEqual(result.contract_metadata["counts"]["attempts"], 0)
        self.assertEqual(result.contract_metadata["attempts"], [])
        self.assertNotIn("contract.metadata", [event.kind for event in result.trace])


if __name__ == "__main__":
    unittest.main()
