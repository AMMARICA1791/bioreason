"""Executable, auditable eight-role council with explicit message handoffs.

Roles are software agents with isolated handlers and shared immutable messages.
They are not independently hosted LLMs.
"""
from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from .core import scout, analyst, inventor, critic, validator
from .model import ask_model

MODEL_ROLES = ("Scout", "Analyst", "Inventor", "Critic",
               "Validator", "Builder", "Auditor", "Coordinator")


@dataclass(frozen=True)
class Message:
    sequence: int
    sender: str
    recipient: str
    kind: str
    payload: dict
    previous_hash: str
    digest: str


def _message(sequence, sender, recipient, kind, payload, previous_hash):
    canonical = json.dumps(
        [sequence, sender, recipient, kind, payload, previous_hash],
        sort_keys=True, ensure_ascii=False, default=str,
    )
    digest = sha256(canonical.encode("utf-8")).hexdigest()
    return Message(sequence, sender, recipient, kind, payload, previous_hash, digest)


class Council:
    """Coordinator invokes bounded agents and records every inter-agent handoff."""

    def __init__(self, model_roles=()):
        self.model_roles = frozenset(model_roles)
        if not self.model_roles.issubset(MODEL_ROLES):
            raise ValueError("Model roles must be named council roles")
        self.messages = []
        self.results = {}

    def send(self, sender, recipient, kind, payload):
        previous = self.messages[-1].digest if self.messages else "GENESIS"
        msg = _message(len(self.messages) + 1, sender, recipient, kind, payload, previous)
        self.messages.append(msg)
        return msg

    def execute(self, query, papers):
        if not isinstance(papers, list):
            raise ValueError("papers must be a list")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a nonempty string")
        for paper in papers:
            if not isinstance(paper, dict) or not isinstance(paper.get("title", ""), str):
                raise ValueError("each paper must have a string title")

        self.send("Coordinator", "Scout", "collect", {"query": query, "count": len(papers)})
        self.results["Scout"] = scout(papers)
        if "Scout" in self.model_roles:
            self.results["Scout"]["model_suggestion"] = ask_model(
                "Scout", {"query": query, "papers": papers}
            )
        self.send("Scout", "Analyst", "records", {
            "count": len(papers),
            "model_suggestion": self.results["Scout"].get("model_suggestion"),
        })

        self.results["Analyst"] = analyst(papers)
        if "Analyst" in self.model_roles:
            self.results["Analyst"]["model_suggestion"] = ask_model(
                "Analyst", {"query": query, "papers": papers,
                            "scout": self.results["Scout"]}
            )
        self.send("Analyst", "Inventor", "title_terms", self.results["Analyst"])
        self.results["Inventor"] = inventor(self.results["Analyst"])
        if "Inventor" in self.model_roles:
            self.results["Inventor"]["model_suggestion"] = ask_model("Inventor", {"query": query, "analysis": self.results["Analyst"]})
        self.send("Inventor", "Critic", "candidate", self.results["Inventor"])

        self.results["Critic"] = critic(papers)
        if "Critic" in self.model_roles:
            self.results["Critic"]["model_suggestion"] = ask_model("Critic", {"query": query, "candidate": self.results["Inventor"]})
        self.send("Critic", "Validator", "review", self.results["Critic"])
        self.results["Validator"] = validator(papers)
        if "Validator" in self.model_roles:
            self.results["Validator"]["model_suggestion"] = ask_model(
                "Validator", {"query": query, "papers": papers,
                              "critique": self.results["Critic"]}
            )
        self.send("Validator", "Builder", "evidence_status", self.results["Validator"])

        self.results["Builder"] = {
            "agent": "Builder",
            "status": "candidate report assembled",
            "candidate_question": self.results["Inventor"]["candidate_question"],
            "limitations": self.results["Critic"]["limitations"],
            "model_candidates": {
                role: self.results[role]["model_suggestion"]
                for role in ("Analyst", "Inventor", "Critic")
                if "model_suggestion" in self.results[role]
            },
        }
        if "Builder" in self.model_roles:
            self.results["Builder"]["model_suggestion"] = ask_model(
                "Builder", {"query": query, "inventor": self.results["Inventor"],
                            "critic": self.results["Critic"],
                            "validator": self.results["Validator"]}
            )
        self.send("Builder", "Auditor", "report", self.results["Builder"])

        traceable = self.results["Validator"]["traceable_records"]
        audit_passed = (
            self.results["Validator"]["verified_findings"] == 0
            and len(self.results["Critic"]["limitations"]) > 0
            and traceable <= len(papers)
        )
        self.results["Auditor"] = {
            "agent": "Auditor",
            "passed": audit_passed,
            "note": "Workflow consistency only; no scientific validity assessment",
        }
        if "Auditor" in self.model_roles:
            self.results["Auditor"]["model_suggestion"] = ask_model(
                "Auditor", {"query": query, "report": self.results["Builder"],
                            "validator": self.results["Validator"],
                            "deterministic_audit_passed": audit_passed}
            )
        self.send("Auditor", "Coordinator", "audit", self.results["Auditor"])
        self.results["Coordinator"] = {
            "agent": "Coordinator", "status": "completed" if audit_passed else "rejected"
        }
        if "Coordinator" in self.model_roles:
            self.results["Coordinator"]["model_suggestion"] = ask_model(
                "Coordinator", {"query": query, "auditor": self.results["Auditor"],
                                "report": self.results["Builder"]}
            )
        self.send("Coordinator", "Archive", "final", self.results["Coordinator"])
        return {
            "query": query,
            "results": self.results,
            "messages": [asdict(message) for message in self.messages],
            "audit_passed": audit_passed,
            "disclosure": "Deterministic software agents, not independent LLMs or validated scientific reasoning",
        }


def verify_chain(messages):
    previous = "GENESIS"
    for index, record in enumerate(messages, 1):
        expected = _message(
            index, record["sender"], record["recipient"],
            record["kind"], record["payload"], previous
        )
        if record != asdict(expected):
            return False
        previous = expected.digest
    return True


def run_council(query, papers, model_roles=()):
    return Council(model_roles=model_roles).execute(query, papers)
