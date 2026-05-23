from __future__ import annotations

from typing import Any


ENVELOPE_SCHEMA_VERSION = "aios.command_result.v2"


def build_envelope(
    command: str,
    legacy: dict[str, Any],
    *,
    root: str | None = None,
    summary_only: bool = False,
    include_content: bool | None = None,
    full: dict[str, Any] | None = None,
) -> dict[str, Any]:
    full_data = full or legacy
    legacy_status = str(legacy.get("status", "pass"))
    payload = _payload(command, legacy)
    meta: dict[str, Any] = {
        "legacy_schema_version": legacy.get("schema_version"),
        "legacy_status": legacy_status,
        "summary_only": summary_only,
    }
    if include_content is not None:
        meta["include_content"] = include_content
    if command == "sync":
        meta.update(dict(legacy.get("meta", {})))
    omitted = _omitted_payload(command, legacy, full_data)
    if omitted:
        meta["omitted_payload"] = omitted

    return {
        "schema_version": ENVELOPE_SCHEMA_VERSION,
        "command": command,
        "status": _canonical_status(legacy_status),
        "root": root or legacy.get("root"),
        "target": _target(command, legacy),
        "summary": legacy.get("summary", {}),
        "messages": _messages(command, legacy),
        "payload": payload,
        "meta": meta,
    }


def _canonical_status(status: str) -> str:
    if status == "warning":
        return "warn"
    if status == "info":
        return "pass"
    return status


def _status_for_severity(severity: str) -> str:
    if severity == "error":
        return "fail"
    if severity == "warning":
        return "warn"
    return "pass"


def _severity_for_status(status: str) -> str:
    if status == "fail":
        return "error"
    if status in {"warn", "warning"}:
        return "warning"
    if status == "info":
        return "info"
    return "info"


def _target(command: str, legacy: dict[str, Any]) -> dict[str, Any]:
    if command in {"inspect", "inventory"}:
        return {"kind": "repository", "label": "repository", "path": None}
    if command == "validate":
        target = dict(legacy.get("target", {}))
        target.setdefault("kind", "repository")
        target.setdefault("label", target.get("kind", "repository"))
        target.setdefault("path", None)
        return target
    if command == "activation":
        path = legacy.get("path")
        return {"kind": "activation", "label": path, "path": path}
    if command == "load-context":
        target = legacy.get("target")
        return {"kind": "file", "label": target, "path": target}
    if command == "sync":
        path = legacy.get("manifest_path")
        return {"kind": "sync-manifest", "label": path, "path": path}
    return {"kind": command, "label": command, "path": None}


def _payload(command: str, legacy: dict[str, Any]) -> dict[str, Any]:
    if command == "inspect":
        return {"checks": legacy.get("checks", [])}
    if command == "inventory":
        return {"items": legacy.get("items", [])}
    if command == "validate":
        return {"results": legacy.get("results", [])}
    if command == "activation":
        return {
            "activation": legacy.get("activation"),
            "references": legacy.get("references", []),
        }
    if command == "load-context":
        return {
            "chunks": legacy.get("chunks", []),
            "excluded": legacy.get("excluded", []),
            "budget": legacy.get("budget", {}),
        }
    if command == "sync":
        return {"results": legacy.get("results", [])}
    return {}


def _messages(command: str, legacy: dict[str, Any]) -> list[dict[str, Any]]:
    if command == "inspect":
        return [_inspect_message(check) for check in legacy.get("checks", [])]
    if command == "validate":
        items = legacy.get("results")
        if items is None:
            items = [
                *legacy.get("errors", []),
                *legacy.get("warnings", []),
                *legacy.get("info", []),
            ]
        return [_validate_message(item) for item in items]
    if command == "activation":
        return [_activation_message(issue) for issue in legacy.get("issues", [])]
    if command == "load-context":
        return [_loader_message(warning) for warning in legacy.get("warnings", [])]
    if command == "sync":
        return list(legacy.get("messages", []))
    return []


def _inspect_message(check: dict[str, Any]) -> dict[str, Any]:
    status = _canonical_status(str(check.get("status", "pass")))
    details = dict(check.get("details", {}))
    return _clean_message(
        {
            "code": check.get("id", "inspect_check"),
            "severity": _severity_for_status(status),
            "status": status if status != "info" else "pass",
            "message": check.get("message", ""),
            "path": check.get("source"),
            "line": details.pop("line", None),
            "details": details,
        }
    )


def _validate_message(item: dict[str, Any]) -> dict[str, Any]:
    severity = str(item.get("severity", "info"))
    details = dict(item.get("details", {}))
    if item.get("validator"):
        details["validator"] = item["validator"]
    if item.get("recommendation"):
        details["recommendation"] = item["recommendation"]
    return _clean_message(
        {
            "code": item.get("code", "validation_result"),
            "severity": severity,
            "status": _canonical_status(str(item.get("status", _status_for_severity(severity)))),
            "message": item.get("message", ""),
            "path": item.get("path"),
            "line": item.get("line"),
            "details": details,
        }
    )


def _activation_message(issue: dict[str, Any]) -> dict[str, Any]:
    severity = str(issue.get("severity", "info"))
    details = {}
    if issue.get("field"):
        details["field"] = issue["field"]
    if issue.get("reference"):
        details["reference"] = issue["reference"]
    return _clean_message(
        {
            "code": issue.get("code", "activation_issue"),
            "severity": severity,
            "status": _canonical_status(str(issue.get("status", _status_for_severity(severity)))),
            "message": issue.get("message", ""),
            "details": details,
        }
    )


def _loader_message(warning: dict[str, Any]) -> dict[str, Any]:
    return _clean_message(
        {
            "code": warning.get("code", "loader_warning"),
            "severity": "warning",
            "status": "warn",
            "message": warning.get("message", ""),
            "path": warning.get("path"),
        }
    )


def _clean_message(message: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in message.items()
        if value not in (None, {}, [])
    }


def _omitted_payload(
    command: str,
    legacy: dict[str, Any],
    full: dict[str, Any],
) -> dict[str, int]:
    omitted: dict[str, int] = {}
    payload_keys = {
        "inspect": ("checks",),
        "inventory": ("items",),
        "validate": ("results",),
        "activation": ("activation", "references"),
        "load-context": ("chunks", "excluded"),
        "sync": ("results",),
    }.get(command, ())
    for key in payload_keys:
        if key in legacy:
            continue
        value = full.get(key)
        if isinstance(value, list):
            omitted[key] = len(value)
        elif value is not None:
            omitted[key] = 1
    return omitted
