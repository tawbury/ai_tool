from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..status import SEVERITY_ERROR, SEVERITY_WARNING, STATUS_FAIL, STATUS_PASS, STATUS_WARN
from .hash import is_valid_hash_string


MANIFEST_SCHEMA_VERSION = "aios.sync_manifest.v0"

OWNERSHIP_VALUES = {"runtime-managed", "user-owned", "mixed-boundary"}
SYNC_MODE_VALUES = {"whole-file", "managed-block", "mixed-boundary"}
MARKER_STYLE_VALUES = {"markdown-html-comment", "hash-line-comment", "yaml-line-comment"}

_WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")


@dataclass(frozen=True)
class ManifestIssue:
    code: str
    severity: str
    message: str
    field: str | None = None
    entry_id: str | None = None

    @property
    def status(self) -> str:
        if self.severity == SEVERITY_ERROR:
            return STATUS_FAIL
        if self.severity == SEVERITY_WARNING:
            return STATUS_WARN
        return STATUS_PASS

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity,
            "status": self.status,
            "message": self.message,
        }
        if self.field:
            data["field"] = self.field
        if self.entry_id:
            data["entry_id"] = self.entry_id
        return data


@dataclass(frozen=True)
class ManifestEntry:
    entry_id: str
    source_path: str
    target_path: str
    ownership: str
    sync_mode: str
    source_hash: str
    target_hash: str
    marker: dict[str, Any] | None
    generated: dict[str, Any]
    raw: dict[str, Any] = field(repr=False)


@dataclass(frozen=True)
class SyncManifest:
    schema_version: str
    repository_id: str
    generated_at: str
    source_root: str
    target_root: str
    managed_entries: list[ManifestEntry]
    raw: dict[str, Any] = field(repr=False)


@dataclass(frozen=True)
class ManifestValidationResult:
    manifest: SyncManifest | None
    issues: list[ManifestIssue]

    @property
    def status(self) -> str:
        if any(issue.severity == SEVERITY_ERROR for issue in self.issues):
            return STATUS_FAIL
        if any(issue.severity == SEVERITY_WARNING for issue in self.issues):
            return STATUS_WARN
        return STATUS_PASS

    @property
    def errors(self) -> list[ManifestIssue]:
        return [issue for issue in self.issues if issue.severity == SEVERITY_ERROR]

    @property
    def warnings(self) -> list[ManifestIssue]:
        return [issue for issue in self.issues if issue.severity == SEVERITY_WARNING]


def load_manifest(path: Path) -> ManifestValidationResult:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return validate_manifest_data(data)


def validate_manifest_data(data: Any) -> ManifestValidationResult:
    issues: list[ManifestIssue] = []
    if not isinstance(data, dict):
        return ManifestValidationResult(
            None,
            [
                ManifestIssue(
                    "manifest_not_object",
                    SEVERITY_ERROR,
                    "Sync manifest must be a JSON object.",
                )
            ],
        )

    if "manifest_version" in data:
        issues.append(
            ManifestIssue(
                "manifest_version_alias",
                SEVERITY_WARNING,
                "manifest_version is a legacy alias; use schema_version.",
                field="manifest_version",
            )
        )

    _require_fields(
        data,
        ("schema_version", "repository_id", "generated_at", "source_root", "target_root", "managed_entries"),
        issues,
    )

    schema_version = _string_value(data.get("schema_version"))
    if schema_version and schema_version != MANIFEST_SCHEMA_VERSION:
        issues.append(
            ManifestIssue(
                "unsupported_schema_version",
                SEVERITY_ERROR,
                f"Unsupported sync manifest schema_version: {schema_version}",
                field="schema_version",
            )
        )

    source_root = _string_value(data.get("source_root"))
    target_root = _string_value(data.get("target_root"))
    _validate_manifest_path(source_root, "source_root", issues)
    _validate_manifest_path(target_root, "target_root", issues, allow_dot=True)

    entries_raw = data.get("managed_entries")
    entries: list[ManifestEntry] = []
    if "managed_entries" in data and not isinstance(entries_raw, list):
        issues.append(
            ManifestIssue(
                "invalid_managed_entries",
                SEVERITY_ERROR,
                "managed_entries must be a list.",
                field="managed_entries",
            )
        )
        entries_raw = []

    seen_entry_ids: set[str] = set()
    for index, entry_raw in enumerate(entries_raw or []):
        entry, entry_issues = _validate_entry(entry_raw, index, source_root, target_root)
        issues.extend(entry_issues)
        entry_id = _string_value(entry_raw.get("entry_id")) if isinstance(entry_raw, dict) else ""
        if entry_id:
            if entry_id in seen_entry_ids:
                issues.append(
                    ManifestIssue(
                        "duplicate_entry_id",
                        SEVERITY_ERROR,
                        f"Duplicate managed entry id: {entry_id}",
                        field=f"managed_entries[{index}].entry_id",
                        entry_id=entry_id,
                    )
                )
            seen_entry_ids.add(entry_id)
        if entry is not None:
            entries.append(entry)

    manifest = None
    if not any(issue.severity == SEVERITY_ERROR for issue in issues):
        manifest = SyncManifest(
            schema_version=schema_version,
            repository_id=str(data["repository_id"]),
            generated_at=str(data["generated_at"]),
            source_root=source_root,
            target_root=target_root,
            managed_entries=entries,
            raw=data,
        )
    return ManifestValidationResult(manifest, issues)


def _validate_entry(
    entry_raw: Any,
    index: int,
    source_root: str,
    target_root: str,
) -> tuple[ManifestEntry | None, list[ManifestIssue]]:
    issues: list[ManifestIssue] = []
    field_prefix = f"managed_entries[{index}]"
    if not isinstance(entry_raw, dict):
        return (
            None,
            [
                ManifestIssue(
                    "managed_entry_not_object",
                    SEVERITY_ERROR,
                    "Managed entry must be an object.",
                    field=field_prefix,
                )
            ],
        )

    _require_fields(
        entry_raw,
        ("entry_id", "source_path", "target_path", "ownership", "sync_mode", "source_hash", "target_hash", "generated"),
        issues,
        field_prefix=field_prefix,
    )

    entry_id = _string_value(entry_raw.get("entry_id"))
    source_path = _string_value(entry_raw.get("source_path"))
    target_path = _string_value(entry_raw.get("target_path"))
    ownership = _string_value(entry_raw.get("ownership"))
    sync_mode = _string_value(entry_raw.get("sync_mode"))
    source_hash = entry_raw.get("source_hash")
    target_hash = entry_raw.get("target_hash")
    marker = entry_raw.get("marker")
    generated = entry_raw.get("generated")

    if ownership and ownership not in OWNERSHIP_VALUES:
        issues.append(
            ManifestIssue(
                "invalid_ownership",
                SEVERITY_ERROR,
                f"Invalid ownership value: {ownership}",
                field=f"{field_prefix}.ownership",
                entry_id=entry_id or None,
            )
        )
    if sync_mode and sync_mode not in SYNC_MODE_VALUES:
        issues.append(
            ManifestIssue(
                "invalid_sync_mode",
                SEVERITY_ERROR,
                f"Invalid sync_mode value: {sync_mode}",
                field=f"{field_prefix}.sync_mode",
                entry_id=entry_id or None,
            )
        )

    _validate_manifest_path(source_path, f"{field_prefix}.source_path", issues, entry_id=entry_id)
    _validate_manifest_path(target_path, f"{field_prefix}.target_path", issues, entry_id=entry_id, allow_dot=False)
    if source_path and source_root and not _is_under_root(source_path, source_root):
        issues.append(
            ManifestIssue(
                "source_path_outside_source_root",
                SEVERITY_ERROR,
                "source_path must be under source_root.",
                field=f"{field_prefix}.source_path",
                entry_id=entry_id or None,
            )
        )
    if target_path and target_root and target_root != "." and not _is_under_root(target_path, target_root):
        issues.append(
            ManifestIssue(
                "target_path_outside_target_root",
                SEVERITY_ERROR,
                "target_path must be under target_root.",
                field=f"{field_prefix}.target_path",
                entry_id=entry_id or None,
            )
        )

    if not is_valid_hash_string(source_hash):
        issues.append(
            ManifestIssue(
                "invalid_hash_format",
                SEVERITY_ERROR,
                "source_hash must use sha256:<lowercase-hex> format.",
                field=f"{field_prefix}.source_hash",
                entry_id=entry_id or None,
            )
        )
    if target_hash is None:
        issues.append(
            ManifestIssue(
                "target_hash_null",
                SEVERITY_ERROR,
                "target_hash must not be null in sync manifest v0.",
                field=f"{field_prefix}.target_hash",
                entry_id=entry_id or None,
            )
        )
    elif not is_valid_hash_string(target_hash):
        issues.append(
            ManifestIssue(
                "invalid_hash_format",
                SEVERITY_ERROR,
                "target_hash must use sha256:<lowercase-hex> format.",
                field=f"{field_prefix}.target_hash",
                entry_id=entry_id or None,
            )
        )

    if not isinstance(generated, dict):
        issues.append(
            ManifestIssue(
                "invalid_generated_metadata",
                SEVERITY_ERROR,
                "generated must be an object.",
                field=f"{field_prefix}.generated",
                entry_id=entry_id or None,
            )
        )
        generated = {}
    else:
        _require_fields(generated, ("generated_by", "generated_at"), issues, field_prefix=f"{field_prefix}.generated")

    marker_issues = _validate_marker(marker, field_prefix, entry_id, sync_mode)
    issues.extend(marker_issues)

    if any(issue.severity == SEVERITY_ERROR for issue in issues):
        return None, issues
    return (
        ManifestEntry(
            entry_id=entry_id,
            source_path=source_path,
            target_path=target_path,
            ownership=ownership,
            sync_mode=sync_mode,
            source_hash=str(source_hash),
            target_hash=str(target_hash),
            marker=marker if isinstance(marker, dict) else None,
            generated=generated,
            raw=entry_raw,
        ),
        issues,
    )


def _validate_marker(marker: Any, field_prefix: str, entry_id: str, sync_mode: str) -> list[ManifestIssue]:
    issues: list[ManifestIssue] = []
    if sync_mode in {"managed-block", "mixed-boundary"}:
        if not isinstance(marker, dict):
            issues.append(
                ManifestIssue(
                    "missing_marker_metadata",
                    SEVERITY_ERROR,
                    "marker metadata is required for managed-block and mixed-boundary sync modes.",
                    field=f"{field_prefix}.marker",
                    entry_id=entry_id or None,
                )
            )
            return issues
        _require_fields(marker, ("marker_version", "marker_style", "entry_id"), issues, field_prefix=f"{field_prefix}.marker")
        marker_style = _string_value(marker.get("marker_style"))
        marker_entry_id = _string_value(marker.get("entry_id"))
        if marker_style and marker_style not in MARKER_STYLE_VALUES:
            issues.append(
                ManifestIssue(
                    "invalid_marker_style",
                    SEVERITY_ERROR,
                    f"Invalid marker_style value: {marker_style}",
                    field=f"{field_prefix}.marker.marker_style",
                    entry_id=entry_id or None,
                )
            )
        if marker_entry_id and marker_entry_id != entry_id:
            issues.append(
                ManifestIssue(
                    "marker_entry_id_mismatch",
                    SEVERITY_ERROR,
                    "marker.entry_id must match entry_id.",
                    field=f"{field_prefix}.marker.entry_id",
                    entry_id=entry_id or None,
                )
            )
        return issues

    if sync_mode == "whole-file" and marker is not None:
        issues.append(
            ManifestIssue(
                "unexpected_marker_metadata",
                SEVERITY_ERROR,
                "marker metadata must be null or omitted for whole-file sync mode.",
                field=f"{field_prefix}.marker",
                entry_id=entry_id or None,
            )
        )
    return issues


def _require_fields(
    data: dict[str, Any],
    fields: tuple[str, ...],
    issues: list[ManifestIssue],
    field_prefix: str | None = None,
) -> None:
    for field_name in fields:
        if field_name not in data:
            field = f"{field_prefix}.{field_name}" if field_prefix else field_name
            issues.append(
                ManifestIssue(
                    "missing_required_field",
                    SEVERITY_ERROR,
                    f"Missing required field: {field}",
                    field=field,
                )
            )


def _validate_manifest_path(
    value: str,
    field: str,
    issues: list[ManifestIssue],
    entry_id: str | None = None,
    allow_dot: bool = False,
) -> None:
    if value is None or value == "":
        issues.append(
            ManifestIssue(
                "empty_path",
                SEVERITY_ERROR,
                "Manifest paths must not be empty.",
                field=field,
                entry_id=entry_id or None,
            )
        )
        return
    if allow_dot and value == ".":
        return
    if "\\" in value:
        issues.append(
            ManifestIssue(
                "non_posix_path",
                SEVERITY_ERROR,
                "Manifest JSON paths must use / separators.",
                field=field,
                entry_id=entry_id or None,
            )
        )
    if value.startswith("/") or value.startswith("\\") or _WINDOWS_ABSOLUTE_RE.match(value):
        issues.append(
            ManifestIssue(
                "absolute_path",
                SEVERITY_ERROR,
                "Manifest paths must be repository-relative.",
                field=field,
                entry_id=entry_id or None,
            )
        )
    parts = value.split("/")
    if ".." in parts:
        issues.append(
            ManifestIssue(
                "parent_traversal_path",
                SEVERITY_ERROR,
                "Manifest paths must not contain parent traversal.",
                field=field,
                entry_id=entry_id or None,
            )
        )
    if any(part == "" for part in parts):
        issues.append(
            ManifestIssue(
                "empty_path_segment",
                SEVERITY_ERROR,
                "Manifest paths must not contain empty path segments.",
                field=field,
                entry_id=entry_id or None,
            )
        )


def _is_under_root(path: str, root: str) -> bool:
    if root == ".":
        return True
    normalized_root = root.rstrip("/")
    return path == normalized_root or path.startswith(f"{normalized_root}/")


def _string_value(value: Any) -> str:
    return value if isinstance(value, str) else ""
