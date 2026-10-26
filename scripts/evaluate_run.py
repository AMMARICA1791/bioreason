"""Recompute solo/council comparisons from the saved GitHub run artifact.

No generative model, network or source mutation occurs during this check.
Honest negative results are valid evaluations, not reasons to fail the workflow.
"""
import json
import pathlib

from bioreason.comparison import compare_solo_to_council
from bioreason.council import MODEL_ROLES, verify_chain

INPUT = pathlib.Path("artifacts/model-council.json")
OUTPUT = pathlib.Path("artifacts/comparison-verification.json")


def check_run(data):
    if data.get("scientific_validation") is not False:
        raise ValueError("Scientific validation must not be claimed")
    if not verify_chain(data["council"]["messages"]):
        raise ValueError("Corrupted base council handoffs")
    dialogue = data["deliberation"]
    if not verify_chain(dialogue["messages"]):
        raise ValueError("Corrupted debate handoffs")
    expected = compare_solo_to_council(
        data["solo_vs_council"]["arms"]["solo"]["candidate"],
        dialogue, data["papers"],
    )
    if expected != data["solo_vs_council"]:
        raise ValueError("Saved comparison does not match original text and source data")
    calls = data["model_calls"]
    expected_calls = ["Inventor"] + list(MODEL_ROLES) * (1 + dialogue["rounds"])
    if calls != expected_calls:
        raise ValueError("Model call trace does not match declared comparison")
    # Count model-provided substantive objections separately from
    # deterministic issue screens. A hash-linked chat turn is not peer review.
    critic_turns = [t for t in dialogue["turns"] if t["role"] == "Critic"]
    critic_audits = [
        t.get("critic_response_audit") for t in critic_turns
    ]
    explicit_challenges = sum(
        a is not None and a.get("audit") == "challenge_explicit"
        for a in critic_audits
    )
    failed_challenges = sum(
        a is not None and a.get("audit") == "critic_failed_to_challenge"
        for a in critic_audits
    )
    unaudited = sum(a is None for a in critic_audits)
    outcomes = expected["outcomes"]
    proxy_success = (
        outcomes["solo_to_last_proxy_delta"] > 0
        and outcomes["first_to_last_proxy_delta"] > 0
        and outcomes["first_to_last_changed"]
        and outcomes["last_scientific_gate"] == "tentative_only"
    )
    return {
        "source_mode": data["source_mode"],
        "source_count": data["record_count"],
        "model_id": data["model_id"],
        "actual_model_calls": len(calls),
        "solo_proxy_score": expected["arms"]["solo"]["proxy_score"],
        "council_first_proxy_score": expected["arms"]["council_first"]["proxy_score"],
        "council_last_proxy_score": expected["arms"]["council_last"]["proxy_score"],
        "solo_to_last_delta": outcomes["solo_to_last_proxy_delta"],
        "first_to_last_delta": outcomes["first_to_last_proxy_delta"],
        "final_gate": outcomes["last_scientific_gate"],
        "critic_turns": len(critic_turns),
        "critic_explicit_objections": explicit_challenges,
        "critic_failed_challenge": failed_challenges,
        "critic_unaudited_turns": unaudited,
        "proxy_improvement_observed_in_one_run": proxy_success,
        "scientific_improvement_demonstrated": False,
        "message_chain_verified": True,
        "comparison_recomputed_from_evidence": True,
        "limitation": (
            "One run, unmatched inference budgets, rule-based proxy only; "
            "no blind expert assessment"
        ),
    }


def main():
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    report = check_run(data)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PASS: comparison independently recomputed from saved candidates")
    print("Solo proxy:", report["solo_proxy_score"])
    print("Council first proxy:", report["council_first_proxy_score"])
    print("Council last proxy:", report["council_last_proxy_score"])
    print("SOLO-COUNCIL PROXY IMPROVEMENT:", report["proxy_improvement_observed_in_one_run"])
    print("CRITIC AUDIT:", report["critic_explicit_objections"], "explicit objections,",
          report["critic_failed_challenge"], "failed challenges,",
          report["critic_unaudited_turns"], "not audited")
    print("SCIENTIFIC IMPROVEMENT DEMONSTRATED: False")


if __name__ == "__main__":
    main()
