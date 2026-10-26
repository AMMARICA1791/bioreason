"""Offline council smoke check with an auditable JSON result."""
import json
import pathlib
import sys

from bioreason.council import run_council, verify_chain


def main():
    papers = json.loads(pathlib.Path("examples/papers.json").read_text(encoding="utf-8"))
    output = run_council("offline reproducibility check", papers)
    assert output["audit_passed"], "Council audit failed"
    assert verify_chain(output["messages"]), "Message chain invalid"
    assert len(output["results"]) == 8, "Not all eight roles executed"
    assert len(output["messages"]) == 9, "Unexpected number of handoffs"
    assert output["results"]["Validator"]["verified_findings"] == 0
    pathlib.Path("artifacts").mkdir(exist_ok=True)
    pathlib.Path("artifacts/council-smoke.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("PASS: eight roles, nine handoffs, intact chain, no scientific validation claim")


if __name__ == "__main__":
    main()
