"""Transparent, rule-based solo-vs-council output comparison.

These are *format/evidence-proxy* metrics. They neither validate biomedical
truth nor prove that collaboration improves research outcomes. The solo arm
must use the same model, topic and retrieved records without peer dialogue.
"""
import re
from .scientific_gate import assess_candidate

MEASURABLE_ENDPOINT = re.compile(
    r"\b(?:sensitivity|specificity|recall|precision|false[\s-]?positive|"
    r"false[\s-]?negative|accuracy|auc|area under|f1[\s-]?score|"
    r"detection rate|diagnostic yield|calibration|time to diagnosis)\b",
    re.IGNORECASE,
)
COMPARATOR = re.compile(
    r"\b(?:compar(?:e|ed|ing|ison)|versus|vs\.?|relative to|"
    r"baseline|standard of care|control group|without|against)\b",
    re.IGNORECASE,
)


def evaluate_candidate(text, papers):
    """Evaluate one immutable text under the same explicit proxy rubric."""
    if not isinstance(text, str):
        raise TypeError("Candidate must be a string")
    screen = assess_candidate(text, papers)
    checks = {
        "contains_question": "?" in text,
        "source_identifier_present": bool(screen["cited_record_ids"]),
        "direct_topic_evidence": (
            bool(screen["record_ids_covering_all_topics"]) and
            "citation_does_not_support_topics" not in screen["reason_codes"]
        ),
        "no_blocking_reason": screen["decision"] == "tentative_only",
        "measurable_endpoint_mentioned": bool(MEASURABLE_ENDPOINT.search(text)),
        "comparator_mentioned": bool(COMPARATOR.search(text)),
    }
    return {
        "candidate": text,
        "screen": screen,
        "checks": checks,
        "proxy_score": sum(checks.values()),
        "proxy_max": len(checks),
        "interpretation": "heuristic evidence and testability proxy, not scientific accuracy",
    }


def compare_solo_to_council(solo, deliberation, papers):
    """Compare a solo reply with the first and last Inventor council replies."""
    reviews = [
        turn for turn in deliberation["turns"] if turn["role"] == "Inventor"
    ]
    if not reviews:
        raise ValueError("No Inventor proposals were recorded")
    if len(reviews) < 2:
        raise ValueError("Comparison requires at least two discussion rounds")
    baseline = evaluate_candidate(solo, papers)
    first = evaluate_candidate(reviews[0]["response"], papers)
    last = evaluate_candidate(reviews[-1]["response"], papers)
    return {
        "arms": {
            "solo": baseline,
            "council_first": first,
            "council_last": last,
        },
        "outcomes": {
            "first_to_last_changed": (
                reviews[0]["response"].strip() != reviews[-1]["response"].strip()
            ),
            "solo_to_last_proxy_delta": (
                last["proxy_score"] - baseline["proxy_score"]
            ),
            "first_to_last_proxy_delta": (
                last["proxy_score"] - first["proxy_score"]
            ),
            "last_scientific_gate": last["screen"]["decision"],
        },
        "validity_limits": [
            "The solo arm and council use the same model and papers, but different inference budgets.",
            "The mechanical proxy may reward formatting without scientific truth.",
            "A single live run cannot show generalizable learning or improvement.",
            "There is no blinded independent expert reference label.",
            "All claims remain unvalidated research leads; a tentative gate is not approval.",
        ],
        "scientific_validation": False,
    }
