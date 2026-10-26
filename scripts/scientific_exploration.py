"""Re-establish science-wide discovery coverage, not a biomedical-only sample.

This first stage collects genuine DOI records across independent fields.
The eight deterministic roles are reported transparently as a *workflow*
audit, not model intelligence. No research discovery is declared.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from bioreason.council import run_council, verify_chain
from bioreason.multidomain import scout_domains

OUTPUT = Path("artifacts/science-exploration.json")


def run(fetcher=None):
    data = scout_domains(fetcher=fetcher) if fetcher else scout_domains()
    result = run_council(
        "Science-wide literature survey across independent disciplines",
        data["records"],
    )
    if len(result["results"]) != 8 or not result["audit_passed"]:
        raise RuntimeError("Eight-role deterministic council did not complete")
    if not verify_chain(result["messages"]):
        raise RuntimeError("Hash-linked handoffs invalid")
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_mode": data["source_mode"],
        "survey": data,
        "deterministic_council": result,
        "model_council": None,
        "scientific_validation": False,
        "scientific_discovery": False,
        "originality_checked": False,
        "next_step": "model-backed hypothesis, peer objections, testable experiment and prior-art checks",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print("PASS: multidisciplinary live domains:", sorted(data["domains"]), flush=True)
    print("PASS: DOI-backed records:", len(data["records"]), flush=True)
    print("PASS: deterministic eight-role chain verified, not scientific reasoning",
          flush=True)
    return report


if __name__ == "__main__":
    run()
