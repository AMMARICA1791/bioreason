"""Council tests require no network or paid services."""
import copy
import unittest
from bioreason.council import run_council, verify_chain


PAPERS = [
    {"title": "Protein folding methods", "id": "A", "source": "SYNTHETIC", "doi": ""},
    {"title": "Protein folding analysis", "id": "B", "source": "SYNTHETIC", "doi": ""},
]


class CouncilTests(unittest.TestCase):
    def test_eight_roles_execute(self):
        output = run_council("protein folding", PAPERS)
        self.assertEqual(set(output["results"]), {
            "Scout", "Analyst", "Inventor", "Critic",
            "Validator", "Builder", "Auditor", "Coordinator",
        })
        self.assertTrue(output["audit_passed"])

    def test_hash_chain(self):
        output = run_council("protein folding", PAPERS)
        self.assertTrue(verify_chain(output["messages"]))
        self.assertEqual(len(output["messages"]), 8)

    def test_tamper_detection(self):
        output = run_council("protein folding", PAPERS)
        messages = copy.deepcopy(output["messages"])
        messages[2]["payload"]["recurring_title_terms"] = []
        self.assertFalse(verify_chain(messages))

    def test_reject_invalid_input(self):
        with self.assertRaises(ValueError):
            run_council("", PAPERS)
        with self.assertRaises(ValueError):
            run_council("query", [{"title": 123}])

    def test_no_false_scientific_validation(self):
        output = run_council("protein folding", PAPERS)
        self.assertEqual(output["results"]["Validator"]["verified_findings"], 0)
        self.assertIn("not independent LLMs", output["disclosure"])


if __name__ == "__main__":
    unittest.main()
