"""Offline tests for the deterministic BioReason baseline."""
import unittest
import io
import json
from unittest.mock import patch
from bioreason.core import coordinator, fetch


class CoreTests(unittest.TestCase):
    def test_traceability_and_limits(self):
        papers = [
            {"title": "Protein folding models", "id": "123", "source": "MED", "doi": "10.test/a"},
            {"title": "Protein folding studies", "id": "124", "source": "MED", "doi": ""},
        ]
        result = coordinator("protein", papers)
        self.assertEqual(result["validator"]["traceable_records"], 2)
        self.assertEqual(result["validator"]["verified_findings"], 0)
        self.assertEqual(result["critic"]["missing_doi"], 1)
        self.assertIn("protein", result["inventor"]["candidate_question"].lower())

    def test_empty(self):
        self.assertEqual(coordinator("x", [])["scout"]["count"], 0)

    def test_no_question_from_unrelated_titles(self):
        papers = [
            {"title": "Zebrafish embryos", "id": "A", "source": "MED", "doi": ""},
            {"title": "Yeast metabolism", "id": "B", "source": "MED", "doi": ""},
        ]
        self.assertIsNone(coordinator("biology", papers)["inventor"]["candidate_question"])

    def test_missing_identifiers_not_traceable(self):
        papers = [{"title": "Protein folding study", "id": "", "source": "MED", "doi": ""}]
        self.assertEqual(coordinator("protein", papers)["validator"]["traceable_records"], 0)

    def test_candidate_is_explicitly_unvalidated(self):
        papers = [
            {"title": "Protein folding analysis", "id": "1", "source": "MED", "doi": ""},
            {"title": "Protein folding methods", "id": "2", "source": "MED", "doi": ""},
        ]
        result = coordinator("protein", papers)
        self.assertEqual(result["validator"]["verified_findings"], 0)
        self.assertIn("unvalidated", result["inventor"]["status"])

    def test_core_metadata_includes_sanitized_abstract(self):
        payload = {"resultList": {"result": [{
            "id": "PMC1",
            "source": "PMC",
            "title": "Cervical cancer imaging study",
            "abstractText": "<p>We study cervical &amp; uterine cancer imaging.</p>",
            "doi": "10.1000/genuine",
        }]}}
        with patch(
            "bioreason.core.urllib.request.urlopen",
            return_value=io.BytesIO(json.dumps(payload).encode("utf-8")),
        ) as mock:
            papers = fetch("cervical cancer", limit=1)
        self.assertEqual(len(papers), 1)
        self.assertIn("cervical & uterine", papers[0]["abstract"])
        self.assertNotIn("<p>", papers[0]["abstract"])
        self.assertIn("resultType=core", mock.call_args.args[0].full_url)

    def test_invalid_limit(self):
        with self.assertRaises(ValueError):
            fetch("biology", 0)


if __name__ == "__main__":
    unittest.main()
