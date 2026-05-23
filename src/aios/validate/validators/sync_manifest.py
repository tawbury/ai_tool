from __future__ import annotations

import json
from pathlib import Path

from ...filesystem import rel_path
from ...status import SEVERITY_ERROR, SEVERITY_INFO
from ...sync.manifest import load_manifest
from ..result import ValidationRun
from ..targets import ValidationTarget


def validate_sync_manifest(root: Path, target: ValidationTarget, run: ValidationRun) -> None:
    path = target.path
    if path is None:
        return

    source = rel_path(root, path)
    try:
        result = load_manifest(path)
    except json.JSONDecodeError as exc:
        run.add(
            "sync-manifest",
            "invalid_json",
            SEVERITY_ERROR,
            f"Sync manifest must be valid JSON: {exc.msg}",
            path=source,
            line=exc.lineno,
        )
        return

    for issue in result.issues:
        run.add(
            "sync-manifest",
            issue.code,
            issue.severity,
            issue.message,
            path=source,
            field=issue.field,
            entry_id=issue.entry_id,
        )

    if result.manifest is not None:
        run.add(
            "sync-manifest",
            "sync_manifest_checked",
            SEVERITY_INFO,
            "Sync manifest schema was validated without source/target runtime evaluation, marker parsing, hash comparison, or dry-run action classification.",
            path=source,
            entries=len(result.manifest.managed_entries),
            schema_version=result.manifest.schema_version,
        )
