"""Command-line interface for the Adversary Emulation Playbook."""

from __future__ import annotations

import argparse
import json
import sys

from .emulate import EmulationEngine
from .gap_analyzer import GapAnalyzer
from .playbook_loader import PlaybookLoader


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="aep-emulate",
        description="MITRE ATT&CK adversary emulation with HUMMBL governance",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list command
    list_parser = subparsers.add_parser("list", help="List available playbooks")
    list_parser.add_argument(
        "--playbook-dir", default=None, help="Directory containing playbooks"
    )

    # run command
    run_parser = subparsers.add_parser("run", help="Run an emulation playbook")
    run_parser.add_argument("playbook", help="Playbook name (without extension)")
    run_parser.add_argument(
        "--detection-rules",
        default=None,
        help="JSON file mapping technique_id to deployed rule IDs",
    )
    run_parser.add_argument(
        "--playbook-dir", default=None, help="Directory containing playbooks"
    )
    run_parser.add_argument(
        "--output", default="-", help="Output file (- for stdout)"
    )
    run_parser.add_argument(
        "--gap-analysis",
        action="store_true",
        help="Also output gap analysis for defenders",
    )

    # validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate a playbook without running it"
    )
    validate_parser.add_argument("playbook", help="Playbook name")
    validate_parser.add_argument(
        "--playbook-dir", default=None, help="Directory containing playbooks"
    )

    args = parser.parse_args(argv)

    if args.command == "list":
        loader = PlaybookLoader(args.playbook_dir)
        for name in loader.list_playbooks():
            print(name)
        return 0

    if args.command == "validate":
        loader = PlaybookLoader(args.playbook_dir)
        try:
            playbook = loader.load(args.playbook)
            print(f"Playbook '{playbook.id}' is valid.")
            print(f"  Threat actor: {playbook.threat_actor}")
            print(f"  Steps: {len(playbook.steps)}")
            for step in playbook.steps:
                status = "OK" if step.lab_only else "WARN: lab_only=False"
                print(f"    [{step.technique_id}] {step.technique_name} — {status}")
            return 0
        except Exception as exc:
            print(f"Validation failed: {exc}", file=sys.stderr)
            return 1

    if args.command == "run":
        engine = EmulationEngine(args.playbook_dir)
        detection_rules: dict[str, list[str]] = {}
        if args.detection_rules:
            with open(args.detection_rules, "r", encoding="utf-8") as f:
                detection_rules = json.load(f)

        report = engine.run(args.playbook, detection_rules=detection_rules)
        output = {
            "emulation_report": report.to_dict(),
            "receipts": report.receipts,
        }

        if args.gap_analysis:
            analyzer = GapAnalyzer()
            gap_report = analyzer.analyze(report)
            output["gap_analysis"] = gap_report.to_dict()
            output["defender_summary"] = analyzer.summarize_for_defenders(gap_report)

        json_out = json.dumps(output, indent=2)
        if args.output == "-":
            print(json_out)
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_out + "\n")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
