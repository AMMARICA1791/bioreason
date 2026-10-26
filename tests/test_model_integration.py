import unittest
from unittest.mock import patch
from bioreason.council import run_council, verify_chain

PAPERS = [{"title": "Protein folding methods", "id": "1", "source": "SYNTHETIC"}, {"title": "Protein folding analysis", "id": "2", "source": "SYNTHETIC"}]

class IntegrationTests(unittest.TestCase):
    @patch("bioreason.council.ask_model")
    def test_reasoning_handoffs(self, mock):
        mock.side_effect = lambda role, evidence: {"role": role, "candidate": "tentative", "status": "unverified"}
        result = run_council("protein", PAPERS, model_roles=("Analyst", "Inventor", "Critic"))
        self.assertEqual([c.args[0] for c in mock.call_args_list], ["Analyst", "Inventor", "Critic"])
        self.assertTrue(verify_chain(result["messages"]))
        self.assertEqual(result["results"]["Validator"]["verified_findings"], 0)
        self.assertEqual(set(result["results"]["Builder"]["model_candidates"]), {"Analyst", "Inventor", "Critic"})
        self.assertEqual(result["results"]["Builder"]["model_candidates"]["Inventor"]["status"], "unverified")

    @patch("bioreason.council.ask_model")
    def test_offline_default(self, mock):
        self.assertTrue(run_council("protein", PAPERS)["audit_passed"])
        mock.assert_not_called()

if __name__ == "__main__":
    unittest.main()
