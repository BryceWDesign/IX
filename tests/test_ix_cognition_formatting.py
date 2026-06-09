import unittest

from ix.formatting import format_ix
from ix.parser import parse_ix


class TestIXCognitionFormatting(unittest.TestCase):
    def test_formats_cognition_attempt_contract(self):
        program = parse_ix(
            '''
            attempt wave6_measured_cognition { purpose "Test measured correction"
            non_goal "Do not claim AGI"
            claim_boundary "Research candidate only"
            require human_approval reason "Human review required"
            handoff_contract IX-CognitionKernel schema ix.cognition.contract.v1
            obligation prediction_before_trial { evidence_required prediction_record
            falsify_if prediction_missing }
            obligation no_self_certification { evidence_required claim_boundary_record
            falsify_if system_self_certifies } }
            '''
        )

        self.assertEqual(
            format_ix(program),
            "\n".join(
                [
                    "attempt wave6_measured_cognition {",
                    "    purpose \"Test measured correction\"",
                    "    non_goal \"Do not claim AGI\"",
                    "    claim_boundary \"Research candidate only\"",
                    "    require human_approval reason \"Human review required\"",
                    "    handoff_contract IX-CognitionKernel schema ix.cognition.contract.v1",
                    "",
                    "    obligation prediction_before_trial {",
                    "        evidence_required prediction_record",
                    "        falsify_if prediction_missing",
                    "    }",
                    "",
                    "    obligation no_self_certification {",
                    "        evidence_required claim_boundary_record",
                    "        falsify_if system_self_certifies",
                    "    }",
                    "}",
                    "",
                ]
            ),
        )

    def test_formats_handoff_contract_without_schema(self):
        program = parse_ix(
            '''
            attempt wave6 {
                handoff_contract IX-CognitionKernel
            }
            '''
        )

        self.assertEqual(
            format_ix(program),
            "attempt wave6 {\n"
            "    handoff_contract IX-CognitionKernel\n"
            "}\n",
        )

    def test_preserves_blank_line_between_top_level_attempt_blocks(self):
        program = parse_ix(
            '''
            attempt first { purpose "one" }
            attempt second { purpose "two" }
            '''
        )

        self.assertEqual(
            format_ix(program),
            "attempt first {\n"
            "    purpose \"one\"\n"
            "}\n"
            "\n"
            "attempt second {\n"
            "    purpose \"two\"\n"
            "}\n",
        )


if __name__ == "__main__":
    unittest.main()
