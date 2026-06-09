import unittest
from dataclasses import FrozenInstanceError

from ix import (
    AttemptBlock,
    ClaimBoundaryStatement,
    CognitionContractStatement,
    EvidenceRequirementStatement,
    FalsifyIfStatement,
    HandoffContractStatement,
    NonGoalStatement,
    ObligationBlock,
    Program,
    PurposeStatement,
)
from ix.errors import SourceSpan


SPAN = SourceSpan("test.ix", 1, 1)


class TestIXCognitionAst(unittest.TestCase):
    def test_cognition_contract_nodes_are_immutable_statements(self):
        purpose = PurposeStatement(span=SPAN, text="measure reality-corrected future reasoning")

        self.assertIsInstance(purpose, CognitionContractStatement)
        with self.assertRaises(FrozenInstanceError):
            purpose.text = "changed"  # type: ignore[misc]

    def test_attempt_block_can_hold_declarative_contract_statements(self):
        obligation = ObligationBlock(
            span=SPAN,
            identifier="prediction_before_trial",
            statements=(
                EvidenceRequirementStatement(span=SPAN, artifact="prediction_record"),
                FalsifyIfStatement(span=SPAN, condition="prediction_missing"),
            ),
        )
        attempt = AttemptBlock(
            span=SPAN,
            name="wave6_measured_cognition",
            statements=(
                PurposeStatement(span=SPAN, text="test measured cognition loop"),
                NonGoalStatement(span=SPAN, text="do not claim AGI"),
                ClaimBoundaryStatement(span=SPAN, text="research candidate only"),
                obligation,
                HandoffContractStatement(
                    span=SPAN,
                    target="IX-CognitionKernel",
                    schema_name="ix.cognition.contract.v1",
                ),
            ),
        )
        program = Program(span=SPAN, statements=(attempt,))

        self.assertEqual(program.statements[0], attempt)
        self.assertEqual(attempt.name, "wave6_measured_cognition")
        self.assertEqual(attempt.statements[0].text, "test measured cognition loop")
        self.assertEqual(obligation.identifier, "prediction_before_trial")
        self.assertEqual(obligation.statements[0].artifact, "prediction_record")
        self.assertEqual(obligation.statements[1].condition, "prediction_missing")
        self.assertEqual(attempt.statements[-1].target, "IX-CognitionKernel")
        self.assertEqual(attempt.statements[-1].schema_name, "ix.cognition.contract.v1")


if __name__ == "__main__":
    unittest.main()
