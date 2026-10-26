"""Offline probe checks: no model downloads required."""
import copy
import json
import unittest

from scripts.model_capability_probe import (
    FIXTURE, base_evidence, critique_from_gate,
    diagnostic_report, validate_cases,
)

CASES = validate_cases(json.loads(FIXTURE.read_text(encoding="utf-8")))


class ModelCapabilityProbeTests(unittest.TestCase):
    def test_frozen_cases_have_distinct_real_record_ids(self):
        self.assertEqual(len(CASES), 2)
        self.assertEqual({x["paper"]["id"] for x in CASES},
                         {"42380812", "42802541"})

    def test_both_cases_get_identical_task_structure(self):
        a, b = [base_evidence(case) for case in CASES]
        self.assertEqual(a["task"], b["task"])
        self.assertEqual(a["requirements"], b["requirements"])
        self.assertNotEqual(a["source"]["id"], b["source"]["id"])

    def test_critic_detects_missing_actual_source_id(self):
        feedback = critique_from_gate(
            "Could cervical cancer screening sensitivity improve "
            "versus standard Pap smear interpretation?", CASES[0],
        )
        self.assertIn("missing_record_citation",
                      feedback["observed_source_screen_reasons"])
        self.assertEqual(feedback["source_to_verify"]["id"], "42380812")
        self.assertIn("source_identifier_present",
                      feedback["missing_testability_checks"])

    def test_beneficial_revision_detected_without_autocitation(self):
        initial = (
            "Could cervical cancer screening sensitivity improve "
            "compared with standard Pap smear interpretation?"
        )
        revised = initial + " Source: 42380812"
        report = diagnostic_report("fake", CASES[0], initial, revised)
        self.assertTrue(report["source_citation_repaired"])
        self.assertFalse(report["source_citation_lost"])
        self.assertGreater(report["proxy_delta"], 0)
        self.assertFalse(report["scientific_validation"])

    def test_citation_loss_is_visible(self):
        good = "Could cervical cancer screening sensitivity improve versus manual review? 42380812"
        bad = good.replace(" 42380812", "")
        report = diagnostic_report("fake", CASES[0], good, bad)
        self.assertTrue(report["source_citation_lost"])
        self.assertLess(report["proxy_delta"], 0)

    def test_abstaining_is_not_scientific_success(self):
        result = diagnostic_report(
            "fake", CASES[0],
            "ABSTAIN: insufficient evidence",
            "ABSTAIN: insufficient evidence",
        )
        self.assertEqual(result["revision"]["screen"]["decision"],
                         "abstained_insufficient_evidence")
        self.assertFalse(result["scientific_validation"])

    def test_reject_duplicate_or_missing_case_source(self):
        duplicate = copy.deepcopy(CASES)
        duplicate[1]["paper"]["id"] = duplicate[0]["paper"]["id"]
        with self.assertRaises(ValueError):
            validate_cases({"schema_version": 1, "cases": duplicate})
        with self.assertRaises(ValueError):
            validate_cases({"schema_version": 2, "cases": CASES})
        with self.assertRaises(ValueError):
            validate_cases({"schema_version": 1, "cases": [CASES[0]]})


if __name__ == "__main__":
    unittest.main()
