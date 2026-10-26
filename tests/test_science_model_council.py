"""Prove multidisciplinary council selection never invents scientific success."""
import unittest

from scripts.science_model_council import select_review_candidate

PAPERS = [
    {"doi": "10.1000/materials", "domain": "materials"},
    {"doi": "10.1000/energy", "domain": "energy"},
    {"doi": "10.1000/computing", "domain": "computing"},
]


class ScienceCouncilTests(unittest.TestCase):
    def test_cross_science_papers_only_produce_tentative_review_lead(self):
        solo = "Could a method from 10.1000/materials and 10.1000/energy be tested for cycling durability?"
        weaker = "Could a materials method improve cycling durability?"
        result = select_review_candidate(solo, weaker, weaker, PAPERS)
        self.assertEqual(result["selected_from"], "solo")
        self.assertEqual(result["candidate"], solo)
        self.assertFalse(result["scientific_validation"])
        self.assertFalse(result["novelty_checked"])

    def test_no_citations_no_selected_lead(self):
        question = "Could a new energy storage method improve power stability?"
        result = select_review_candidate(question, question, question, PAPERS)
        self.assertEqual(result["selected_from"], "none")
        self.assertIsNone(result["candidate"])
        self.assertEqual(result["status"], "no_source_grounded_lead")

    def test_first_council_lead_is_not_erased_by_bad_revision(self):
        weak = "Could neuromorphic devices improve photodetectors?"
        good = "Could concepts in 10.1000/materials and 10.1000/computing be tested for latency?"
        result = select_review_candidate(weak, good, weak, PAPERS)
        self.assertEqual(result["selected_from"], "council_initial")
        self.assertEqual(result["candidate"], good)

    def test_one_field_can_yield_a_cautious_testable_research_lead(self):
        one = "Could a new perovskite detector 10.1000/materials improve device sensitivity?"
        result = select_review_candidate(one, one, one, PAPERS)
        self.assertEqual(result["selected_from"], "solo")
        self.assertEqual(result["cited_domains"], ["materials"])
        self.assertFalse(result["cross_domain_evidence"])
        self.assertFalse(result["scientific_validation"])

    def test_fabricated_second_doi_does_not_pass(self):
        bad = "Could 10.1000/materials and 10.1000/fabricated be tested in a comparison?"
        result = select_review_candidate(bad, bad, bad, PAPERS)
        self.assertEqual(result["selected_from"], "none")


if __name__ == "__main__":
    unittest.main()
