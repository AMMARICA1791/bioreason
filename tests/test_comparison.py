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

    def test_topic_exists_but_is_not_cited_cannot_get_grounding_point(self):
        response = "Could cervical cancer detection sensitivity improve?"
        evaluated = evaluate_candidate(response, PAPERS)
        self.assertTrue(evaluated["checks"]["contains_question"])
        self.assertFalse(evaluated["checks"]["source_identifier_present"])
        self.assertFalse(evaluated["checks"]["direct_topic_evidence"])
        self.assertFalse(evaluated["checks"]["no_blocking_reason"])
        self.assertEqual(evaluated["screen"]["decision"], "hold_for_independent_review")

    def test_detects_plural_detection_rates_in_real_model_question(self):
        response = (
            "What is the relationship between cervical cancer AI screening "
            "and traditional methods, and how does this affect detection rates? "
            "Source ID: PMC42"
        )
        score = evaluate_candidate(response, PAPERS)
        self.assertTrue(score["checks"]["measurable_endpoint_mentioned"])
        self.assertEqual(score["proxy_score"], 6)

    def test_keeps_grounded_solo_when_council_loses_citation(self):
        solo = (
            "Could cervical cancer screening detection rates improve compared "
            "with traditional practice? Source: PMC42"
        )
        ungrounded = (
            "Could cervical cancer screening detection rates improve compared "
            "with traditional practice?"
        )
        report = compare_solo_to_council(
            solo, turns(ungrounded, ungrounded), PAPERS
        )
        self.assertEqual(report["selection"]["source"], "solo")
        self.assertEqual(report["selection"]["candidate"], solo)
        self.assertEqual(
            report["selection"]["status"], "tentative_human_review_only"
        )
        self.assertFalse(report["selection"]["scientific_validation"])
        self.assertLess(report["outcomes"]["solo_to_last_proxy_delta"], 0)

    def test_promotes_council_only_with_strict_screened_improvement(self):
        weak_solo = (
            "Could cervical cancer screening improve? PMC42"
        )
        better = (
            "Could cervical cancer screening specificity improve compared "
            "with traditional methods? PMC42"
        )
        result = compare_solo_to_council(
            weak_solo, turns(weak_solo, better), PAPERS
        )
        self.assertEqual(result["selection"]["source"], "council_last")
        self.assertEqual(result["selection"]["candidate"], better)
        self.assertTrue(result["selection"]["council_beats_solo_proxy"])
        self.assertFalse(result["scientific_validation"])

    def test_never_selects_unsupported_interdisciplinary_claim(self):
        invalid = (
            "Could cervical cancer screening accuracy improve through "
            "glaucoma retinal photos? PMC42 PMC43"
        )
        result = compare_solo_to_council(
            invalid, turns(invalid, invalid), PAPERS
        )
        self.assertEqual(result["selection"]["source"], "none")
        self.assertIsNone(result["selection"]["candidate"])
        self.assertEqual(
            result["selection"]["status"],
            "no_candidate_supported_by_screen",
        )

    def test_equal_tentative_quality_prefers_solo(self):
        solo = "Could cervical cancer sensitivity improve versus control? PMC42"
        council = "Can cervical cancer sensitivity improve versus control? PMC42"
        result = compare_solo_to_council(
            solo, turns(council, council), PAPERS
        )
        self.assertEqual(result["selection"]["source"], "solo")
        self.assertEqual(result["outcomes"]["solo_to_last_proxy_delta"], 0)

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
