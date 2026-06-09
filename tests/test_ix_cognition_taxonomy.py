import unittest

from ix.cognition import (
    CANONICAL_COGNITION_OBLIGATION_MAP,
    CognitionObligation,
    cognition_obligation_ids,
    cognition_obligation_payloads,
    cognition_obligations,
    get_cognition_obligation,
    require_cognition_obligation,
)


class TestIXCognitionTaxonomy(unittest.TestCase):
    def test_canonical_obligation_ids_are_stable_and_unique(self):
        obligation_ids = cognition_obligation_ids()

        self.assertEqual(len(obligation_ids), 20)
        self.assertEqual(len(set(obligation_ids)), len(obligation_ids))
        self.assertEqual(obligation_ids[0], "purpose_discipline")
        self.assertEqual(obligation_ids[-1], "kernel_handoff_package")
        self.assertIn("prediction_before_trial", obligation_ids)
        self.assertIn("no_self_certification", obligation_ids)
        self.assertIn("falsification_ledger", obligation_ids)

    def test_canonical_obligations_have_evidence_and_falsification_semantics(self):
        for obligation in cognition_obligations():
            with self.subTest(identifier=obligation.identifier):
                self.assertIsInstance(obligation, CognitionObligation)
                self.assertTrue(obligation.identifier)
                self.assertTrue(obligation.title)
                self.assertTrue(obligation.purpose)
                self.assertTrue(obligation.evidence_artifacts)
                self.assertTrue(obligation.falsification_conditions)
                self.assertEqual(obligation.identifier, obligation.identifier.strip())
                self.assertNotIn(" ", obligation.identifier)

    def test_obligation_map_is_read_only_lookup(self):
        self.assertEqual(
            CANONICAL_COGNITION_OBLIGATION_MAP["prediction_before_trial"].title,
            "Prediction before trial",
        )
        with self.assertRaises(TypeError):
            CANONICAL_COGNITION_OBLIGATION_MAP["new"] = CognitionObligation(  # type: ignore[index]
                identifier="new",
                title="New",
                purpose="Not allowed",
                evidence_artifacts=("record",),
                falsification_conditions=("missing",),
            )

    def test_get_and_require_obligation(self):
        optional = get_cognition_obligation("reality_delta_comparison")
        required = require_cognition_obligation("reality_delta_comparison")

        self.assertIsNotNone(optional)
        self.assertEqual(optional, required)
        self.assertEqual(required.evidence_artifacts[0], "delta_record")
        self.assertIsNone(get_cognition_obligation("not_real"))
        with self.assertRaisesRegex(ValueError, "Unknown cognition obligation"):
            require_cognition_obligation("not_real")

    def test_obligation_payloads_are_json_serializable_shapes(self):
        payloads = cognition_obligation_payloads(
            ["prediction_before_trial", "no_self_certification"]
        )

        self.assertEqual(
            [payload["id"] for payload in payloads],
            ["prediction_before_trial", "no_self_certification"],
        )
        for payload in payloads:
            with self.subTest(identifier=payload["id"]):
                self.assertEqual(
                    sorted(payload),
                    [
                        "evidence_artifacts",
                        "falsification_conditions",
                        "id",
                        "purpose",
                        "title",
                    ],
                )
                self.assertIsInstance(payload["evidence_artifacts"], list)
                self.assertIsInstance(payload["falsification_conditions"], list)


if __name__ == "__main__":
    unittest.main()
