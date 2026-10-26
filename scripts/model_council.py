"""Run the eight-role BioReason council on live biomedical records with local inference.

Each of the eight roles receives an actual local model inference turn.
Other council roles remain deterministic; outputs are unvalidated research leads.
A live literature outage fails visibly rather than masquerading as live evidence.
"""
import json
import pathlib
from datetime import datetime, timezone
from unittest.mock import patch

from bioreason.core import fetch
from bioreason.council import MODEL_ROLES, run_council, verify_chain

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
ROLES = MODEL_ROLES
QUERY = "OPEN_ACCESS:y AND FIRST_PDATE:[2026-01-01 TO 2026-12-31] AND (AI OR machine learning)"
OUTPUT = pathlib.Path("artifacts/model-council.json")


def main():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    print("Collecting live Europe PMC research records", flush=True)
    papers = fetch(QUERY, limit=10)
    if not papers:
        raise RuntimeError("Europe PMC did not return live research records")
    if not all(paper.get("id") and paper.get("source") for paper in papers):
        raise RuntimeError("Live research records are missing source identifiers")
    print("Live records received:", len(papers), flush=True)

    print("Loading real local model:", MODEL_ID, flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID)
    model.eval()

    # Qwen's saved sampling defaults are irrelevant to deterministic generation.
    # Explicitly clear them so Transformers does not emit misleading warnings.
    model.generation_config.temperature = None
    model.generation_config.top_p = None
    model.generation_config.top_k = None
    calls = []

    def local_inference(role, evidence):
        prompt = [
            {"role": "system", "content": (
                "You are the BioReason " + role + ". Analyze only the supplied "
                "bibliographic metadata. State uncertainty. Never invent papers, "
                "citations, causes, novelty claims, or scientific validation. "
                "Metadata alone does not prove findings. Keep the response concise."
            )},
            {"role": "user", "content": json.dumps(evidence, ensure_ascii=False)[:5000]},
        ]
        formatted = tokenizer.apply_chat_template(
            prompt, tokenize=False, add_generation_prompt=True,
        )
        encoded = tokenizer(
            formatted, return_tensors="pt", return_attention_mask=True,
        )
        with torch.no_grad():
            generated = model.generate(
                **encoded, max_new_tokens=96, do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        answer = tokenizer.decode(
            generated[0][encoded["input_ids"].shape[-1]:],
            skip_special_tokens=True,
        ).strip()
        if not answer:
            raise RuntimeError("Local model returned an empty response for " + role)
        calls.append(role)
        return {
            "role": role, "candidate": answer,
            "status": "unverified model-generated suggestion", "model": MODEL_ID,
        }

    with patch("bioreason.council.ask_model", side_effect=local_inference):
        result = run_council(QUERY, papers, model_roles=ROLES)

    assert calls == list(ROLES), "Model inference did not run for all three roles"
    assert verify_chain(result["messages"]), "Broken council message chain"
    assert len(result["results"]) == 8 and result["audit_passed"]
    assert set(result["results"]["Builder"]["model_candidates"]) == {"Analyst", "Inventor", "Critic"}
    assert all("model_suggestion" in result["results"][role] for role in ROLES)
    assert result["results"]["Validator"]["verified_findings"] == 0

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps({
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_id": MODEL_ID,
        "model_calls": calls,
        "source_mode": "europe_pmc_live",
        "record_count": len(papers),
        "papers": papers,
        "scientific_validation": False,
        "council": result,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("PASS: live Europe PMC records:", len(papers), flush=True)
    print("PASS: actual local model generated outputs for all eight roles:", ", ".join(calls), flush=True)
    print("PASS: eight-role council, verified handoff chain; findings unvalidated", flush=True)


if __name__ == "__main__":
    main()
