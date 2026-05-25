from __future__ import annotations

import json
from pathlib import Path

from ...filesystem import rel_path
from ...providers.capability import validate_provider_capability_data
from ...status import SEVERITY_ERROR, SEVERITY_INFO
from ..result import ValidationRun
from ..targets import ValidationTarget


STATIC_DETAILS = {
    "provider_execution": False,
    "sandbox_execution": False,
    "mutation_performed": False,
}


def validate_provider_capability(root: Path, target: ValidationTarget, run: ValidationRun) -> None:
    path = target.path
    if path is None:
        return

    try:
        source = rel_path(root, path)
    except ValueError:
        source = str(path)
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        run.add(
            "provider-capability",
            "invalid_json",
            SEVERITY_ERROR,
            f"Provider capability must be valid JSON: {exc.msg}",
            path=source,
            line=exc.lineno,
            **STATIC_DETAILS,
        )
        return

    result = validate_provider_capability_data(data)
    for issue in result.issues:
        run.add(
            "provider-capability",
            issue.code,
            issue.severity,
            issue.message,
            path=source,
            field=issue.field,
            **STATIC_DETAILS,
        )

    if result.errors:
        return

    capability = data if isinstance(data, dict) else {}
    run.add(
        "provider-capability",
        "provider_capability_checked",
        SEVERITY_INFO,
        "Provider capability declaration was statically validated without provider execution, sandbox execution, discovery, adapter execution, generated content, or mutation.",
        path=source,
        provider_id=capability.get("provider_id"),
        provider_version=capability.get("provider_version"),
        supported_sync_modes=capability.get("supported_sync_modes"),
        deterministic_capable=capability.get("deterministic_capable"),
        no_write_capable=capability.get("no_write_capable"),
        network_policy=capability.get("network_policy"),
        **STATIC_DETAILS,
    )
