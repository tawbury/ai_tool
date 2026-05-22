from __future__ import annotations

import argparse
import json
import sys
import traceback

from .filesystem import find_repo_root
from .inspect import run_inspection
from .semantic_loader import LoaderInput, load_context
from .semantic_loader.models import VALID_PROFILES
from .validate.engine import run_validation
from .validate.targets import resolve_targets


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
    load_parser = subparsers.add_parser("load-context", help="Extract semantic context from a Markdown file")
    load_parser.add_argument("path", help="Markdown file to load")
    load_parser.add_argument(
        "--profile",
        default="minimal-worker",
        help="Loading profile to use (default: minimal-worker)",
    )
    load_parser.add_argument(
        "--include-layer",
        action="append",
        default=[],
        help="Semantic layer to include in addition to profile defaults. Repeatable.",
    )
    load_parser.add_argument(
        "--exclude-layer",
        action="append",
        default=[],
        help="Semantic layer to exclude in addition to profile defaults. Repeatable.",
    )
    load_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    load_parser.add_argument("--no-content", action="store_true", help="With --json, omit chunk content")
    load_parser.add_argument("--summary-only", action="store_true", help="With --json, omit chunks and exclusions")

    validate_parser = subparsers.add_parser("validate", help="Run read-only executable validation checks")
    validate_parser.add_argument("path", nargs="?", help="Optional file path to validate")
    validate_parser.add_argument("--agent", help="Validate a named agent, such as developer")
    validate_parser.add_argument("--workflow", help="Validate a named workflow, such as l2_review")
    validate_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    args = parser.parse_args(argv)
    if args.command not in {"inspect", "load-context", "validate"}:
        parser.print_help()
        return 2

    if args.command == "load-context" and args.profile not in VALID_PROFILES:
        valid = ", ".join(sorted(VALID_PROFILES))
        print(f"aios load-context: unknown profile '{args.profile}'. Valid profiles: {valid}", file=sys.stderr)
        return 2

    root = find_repo_root()
    if root is None:
        print("aios: cannot determine repository root", file=sys.stderr)
        return 2

    try:
        if args.command == "inspect":
            result = run_inspection(root)
            if args.json:
                print(json.dumps(result.to_dict(summary_only=args.summary_only), ensure_ascii=False, indent=2))
            else:
                _print_human_summary(result)
            return 1 if result.status == "fail" else 0

        if args.command == "validate":
            try:
                targets = resolve_targets(root, path_arg=args.path, agent=args.agent, workflow=args.workflow)
            except ValueError as exc:
                print(f"aios validate: {exc}", file=sys.stderr)
                return 2
            result = run_validation(root, targets)
            if args.json:
                print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            else:
                _print_validate_summary(root, result)
            return 1 if result.status == "fail" else 0

        bundle = load_context(
            root,
            LoaderInput(
                path=args.path,
                profile=args.profile,
                include_layers=set(args.include_layer),
                excluded_layers=set(args.exclude_layer),
            ),
        )
        if args.json:
            print(
                json.dumps(
                    bundle.to_dict(include_content=not args.no_content, summary_only=args.summary_only),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            _print_load_context_summary(bundle)
        return 0
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        if args.json:
            print(json.dumps({"status": "crash", "error": str(exc)}, ensure_ascii=False, indent=2))
        else:
            print(f"aios {args.command} crashed: {exc}", file=sys.stderr)
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


def _print_load_context_summary(bundle) -> None:
    data = bundle.to_dict(include_content=False)
    summary = data["summary"]
    print("AIOS Semantic Loader v1")
    print(f"Root: {data['root']}")
    print(f"Target: {data['target']}")
    print(f"Profile: {data['profile']}")
    print(f"Status: {data['status']}")
    print(
        "Summary: "
        f"{summary['chunks']} chunks, "
        f"{summary['excluded']} excluded, "
        f"{summary['warnings']} warnings, "
        f"{summary['chars']} chars"
    )

    if data["chunks"]:
        print()
        print("Loaded Chunks:")
        for chunk in data["chunks"]:
            print(
                f"- {chunk['semantic_layer']} "
                f"[{chunk['path']}:{chunk['line_start']}-{chunk['line_end']}] "
                f"{chunk['extraction_method']} confidence={chunk['confidence']} chars={chunk['chars']}"
            )

    if data["excluded"]:
        print()
        print("Excluded Layers:")
        for item in data["excluded"]:
            print(
                f"- {item['semantic_layer']} "
                f"[{item['path']}:{item['line_start']}-{item['line_end']}] "
                f"reason={item['reason']}"
            )

    if data["warnings"]:
        print()
        print("Warnings:")
        for warning in data["warnings"]:
            print(f"- {warning['code']} [{warning['path']}]: {warning['message']}")


def _print_validate_summary(root, result) -> None:
    data = result.to_dict()
    summary = data["summary"]
    print("AIOS Validate v0")
    print(f"Root: {root}")
    print(f"Status: {data['status']}")
    print(f"Target: {data['target'].get('kind')} {data['target'].get('label')}")
    print(
        "Summary: "
        f"{summary['errors']} error, "
        f"{summary['warnings']} warning, "
        f"{summary['info']} info, "
        f"{summary['results']} results"
    )

    grouped = {"error": [], "warning": [], "info": []}
    for item in data["results"]:
        grouped.get(item["severity"], []).append(item)

    for severity, title in [("error", "Errors"), ("warning", "Warnings"), ("info", "Info")]:
        entries = grouped[severity]
        if not entries:
            continue
        print()
        print(f"{title}:")
        for item in entries:
            location = f" [{item['path']}]" if item.get("path") else ""
            line = f":{item['line']}" if item.get("line") else ""
            print(f"- {item['code']}{location}{line}: {item['message']}")
