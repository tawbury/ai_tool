from __future__ import annotations

import json
from pathlib import Path

from ...filesystem import rel_path
from ...status import SEVERITY_ERROR, SEVERITY_INFO
from ...sync.replay import compare_replay_outputs, load_replay_manifest
from ..result import ValidationRun
from ..targets import ValidationTarget


def validate_replay_manifest(
    root: Path,
    target: ValidationTarget,
    run: ValidationRun,
    replay_compare: str | None = None,
) -> None:
    path = target.path
    if path is None:
        return

    try:
        source = rel_path(root, path)
    except ValueError:
        source = str(path)
    try:
        result = load_replay_manifest(path)
    except json.JSONDecodeError as exc:
        run.add(
            "replay-manifest",
            "invalid_json",
            SEVERITY_ERROR,
            f"Replay manifest must be valid JSON: {exc.msg}",
            path=source,
            line=exc.lineno,
        )
        return

    for issue in result.issues:
        run.add(
            "replay-manifest",
            issue.code,
            issue.severity,
            issue.message,
            path=source,
            field=issue.field,
            case_id=issue.case_id,
        )

    if result.manifest is not None:
        run.add(
            "replay-manifest",
            "replay_manifest_checked",
            SEVERITY_INFO,
            "Replay manifest fixtures were statically validated without provider execution, adapter execution, generated content creation, or output replay.",
            path=source,
            cases=len(result.manifest.cases),
            schema_version=result.manifest.schema_version,
            provider_id=result.manifest.provider_id,
            provider_version=result.manifest.provider_version,
        )
        if replay_compare == "fixture":
            _compare_replay_fixtures(path, source, result.manifest.cases, run)


def _compare_replay_fixtures(path: Path, source: str, cases, run: ValidationRun) -> None:
    checked = 0
    comparison_errors = 0
    replay_root = path.resolve().parent.parent
    for case in cases:
        fixture_path = replay_root / case.expected_output_fixture
        try:
            with fixture_path.open("r", encoding="utf-8") as handle:
                expected = json.load(handle)
        except FileNotFoundError:
            run.add(
                "replay-manifest",
                "replay_fixture_missing",
                SEVERITY_ERROR,
                "Replay expected output fixture is missing.",
                path=source,
                field="expected_output_fixture",
                case_id=case.case_id,
                comparison_mode="fixture",
            )
            comparison_errors += 1
            continue
        except json.JSONDecodeError as exc:
            run.add(
                "replay-manifest",
                "replay_fixture_invalid_json",
                SEVERITY_ERROR,
                f"Replay expected output fixture must be valid JSON: {exc.msg}",
                path=source,
                line=exc.lineno,
                field="expected_output_fixture",
                case_id=case.case_id,
                comparison_mode="fixture",
            )
            comparison_errors += 1
            continue
        if not isinstance(expected, dict):
            run.add(
                "replay-manifest",
                "replay_fixture_not_object",
                SEVERITY_ERROR,
                "Replay expected output fixture must be a JSON object.",
                path=source,
                field="expected_output_fixture",
                case_id=case.case_id,
                comparison_mode="fixture",
            )
            comparison_errors += 1
            continue

        candidate = dict(expected)
        for issue in compare_replay_outputs(expected, candidate, case_id=case.case_id):
            comparison_errors += 1
            details = issue.to_dict()
            details.pop("code", None)
            details.pop("severity", None)
            details.pop("status", None)
            message = details.pop("message", issue.message)
            comparison_field = details.pop("comparison_field", issue.comparison_field)
            case_id = details.pop("case_id", issue.case_id)
            run.add(
                "replay-manifest",
                issue.code,
                issue.severity,
                message,
                path=source,
                case_id=case_id,
                comparison_field=comparison_field,
                comparison_mode="fixture",
                **details,
            )
        checked += 1

    if comparison_errors:
        return

    run.add(
        "replay-manifest",
        "replay_comparison_checked",
        SEVERITY_INFO,
        "Fixture-backed replay comparison completed without provider execution, adapter execution, generated content creation, or snapshot update.",
        path=source,
        comparison_mode="fixture",
        cases=checked,
    )
