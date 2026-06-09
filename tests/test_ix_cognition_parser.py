import unittest

from ix.ast import (
    AttemptBlock,
    ClaimBoundaryStatement,
    EvidenceRequirementStatement,
    FalsifyIfStatement,
    HandoffContractStatement,
    NonGoalStatement,
    ObligationBlock,
    PurposeStatement,
    RequireApprovalStatement,
)
from ix.errors import IXSyntaxError
from ix.parser import parse_ix


class TestIXCognitionParser(unittest.TestCase):
    def test_parse_cognition_attempt_contract(self):
        program = parse_ix(
            '''
            attempt wave6_measured_cognition {
                purpose "Test whether measured reality corrects future reasoning"
                non_goal "Do not claim AGI"
                claim_boundary "Research candidate only"
                require human_approval reason "Human review required before advancement"
                handoff_contract IX-CognitionKernel schema ix.cognition.contract.v1

                obligation prediction_before_trial {
                    evidence_required prediction_record
                    falsify_if prediction_missing
                }
            }
            '''
        )

        self.assertEqual(len(program.statements), 1)
        attempt = program.statements[0]
        self.assertIsInstance(attempt, AttemptBlock)
        self.assertEqual(attempt.name, "wave6_measured_cognition")
        self.assertIsInstance(attempt.statements[0], PurposeStatement)
        self.assertEqual(
            attempt.statements[0].text,
            '"Test whether measured reality corrects future reasoning"',
        )
        self.assertIsInstance(attempt.statements[1], NonGoalStatement)
        self.assertIsInstance(attempt.statements[2], ClaimBoundaryStatement)
        self.assertIsInstance(attempt.statements[3], RequireApprovalStatement)
        self.assertIsInstance(attempt.statements[4], HandoffContractStatement)
        self.assertEqual(attempt.statements[4].target, "IX-CognitionKernel")
        self.assertEqual(attempt.statements[4].schema_name, "ix.cognition.contract.v1")

        obligation = attempt.statements[5]
        self.assertIsInstance(obligation, ObligationBlock)
        self.assertEqual(obligation.identifier, "prediction_before_trial")
        self.assertIsInstance(obligation.statements[0], EvidenceRequirementStatement)
        self.assertEqual(obligation.statements[0].artifact, "prediction_record")
        self.assertIsInstance(obligation.statements[1], FalsifyIfStatement)
        self.assertEqual(obligation.statements[1].condition, "prediction_missing")

    def test_parse_inline_attempt_and_obligation_braces(self):
        program = parse_ix(
            '''
            attempt wave6 { obligation no_self_certification {
                evidence_required claim_boundary_record
                falsify_if system_self_certifies
            } }
            '''
        )

        attempt = program.statements[0]
        self.assertIsInstance(attempt, AttemptBlock)
        self.assertEqual(attempt.name, "wave6")
        self.assertEqual(len(attempt.statements), 1)
        self.assertIsInstance(attempt.statements[0], ObligationBlock)

    def test_parse_handoff_contract_without_schema(self):
        program = parse_ix(
            '''
            attempt wave6 {
                handoff_contract IX-CognitionKernel
            }
            '''
        )

        attempt = program.statements[0]
        self.assertIsInstance(attempt, AttemptBlock)
        handoff = attempt.statements[0]
        self.assertIsInstance(handoff, HandoffContractStatement)
        self.assertEqual(handoff.target, "IX-CognitionKernel")
        self.assertIsNone(handoff.schema_name)

    def test_reject_attempt_missing_opening_brace(self):
        with self.assertRaisesRegex(IXSyntaxError, "Expected .* after attempt block header"):
            parse_ix("attempt wave6")

    def test_reject_obligation_missing_opening_brace(self):
        with self.assertRaisesRegex(IXSyntaxError, "Expected .* after obligation block header"):
            parse_ix(
                '''
                attempt wave6 {
                    obligation prediction_before_trial
                }
                '''
            )

    def test_reject_empty_cognition_statement_tails(self):
        invalid_sources = [
            "purpose",
            "non_goal",
            "claim_boundary",
            "evidence_required",
            "falsify_if",
        ]

        for source in invalid_sources:
            with self.subTest(source=source):
                with self.assertRaises(IXSyntaxError):
                    parse_ix(source)

    def test_reject_invalid_contract_identifiers(self):
        invalid_sources = [
            "attempt 6wave { purpose x }",
            "attempt wave6 { obligation 6prediction { falsify_if missing } }",
            "attempt wave6 { evidence_required bad/path }",
            "attempt wave6 { handoff_contract 6Kernel }",
        ]

        for source in invalid_sources:
            with self.subTest(source=source):
                with self.assertRaises(IXSyntaxError):
                    parse_ix(source)


if __name__ == "__main__":
    unittest.main()
