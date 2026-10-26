"""Auditable, bounded council discussion and cross-run corrective memory.

This is prompt-level adaptation, NOT model-weight training. Only allowlisted
deterministic issue codes may enter next-run prompts as lessons; generated prose
is archived as tentative dialogue but never promoted to trusted instructions.
"""
import json
import re
from pathlib import Path

from .council import Council, MODEL_ROLES, verify_chain
from .scientific_gate import assess_candidate
from .peer_review import make_review_obligations, assess_critic

VERSION = 1
ROUNDS = 2
ANCHOR_ROLES = frozenset({"Analyst", "Inventor", "Validator", "Builder"})
LESSON_GUIDANCE = {
    "missing_source_anchor": (
        "Tie specific claims to a supplied record ID; if evidence is too limited, "
        "state that limitation explicitly."
    ),
    "unknown_doi": "Do not invent a DOI: cite only DOI values supplied in the records.",
    "unchanged_revision": (
        "Respond to the previous objections with a substantive revision, "
        "or explain why the original proposal is still the best tentative one."
    ),
    "unsupported_cross_topic_bridge": (
        "A prior hypothesis linked biomedical topics that had no joint supporting "
        "record. Keep the bridge on hold and request direct evidence; do not "
        "repeat it as a medical conclusion."
    ),
    "topic_not_supported_by_retrieved_records": (
        "Do not introduce a biomedical disease or mechanism absent from the "
        "retrieved records without flagging the missing evidence."
    ),
    "no_explicit_testable_question": (
        "Inventor must produce one concrete, interrogative research question "
        "with an exact retrieved record ID, or abstain explicitly."
    ),
    "non_falsifiable_catalogue_question": (
        "Do not produce an encyclopedic list of applications. Propose a "
        "single falsifiable comparison with one specific observed outcome."
    ),
    "diffuse_evidence_citations": (
        "Do not append the entire bibliography as evidence. Use at most "
        "three directly relevant identifiers; state why each matters."
    ),
    "critic_failed_to_challenge": (
        "The Critic must identify at least one specific failure exposed by "
        "the evidence gate; paraphrasing the Inventor is not a review."
    ),
}
ROLE_TASKS = {
    "Scout": "Identify the strongest traceable records and missing coverage.",
    "Analyst": "Compare patterns across record titles, highlighting uncertainty.",
    "Inventor": "Propose or revise one testable question, not a discovery.",
    "Critic": "Challenge the proposal; point out unsupported implications.",
    "Validator": "Check the stated evidence references and unresolved gaps.",
    "Builder": "Revise the tentative plan in response to other agents.",
    "Auditor": "Review the dialogue and identify process faults and missing proof.",
    "Coordinator": "Summarize disagreements and assign priorities for next cycle.",
}


def load_memory(path):
    """Accept only narrowly scoped, code-based lessons from persisted state."""
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError, OSError):
        return {"version": VERSION, "completed_cycles": 0, "lessons": []}
    if not isinstance(value, dict) or value.get("version") != VERSION:
        return {"version": VERSION, "completed_cycles": 0, "lessons": []}
    lessons = []
    seen = set()
    for item in value.get("lessons", []):
        if not isinstance(item, dict):
            continue
        code = item.get("code")
        if code not in LESSON_GUIDANCE or code in seen:
            continue
        seen.add(code)
        count = item.get("count", 0)
        lessons.append({"code": code, "count": min(count, 10000)
                        if type(count) is int and count > 0 else 0})
    cycles = value.get("completed_cycles", 0)
    return {
        "version": VERSION,
        "completed_cycles": min(cycles, 10000)
        if type(cycles) is int and cycles > 0 else 0,
        "lessons": lessons,
    }


def save_memory(path, memory):
    """Store a small JSON state without preserving untrusted generated prose."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    canonical = {
        "version": VERSION,
        "completed_cycles": memory["completed_cycles"],
        "lessons": memory["lessons"],
    }
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(canonical, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _issue_codes(answer, papers, role, last_answer=None):
    issues = []
    ids = [str(paper["id"]) for paper in papers if paper.get("id")]
    if role in ANCHOR_ROLES and ids:
        if not any(
            re.search(r"(?<!\w)" + re.escape(identifier) + r"(?!\w)", answer)
            for identifier in ids
        ):
            issues.append("missing_source_anchor")
    dois = {
        str(paper.get("doi", "")).strip().rstrip(".,;)").lower()
        for paper in papers if paper.get("doi")
    }
    mentioned = re.findall(r"\b10\.\d{4,9}/[^\s<>\"]+", answer)
    if any(doi.rstrip(".,;)").lower() not in dois for doi in mentioned):
        issues.append("unknown_doi")
    if last_answer is not None and answer.strip() == last_answer.strip():
        issues.append("unchanged_revision")
    return issues


def _lessons(memory):
    active = {
        item["code"] for item in memory["lessons"] if item["count"] > 0
    }
    return [LESSON_GUIDANCE[code] for code in LESSON_GUIDANCE if code in active]


def _observe(memory, issues):
    counts = {item["code"]: item["count"] for item in memory["lessons"]}
    for code in issues:
        counts[code] = min(10000, counts.get(code, 0) + 1)
    memory["lessons"] = [
        {"code": code, "count": counts[code]}
        for code in LESSON_GUIDANCE if code in counts
    ]


def discuss(query, papers, base_council, infer, memory=None, rounds=ROUNDS):
    """Conduct multi-round responses among all eight roles.

    infer(role, evidence) is a real or test-injected model adapter. A validated
    base_council is required so that dialogue cannot masquerade as council proof.
    """
    if type(rounds) is not int or not 1 <= rounds <= 3:
        raise ValueError("Discussion rounds must be between 1 and 3")
    if not base_council.get("audit_passed") or not verify_chain(base_council["messages"]):
        raise ValueError("Cannot deliberate on an invalid council record")
    memory = load_memory_object(memory)
    before = json.loads(json.dumps(memory))
    turns = []
    ledger = Council()
    previous_by_role = {}
    latest_proposal = None
    records = [
        {"id": p.get("id", ""), "doi": p.get("doi", ""),
         "title": p.get("title", "")[:160],
         "abstract_excerpt": p.get("abstract", "")[:180]}
        for p in papers[:10]
    ]

    for round_number in range(1, rounds + 1):
        for idx, role in enumerate(MODEL_ROLES):
            # Keep substantive objections available across an entire round.
            # The rolling four-message context previously dropped Critic's
            # feedback before Inventor's second turn, preventing revision.
            previous_critic = next(
                (turn for turn in reversed(turns) if turn["role"] == "Critic"),
                None,
            )
            previous_validator = next(
                (turn for turn in reversed(turns) if turn["role"] == "Validator"),
                None,
            )
            revision_feedback = None
            if role == "Inventor" and round_number > 1 and latest_proposal:
                # Select a relevant *candidate* record for re-examination,
                # not an automatically approved citation. The model must
                # still cite and the independent quality gate must check it.
                terms = set(re.findall(r"[a-z]{4,}", latest_proposal["text"].lower()))
                ranked = sorted(
                    papers,
                    key=lambda paper: len(
                        terms & set(re.findall(
                            r"[a-z]{4,}", paper.get("title", "").lower()
                        ))
                    ),
                    reverse=True,
                )
                record = ranked[0] if ranked else None
                previous_obligations = make_review_obligations(latest_proposal["screen"])
                revision_feedback = {
                    "deterministic_review_challenges": previous_obligations["specific_challenges"],
                    "critic_response_audit": (
                        previous_critic.get("critic_response_audit")
                        if previous_critic else None
                    ),
                    "required_action": (
                        "Address the prior Critic objection and specific hold "
                        "reasons. Rewrite a falsifiable question with one exact "
                        "supporting record ID, or abstain. Do not mechanically "
                        "append a citation to an unsupported claim."
                    ),
                    "previous_gate_decision": latest_proposal["screen"]["decision"],
                    "specific_hold_reasons": latest_proposal["screen"]["reason_codes"],
                    "critic_objection": (
                        previous_critic["response"][:550]
                        if previous_critic else "No independent critique recorded"
                    ),
                    "validator_feedback": (
                        previous_validator["response"][:330]
                        if previous_validator else None
                    ),
                    "possible_source_to_review_not_automatically_approved": (
                        {"id": record.get("id"), "title": record.get("title", "")[:160],
                         "abstract_excerpt": record.get("abstract", "")[:190]}
                        if record else None
                    ),
                }
            recent = [
                {"role": t["role"], "response": t["response"][:350],
                 "issue_codes": t["issue_codes"]}
                for t in turns[-4:]
            ]
            mandatory_critical_review = (
                make_review_obligations(latest_proposal["screen"])
                if role == "Critic" and latest_proposal else None
            )
            evidence = {
                "mandatory_critical_review": mandatory_critical_review,
                "mandatory_revision_feedback": revision_feedback,
                "query": query,
                "round": round_number,
                "role_task": ROLE_TASKS[role],
                "latest_inventor_proposal": (
                    latest_proposal["text"][:500] if latest_proposal else None
                ),
                "latest_inventor_screen": (
                    latest_proposal["screen"] if latest_proposal else None
                ),
                "records": records,
                "baseline_suggestion": (
                    base_council["results"][role]
                    .get("model_suggestion", {}).get("candidate", "")[:350]
                ),
                "recent_dialogue_from_other_agents": recent,
                "previous_own_turn": previous_by_role.get(role, "")[:350],
                "remembered_corrective_lessons": _lessons(memory),
                "instruction": (
                    "Respond to the other agents' latest arguments. "
                    "Give a specific contribution and reference provided IDs "
                    "when citing evidence. Treat all model text as tentative. "
                    "For cross-topic claims, require a retrieved record "
                    "that explicitly addresses the bridge. Critic, Validator "
                    "and Auditor must challenge any held proposal; never "
                    "approve it merely because colleagues repeated it."
                ),
            }
            suggestion = infer(role, evidence)
            if not isinstance(suggestion, dict) or not isinstance(
                suggestion.get("candidate"), str
            ) or not suggestion["candidate"].strip():
                raise ValueError("Model failed to supply a nonempty debate reply")
            if suggestion.get("role") != role:
                raise ValueError("Model role mismatch")
            answer = suggestion["candidate"].strip()
            issues = _issue_codes(
                answer, papers, role, previous_by_role.get(role)
            )
            scientific_screen = None
            if role == "Inventor":
                scientific_screen = assess_candidate(answer, papers)
                latest_proposal = {"text": answer, "screen": scientific_screen}
                for code in (
                    "unsupported_cross_topic_bridge",
                    "topic_not_supported_by_retrieved_records",
                    "no_explicit_testable_question",
                    "non_falsifiable_catalogue_question",
                    "diffuse_evidence_citations",
                ):
                    if code in scientific_screen["reason_codes"] and code not in issues:
                        issues.append(code)
            critic_response_audit = None
            if role == "Critic" and mandatory_critical_review:
                critic_response_audit = assess_critic(
                    answer, mandatory_critical_review
                )
                if critic_response_audit["audit"] == "critic_failed_to_challenge":
                    issues.append("critic_failed_to_challenge")
            _observe(memory, issues)
            turn = {
                "round": round_number,
                "role": role,
                "response": answer,
                "status": (
                    "held_pending_evidence" if scientific_screen
                    and scientific_screen["decision"] == "hold_for_independent_review"
                    else "unverified model deliberation"
                ),
                "issue_codes": issues,
            }
            if scientific_screen is not None:
                turn["scientific_screen"] = scientific_screen
            if critic_response_audit is not None:
                turn["critic_response_audit"] = critic_response_audit
                # The deterministic objections are carried intact even when
                # the LLM fails to formulate a rigorous scientific critique.
                turn["review_obligations"] = mandatory_critical_review
            turns.append(turn)
            previous_by_role[role] = answer
            recipient = MODEL_ROLES[(idx + 1) % len(MODEL_ROLES)]
            ledger.send(role, recipient, "debate_reply", turn)

    chain = [record.__dict__ for record in ledger.messages]
    if not verify_chain(chain):
        raise RuntimeError("Discussion ledger hash chain failed verification")
    memory["completed_cycles"] = min(10000, memory["completed_cycles"] + 1)
    return {
        "rounds": rounds,
        "turns": turns,
        "messages": chain,
        "chain_verified": True,
        "candidate_reviews": [
            {"round": turn["round"], "status": turn["status"],
             "scientific_screen": turn["scientific_screen"],
             "candidate": turn["response"]}
            for turn in turns if turn["role"] == "Inventor"
        ],
        "final_tentative_candidate": (
            latest_proposal["text"] if latest_proposal
            and latest_proposal["screen"]["decision"] == "tentative_only" else None
        ),
        "publication_gate": (
            "tentative_review_only" if latest_proposal
            and latest_proposal["screen"]["decision"] == "tentative_only"
            else "hold_for_independent_review"
        ),
        "memory_before": before,
        "memory_after": memory,
        "memory_mechanism": (
            "Allowlisted deterministic error feedback carried into the next "
            "round and restored from the latest successful workflow cache; "
            "no model-weight updates or scientific validation"
        ),
        "scientific_validation": False,
    }


def load_memory_object(value):
    if value is None:
        return load_memory("/nonexistent/bioreason-memory.json")
    if not isinstance(value, dict):
        raise ValueError("Memory must be a JSON object")
    # Apply the same strict schema filter as a disk read.
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "memory.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return load_memory(path)
