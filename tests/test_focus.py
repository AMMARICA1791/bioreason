"""Focused retrieval must never disguise unrelated or synthetic papers as evidence."""
import unittest

from bioreason.focus import collect_focused_records, QUERIES


def paper(identifier, title, abstract=""):
    return {"id": identifier, "source": "PMC", "title": title,
            "abstract": abstract, "doi": ""}


class FocusTests(unittest.TestCase):
    def test_filters_unrelated_records_duplicates_and_requires_three(self):
        def fetcher(query, limit):
            self.assertEqual(limit, 25)
            self.assertEqual(query, QUERIES[0])
            return [
                paper("X", "Glaucoma classification from retinal photos"),
                paper("A", "Deep learning for cervical cancer diagnosis"),
                paper("A", "Deep learning for cervical cancer diagnosis"),
                paper("B", "Cervical cancer screening by AI"),
                paper("C", "Cervical carcinoma classification models"),
                paper("Y", "Protein folding prediction by neural nets"),
            ]

        query, selected = collect_focused_records(fetcher)
        self.assertEqual(query, QUERIES[0])
        self.assertEqual([p["id"] for p in selected], ["A", "B", "C"])

    def test_expands_date_not_scientific_topic_when_records_sparse(self):
        calls = []

        def fetcher(query, limit):
            calls.append(query)
            if query == QUERIES[0]:
                return [paper("A", "Cervical cancer model")]
            return [
                paper("B", "Cervical cancer classification"),
                paper("C", "Cervical carcinoma detection"),
                paper("D", "Deep learning in cervical cancer"),
            ]

        query, selected = collect_focused_records(fetcher)
        self.assertEqual(query, QUERIES[1])
        self.assertEqual(len(selected), 3)
        self.assertEqual(calls, list(QUERIES))

    def test_no_cross_domain_fallback(self):
        def fetcher(query, limit):
            return [paper("G", "Glaucoma diagnosis"),
                    paper("L", "Lung cancer imaging")]
        with self.assertRaisesRegex(RuntimeError, "No coherent focused set"):
            collect_focused_records(fetcher)

    def test_abstract_topic_is_accepted_when_title_generic(self):
        records = [
            paper("A", "Clinical imaging study", "Cervical cancer"),
            paper("B", "Clinical imaging study", "Cervical carcinoma"),
            paper("C", "Clinical imaging study", "Cervical cancer screening"),
        ]
        query, selected = collect_focused_records(lambda q, limit: records)
        self.assertEqual(len(selected), 3)


if __name__ == "__main__":
    unittest.main()
