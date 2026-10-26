"""Diagnostic: can an offline local model follow a source-aware critique?

Compares two pretrained local models on the SAME frozen literature snippets,
same prompts, same decoding and a single deterministic critique per model.
This is NOT a BioReason council performance or scientific truth benchmark.
No external paid inference APIs or automatic scientific publication.

Run: PYTHONPATH=src python scripts/model_capability_probe.py
"""
import json
import pathlib
from datetime import datetime, timezone

from bioreason.comparison import evaluate_candidate

FIXTURE = pathlib.Path("evaluation/model_capability_cases.json")
OUTPUT = pathlib.Path("artifacts/model-capability-probe.json")
MODELS = (
    "Qwen/Qwen2.5-0.5B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct",
)
GENERATION_LIMIT = 112


def validate_cases(data):
    if data.get("schema_version") != 1:
        raise ValueError("Unexpected fixture version")
    cases = data.get("cases", [])
    if not isinstance(cases, list) or len(cases) != 2:
        raise ValueError("Diagnostic requires exactly two frozen cases")
    identifiers = set()
    for case in cases:
        paper = case.get("paper", {})
        rid = str(paper.get("id", "")).strip()
        if not rid or rid in identifiers or not paper.get("title") or not case.get("case_id"):
            raise ValueError("Missing or repeated source metadata")
        identifiers.add(rid)
    return cases


def base_evidence(case):
    """Only information a model must see to propose a research lead."""
    return {
        "task": "Ask ONE narrow, falsifiable research question, not a conclusion.",
        "source": case["paper"],
        "topic": case["topic"],
        "possible_endpoint_to_investigate": case["outcome_hint"],
        "possible_comparator_to_investigate": case["baseline_hint"],
        "requirements": (
            "Write one actual research question with a measurable endpoint "
            "and a comparison, followed by the precise paper record ID. "
            "Use source metadata only as motivation, not as proof of better "
            "diagnostic accuracy. If the evidence is insufficient to even "
            "formulate a question, answer exactly ABSTAIN: insufficient evidence."
        ),
    }


def critique_from_gate(text, case):
    """Precommitted deterministic critique, NOT an extra model opinion."""
    score = evaluate_candidate(text, [case["paper"]])
    missing = [key for key, passed in score["checks"].items() if not passed]
    return {
        "previous_answer": text[:750],
        "observed_source_screen_reasons": score["screen"]["reason_codes"],
        "missing_testability_checks": missing,
        "source_to_verify": {
            "id": case["paper"]["id"],
            "title": case["paper"]["title"],
        },
        "requirement": (
            "Reconsider the question critically; fix any missing source ID, "
            "measurable outcome, or baseline, without claiming the paper "
            "proves improved outcomes. A source ID should be cited only if "
            "the paper is relevant. It is acceptable to ABSTAIN: insufficient "
            "evidence. Do not use template placeholders."
        ),
    }


def diagnostic_report(model_id, case, initial, revised):
    source = [case["paper"]]
    first = evaluate_candidate(initial, source)
    last = evaluate_candidate(revised, source)
    return {
        "model": model_id,
        "case_id": case["case_id"],
        "source_id": case["paper"]["id"],
        "initial": first,
        "revision": last,
        "changed": initial.strip() != revised.strip(),
        "proxy_delta": last["proxy_score"] - first["proxy_score"],
        "source_citation_repaired": (
            not first["checks"]["source_identifier_present"]
            and last["checks"]["source_identifier_present"]
        ),
        "source_citation_lost": (
            first["checks"]["source_identifier_present"]
            and not last["checks"]["source_identifier_present"]
        ),
        "scientific_validation": False,
    }


def run_model(model_id, cases):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.set_num_threads(2)
    print("Loading local CPU model:", model_id, flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)
    model.eval()
    model.generation_config.temperature = None
    model.generation_config.top_p = None
    model.generation_config.top_k = None

    def infer(evidence):
        prompt = [
            {"role": "system", "content": (
                "You are evaluating bibliographic research leads. "
                "Use only supplied real record metadata, not invented findings. "
                "Ask a falsifiable question with an exact source record ID "
                "if supported, or explicitly abstain. Never claim clinical "
                "efficacy was established. No placeholders or template slots."
            )},
            {"role": "user", "content": json.dumps(evidence, ensure_ascii=False)},
        ]
        formatted = tokenizer.apply_chat_template(
            prompt, tokenize=False, add_generation_prompt=True,
        )
        encoded = tokenizer(formatted, return_tensors="pt", return_attention_mask=True)
        with torch.no_grad():
            result = model.generate(
                **encoded,
                max_new_tokens=GENERATION_LIMIT,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        reply = tokenizer.decode(
            result[0][encoded["input_ids"].shape[-1]:],
            skip_special_tokens=True,
        ).strip()
        if not reply:
            raise RuntimeError("Empty generation from " + model_id)
        return reply

    results = []
    for case in cases:
        initial = infer(base_evidence(case))
        revised = infer({
            "initial_problem": base_evidence(case),
            "review": critique_from_gate(initial, case),
        })
        report = diagnostic_report(model_id, case, initial, revised)
        results.append(report)
        print(
            "RESULT", model_id, case["case_id"],
            "score", report["initial"]["proxy_score"],
            "->", report["revision"]["proxy_score"],
            "citation_repaired", report["source_citation_repaired"],
            "citation_lost", report["source_citation_lost"],
            flush=True,
        )
    del model
    return results


def main():
    cases = validate_cases(json.loads(FIXTURE.read_text(encoding="utf-8")))
    rows = []
    for model in MODELS:
        rows.extend(run_model(model, cases))
    assert len(rows) == len(cases) * len(MODELS)
    output = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "preliminary local model-capability diagnosis, not proof of council improvement",
        "models": MODELS,
        "generation": {
            "do_sample": False,
            "max_new_tokens": GENERATION_LIMIT,
            "four_cpu_threads_max": True,
        },
        "cases": len(cases),
        "model_generations": 2 * len(cases) * len(MODELS),
        "case_results": rows,
        "scientific_validation": False,
        "model_training_performed": False,
        "limits": [
            "Two curated cases are insufficient for scientific conclusions.",
            "Citation and testability proxy scores are not scientific accuracy.",
            "A model corrected by feedback does not prove eight-agent teamwork adds value.",
            "This diagnostic holds prompts and metadata constant, not parameter counts.",
            "No model responses are automatically accepted for clinical use.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print("PASS: controlled source-aware model-capability diagnostic", flush=True)
    print("Models:", ", ".join(MODELS), "inferences:", output["model_generations"],
          flush=True)
    print("SCIENTIFIC IMPROVEMENT PROVEN: False", flush=True)


if __name__ == "__main__":
    main()
