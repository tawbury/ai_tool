from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..status import STATUS_FAIL, STATUS_PASS, STATUS_WARN


SYNC_DRY_RUN_SCHEMA_VERSION = "aios.sync_dry_run.v0"

SEVERITY_INFORMATIONAL = "informational"
SEVERITY_WARNING = "warning"
SEVERITY_BLOCKING = "blocking"

ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACTION_SKIP = "skip"
ACTION_CONFLICT = "conflict"
ACTION_DRIFT_STOP = "drift-stop"
ACTION_ORPHAN_WARNING = "orphan-warning"


@dataclass(frozen=True)
class SyncDryRunMessage:
    code: str
    severity: str
    status: str
    message: str
    path: str | None = None
    line: int | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity,
            "status": self.status,
            "message": self.message,
        }
        if self.path:
            data["path"] = self.path
        if self.line is not None:
            data["line"] = self.line
        if self.details:
            data["details"] = self.details
        return data


@dataclass(frozen=True)
class SyncDryRunItem:
    entry_id: str
    action: str
    severity: str
    stop_reason: str | None
    recovery_hint: str | None
    source_path: str | None
    target_path: str
    ownership: str
    sync_mode: str
    drift_state: str
    hashes: dict[str, Any] = field(default_factory=dict)
    marker: dict[str, Any] | None = None
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def status(self) -> str:
        if self.severity == SEVERITY_BLOCKING:
            return STATUS_FAIL
        if self.severity == SEVERITY_WARNING:
            return STATUS_WARN
        return STATUS_PASS

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "action": self.action,
            "severity": self.severity,
            "stop_reason": self.stop_reason,
            "recovery_hint": self.recovery_hint,
            "source_path": self.source_path,
            "target_path": self.target_path,
            "ownership": self.ownership,
            "sync_mode": self.sync_mode,
            "drift_state": self.drift_state,
            "hashes": self.hashes,
            "marker": self.marker,
            "details": self.details,
        }


@dataclass(frozen=True)
class SyncDryRunResult:
    root: str
    manifest_path: str | None
    results: list[SyncDryRunItem] = field(default_factory=list)
    messages: list[SyncDryRunMessage] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def status(self) -> str:
        if any(item.severity == SEVERITY_BLOCKING for item in self.results):
            return STATUS_FAIL
        if any(message.status == STATUS_FAIL for message in self.messages):
            return STATUS_FAIL
        if any(item.severity == SEVERITY_WARNING for item in self.results):
            return STATUS_WARN
        if any(message.status == STATUS_WARN for message in self.messages):
            return STATUS_WARN
        return STATUS_PASS

    def summary(self) -> dict[str, int]:
        return {
            "total": len(self.results),
            "create": _count_action(self.results, ACTION_CREATE),
            "update": _count_action(self.results, ACTION_UPDATE),
            "skip": _count_action(self.results, ACTION_SKIP),
            "conflict": _count_action(self.results, ACTION_CONFLICT),
            "drift_stop": _count_action(self.results, ACTION_DRIFT_STOP),
            "orphan_warning": _count_action(self.results, ACTION_ORPHAN_WARNING),
            "blocking": sum(1 for item in self.results if item.severity == SEVERITY_BLOCKING),
            "warnings": sum(1 for item in self.results if item.severity == SEVERITY_WARNING),
            "informational": sum(1 for item in self.results if item.severity == SEVERITY_INFORMATIONAL),
            "messages": len(self.messages),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SYNC_DRY_RUN_SCHEMA_VERSION,
            "status": self.status,
            "root": self.root,
            "mode": "dry-run",
            "manifest_path": self.manifest_path,
            "summary": self.summary(),
            "results": [item.to_dict() for item in self.results],
            "messages": [message.to_dict() for message in self.messages],
            "meta": {"dry_run": True, "mutation_performed": False, **self.meta},
        }


def message_for_item(item: SyncDryRunItem, message: str, *, line: int | None = None) -> SyncDryRunMessage:
    return SyncDryRunMessage(
        code=item.stop_reason or item.action,
        severity="error" if item.severity == SEVERITY_BLOCKING else "warning",
        status=item.status,
        message=message,
        path=item.target_path,
        line=line,
        details={
            "entry_id": item.entry_id,
            "action": item.action,
            "recovery_hint": item.recovery_hint,
        },
    )


def _count_action(results: list[SyncDryRunItem], action: str) -> int:
    return sum(1 for item in results if item.action == action)
