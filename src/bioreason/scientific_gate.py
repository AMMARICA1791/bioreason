"""Conservative scientific-coherence and provenance screen for research leads.

This is NOT a scientific fact checker or biomedical ontology. It detects a
small, testable set of known biomedical topic phrases and requires a retrieved
record supporting a proposed combination. Cross-topic novelty is not declared
impossible; it is HELD pending evidence and independent scientific review.
"""
import re

TOPIC_TERMS = {
    "cervical cancer": (r"\bcervical (?:cancer|carcinoma|neoplas(?:ia|m))\b",),
    "glaucoma": (r"\bglaucoma(?:tous)?\b",),
    "breast cancer": (r"\bbreast (?:cancer|carcinoma|tumou?r)\b",),
    "prostate cancer": (r"\bprostate (?:cancer|carcinoma|tumou?r)\b",),
    "lung cancer": (r"\blung (?:cancer|carcinoma|tumou?r)\b",),
    "diabetic retinopathy": (r"\bdiabetic retinopathy\b",),
    "diabetes": (r"\bdiabet(?:es|ic)\b",),
    "alzheimer disease": (r"\balzheimer'?s?(?: disease)?\b",),
    "parkinson disease": (r"\bparkinson'?s?(?: disease)?\b",),
    "kidney disease": (r"\b(?:kidney|renal) disease\b",),
    "asthma": (r"\basthma(?:tic)?\b",),
    "multiple sclerosis": (r"\bmultiple sclerosis\b",),
    "protein folding": (r"\bprotein fold(?:ing|ed)?\b",),
    "cystic fibrosis": (r"\bcystic fibrosis\b",),
    "tuberculosis": (r"\btuberculosis\b",),
    "malaria": (r"\bmalaria\b",),
    "stroke": (r"\bstroke\b",),
}


def _topics(text):
    return {
        topic for topic, patterns in TOPIC_TERMS.items()
        if any(re.search(pattern, text, flags=re.IGNORECASE)
               for pattern in patterns)
    }


_VALID_ABSTENTION = re.compile(
    r"^\s*ABSTAIN\s*:\s*(?:insufficient (?:evidence|source support|supporting "
    r"evidence)|missing evidence|no supporting record|not enough evidence)"
    r"\.?\s*$",
    re.IGNORECASE,
)


def is_valid_abstention(text):
    """Only concise declarations of uncertainty qualify as clean abstentions."""
    return isinstance(text, str) and bool(_VALID_ABSTENTION.fullmatch(text))


def assess_candidate(candidate, records):
    """Return a blocking evidence gate, not a prediction of scientific truth.

    A *tentative* decision only means that limited lexical checks passed; it
    must never be interpreted as independently validated biomedical evidence.
    """
    if not isinstance(candidate, str):
        raise TypeError("candidate must be text")
    if not isinstance(records, list):
        raise TypeError("records must be a list")
    if is_valid_abstention(candidate):
        return {
            "decision": "abstained_insufficient_evidence",
            "reason_codes": ["explicit_abstention_insufficient_evidence"],
            "recognized_topics": [],
            "topics_not_in_sources": [],
            "record_ids_covering_all_topics": [],
            "cited_record_ids": [],
            "coverage": "explicit abstention; not a research claim",
            "scientific_validation": False,
        }
    topics = sorted(_topics(candidate))
    record_topics = {}
    for paper in records:
        identifier = str(paper.get("id", "")).strip()
        if not identifier:
            continue
        context = (str(paper.get("title", "")) + " " +
                   str(paper.get("abstract", "")))
        record_topics[identifier] = _topics(context)
    all_topics = set().union(*record_topics.values()) if record_topics else set()
    missing = sorted(set(topics) - all_topics)
    records_covering_all = sorted(
        rid for rid, present in record_topics.items()
        if topics and set(topics).issubset(present)
    )

    reasons = []
    if not topics:
        reasons.append("unassessed_biomedical_topics")
    if "?" not in candidate:
        reasons.append("no_explicit_testable_question")
    # A catalogue question is not a falsifiable hypothesis, even with real IDs.
    if re.search(
        r"\b(?:what are some|what (?:are|is) the (?:applications|uses|benefits|roles)|"
        r"list (?:some|the)|give examples of|overview of)\b",
        candidate, re.IGNORECASE,
    ):
        reasons.append("non_falsifiable_catalogue_question")
    if missing:
        reasons.append("topic_not_supported_by_retrieved_records")
    if len(topics) >= 2 and not records_covering_all:
        reasons.append("unsupported_cross_topic_bridge")

    # Explicitly prevent fake bibliography references from satisfying
    # provenance. An ID must be present in supplied records.
    cited_ids = sorted(
        rid for rid in record_topics
        if re.search(r"(?<!\w)" + re.escape(rid) + r"(?!\w)", candidate)
    )
    if topics and not cited_ids:
        reasons.append("missing_record_citation")
    if len(cited_ids) > 3:
        reasons.append("diffuse_evidence_citations")
    if topics and cited_ids and not any(
        set(topics).issubset(record_topics[rid]) for rid in cited_ids
    ):
        reasons.append("citation_does_not_support_topics")

    # DOI strings in a proposed claim must be present in the retrieved source
    # metadata. They are not independent proof of the claim even when matched.
    known_dois = {
        str(p.get("doi", "")).strip().rstrip(".,;)").lower()
        for p in records if p.get("doi")
    }
    mentioned_dois = [
        match.rstrip(".,;)").lower()
        for match in re.findall(r"\b10\.\d{4,9}/[^\s<>\"]+", candidate)
    ]
    if any(doi not in known_dois for doi in mentioned_dois):
        reasons.append("doi_not_in_retrieved_records")

    reasons = sorted(set(reasons))
    return {
        "decision": "hold_for_independent_review" if reasons else "tentative_only",
        "reason_codes": reasons,
        "recognized_topics": topics,
        "topics_not_in_sources": missing,
        "record_ids_covering_all_topics": records_covering_all,
        "cited_record_ids": cited_ids,
        "coverage": "limited phrase-based screen, NOT a medical ontology",
        "scientific_validation": False,
    }
