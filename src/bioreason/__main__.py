"""Command-line entry point for BioReason."""
import argparse
import json
from .core import coordinator, fetch
from .council import run_council


def main():
    parser = argparse.ArgumentParser(description="BioReason evidence-first research triage")
    parser.add_argument("query", help="Europe PMC query")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--input", help="Local JSON array for offline runs")
    parser.add_argument("--legacy", action="store_true", help="Use the original flat pipeline")
    parser.add_argument("--model-roles", default="", help="Comma-separated opt-in model roles: Analyst,Inventor,Critic")
    args = parser.parse_args()
    if args.input:
        with open(args.input, encoding="utf-8") as handle:
            papers = json.load(handle)
    else:
        papers = fetch(args.query, args.limit)
    roles = tuple(x.strip() for x in args.model_roles.split(",") if x.strip())
    if args.legacy and roles:
        parser.error("--model-roles cannot be combined with --legacy")
    result = coordinator(args.query, papers) if args.legacy else run_council(args.query, papers, model_roles=roles)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
