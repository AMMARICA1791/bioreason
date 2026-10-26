"""Choose a coherent, source-verifiable biomedical literature slice.

The council must not combine unrelated disciplines merely because all titles
mention AI. A failed or sparse topic search is reported, not silently
replaced by synthetic or unrelated material.
"""
from .scientific_gate import _topics

TOPIC = "cervical cancer"
MIN_RECORDS = 3
MAX_RECORDS = 10
QUERIES = (
    'OPEN_ACCESS:y AND FIRST_PDATE:[2026-01-01 TO 2026-12-31] '
    'AND ("cervical cancer" OR "cervical carcinoma") '
    'AND ("deep learning" OR "machine learning" OR "artificial intelligence")',
    'OPEN_ACCESS:y AND FIRST_PDATE:[2025-01-01 TO 2026-12-31] '
    'AND ("cervical cancer" OR "cervical carcinoma") '
    'AND ("deep learning" OR "machine learning" OR "artificial intelligence")',
)


def collect_focused_records(fetcher, topic=TOPIC, min_records=MIN_RECORDS):
    """Return (query, bounded records); fail closed if subject coverage is poor."""
    if topic != TOPIC:
        raise ValueError("Only the explicitly reviewed cervical cancer focus is supported")
    if type(min_records) is not int or not 1 <= min_records <= MAX_RECORDS:
        raise ValueError("min_records must be within 1..10")
    count_seen = 0
    for query in QUERIES:
        fetched = fetcher(query, limit=25)
        if not isinstance(fetched, list):
            raise RuntimeError("Europe PMC fetch did not return records")
        seen = set()
        eligible = []
        for paper in fetched:
            if not isinstance(paper, dict):
                continue
            record_id = str(paper.get("id", "")).strip()
            source = str(paper.get("source", "")).strip()
            if not record_id or not source:
                continue
            if (source, record_id) in seen:
                continue
            topics = _topics(str(paper.get("title", "")) + " " +
                             str(paper.get("abstract", "")))
            if topic not in topics:
                continue
            seen.add((source, record_id))
            eligible.append(paper)
        count_seen = max(count_seen, len(eligible))
        if len(eligible) >= min_records:
            return query, eligible[:MAX_RECORDS]
    raise RuntimeError(
        "No coherent focused set of at least " + str(min_records) +
        " traceable records available; largest subset contained " +
        str(count_seen) + ". No synthetic or cross-domain fallback used."
    )
