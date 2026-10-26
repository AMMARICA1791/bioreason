"""Multi-domain science scouting from public Crossref journal metadata.

This is a source-collection and evidence-triage component, NOT a discovery
engine. Each domain keeps its own bibliography; a connection between two
papers is not asserted just because they share a keyword.
"""
import html
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone

CROSSREF_WORKS = "https://api.crossref.org/works"
DOMAIN_SPECS = (
    {
        "domain": "materials",
        "query": "perovskite photodetector",
        "title_anchor": r"\b(?:perovskite|photodetector|semiconductor)\b",
    },
    {
        "domain": "energy",
        "query": "sodium ion battery",
        "title_anchor": r"\b(?:sodium[\s-]+ion|batter(?:y|ies)|electrolyte)\b",
    },
    {
        "domain": "computing",
        "query": "neuromorphic computing",
        "title_anchor": r"\b(?:neuromorphic|spiking neural|memristor)\b",
    },
    {
        "domain": "bioengineering",
        "query": "microfluidic biosensor",
        "title_anchor": r"\b(?:microfluidic|biosensor|lab[\s-]+on[\s-]+chip)\b",
    },
)
MIN_DOMAINS = 3
PER_DOMAIN = 2


def _clean_text(value, limit):
    raw = value if isinstance(value, str) else ""
    return re.sub(
        r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))
    ).strip()[:limit]


def _published_year(work):
    parts = work.get("published", {}).get("date-parts", [])
    if parts and isinstance(parts[0], list) and parts[0]:
        year = parts[0][0]
        if type(year) is int:
            return year
    return None


def crossref_fetch(query, *, rows=25, start_year=2025):
    """Real public bibliographic query with a bounded request and no key."""
    if not 1 <= rows <= 25 or not 2000 <= start_year <= 2100:
        raise ValueError("Invalid bounded Crossref query")
    params = urllib.parse.urlencode({
        "query.title": query,
        "rows": rows,
        "filter": f"from-pub-date:{start_year}-01-01,type:journal-article",
        "select": "DOI,title,abstract,type,published,URL",
    })
    request = urllib.request.Request(
        CROSSREF_WORKS + "?" + params,
        headers={
            "User-Agent": "BioReason/0.3 (public educational research metadata)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        payload = json.load(response)
    items = payload.get("message", {}).get("items")
    if not isinstance(items, list):
        raise RuntimeError("Crossref result missing bibliography items")
    return items


def curate_topic(topic, works, *, current_year=None, count=PER_DOMAIN):
    """Filter misleading search matches; never fabricate paper identifiers."""
    if current_year is None:
        current_year = datetime.now(timezone.utc).year
    if type(works) is not list or not 1 <= count <= 5:
        raise ValueError("Malformed source selection")
    results = []
    seen = set()
    anchor = re.compile(topic["title_anchor"], re.IGNORECASE)
    for work in works:
        if not isinstance(work, dict) or work.get("type") != "journal-article":
            continue
        titles = work.get("title") or []
        title = _clean_text(titles[0], 250) if isinstance(titles, list) and titles else ""
        doi = str(work.get("DOI") or "").strip().lower()
        year = _published_year(work)
        if not title or not doi.startswith("10.") or doi in seen:
            continue
        if not anchor.search(title):
            continue
        if year is None or year < 2025 or year > current_year:
            continue
        seen.add(doi)
        results.append({
            "domain": topic["domain"],
            "title": title,
            "abstract": _clean_text(work.get("abstract"), 700),
            "id": doi,
            "doi": doi,
            "source": "Crossref",
            "year": year,
            "url": "https://doi.org/" + doi,
            "provenance": "bibliographic_metadata_not_full_text",
        })
        if len(results) >= count:
            break
    return results


def scout_domains(fetcher=crossref_fetch, specs=DOMAIN_SPECS):
    """Require 3 independent live domains or fail visibly, no fake fallback."""
    groups = {}
    failures = []
    globally_seen = set()
    for spec in specs:
        name = spec["domain"]
        try:
            retrieved = fetcher(spec["query"], rows=25)
            selected = curate_topic(spec, retrieved)
            unique = [paper for paper in selected if paper["doi"] not in globally_seen]
            if len(unique) < PER_DOMAIN:
                raise RuntimeError("Not enough unique relevant DOI records")
            for paper in unique:
                globally_seen.add(paper["doi"])
            groups[name] = unique
        except (ValueError, RuntimeError, OSError, TimeoutError) as exc:
            failures.append({"domain": name, "error_type": type(exc).__name__})
    if len(groups) < MIN_DOMAINS:
        raise RuntimeError(
            f"Insufficient independent scientific coverage: {len(groups)} domains. "
            "No synthetic or unrelated fallback is permitted."
        )
    return {
        "source_mode": "crossref_live",
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "domains": groups,
        "domain_failures": failures,
        "records": [p for records in groups.values() for p in records],
        "scientific_validation": False,
        "originality_checked": False,
    }


def review_question(text, records):
    """Check DOI-to-domain traceability, not the truth of a proposed bridge."""
    if not isinstance(text, str) or not isinstance(records, list):
        raise TypeError("Expected question text and real records")
    identifiers = {paper["doi"]: paper for paper in records}
    # Preserve the DOI interior and discard only sentence / Markdown suffixes.
    raw_citations = re.findall(r"\b10\.\d{4,9}/[^\s<>\"]+", text.lower())
    cited = sorted({
        x.rstrip(".,;:!?)]}'\"*")
        for x in raw_citations
    })
    supported = [doi for doi in cited if doi in identifiers]
    represented = sorted({identifiers[doi]["domain"] for doi in supported})
    issues = []
    if not text.strip().endswith("?") and "?" not in text:
        issues.append("missing_testable_question")
    if not cited:
        issues.append("missing_exact_doi")
    if any(doi not in identifiers for doi in cited):
        issues.append("unknown_doi")
    if len(cited) > 3:
        issues.append("diffuse_citations")
    if re.search(r"\[(?:method|source|discipline|baseline|doi)\b", text, re.I):
        issues.append("copied_template")
    # A source from two fields is needed to label a cross-domain question.
    # It is NOT proof that a transfer mechanism exists.
    cross_domain = len(represented) >= 2
    return {
        "decision": "hold_for_review" if issues else "tentative_human_review_only",
        "reason_codes": sorted(issues),
        "recognized_dois": supported,
        "cited_domains": represented,
        "cross_domain_sources": cross_domain,
        "link_between_domains_established": False,
        "originality_checked": False,
        "scientific_validation": False,
    }
