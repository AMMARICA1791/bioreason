"""Deterministic, auditable peer-review obligations for council dialogue.

This is NOT scientific peer review. It guarantees that obvious gate failures
generate concrete challenges even if the small Critic LLM merely paraphrases.
Model critique quality is audited rather than inferred from role labels.
"""
import re

CHALLENGES = {
    "missing_record_citation": (
        "The hypothesis cites no exact retrieved source ID. Identify a relevant "
        "record, justify its relation to the outcome, and cite its exact ID; "
        "otherwise abstain."
    ),
    "citation_does_not_support_topics": (
        "The cited record does not mention all proposed disease topics. "
        "Find a directly relevant paper or remove the unsupported claim."
    ),
    "unsupported_cross_topic_bridge": (
        "No provided record discusses the combined disease topics. "
        "Do not infer the bridge from separate papers."
    ),
    "topic_not_supported_by_retrieved_records": (
        "A biomedical topic in the proposal is absent from the retrieved "
        "evidence; provide a relevant paper or drop that topic."
    ),
    "no_explicit_testable_question": (
        "The proposal contains no explicit research question. Ask one "
        "falsifiable question with a measurable outcome."
    ),
    "non_falsifiable_catalogue_question": (
        "A list of applications is not a falsifiable study. Specify one "
        "intervention, outcome, comparison and source."
    ),
    "diffuse_evidence_citations": (
        "More than three study IDs are cited indiscriminately. "
        "Use a focused relevant record and explain its applicability."
    ),
    "doi_not_in_retrieved_records": (
        "A proposed DOI is not in the supplied metadata. "
        "Remove it or find a verifiable source."
    ),
    "doi_record_id_mismatch": (
        "The DOI belongs to a different retrieved paper than the cited ID. "
        "Identify which record supports the question and cite matching metadata."
    ),
    "unassessed_biomedical_topics": (
        "The limited topic screen cannot classify this proposal. "
        "Narrow the idea to the evidence or request expert review."
    ),
    "generic_comparison_missing": (
        "Provide an explicitly defined baseline and a measurable endpoint."
    ),
}

SOURCE_CHALLENGES = frozenset({
    "missing_record_citation", "citation_does_not_support_topics",
    "unsupported_cross_topic_bridge", "topic_not_supported_by_retrieved_records",
    "diffuse_evidence_citations", "doi_not_in_retrieved_records",
    "doi_record_id_mismatch",
})

CRITIQUE_SOURCE_WORDS = re.compile(
    r"\b(?:citat(?:ion|ions|e|ed)|source|sources|referenc(?:e|es)|"
    r"paper|papers|record|records|bibliograph(?:y|ic)|doi|"
    r"\b(?:pmc|med)\d+)\b", re.IGNORECASE,
)
CRITIQUE_CHALLENGE_WORDS = re.compile(
    r"\b(?:missing|absent|unsupported|insufficient|lacks?|unverifi(?:ed|able)|"
    r"cannot|not|without|must|need(?:s|ed)?|requires?|lack of|"
    r"fail(?:s|ed|ure)?|block(?:ed)?|uncertain)\b", re.IGNORECASE,
)


def make_review_obligations(screen):
    reasons = list(screen.get("reason_codes", []))
    challenges = [CHALLENGES[c] for c in reasons if c in CHALLENGES]
    return {
        "decision": screen.get("decision", "hold_for_independent_review"),
        "reason_codes": reasons,
        "specific_challenges": challenges,
        "must_request_direct_source_support": any(c in SOURCE_CHALLENGES for c in reasons),
        "research_validation": False,
    }


def assess_critic(critic_text, obligations):
    """Flag vacuous objections; never turn an LLM opinion into verified science."""
    if not isinstance(critic_text, str):
        raise TypeError("Critic response must be text")
    needs_source = obligations["must_request_direct_source_support"]
    has_source = bool(CRITIQUE_SOURCE_WORDS.search(critic_text))
    has_challenge = bool(CRITIQUE_CHALLENGE_WORDS.search(critic_text))
    if not obligations["specific_challenges"]:
        return {
            "audit": "no_automatic_criticism_required",
            "missing_source_challenge": False,
            "uncritical_paraphrase": False,
            "scientific_validation": False,
        }
    return {
        "audit": (
            "challenge_explicit" if has_challenge and (not needs_source or has_source)
            else "critic_failed_to_challenge"
        ),
        "missing_source_challenge": bool(needs_source and not has_source),
        "uncritical_paraphrase": not has_challenge,
        "scientific_validation": False,
    }
