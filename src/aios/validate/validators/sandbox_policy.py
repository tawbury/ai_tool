from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ...filesystem import rel_path
from ...providers.sandbox_policy import validate_sandbox_policy_data
from ...status import SEVERITY_ERROR, SEVERITY_INFO
from ..result import ValidationRun
from ..targets import ValidationTarget


STATIC_DETAILS = {
    "sandbox_execution": False,
    "subprocess_execution": False,
    "provider_execution": False,
    "mutation_performed": False,
}


def validate_sandbox_policy(root: Path, target: ValidationTarget, run: ValidationRun) -> None:
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
            "sandbox-policy",
            "invalid_json",
            SEVERITY_ERROR,
            f"Sandbox policy must be valid JSON: {exc.msg}",
            path=source,
            line=exc.lineno,
            **STATIC_DETAILS,
        )
        return

    policy = data if isinstance(data, dict) else {}
    policy_details = _policy_details(policy)
    result = validate_sandbox_policy_data(data)
    for issue in result.issues:
        run.add(
            "sandbox-policy",
            issue.code,
            issue.severity,
            issue.message,
            path=source,
            field=issue.field,
            **policy_details,
            **STATIC_DETAILS,
        )

    if result.errors:
        return

    run.add(
        "sandbox-policy",
        "sandbox_policy_checked",
        SEVERITY_INFO,
        "Sandbox policy was statically validated without sandbox launch, subprocess execution, provider execution, replay execution, generated content, or mutation.",
        path=source,
        sandbox_mode=policy.get("sandbox_mode"),
        network_disabled=policy.get("network_disabled"),
        deterministic_execution=policy.get("deterministic_execution"),
        no_write_required=policy.get("no_write_required"),
        **STATIC_DETAILS,
    )


def _policy_details(policy: dict[str, Any]) -> dict[str, Any]:
    details: dict[str, Any] = {}
    for key in ("sandbox_mode", "network_disabled", "deterministic_execution", "no_write_required"):
        if key in policy:
            details[key] = policy.get(key)
    return details
