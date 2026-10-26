"""Offline guarantees for roundtable dialogue and safe corrective memory."""
import tempfile
import unittest
from pathlib import Path

from bioreason.council import MODEL_ROLES, run_council, verify_chain
from bioreason.deliberation import (
    LESSON_GUIDANCE, discuss, load_memory, save_memory,
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
                "missing_source_anchor", "unknown_doi", "unchanged_revision"
            })

    def test_bad_council_and_invalid_rounds_rejected(self):
        broken = dict(self.base, audit_passed=False)
        with self.assertRaises(ValueError):
            discuss("protein", PAPERS, broken, self.infer)
        with self.assertRaises(ValueError):
            discuss("protein", PAPERS, self.base, self.infer, rounds=9)
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
