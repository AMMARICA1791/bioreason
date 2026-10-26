"""Offline solo-vs-council comparisons, including negative and reversal cases."""
import unittest
from bioreason.comparison import (
    evaluate_candidate, compare_solo_to_council,
)

PAPERS = [
    {"title": "Cervical cancer deep learning screening with a control group",
     "id": "PMC42", "source": "PMC", "abstract": "Screening sensitivity and specificity."},
    {"title": "Retinal fundus imaging for glaucoma detection",
     "id": "PMC43", "source": "PMC"},
]


def turns(first, last):
    return {"turns": [
        {"role": "Inventor", "round": 1, "response": first},
        {"role": "Inventor", "round": 2, "response": last},
    ]}


class ComparisonTests(unittest.TestCase):
    def test_identical_scoring_when_same_candidate_in_different_arms(self):
        good = (
            "Could cervical cancer screening sensitivity improve compared with "
            "standard care? PMC42"
        )
        evidence = compare_solo_to_council(good, turns(good, good), PAPERS)
        self.assertEqual(evidence["outcomes"]["solo_to_last_proxy_delta"], 0)
        self.assertEqual(evidence["outcomes"]["first_to_last_proxy_delta"], 0)
        self.assertFalse(evidence["outcomes"]["first_to_last_changed"])
        self.assertEqual(evidence["arms"]["solo"]["proxy_score"], 6)
        self.assertFalse(evidence["scientific_validation"])

    def test_improved_citation_and_question_must_be_measured(self):
        weak = "What are some AI applications in healthcare?"
        good = (
            "Could cervical cancer detection sensitivity improve compared with "
            "standard care? PMC42"
        )
        report = compare_solo_to_council(weak, turns(weak, good), PAPERS)
        self.assertGreater(report["outcomes"]["solo_to_last_proxy_delta"], 0)
        self.assertEqual(report["outcomes"]["last_scientific_gate"], "tentative_only")
        self.assertFalse(report["scientific_validation"])

    def test_regression_is_reported_not_hidden(self):
        weak = "What are some AI applications?"
        good = (
            "Could cervical cancer detection specificity improve compared with "
            "standard care? PMC42"
        )
        report = compare_solo_to_council(good, turns(good, weak), PAPERS)
        self.assertLess(report["outcomes"]["solo_to_last_proxy_delta"], 0)
        self.assertEqual(report["outcomes"]["last_scientific_gate"], "hold_for_independent_review")

    def test_cross_disease_bridge_cannot_score_as_tentative(self):
        mixed = (
            "Could cervical cancer diagnosis improve versus standard care "
            "using glaucoma fundus images? PMC42 PMC43"
        )
        report = evaluate_candidate(mixed, PAPERS)
        self.assertFalse(report["checks"]["no_blocking_reason"])
        self.assertIn("unsupported_cross_topic_bridge", report["screen"]["reason_codes"])

    def test_invalid_and_incomplete_inputs_refused(self):
        with self.assertRaises(TypeError):
            evaluate_candidate(None, PAPERS)
        with self.assertRaises(ValueError):
            compare_solo_to_council("sample", {"turns": []}, PAPERS)
        with self.assertRaises(ValueError):
            compare_solo_to_council(
                "sample", {"turns": [{"role": "Inventor", "response": "sample"}]}, PAPERS
            )


if __name__ == "__main__":
    unittest.main()
