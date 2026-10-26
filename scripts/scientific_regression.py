"""Run fixed negative/positive biomedical evidence regression cases.

CAUTION: crafted software tests, not a blinded expert-labelled clinical benchmark.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from bioreason.scientific_gate import assess_candidate

ROOT = Path(__file__).resolve().parents[1]
CASES_FILE = ROOT / "evaluation/scientific_regression_cases.json"
OUT = ROOT / "artifacts/scientific-regression.json"


def run():
    cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))["cases"]
    decisions = []
    for case in cases:
        result = assess_candidate(case["candidate"], case["papers"])
        decisions.append({
            "case": case["id"],
            "expected": case["expected"],
            "actual": result["decision"],
            "pass": result["decision"] == case["expected"],
            "reasons": result["reason_codes"],
        })
    false_release = sum(
        x["expected"] == "hold_for_independent_review"
        and x["actual"] != "hold_for_independent_review"
        for x in decisions
    )
    false_hold = sum(
        x["expected"] == "tentative_only" and x["actual"] != "tentative_only"
        for x in decisions
    )
    summary = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": CASES_FILE.name,
        "assessment": "synthetic regression, not scientifically validated",
        "case_count": len(decisions),
        "passed": sum(x["pass"] for x in decisions),
        "false_release": false_release,
        "false_hold": false_hold,
        "decisions": decisions,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("Scientific evidence regression:", summary["passed"], "/", len(decisions))
    print("False releases:", false_release, "false holds:", false_hold)
    print("NOTE: synthetic tests do not establish clinical accuracy")
    if summary["passed"] != len(decisions):
        raise SystemExit("FAIL: scientific evidence regression changed")
    return summary


if __name__ == "__main__":
    run()
