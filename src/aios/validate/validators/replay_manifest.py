from __future__ import annotations

import json
from pathlib import Path

from ...filesystem import rel_path
from ...status import SEVERITY_ERROR, SEVERITY_INFO
from ...sync.replay import load_replay_manifest
from ..result import ValidationRun
from ..targets import ValidationTarget


def validate_replay_manifest(root: Path, target: ValidationTarget, run: ValidationRun) -> None:
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
