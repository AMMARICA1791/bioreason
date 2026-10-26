"""Deterministic, evidence-first biomedical literature triage prototype."""
import json
import re
import urllib.parse
import urllib.request
from collections import Counter

API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def fetch(query, limit=10):
    if not 1 <= limit <= 25:
        raise ValueError("limit must be between 1 and 25")
    params = urllib.parse.urlencode({"query": query, "format": "json", "pageSize": limit})
    request = urllib.request.Request(
        API + "?" + params, headers={"User-Agent": "BioReason/0.2 research prototype"}
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.load(response)
    return [
        {
            "title": record.get("title", ""),
            "year": record.get("pubYear", ""),
            "id": record.get("id", ""),
            "doi": record.get("doi", ""),
            "source": record.get("source", ""),
        }
        for record in data.get("resultList", {}).get("result", [])
    ]


def scout(papers):
    return {"agent": "Scout", "papers": papers, "count": len(papers)}


def analyst(papers):
    stop_words = {
        "using", "based", "study", "research", "through", "among",
        "between", "their", "effects", "analysis", "clinical",
    }
    words = Counter(
        word
        for paper in papers
        for word in re.findall(r"[a-z]{5,}", paper.get("title", "").lower())
        if word not in stop_words
    )
    return {"agent": "Analyst", "recurring_title_terms": words.most_common(12)}


def inventor(analysis):
    terms = [word for word, count in analysis["recurring_title_terms"] if count >= 2][:3]
    question = (
        "Could the relationship between " + ", ".join(terms) + " be investigated?"
        if len(terms) > 1 else None
    )
    return {
        "agent": "Inventor",
        "candidate_question": question,
        "status": "unvalidated question, not a discovery",
    }


def critic(papers):
    return {
        "agent": "Critic",
        "limitations": [
            "Title-only analysis cannot establish scientific conclusions",
            "Co-occurrence is not causality",
            "No novelty or patent search performed",
        ],
        "missing_doi": sum(not paper.get("doi") for paper in papers),
    }


def validator(papers):
    return {
        "agent": "Validator",
        "traceable_records": sum(
            bool(paper.get("id") and paper.get("source")) for paper in papers
        ),
        "verified_findings": 0,
        "note": "Bibliographic traceability only; no independent scientific validation",
    }


def coordinator(query, papers):
    analysis = analyst(papers)
    return {
        "query": query,
        "scout": scout(papers),
        "analyst": analysis,
        "inventor": inventor(analysis),
        "critic": critic(papers),
        "validator": validator(papers),
        "builder": {"agent": "Builder", "status": "pipeline executed"},
        "auditor": {"agent": "Auditor", "status": "limitations explicitly reported"},
    }
