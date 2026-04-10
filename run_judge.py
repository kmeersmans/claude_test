#!/usr/bin/env python3
"""CLI entry point for the LLM judge.

Usage:
    # Judge a single PDF
    python run_judge.py input/my_paper.pdf

    # Judge all PDFs in the input folder
    python run_judge.py --all

    # Judge with a specific provider (overrides config)
    python run_judge.py --provider bedrock input/my_paper.pdf
"""

import argparse
import json
import sys
from pathlib import Path

from src.judge import judge_document
from src.pdf_reader import list_pdfs, INPUT_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM-as-a-Judge: evaluate PDF documents")
    parser.add_argument(
        "pdf",
        nargs="?",
        type=Path,
        help="Path to a single PDF file to evaluate",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help=f"Evaluate all PDFs in {INPUT_DIR}",
    )
    parser.add_argument(
        "--provider",
        choices=["ollama", "bedrock"],
        help="Override the active LLM provider from config",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write JSON results to this file (default: print to stdout)",
    )

    args = parser.parse_args()

    # Apply provider override if requested
    if args.provider:
        import yaml
        from src.config_loader import CONFIG_DIR
        config_path = CONFIG_DIR / "llm_config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        config["active_provider"] = args.provider
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        print(f"[info] Switched active provider to: {args.provider}")

    # Determine which PDFs to process
    if args.all:
        pdfs = list_pdfs()
        if not pdfs:
            print(f"No PDF files found in {INPUT_DIR}", file=sys.stderr)
            sys.exit(1)
    elif args.pdf:
        pdfs = [args.pdf]
    else:
        parser.print_help()
        sys.exit(1)

    # Run the judge on each PDF
    results = []
    for pdf_path in pdfs:
        print(f"\n{'='*60}")
        print(f"  Evaluating: {pdf_path.name}")
        print(f"{'='*60}")
        try:
            result = judge_document(pdf_path)
            results.append(result)

            # Pretty-print evaluations
            for ev in result["evaluations"]:
                print(f"\n  [{ev['criterion_id']}] Score: {ev['score']}")
                print(f"    {ev.get('justification', '')}")

        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            results.append({"document": pdf_path.name, "error": str(e)})

    # Optionally write results to file
    if args.output:
        # Remove raw_response from file output to keep it clean
        clean = []
        for r in results:
            c = {k: v for k, v in r.items() if k != "raw_response"}
            clean.append(c)
        with open(args.output, "w") as f:
            json.dump(clean, f, indent=2)
        print(f"\n[info] Results written to {args.output}")


if __name__ == "__main__":
    main()
