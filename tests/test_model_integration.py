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
    def test_all_eight_roles_run_real_adapter_and_handoff(self, mock):
        from bioreason.council import MODEL_ROLES
        mock.side_effect = lambda role, evidence: {
            "role": role,
            "candidate": "tentative " + role,
            "status": "unverified model-generated suggestion",
        }
        output = run_council("protein folding", PAPERS, model_roles=MODEL_ROLES)
        self.assertEqual([call.args[0] for call in mock.call_args_list], list(MODEL_ROLES))
        self.assertEqual(len(output["results"]), 8)
        self.assertTrue(verify_chain(output["messages"]))
        self.assertTrue(output["audit_passed"])
        for role in MODEL_ROLES:
            self.assertEqual(output["results"][role]["model_suggestion"]["role"], role)
        self.assertEqual(output["messages"][1]["payload"]["model_suggestion"]["role"], "Scout")
        self.assertIn("scout", mock.call_args_list[1].args[1])
        self.assertEqual(output["results"]["Validator"]["verified_findings"], 0)
        self.assertFalse("verified" in output["results"]["Coordinator"]["status"])

    @patch("bioreason.council.ask_model")
    def test_offline_default(self, mock):
        self.assertTrue(run_council("protein", PAPERS)["audit_passed"])
        mock.assert_not_called()

if __name__ == "__main__":
    unittest.main()
