"""Run a real literature collection cycle; retain an explicit offline fallback."""
import json
import pathlib
from datetime import datetime, timezone
from bioreason.core import fetch
from bioreason.council import run_council, verify_chain

QUERY = "OPEN_ACCESS:y AND FIRST_PDATE:[2026-01-01 TO 2026-12-31] AND (AI OR machine learning)"
OUT = pathlib.Path("artifacts/live-council.json")


def main():
    OUT.parent.mkdir(exist_ok=True)
    status = {"started_utc": datetime.now(timezone.utc).isoformat(), "query": QUERY}
    try:
        papers = fetch(QUERY, limit=10)
        if not papers:
            raise RuntimeError("Europe PMC returned no records")
        status["source_mode"] = "europe_pmc_live"
    except Exception as exc:
        status["source_mode"] = "offline_fallback"
        status["live_error_type"] = type(exc).__name__
        papers = json.loads(pathlib.Path("examples/papers.json").read_text(encoding="utf-8"))
    result = run_council(QUERY, papers)
    status["record_count"] = len(papers)
    status["eight_roles"] = len(result["results"]) == 8
    status["handoff_chain_valid"] = verify_chain(result["messages"])
    status["audit_passed"] = result["audit_passed"]
    status["model_inference"] = "not enabled; deterministic council only"
    OUT.write_text(json.dumps({"execution": status, "council": result},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert status["eight_roles"] and status["handoff_chain_valid"] and status["audit_passed"]
    print(json.dumps(status, ensure_ascii=False))
    if status["source_mode"] != "europe_pmc_live":
        print("WARNING: live literature collection unavailable; synthetic fallback explicitly recorded")


if __name__ == "__main__":
    main()
