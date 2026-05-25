from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ...filesystem import rel_path
from ...providers.trace import validate_provider_execution_trace_data
from ...status import SEVERITY_ERROR, SEVERITY_INFO
from ..result import ValidationRun
from ..targets import ValidationTarget


STATIC_DETAILS = {
    "provider_execution": False,
    "sandbox_execution": False,
    "mutation_performed": False,
}


def validate_provider_execution_trace(root: Path, target: ValidationTarget, run: ValidationRun) -> None:
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
            "provider-execution-trace",
            "invalid_json",
            SEVERITY_ERROR,
            f"Provider execution trace must be valid JSON: {exc.msg}",
            path=source,
            line=exc.lineno,
            **STATIC_DETAILS,
        )
        return

    trace = data if isinstance(data, dict) else {}
    trace_details = _trace_details(trace)
    result = validate_provider_execution_trace_data(data)
    for issue in result.issues:
        run.add(
            "provider-execution-trace",
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
        "provider-execution-trace",
        "provider_execution_trace_checked",
        SEVERITY_INFO,
        "Provider execution trace was statically validated without provider execution, sandbox execution, replay execution, generated content, or mutation.",
        path=source,
        provider_id=trace.get("provider_id"),
        provider_version=trace.get("provider_version"),
        provider_mode=trace.get("provider_mode"),
        deterministic_execution=trace.get("deterministic_execution"),
        no_write_confirmed=trace.get("no_write_confirmed"),
        network_disabled=trace.get("network_disabled"),
        **STATIC_DETAILS,
    )


def _trace_details(trace: dict[str, Any]) -> dict[str, Any]:
    details: dict[str, Any] = {}
    for key in ("provider_id", "provider_version", "provider_mode", "failure_code", "unavailable_reason"):
        if key in trace:
            details[key] = trace.get(key)
    return details
