"""Command-line entry point for BioReason."""
import argparse
import json
from .core import coordinator, fetch


def main():
    parser = argparse.ArgumentParser(description="BioReason evidence-first research triage")
    parser.add_argument("query", help="Europe PMC query")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--input", help="Local JSON array for offline runs")
    args = parser.parse_args()
    if args.input:
        with open(args.input, encoding="utf-8") as handle:
            papers = json.load(handle)
    else:
        papers = fetch(args.query, args.limit)
    print(json.dumps(coordinator(args.query, papers), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
