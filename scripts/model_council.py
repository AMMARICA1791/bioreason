"""Run the eight-role council with three real, local model-backed roles.

This opt-in experiment downloads an openly available small language model.
Model outputs remain unverified; no API key or paid inference endpoint is used.
"""
import json
import pathlib
from datetime import datetime, timezone
from unittest.mock import patch

from bioreason.council import run_council, verify_chain

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
ROLES = ("Analyst", "Inventor", "Critic")
OUTPUT = pathlib.Path("artifacts/model-council.json")


def main():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    print("Loading real local model:", MODEL_ID, flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID)
    model.eval()
    calls = []

    def local_inference(role, evidence):
        prompt = [
            {"role": "system", "content": (
                "You are the BioReason " + role + ". Analyze only the supplied "
                "bibliographic evidence. State uncertainty. Never invent studies, "
                "causal findings, novelty claims, or validation. Keep it brief."
            )},
            {"role": "user", "content": json.dumps(evidence, ensure_ascii=False)[:5000]},
        ]
        encoded = tokenizer.apply_chat_template(
            prompt, tokenize=True, add_generation_prompt=True,
            return_tensors="pt",
        )
        with torch.no_grad():
            generated = model.generate(
                encoded, max_new_tokens=96, do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        answer = tokenizer.decode(generated[0][encoded.shape[-1]:], skip_special_tokens=True).strip()
        if not answer:
            raise RuntimeError("Local model returned an empty response for " + role)
        calls.append(role)
        return {"role": role, "candidate": answer,
                "status": "unverified model-generated suggestion", "model": MODEL_ID}

    papers = json.loads(pathlib.Path("examples/papers.json").read_text(encoding="utf-8"))
    with patch("bioreason.council.ask_model", side_effect=local_inference):
        result = run_council("protein folding", papers, model_roles=ROLES)

    assert calls == list(ROLES), "Model inference not executed for all three roles"
    assert verify_chain(result["messages"]), "Broken handoff chain"
    assert len(result["results"]) == 8 and result["audit_passed"]
    assert set(result["results"]["Builder"]["model_candidates"]) == set(ROLES)
    assert result["results"]["Validator"]["verified_findings"] == 0

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps({
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_id": MODEL_ID,
        "model_calls": calls,
        "source_mode": "synthetic_fixture_for_model_smoke_test",
        "scientific_validation": False,
        "council": result,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("PASS: actual local model generated outputs for", ", ".join(calls), flush=True)


if __name__ == "__main__":
    main()
