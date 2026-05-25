from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ...filesystem import rel_path
from ...providers.sandbox_result import validate_sandbox_execution_result_data
from ...status import SEVERITY_ERROR, SEVERITY_INFO
from ..result import ValidationRun
from ..targets import ValidationTarget


STATIC_DETAILS = {
    "sandbox_execution": False,
    "subprocess_execution": False,
    "provider_execution": False,
    "replay_execution": False,
    "mutation_performed": False,
}


def validate_sandbox_result(root: Path, target: ValidationTarget, run: ValidationRun) -> None:
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
            "sandbox-result",
            "invalid_json",
            SEVERITY_ERROR,
            f"Sandbox result must be valid JSON: {exc.msg}",
            path=source,
            line=exc.lineno,
            **STATIC_DETAILS,
        )
        return

    result_data = data if isinstance(data, dict) else {}
    result_details = _result_details(result_data)
    validation = validate_sandbox_execution_result_data(data)
    for issue in validation.issues:
        run.add(
            "sandbox-result",
            issue.code,
            issue.severity,
            issue.message,
            path=source,
            field=issue.field,
            **result_details,
            **STATIC_DETAILS,
        )

    if validation.errors:
        return

    run.add(
        "sandbox-result",
        "sandbox_result_checked",
        SEVERITY_INFO,
        "Sandbox result was statically validated without sandbox launch, subprocess execution, provider execution, replay execution, generated content, or mutation.",
        path=source,
        sandbox_mode=result_data.get("sandbox_mode"),
        request_id=result_data.get("request_id"),
        status=result_data.get("status"),
        failure_code=result_data.get("failure_code"),
        trace_id=result_data.get("trace_id"),
        network_disabled=result_data.get("network_disabled"),
        no_write_confirmed=result_data.get("no_write_confirmed"),
        **STATIC_DETAILS,
    )


def _result_details(result_data: dict[str, Any]) -> dict[str, Any]:
    details: dict[str, Any] = {}
    for key in ("sandbox_mode", "request_id", "status", "failure_code", "trace_id", "network_disabled", "no_write_confirmed"):
        if key in result_data:
            details[key] = result_data.get(key)
    return details
