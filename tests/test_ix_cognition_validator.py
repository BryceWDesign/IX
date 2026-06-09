import unittest

from ix.parser import parse_ix
from ix.validator import validate_ix


class TestIXCognitionValidator(unittest.TestCase):
    def test_accepts_structurally_valid_cognition_contract(self):
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

        self.assertEqual(validate_ix(program), [])

    def test_rejects_cognition_statements_outside_required_blocks(self):
        invalid_sources = {
            "purpose": 'purpose "loose purpose"',
            "non_goal": 'non_goal "loose boundary"',
            "claim_boundary": 'claim_boundary "loose claim"',
            "handoff_contract": "handoff_contract IX-CognitionKernel",
            "evidence_required": "evidence_required prediction_record",
            "falsify_if": "falsify_if prediction_missing",
            "obligation": "obligation prediction_before_trial { falsify_if missing }",
        }

        for label, source in invalid_sources.items():
            with self.subTest(label=label):
                diagnostics = validate_ix(parse_ix(source))
                self.assertTrue(diagnostics)

    def test_rejects_attempt_inside_agent_or_if_block(self):
        invalid_sources = {
            "agent": 'agent Router { attempt wave6 { purpose "x" } }',
            "if": 'if ready { attempt wave6 { purpose "x" } }',
            "nested": 'attempt outer { attempt inner { purpose "x" } }',
        }

        for label, source in invalid_sources.items():
            with self.subTest(label=label):
                diagnostics = validate_ix(parse_ix(source))
                messages = [diagnostic.message for diagnostic in diagnostics]
                self.assertIn("Attempt blocks must be declared at top level", messages)

    def test_rejects_executable_statements_inside_attempt(self):
        program = parse_ix(
            '''
            attempt wave6 {
                purpose "x"
                reply "not allowed in declarative contract"
            }
            '''
        )

        diagnostics = validate_ix(program)

        self.assertEqual(len(diagnostics), 1)
        self.assertIn("Unsupported statement inside attempt block", diagnostics[0].message)

    def test_rejects_unsupported_obligation_children(self):
        invalid_sources = {
            "purpose": 'attempt wave6 { obligation x { purpose "not here" } }',
            "nested_obligation": "attempt wave6 { obligation x { obligation y { falsify_if z } } }",
            "reply": 'attempt wave6 { obligation x { reply "not here" } }',
        }

        for label, source in invalid_sources.items():
            with self.subTest(label=label):
                diagnostics = validate_ix(parse_ix(source))
                messages = [diagnostic.message for diagnostic in diagnostics]
                self.assertIn(
                    "Only evidence_required and falsify_if are supported inside obligations",
                    messages,
                )

    def test_rejects_empty_attempt_and_empty_obligation(self):
        invalid_sources = {
            "attempt": "attempt wave6 { }",
            "obligation": "attempt wave6 { obligation prediction_before_trial { } }",
        }

        for label, source in invalid_sources.items():
            with self.subTest(label=label):
                diagnostics = validate_ix(parse_ix(source))
                self.assertTrue(
                    any("cannot be empty" in diagnostic.message for diagnostic in diagnostics)
                )

    def test_rejects_duplicate_attempts_obligations_and_evidence(self):
        program = parse_ix(
            '''
            attempt wave6 {
                obligation prediction_before_trial {
                    evidence_required prediction_record
                    evidence_required prediction_record
                    falsify_if prediction_missing
                }
                obligation prediction_before_trial {
                    falsify_if duplicate
                }
            }
            attempt wave6 {
                purpose "duplicate"
            }
            '''
        )

        diagnostics = validate_ix(program)
        messages = [diagnostic.message for diagnostic in diagnostics]

        self.assertIn("Duplicate evidence requirement: prediction_record", messages)
        self.assertIn("Duplicate obligation identifier: prediction_before_trial", messages)
        self.assertIn("Duplicate attempt name: wave6", messages)

    def test_rejects_empty_string_contract_text(self):
        invalid_sources = {
            "purpose": 'attempt wave6 { purpose "" }',
            "non_goal": 'attempt wave6 { non_goal "   " }',
            "claim_boundary": 'attempt wave6 { claim_boundary "" }',
            "approval": 'attempt wave6 { require human_approval reason "" }',
            "falsify_if": 'attempt wave6 { obligation x { falsify_if "" } }',
        }

        for label, source in invalid_sources.items():
            with self.subTest(label=label):
                diagnostics = validate_ix(parse_ix(source))
                self.assertTrue(diagnostics)
                self.assertTrue(
                    any("cannot be empty" in diagnostic.message for diagnostic in diagnostics)
                )


if __name__ == "__main__":
    unittest.main()
