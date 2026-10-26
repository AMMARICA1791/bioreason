"""No-network tests for broad science scouting and citation integrity."""
import io
import json
import unittest
from unittest.mock import patch

from bioreason.multidomain import (
    DOMAIN_SPECS, _clean_text, crossref_fetch,
    curate_topic, review_question, scout_domains,
)


def article(title, doi, *, year=2026, abstract=""):
    return {
        "type": "journal-article", "title": [title], "DOI": doi,
        "abstract": abstract, "published": {"date-parts": [[year, 3, 1]]},
    }


FIXTURES = {
    "perovskite photodetector": [
        article("New perovskite photodetector device",
                "10.1000/perov.2026"),
        article("Semiconductor perovskite photodetector response",
                "10.1000/perov.2025", year=2025),
    ],
    "sodium ion battery": [
        article("Battery electrodes for sodium ion storage",
                "10.1000/battery.2026"),
        article("Electrolyte stability in sodium ion batteries",
                "10.1000/battery.2025", year=2025),
    ],
    "neuromorphic computing": [
        article("Neuromorphic computing with memristor",
                "10.1000/neuro.2026"),
        article("Spiking neural electronics systems",
                "10.1000/neuro.2025", year=2025),
    ],
    "microfluidic biosensor": [
        article("A microfluidic biosensor for point of care diagnostics",
                "10.1000/biosensor.2026"),
        article("Integrated biosensor microfluidic sensing",
                "10.1000/biosensor.2025", year=2025),
    ],
}


class MultidomainTests(unittest.TestCase):
    def test_four_independent_science_domains_selected(self):
        calls = []
        def fetcher(query, rows=25):
            calls.append(query)
            return FIXTURES[query]
        result = scout_domains(fetcher=fetcher)
        self.assertEqual(len(result["domains"]), 4)
        self.assertEqual(len(result["records"]), 8)
        self.assertEqual(len(set(p["doi"] for p in result["records"])), 8)
        self.assertTrue(all(p["source"] == "Crossref" for p in result["records"]))
        self.assertFalse(result["scientific_validation"])
        self.assertFalse(result["originality_checked"])
        self.assertEqual(len(calls), 4)

    def test_no_unrelated_or_unidentified_studies(self):
        spec = DOMAIN_SPECS[0]
        studies = [
            article("Glaucoma retinal diagnosis", "10.1000/irrelevant"),
            article("Perovskite photodetector", ""),
            article("Perovskite photodetector", "10.1000/old", year=2020),
            article("Perovskite photodetector study", "10.1000/okay"),
            article("Photodetector semiconductor example", "10.1000/okay"),
        ]
        results = curate_topic(spec, studies, current_year=2026)
        self.assertEqual([p["doi"] for p in results], ["10.1000/okay"])

    def test_no_fake_fallback_if_less_than_three_domains(self):
        def fetcher(query, rows=25):
            if query in list(FIXTURES)[:2]:
                return FIXTURES[query]
            return []
        with self.assertRaisesRegex(RuntimeError, "Insufficient independent"):
            scout_domains(fetcher=fetcher)

    def test_partial_domain_failure_is_disclosed(self):
        def fetcher(query, rows=25):
            if query == "microfluidic biosensor":
                raise TimeoutError("network not ready")
            return FIXTURES[query]
        result = scout_domains(fetcher=fetcher)
        self.assertEqual(len(result["domains"]), 3)
        self.assertEqual(result["domain_failures"][0]["domain"], "bioengineering")
        self.assertEqual(result["domain_failures"][0]["error_type"], "TimeoutError")

    def test_source_text_sanitized_not_trusted(self):
        self.assertEqual(_clean_text("<jats:p>Perovskite &amp; optics</jats:p>", 200),
                         "Perovskite & optics")
        self.assertEqual(_clean_text(None, 100), "")

    def test_real_crossref_request_shape_without_web(self):
        response = {"message": {"items": [article("Perovskite photodetector",
                                                 "10.1000/a")]}}
        with patch("bioreason.multidomain.urllib.request.urlopen",
                   return_value=io.BytesIO(json.dumps(response).encode())) as mock:
            received = crossref_fetch("perovskite photodetector")
        self.assertEqual(len(received), 1)
        from urllib.parse import parse_qs, urlsplit
        params = parse_qs(urlsplit(mock.call_args.args[0].full_url).query)
        self.assertEqual(params["query.title"], ["perovskite photodetector"])
        self.assertEqual(params["rows"], ["25"])
        self.assertIn("type:journal-article", params["filter"][0])

    def test_cross_science_question_only_has_provenance_not_proof(self):
        records = [
            {"doi": "10.1000/perov.2026", "domain": "materials"},
            {"doi": "10.1000/neuro.2026", "domain": "computing"},
        ]
        r = review_question(
            "Could techniques in 10.1000/perov.2026 and 10.1000/neuro.2026 "
            "be tested together for photodetection latency?", records)
        self.assertEqual(r["decision"], "tentative_human_review_only")
        self.assertTrue(r["cross_domain_sources"])
        self.assertFalse(r["link_between_domains_established"])
        self.assertFalse(r["scientific_validation"])

    def test_explicit_abstention_is_responsible_not_a_discovery(self):
        out = review_question("ABSTAIN: insufficient evidence", [])
        self.assertEqual(out["decision"], "abstained_insufficient_evidence")
        self.assertEqual(out["recognized_dois"], [])
        self.assertFalse(out["scientific_validation"])

    def test_invented_doi_holds_proposal(self):
        records = [{"doi": "10.1000/perov.2026", "domain": "materials"}]
        r = review_question("Can 10.1000/nonexistent improve sensitivity?", records)
        self.assertEqual(r["reason_codes"], ["unknown_doi"])
        self.assertEqual(r["decision"], "hold_for_review")

    def test_empty_citations_held_even_if_interesting(self):
        r = review_question("Can emerging neuromorphic technology improve sensors?", [])
        self.assertIn("missing_exact_doi", r["reason_codes"])

    def test_doi_markdown_punctuation_keeps_identity(self):
        r = review_question(
            "Could methods in [DOI: 10.1000/a] improve sensor response?",
            [{"doi": "10.1000/a", "domain": "materials"}],
        )
        self.assertEqual(r["decision"], "tentative_human_review_only")
        self.assertEqual(r["recognized_dois"], ["10.1000/a"])


if __name__ == "__main__":
    unittest.main()
