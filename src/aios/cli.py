from __future__ import annotations

import argparse
import json
import sys
import traceback

from .activation import run_activation_check
from .filesystem import find_repo_root
from .inspect import run_inspection
from .inventory import INVENTORY_TYPES, build_inventory
from .semantic_loader import LoaderInput, load_context
from .semantic_loader.models import VALID_PROFILES
from .status import EXIT_CRASH, EXIT_FAIL, EXIT_PASS, STATUS_FAIL
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
    load_parser.add_argument(
        "--max-chars",
        type=int,
        help="Override the profile hard character budget for included context",
    )

    validate_parser = subparsers.add_parser("validate", help="Run read-only executable validation checks")
    validate_parser.add_argument("path", nargs="?", help="Optional file path to validate")
    validate_parser.add_argument("--agent", help="Validate a named agent, such as developer")
    validate_parser.add_argument("--workflow", help="Validate a named workflow, such as l2_review")
    validate_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    validate_parser.add_argument(
        "--summary-only",
        action="store_true",
        help="With --json, omit the full results list and include only non-empty severity groups",
    )
    validate_parser.add_argument(
        "--include-pass",
        action="store_true",
        help="With --json, include explicit pass results when the result model records them",
    )

    inventory_parser = subparsers.add_parser("inventory", help="Discover .ai OS repository inventory")
    inventory_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    inventory_parser.add_argument(
        "--type",
        choices=sorted(INVENTORY_TYPES),
        help="Filter inventory by item type",
    )
    inventory_parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Omit inventory items and emit only summary counts",
    )

    activation_parser = subparsers.add_parser("activation", help="Validate an activation YAML contract")
    activation_parser.add_argument("path", help="Activation YAML file to validate")
    activation_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    activation_parser.add_argument(
        "--summary-only",
        action="store_true",
        help="With --json, omit activation body and reference details",
    )

    args = parser.parse_args(argv)
    if args.command not in {"inspect", "load-context", "validate", "inventory", "activation"}:
        parser.print_help()
        return EXIT_CRASH

    if args.command == "load-context" and args.profile not in VALID_PROFILES:
        valid = ", ".join(sorted(VALID_PROFILES))
        print(f"aios load-context: unknown profile '{args.profile}'. Valid profiles: {valid}", file=sys.stderr)
        return EXIT_CRASH

    root = find_repo_root()
    if root is None:
        print("aios: cannot determine repository root", file=sys.stderr)
        return EXIT_CRASH

    try:
        if args.command == "inspect":
            result = run_inspection(root)
            if args.json:
                print(json.dumps(result.to_dict(summary_only=args.summary_only), ensure_ascii=False, indent=2))
            else:
                _print_human_summary(result)
            return EXIT_FAIL if result.status == STATUS_FAIL else EXIT_PASS

        if args.command == "validate":
            try:
                targets = resolve_targets(root, path_arg=args.path, agent=args.agent, workflow=args.workflow)
            except ValueError as exc:
                print(f"aios validate: {exc}", file=sys.stderr)
                return EXIT_CRASH
            result = run_validation(root, targets)
            if args.json:
                print(
                    json.dumps(
                        result.to_dict(summary_only=args.summary_only, include_pass=args.include_pass),
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            else:
                _print_validate_summary(root, result)
            return EXIT_FAIL if result.status == STATUS_FAIL else EXIT_PASS

        if args.command == "inventory":
            inventory = build_inventory(root).filter_type(args.type)
            if args.json:
                print(json.dumps(inventory.to_dict(summary_only=args.summary_only), ensure_ascii=False, indent=2))
            else:
                _print_inventory_summary(inventory, summary_only=args.summary_only)
            return EXIT_PASS

        if args.command == "activation":
            activation_path = (root / args.path).resolve()
            if not activation_path.is_file():
                print(f"aios activation: target does not exist: {args.path}", file=sys.stderr)
                return EXIT_FAIL
            result = run_activation_check(root, activation_path)
            if args.json:
                print(json.dumps(result.to_dict(summary_only=args.summary_only), ensure_ascii=False, indent=2))
            else:
                _print_activation_summary(result)
            return EXIT_FAIL if result.status == STATUS_FAIL else EXIT_PASS

        bundle = load_context(
            root,
            LoaderInput(
                path=args.path,
                profile=args.profile,
                include_layers=set(args.include_layer),
                excluded_layers=set(args.exclude_layer),
                max_chars=args.max_chars,
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
        return EXIT_PASS
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        if args.json:
            print(json.dumps({"status": "crash", "error": str(exc)}, ensure_ascii=False, indent=2))
        else:
            print(f"aios {args.command} crashed: {exc}", file=sys.stderr)
            traceback.print_exc()
        return EXIT_CRASH


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
    budget = data.get("budget", {})
    if budget:
        print(
            "Budget: "
            f"{budget['used_chars']} used, "
            f"{budget['soft_chars']} soft, "
            f"{budget['hard_chars']} hard, "
            f"{budget['excluded_chars']} excluded, "
            f"{budget['budget_excluded_chunks']} budget-excluded chunks"
        )
        budget_warnings = [
            warning["code"]
            for warning in data.get("warnings", [])
            if warning["code"].startswith("budget_")
        ]
        if budget_warnings:
            print(f"Budget Warnings: {', '.join(budget_warnings)}")

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


def _print_inventory_summary(inventory, summary_only: bool = False) -> None:
    data = inventory.to_dict(summary_only=summary_only)
    print("AIOS Inventory v0")
    print(f"Root: {data['root']}")
    print(f"Status: {data['status']}")
    print(f"Total: {data['summary']['total']}")
    print("Counts:")
    for item_type, count in data["summary"]["counts"].items():
        if count:
            print(f"- {item_type}: {count}")

    if summary_only:
        return

    items = data.get("items", [])
    if not items:
        return
    print()
    print("Items:")
    for item in items:
        print(f"- {item['type']} {item['name']} [{item['relative_path']}]")


def _print_activation_summary(result) -> None:
    data = result.to_dict(summary_only=False)
    summary = data["summary"]
    print("AIOS Activation")
    print(f"Root: {data['root']}")
    print(f"Target: {data['path']}")
    print(f"Schema: {summary['activation_schema_version']}")
    print(f"Status: {data['status']}")
    print(
        "Summary: "
        f"{summary['errors']} error, "
        f"{summary['warnings']} warning, "
        f"{summary['info']} info, "
        f"{summary['resolved_references']}/{summary['references']} references resolved"
    )
    print("Inactive Counts:")
    for item_type, count in summary["inactive_counts"].items():
        print(f"- {item_type}: {count}")

    if data["issues"]:
        print()
        print("Issues:")
        for issue in data["issues"]:
            field = f" [{issue['field']}]" if issue.get("field") else ""
            reference = f" reference={issue['reference']}" if issue.get("reference") else ""
            print(f"- {issue['severity']} {issue['code']}{field}:{reference} {issue['message']}")

    unresolved = [ref for ref in data.get("references", []) if not ref["resolved"]]
    if unresolved:
        print()
        print("Unknown References:")
        for ref in unresolved:
            print(f"- {ref['type']}: {ref['reference']}")
