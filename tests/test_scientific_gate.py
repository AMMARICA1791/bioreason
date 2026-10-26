"""Adversarial regression tests: supported hypotheses vs unsupported bridges."""
import unittest

from bioreason.scientific_gate import assess_candidate

PAPERS = [
    {
        "id": "PMC13650561",
        "source": "PMC",
        "title": "A comprehensive study on cervical cancer diagnosis using deep learning",
        "doi": "10.1000/cervical",
    },
    {
        "id": "PMC13639773",
        "source": "PMC",
        "title": "Code-free machine learning for glaucoma classification from retinal fundus photographs",
        "doi": "10.1000/glaucoma",
    },
    {
        "id": "PMC900",
        "source": "PMC",
        "title": "Artificial intelligence for protein folding prediction",
        "doi": "",
    },
]


class ScientificGateTests(unittest.TestCase):
    def test_known_failure_cross_domain_glaucoma_cervical(self):
        proposal = (
            "Can we enhance cervical cancer diagnosis by improving the "
            "classification of glaucoma images? PMC13650561 PMC13639773"
        )
        result = assess_candidate(proposal, PAPERS)
        self.assertEqual(result["decision"], "hold_for_independent_review")
        self.assertIn("unsupported_cross_topic_bridge", result["reason_codes"])
        self.assertIn("citation_does_not_support_topics", result["reason_codes"])
        self.assertEqual(result["record_ids_covering_all_topics"], [])
        self.assertFalse(result["scientific_validation"])

    def test_anchored_single_topic_survives_with_only_tentative_status(self):
        result = assess_candidate(
            "Could deep learning improve cervical cancer classification? PMC13650561",
            PAPERS,
        )
        self.assertEqual(result["decision"], "tentative_only")
        self.assertEqual(result["record_ids_covering_all_topics"], ["PMC13650561"])
        self.assertFalse(result["scientific_validation"])

    def test_topic_absent_from_records_is_held(self):
        result = assess_candidate(
            "Does tuberculosis increase cervical cancer risk? PMC13650561", PAPERS
        )
        self.assertIn("topic_not_supported_by_retrieved_records", result["reason_codes"])
        self.assertEqual(result["decision"], "hold_for_independent_review")

    def test_fake_record_id_not_accepted(self):
        result = assess_candidate(
            "Does the cervical cancer model improve screening? PMC99999999", PAPERS
        )
        self.assertIn("missing_record_citation", result["reason_codes"])
        self.assertEqual(result["cited_record_ids"], [])

    def test_wrong_real_id_does_not_support_claim(self):
        result = assess_candidate(
            "Does a cervical cancer model improve screening? PMC13639773", PAPERS
        )
        self.assertIn("citation_does_not_support_topics", result["reason_codes"])

    def test_unrecognized_topic_fail_closed_but_no_fabricated_certainty(self):
        result = assess_candidate(
            "Could a previously unknown microbial pathway be investigated? PMC900",
            PAPERS,
        )
        self.assertIn("unassessed_biomedical_topics", result["reason_codes"])
        self.assertEqual(result["coverage"], "limited phrase-based screen, NOT a medical ontology")

    def test_broad_catalogue_question_blocked_even_with_authentic_citation(self):
        result = assess_candidate(
            "What are some applications of AI in cervical cancer care? PMC13650561",
            PAPERS,
        )
        self.assertEqual(result["decision"], "hold_for_independent_review")
        self.assertIn("non_falsifiable_catalogue_question", result["reason_codes"])

    def test_scattered_citation_list_is_not_focused_evidence(self):
        papers = PAPERS + [
            {"id": "PMC901", "title": "Cervical cancer classification"},
            {"id": "PMC902", "title": "Cervical cancer models"},
        ]
        result = assess_candidate(
            "Can cervical cancer diagnosis sensitivity improve? "
            "PMC13650561 PMC13639773 PMC901 PMC902", papers
        )
        self.assertIn("diffuse_evidence_citations", result["reason_codes"])
        self.assertEqual(result["decision"], "hold_for_independent_review")

    def test_clean_abstention_is_safe_without_hallucinated_reference(self):
        result = assess_candidate("ABSTAIN: insufficient evidence", PAPERS)
        self.assertEqual(result["decision"], "abstained_insufficient_evidence")
        self.assertEqual(result["cited_record_ids"], [])
        self.assertFalse(result["scientific_validation"])

    def test_abstention_cannot_hide_fabricated_claims(self):
        result = assess_candidate(
            "ABSTAIN: insufficient evidence; but DOI 10.9999/fabricated proves it",
            PAPERS,
        )
        self.assertEqual(result["decision"], "hold_for_independent_review")
        self.assertIn("doi_not_in_retrieved_records", result["reason_codes"])

    def test_verbatim_square_bracket_template_cannot_pass(self):
        text = (
            "Could [specific method] improve [measurable endpoint] versus "
            "[baseline]? Source: [EXACT paper ID from the given record]"
        )
        result = assess_candidate(text, PAPERS)
        self.assertEqual(result["decision"], "hold_for_independent_review")
        self.assertIn("unresolved_template_placeholders", result["reason_codes"])
        self.assertFalse(result["scientific_validation"])

    def test_verbatim_angle_bracket_template_cannot_pass(self):
        text = (
            "Could <specific intervention> improve cervical cancer screening "
            "sensitivity compared with <baseline>? PMC13650561"
        )
        result = assess_candidate(text, PAPERS)
        self.assertEqual(result["decision"], "hold_for_independent_review")
        self.assertIn("unresolved_template_placeholders", result["reason_codes"])

    def test_inventor_must_ask_an_actual_research_question(self):
        result = assess_candidate(
            "Cervical cancer deep learning is important. PMC13650561", PAPERS
        )
        self.assertEqual(result["decision"], "hold_for_independent_review")
        self.assertIn("no_explicit_testable_question", result["reason_codes"])

    def test_fabricated_doi_blocks_candidate_despite_real_id(self):
        result = assess_candidate(
            "Can cervical cancer diagnosis improve? PMC13650561 DOI 10.9999/fiction",
            PAPERS,
        )
        self.assertIn("doi_not_in_retrieved_records", result["reason_codes"])
        self.assertEqual(result["decision"], "hold_for_independent_review")

    def test_supporting_joint_record_allows_tentative_cross_domain(self):
        bridge_record = {
            "id": "PMC500",
            "source": "PMC",
            "title": "Retinal glaucoma imaging features for cervical cancer screening: feasibility report",
        }
        result = assess_candidate(
            "Could glaucoma imaging inform cervical cancer research? PMC500",
            PAPERS + [bridge_record],
        )
        self.assertEqual(result["decision"], "tentative_only")
        self.assertIn("PMC500", result["record_ids_covering_all_topics"])

    def test_standalone_topic_grounded_in_abstract(self):
        result = assess_candidate(
            "Could diabetic retinopathy models be studied? PMC600",
            [{"title": "Ophthalmic multimodal screening", "id": "PMC600",
              "abstract": "This paper evaluates diabetic retinopathy imaging."}],
        )
        self.assertEqual(result["decision"], "tentative_only")


if __name__ == "__main__":
    unittest.main()
