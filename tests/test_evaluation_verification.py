"""Verify the saved experimental comparison cannot silently change claims."""
import copy
import unittest

from bioreason.comparison import compare_solo_to_council
from bioreason.council import MODEL_ROLES, run_council
from bioreason.deliberation import discuss
from scripts.evaluate_run import check_run

PAPERS = [
    {"title": "Cervical cancer deep learning diagnostic sensitivity",
     "id": "PMC10", "source": "PMC", "abstract": ""},
    {"title": "Cervical cancer classification methods",
     "id": "PMC11", "source": "PMC", "abstract": ""},
]


def build_evidence():
    base = run_council("cervical cancer", PAPERS)

    def inference(role, data):
        return {
            "role": role,
            "candidate": (
                "Could cervical cancer detection sensitivity improve compared "
                "with standard practice? PMC10"
            ) if role == "Inventor" else "No scientific facts were confirmed.",
        }

    discussion = discuss("cervical cancer", PAPERS, base, inference, rounds=2)
    solo = "What are some AI applications?"
    comparison = compare_solo_to_council(solo, discussion, PAPERS)
    return {
        "scientific_validation": False,
        "model_id": "synthetic adapter (no inference)",
        "source_mode": "offline_fixture",
        "record_count": 2,
        "model_calls": ["Inventor"] + list(MODEL_ROLES) * 3,
        "papers": PAPERS,
        "council": base,
        "deliberation": discussion,
        "solo_vs_council": comparison,
    }


class EvaluationVerificationTests(unittest.TestCase):
    def test_report_recomputes_nonscientific_proxy(self):
        d = build_evidence()
        report = check_run(d)
        self.assertTrue(report["comparison_recomputed_from_evidence"])
        self.assertEqual(report["actual_model_calls"], 25)
        self.assertFalse(report["scientific_improvement_demonstrated"])
        self.assertFalse(report["proxy_improvement_observed_in_one_run"])
        self.assertEqual(report["critic_turns"], 2)
        self.assertEqual(report["critic_unaudited_turns"], 0)
        self.assertEqual(report["critic_failed_challenge"], 2)

    def test_missing_critique_audit_reported_not_claimed_success(self):
        d = build_evidence()
        for turn in d["deliberation"]["turns"]:
            if turn["role"] == "Critic":
                turn.pop("critic_response_audit", None)
        # Altering the archived turn also requires a new hash chain; so test
        # unaudited metrics through a fresh valid trace, never bypass integrity.
        from bioreason.council import Council
        trace = Council()
        for turn in d["deliberation"]["turns"]:
            trace.send(turn["role"], MODEL_ROLES[(MODEL_ROLES.index(turn["role"])+1) % 8],
                       "debate_reply", turn)
        d["deliberation"]["messages"] = [message.__dict__ for message in trace.messages]
        result = check_run(d)
        self.assertEqual(result["critic_unaudited_turns"], 2)
        self.assertEqual(result["critic_explicit_objections"], 0)

    def test_changed_candidate_cannot_hide_tampering(self):
        d = build_evidence()
        bad = copy.deepcopy(d)
        bad["solo_vs_council"]["arms"]["solo"]["candidate"] = (
            "Could cervical cancer sensitivity improve versus control? PMC10"
        )
        with self.assertRaisesRegex(ValueError, "does not match"):
            check_run(bad)

    def test_changed_model_call_count_is_rejected(self):
        bad = build_evidence()
        bad["model_calls"].pop()
        with self.assertRaisesRegex(ValueError, "call trace"):
            check_run(bad)

    def test_message_tampering_refused(self):
        bad = build_evidence()
        bad["deliberation"]["messages"][1]["kind"] = "forged"
        with self.assertRaisesRegex(ValueError, "Corrupted debate"):
            check_run(bad)


if __name__ == "__main__":
    unittest.main()
