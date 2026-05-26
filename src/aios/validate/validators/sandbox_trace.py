from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ...filesystem import rel_path
from ...providers.sandbox_trace import validate_sandbox_trace_data
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


def validate_sandbox_trace(root: Path, target: ValidationTarget, run: ValidationRun) -> None:
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
            "sandbox-trace",
            "invalid_json",
            SEVERITY_ERROR,
            f"Sandbox trace must be valid JSON: {exc.msg}",
            path=source,
            line=exc.lineno,
            **STATIC_DETAILS,
        )
        return

    trace = data if isinstance(data, dict) else {}
    trace_details = _trace_details(trace)
    result = validate_sandbox_trace_data(data)
    for issue in result.issues:
        run.add(
            "sandbox-trace",
            issue.code,
            issue.severity,
            issue.message,
            path=source,
            field=issue.field,
            **trace_details,
            **STATIC_DETAILS,
        )

    if result.errors:
        return

    run.add(
        "sandbox-trace",
        "sandbox_trace_checked",
        SEVERITY_INFO,
        "Sandbox trace was statically validated without sandbox launch, subprocess execution, provider execution, replay execution, generated content, or mutation.",
        path=source,
        trace_id=trace.get("trace_id"),
        request_id=trace.get("request_id"),
        sandbox_mode=trace.get("sandbox_mode"),
        provider_mode=trace.get("provider_mode"),
        status=trace.get("status"),
        failure_code=trace.get("failure_code"),
        network_disabled=trace.get("network_disabled"),
        no_write_confirmed=trace.get("no_write_confirmed"),
        **STATIC_DETAILS,
    )


def _trace_details(trace: dict[str, Any]) -> dict[str, Any]:
    details: dict[str, Any] = {}
    for key in (
        "trace_id",
        "request_id",
        "sandbox_mode",
        "provider_mode",
        "status",
        "failure_code",
        "network_disabled",
        "no_write_confirmed",
    ):
        if key in trace:
            details[key] = trace.get(key)
    return details
