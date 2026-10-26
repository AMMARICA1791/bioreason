"""A model that parrots an Inventor must not count as a meaningful Critic."""
import unittest

from bioreason.peer_review import make_review_obligations, assess_critic


class PeerReviewTests(unittest.TestCase):
    def test_missing_citation_generates_explicit_mandatory_objection(self):
        duties = make_review_obligations({
            "decision": "hold_for_independent_review",
            "reason_codes": ["missing_record_citation"],
        })
        self.assertTrue(duties["must_request_direct_source_support"])
        self.assertIn("exact retrieved source ID", duties["specific_challenges"][0])
        self.assertFalse(duties["research_validation"])

    def test_paraphrase_without_challenge_fails_audit(self):
        duties = make_review_obligations({
            "decision": "hold_for_independent_review",
            "reason_codes": ["missing_record_citation"],
        })
        result = assess_critic(
            "Can a deep learning cancer model improve screening accuracy?", duties
        )
        self.assertEqual(result["audit"], "critic_failed_to_challenge")
        self.assertTrue(result["missing_source_challenge"])
        self.assertTrue(result["uncritical_paraphrase"])

    def test_praising_a_paper_is_not_critical_review(self):
        duties = make_review_obligations({
            "decision": "hold_for_independent_review",
            "reason_codes": ["missing_record_citation"],
        })
        result = assess_critic(
            "This paper reviews artificial intelligence in cervical cancer.", duties
        )
        self.assertEqual(result["audit"], "critic_failed_to_challenge")
        # Mentioning "paper" without identifying a source defect is NOT a
        # relevant source challenge under the tightened review audit.
        self.assertTrue(result["missing_source_challenge"])
        self.assertTrue(result["uncritical_paraphrase"])

    def test_precise_source_challenge_is_counted_not_validated(self):
        duties = make_review_obligations({
            "decision": "hold_for_independent_review",
            "reason_codes": ["missing_record_citation"],
        })
        result = assess_critic(
            "BLOCKED: the hypothesis lacks an exact source record ID. "
            "Cite a relevant study or withdraw it.", duties
        )
        self.assertEqual(result["audit"], "challenge_explicit")
        self.assertFalse(result["scientific_validation"])

    def test_cross_topic_requires_an_objection(self):
        duties = make_review_obligations({
            "decision": "hold_for_independent_review",
            "reason_codes": ["unsupported_cross_topic_bridge"],
        })
        self.assertIn("combined disease topics", duties["specific_challenges"][0])
        self.assertEqual(
            assess_critic("Two studies mention different diseases.", duties)["audit"],
            "critic_failed_to_challenge",
        )

    def test_generic_negative_opinion_about_a_paper_is_not_source_review(self):
        duties = make_review_obligations({
            "decision": "hold_for_independent_review",
            "reason_codes": ["missing_record_citation"],
        })
        result = assess_critic(
            "This paper looks interesting but it is not very persuasive.",
            duties,
        )
        self.assertEqual(result["audit"], "critic_failed_to_challenge")
        self.assertTrue(result["missing_source_challenge"])

    def test_doi_id_mismatch_requires_its_own_specific_objection(self):
        duties = make_review_obligations({
            "decision": "hold_for_independent_review",
            "reason_codes": ["doi_record_id_mismatch"],
        })
        self.assertTrue(duties["must_request_direct_source_support"])
        vague = assess_critic(
            "The proposal is BLOCKED because its paper source should be checked.",
            duties,
        )
        self.assertEqual(vague["audit"], "critic_failed_to_challenge")
        exact = assess_critic(
            "BLOCKED: the cited DOI belongs to a different source record "
            "from the stated study ID, so these references do not match.",
            duties,
        )
        self.assertEqual(exact["audit"], "challenge_explicit")
        self.assertFalse(exact["scientific_validation"])

    def test_tentative_candidate_cannot_gain_scientific_validation(self):
        duties = make_review_obligations({
            "decision": "tentative_only", "reason_codes": [],
        })
        result = assess_critic("Exploratory question; further validation needed.", duties)
        self.assertEqual(result["audit"], "no_automatic_criticism_required")
        self.assertFalse(result["scientific_validation"])


if __name__ == "__main__":
    unittest.main()
