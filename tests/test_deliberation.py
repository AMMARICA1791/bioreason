"""Offline guarantees for roundtable dialogue and safe corrective memory."""
import tempfile
import unittest
from pathlib import Path

from bioreason.council import MODEL_ROLES, run_council, verify_chain
from bioreason.deliberation import (
    LESSON_GUIDANCE, _issue_codes, discuss, load_memory, save_memory,
)

PAPERS = [
    {"title": "Protein folding analysis", "id": "PMC123", "source": "MED", "doi": "10.1000/real"},
    {"title": "Protein folding models", "id": "PMC124", "source": "MED", "doi": ""},
]


class DeliberationTests(unittest.TestCase):
    def setUp(self):
        self.base = run_council("protein", PAPERS)
        self.calls = []

    def infer(self, role, evidence):
        self.calls.append((role, evidence))
        return {
            "role": role,
            "candidate": "Tentative proposal from " + role,
            "status": "unverified model-generated suggestion",
        }

    def test_real_markdown_wrapped_doi_does_not_poison_memory(self):
        papers = [
            {"id": "42380812", "source": "MED",
             "doi": "10.1186/s12885-026-16427-y",
             "title": "Artificial intelligence for cervical cancer screening"}
        ]
        answer = (
            "Could cervical cancer screening detection improve? "
            "[DOI: 10.1186/s12885-026-16427-y] Source ID: 42380812"
        )
        issues = _issue_codes(answer, papers, "Inventor")
        self.assertNotIn("unknown_doi", issues)
        self.assertNotIn("missing_source_anchor", issues)
        bogus = answer.replace("16427-y", "fake-id")
        self.assertIn("unknown_doi", _issue_codes(bogus, papers, "Inventor"))

    def test_two_rounds_eight_roles_with_real_handoffs(self):
        result = discuss("protein", PAPERS, self.base, self.infer, rounds=2)
        self.assertEqual(len(self.calls), 16)
        self.assertEqual(
            [turn["role"] for turn in result["turns"]],
            list(MODEL_ROLES) * 2,
        )
        self.assertEqual(len(result["messages"]), 16)
        self.assertTrue(verify_chain(result["messages"]))
        self.assertTrue(result["chain_verified"])
        self.assertIn("Scout", self.calls[1][1]["recent_dialogue_from_other_agents"][0]["role"])
        self.assertEqual(result["memory_after"]["completed_cycles"], 1)
        self.assertFalse(result["scientific_validation"])

    def test_lesson_is_applied_within_run_and_next_cycle(self):
        first = discuss("protein", PAPERS, self.base, self.infer, rounds=1)
        self.assertIn(
            "missing_source_anchor",
            [item["code"] for item in first["memory_after"]["lessons"]],
        )
        self.assertTrue(
            self.calls[3][1]["remembered_corrective_lessons"]
        )
        self.calls.clear()
        second = discuss(
            "protein", PAPERS, self.base, self.infer,
            memory=first["memory_after"], rounds=1,
        )
        self.assertTrue(self.calls[0][1]["remembered_corrective_lessons"])
        self.assertEqual(second["memory_before"]["completed_cycles"], 1)
        self.assertEqual(second["memory_after"]["completed_cycles"], 2)

    def test_unrecognized_doi_is_detected_and_not_claimed_verified(self):
        def with_fake_doi(role, evidence):
            response = self.infer(role, evidence)
            if role == "Critic":
                response["candidate"] = "Study DOI 10.9999/invented demonstrates certainty."
            return response

        result = discuss("protein", PAPERS, self.base, with_fake_doi, rounds=1)
        critique = next(t for t in result["turns"] if t["role"] == "Critic")
        self.assertIn("unknown_doi", critique["issue_codes"])
        self.assertIn(
            "unknown_doi",
            [item["code"] for item in result["memory_after"]["lessons"]],
        )
        self.assertEqual(result["turns"][3]["status"], "unverified model deliberation")

    def test_identical_second_round_is_observed(self):
        result = discuss("protein", PAPERS, self.base, self.infer, rounds=2)
        second = result["turns"][8:]
        self.assertTrue(all("unchanged_revision" in t["issue_codes"] for t in second))

    def test_only_allowlisted_codes_can_be_remembered(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "lessons.json"
            path.write_text(
                '{"version":1,"completed_cycles":3,"lessons":['
                '{"code":"unknown_doi","count":2},'
                '{"code":"run_untrusted_shell","count":999},'
                '{"code":"unknown_doi","count":8}]}',
                encoding="utf-8",
            )
            sanitized = load_memory(path)
            self.assertEqual(sanitized["lessons"], [
                {"code": "unknown_doi", "count": 2}
            ])
            save_memory(path, sanitized)
            self.assertEqual(load_memory(path), sanitized)
            self.assertEqual(set(LESSON_GUIDANCE), {
                "missing_source_anchor", "unknown_doi", "unchanged_revision",
                "unsupported_cross_topic_bridge",
                "topic_not_supported_by_retrieved_records",
                "no_explicit_testable_question",
                "non_falsifiable_catalogue_question",
                "diffuse_evidence_citations",
                "critic_failed_to_challenge",
                "unresolved_template_placeholders",
                "doi_record_id_mismatch",
            })

    def test_incoherent_bridge_blocked_and_critic_informed(self):
        papers = [
            {"title": "Deep learning in cervical cancer diagnosis",
             "id": "PMC13650561", "source": "PMC"},
            {"title": "Glaucoma classification from retinal fundus images",
             "id": "PMC13639773", "source": "PMC"},
        ]
        base = run_council("medical imaging", papers)
        seen = []

        def infer(role, evidence):
            seen.append((role, evidence))
            if role == "Inventor":
                return {
                    "role": role,
                    "candidate": (
                        "Can glaucoma retinal images improve cervical cancer "
                        "diagnosis? PMC13650561 PMC13639773"
                    ),
                }
            return {"role": role, "candidate": "No independently established link."}

        result = discuss("medical imaging", papers, base, infer, rounds=1)
        inventor = result["turns"][2]
        self.assertEqual(inventor["status"], "held_pending_evidence")
        self.assertIn(
            "unsupported_cross_topic_bridge",
            inventor["scientific_screen"]["reason_codes"],
        )
        self.assertIn(
            "unsupported_cross_topic_bridge",
            [entry["code"] for entry in result["memory_after"]["lessons"]],
        )
        self.assertEqual(result["publication_gate"], "hold_for_independent_review")
        self.assertIsNone(result["final_tentative_candidate"])
        self.assertEqual(
            seen[3][1]["latest_inventor_screen"]["decision"],
            "hold_for_independent_review",
        )
        self.assertTrue(verify_chain(result["messages"]))

    def test_real_revision_lifts_bridge_hold_but_not_scientific_validation(self):
        papers = [
            {"title": "Deep learning in cervical cancer diagnosis",
             "id": "PMC13650561", "source": "PMC"},
            {"title": "Glaucoma classification from retinal fundus images",
             "id": "PMC13639773", "source": "PMC"},
        ]
        base = run_council("medical imaging", papers)

        def infer(role, evidence):
            if role == "Inventor":
                if evidence["round"] == 1:
                    return {"role": role, "candidate":
                        "Glaucoma images predict cervical cancer PMC13650561 PMC13639773"}
                return {"role": role, "candidate":
                    "Could cervical cancer detection be studied using deep learning? PMC13650561"}
            return {"role": role, "candidate": "Tentative discussion and uncertainty."}

        result = discuss("medical imaging", papers, base, infer, rounds=2)
        self.assertEqual(
            [r["scientific_screen"]["decision"] for r in result["candidate_reviews"]],
            ["hold_for_independent_review", "tentative_only"],
        )
        self.assertEqual(result["publication_gate"], "tentative_review_only")
        self.assertFalse(result["scientific_validation"])
        self.assertTrue(verify_chain(result["messages"]))

    def test_second_round_inventor_receives_actual_prior_critic(self):
        # Regression for the four-message window dropping previous critique.
        papers = [
            {"title": "Cervical cancer Pap smear screening studies",
             "id": "PMC456", "source": "PMC",
             "abstract": "Comparison of sensitivity in image screening."},
            {"title": "Cervical cancer deep learning classification",
             "id": "PMC789", "source": "PMC"},
        ]
        base = run_council("cervical cancer screening", papers)
        inventor_evidence = []

        def infer(role, evidence):
            if role == "Inventor":
                inventor_evidence.append(evidence)
                if evidence["round"] == 1:
                    return {"role": role, "candidate":
                            "Could cervical cancer screening sensitivity improve?"}
                feedback = evidence["mandatory_revision_feedback"]
                return {"role": role, "candidate":
                        "Could cervical cancer screening sensitivity improve "
                        "compared with standard practice? PMC456"}
            if role == "Critic":
                return {"role": role, "candidate":
                        "BLOCKED: the Inventor failed to cite an exact source record ID."}
            return {"role": role, "candidate":
                    "Bibliographic metadata does not prove improvement."}

        output = discuss("cervical cancer screening", papers, base, infer, rounds=2)
        self.assertIsNone(inventor_evidence[0]["mandatory_revision_feedback"])
        feedback = inventor_evidence[1]["mandatory_revision_feedback"]
        self.assertEqual(feedback["previous_gate_decision"],
                         "hold_for_independent_review")
        self.assertIn("missing_record_citation", feedback["specific_hold_reasons"])
        self.assertIn("failed to cite", feedback["critic_objection"])
        self.assertEqual(
            feedback["possible_source_to_review_not_automatically_approved"]["id"],
            "PMC456",
        )
        self.assertEqual(output["candidate_reviews"][0]["status"], "held_pending_evidence")
        self.assertEqual(output["candidate_reviews"][1]["status"],
                         "unverified model deliberation")
        self.assertEqual(output["publication_gate"], "tentative_review_only")
        self.assertTrue(verify_chain(output["messages"]))

    def test_inventor_feedback_does_not_auto_attach_a_source(self):
        papers = [
            {"title": "Cervical cancer screening", "id": "PMC1", "source": "PMC"},
            {"title": "Cervical cancer imaging", "id": "PMC2", "source": "PMC"},
        ]
        base = run_council("cervical cancer", papers)
        def stubborn(role, evidence):
            return {"role": role, "candidate":
                    "Could cervical cancer screening accuracy improve?"}
        output = discuss("cervical cancer", papers, base, stubborn, rounds=2)
        self.assertIsNone(output["final_tentative_candidate"])
        self.assertEqual(output["publication_gate"], "hold_for_independent_review")
        self.assertTrue(all(
            "missing_record_citation" in record["scientific_screen"]["reason_codes"]
            for record in output["candidate_reviews"]
        ))

    def test_shallow_critic_is_flagged_and_a_real_objection_is_delivered(self):
        papers = [
            {"title": "Cervical cancer imaging and screening",
             "id": "PMC1", "source": "PMC"},
        ]
        council = run_council("cervical cancer", papers)
        inputs = {}

        def infer(role, evidence):
            inputs.setdefault((evidence["round"], role), evidence)
            if role == "Inventor":
                return {
                    "role": role,
                    "candidate": "Could cervical cancer screening accuracy improve?",
                }
            if role == "Critic":
                return {
                    "role": role,
                    "candidate": "Could cervical cancer screening accuracy improve?",
                }
            return {"role": role, "candidate": "Findings remain unverified."}

        outcome = discuss("cervical cancer", papers, council, infer, rounds=2)
        first_critic = outcome["turns"][3]
        self.assertEqual(
            first_critic["critic_response_audit"]["audit"],
            "critic_failed_to_challenge",
        )
        self.assertIn("critic_failed_to_challenge", first_critic["issue_codes"])
        duties = inputs[(1, "Critic")]["mandatory_critical_review"]
        self.assertIn("missing_record_citation", duties["reason_codes"])
        feedback = inputs[(2, "Inventor")]["mandatory_revision_feedback"]
        self.assertIn("source ID", feedback["deterministic_review_challenges"][0])
        self.assertEqual(
            feedback["critic_response_audit"]["audit"],
            "critic_failed_to_challenge",
        )
        self.assertTrue(verify_chain(outcome["messages"]))
        self.assertEqual(outcome["publication_gate"], "hold_for_independent_review")

    def test_abstention_is_not_incentivized_into_a_false_reference(self):
        papers = [
            {"title": "Cervical cancer diagnostic review",
             "id": "PMC600", "source": "PMC"},
        ]
        base = run_council("novel mechanism", papers)

        def abstain(role, evidence):
            if role == "Inventor":
                return {"role": role, "candidate": "ABSTAIN: insufficient evidence"}
            return {"role": role, "candidate": "Additional evidence is required."}

        result = discuss("novel mechanism", papers, base, abstain, rounds=2)
        inventors = [x for x in result["turns"] if x["role"] == "Inventor"]
        self.assertEqual(len(inventors), 2)
        self.assertTrue(all(x["status"] == "abstained_insufficient_evidence"
                            for x in inventors))
        self.assertTrue(all("missing_source_anchor" not in x["issue_codes"]
                            for x in inventors))
        self.assertEqual(result["publication_gate"], "abstained_insufficient_evidence")
        self.assertIsNone(result["final_tentative_candidate"])
        self.assertFalse(result["scientific_validation"])

    def test_bad_council_and_invalid_rounds_rejected(self):

        broken = dict(self.base, audit_passed=False)
        with self.assertRaises(ValueError):
            discuss("protein", PAPERS, broken, self.infer)
        with self.assertRaises(ValueError):
            discuss("protein", PAPERS, self.base, self.infer, rounds=9)
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
