from __future__ import annotations

import argparse
import json
import sys
import traceback

from .filesystem import find_repo_root
from .inspect import run_inspection


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aios", description="Read-only .ai OS inspection tools")
    subparsers = parser.add_subparsers(dest="command")

    inspect_parser = subparsers.add_parser("inspect", help="Inspect repository reference integrity")
    inspect_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    inspect_parser.add_argument(
        "--summary-only",
        action="store_true",
        help="With --json, omit passing checks to keep output compact",
    )

    args = parser.parse_args(argv)
    if args.command != "inspect":
        parser.print_help()
        return 2

    root = find_repo_root()
    if root is None:
        print("aios inspect: cannot determine repository root", file=sys.stderr)
        return 2

    try:
        result = run_inspection(root)
        if args.json:
            print(json.dumps(result.to_dict(summary_only=args.summary_only), ensure_ascii=False, indent=2))
        else:
            _print_human_summary(result)
        return 1 if result.status == "fail" else 0
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        if args.json:
            print(json.dumps({"status": "crash", "error": str(exc)}, ensure_ascii=False, indent=2))
        else:
            print(f"aios inspect crashed: {exc}", file=sys.stderr)
            traceback.print_exc()
        return 2


def _print_human_summary(result) -> None:
    data = result.to_dict()
    summary = data["summary"]
    print("AIOS Inspect v1")
    print(f"Root: {data['root']}")
    print(f"Status: {data['status']}")
    print(
        "Summary: "
        f"{summary['errors']} fail, "
        f"{summary['warnings']} warning, "
        f"{summary['info']} info, "
        f"{summary['passes']} pass"
    )
    print(
        "Inventory: "
        f"{summary['files_scanned']} files scanned, "
        f"{summary['skills_found']} skills, "
        f"{summary['workflows_found']} workflow files"
    )

    grouped = {"fail": [], "warning": [], "info": []}
    for check in data["checks"]:
        if check["status"] in grouped:
            grouped[check["status"]].append(check)

    for status, title in [("fail", "Failures"), ("warning", "Warnings"), ("info", "Info")]:
        entries = grouped[status]
        if not entries:
            continue
        print()
        print(f"{title}:")
        for check in entries:
            source = f" [{check['source']}]" if "source" in check else ""
            print(f"- {check['id']}{source}: {check['message']}")
            details = check.get("details", {})
            if "line" in details:
                print(f"  line: {details['line']}")
            if "recommendation" in details and details["recommendation"]:
                print(f"  recommendation: {details['recommendation']}")
            if "paths" in details:
                for path in details["paths"][:10]:
                    print(f"  path: {path}")
            if "hits" in details:
                for hit in details["hits"][:10]:
                    print(f"  hit: {hit['file']}:{hit['line']}")
