from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..status import SEVERITY_ERROR, SEVERITY_WARNING, STATUS_FAIL, STATUS_PASS, STATUS_WARN
from .hash import HASH_POLICY_V0, is_valid_hash_string


REPLAY_MANIFEST_SCHEMA_VERSION = "aios.preview_replay_manifest.v0"
PROVIDER_SNAPSHOT_SCHEMA_VERSION = "aios.preview_provider_snapshot.v0"
REAL_PREVIEW_INPUT_SCHEMA_VERSION = "aios.real_preview.input.v0"
REAL_PREVIEW_OUTPUT_SCHEMA_VERSION = "aios.real_preview.output.v0"

UNAVAILABLE_REASONS = {
    "adapter-unavailable",
    "source-missing",
    "unsupported-sync-mode",
    "activation-unresolved",
    "nondeterministic-output",
    "provider-timeout",
    "generation-disabled",
    "marker-invalid",
}
SYNC_MODE_VALUES = {"whole-file", "managed-block", "mixed-boundary"}
OWNERSHIP_VALUES = {"runtime-managed", "user-owned", "mixed-boundary"}
MARKER_STYLE_VALUES = {"markdown-html-comment", "hash-line-comment", "yaml-line-comment"}

_WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")
_PLACEHOLDER_RE = re.compile(r"<|>|TODO|placeholder", re.IGNORECASE)


@dataclass(frozen=True)
class ReplayIssue:
    code: str
    severity: str
    message: str
    field: str | None = None
    case_id: str | None = None

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
        if self.case_id:
            data["case_id"] = self.case_id
        return data


@dataclass(frozen=True)
class ReplayCase:
    case_id: str
    input_fixture: str
    expected_output_fixture: str
    replay_dimensions: list[str]
    raw: dict[str, Any] = field(repr=False)


@dataclass(frozen=True)
class ProviderSnapshot:
    provider_id: str
    provider_version: str
    deterministic_capable: bool
    supported_sync_modes: list[str]
    hash_policy: str
    raw: dict[str, Any] = field(repr=False)


@dataclass(frozen=True)
class ReplayManifest:
    schema_version: str
    provider_id: str
    provider_version: str
    hash_policy: str
    cases: list[ReplayCase]
    provider_snapshot: ProviderSnapshot | None
    raw: dict[str, Any] = field(repr=False)


@dataclass(frozen=True)
class ReplayValidationResult:
    manifest: ReplayManifest | None
    issues: list[ReplayIssue]

    @property
    def status(self) -> str:
        if any(issue.severity == SEVERITY_ERROR for issue in self.issues):
            return STATUS_FAIL
        if any(issue.severity == SEVERITY_WARNING for issue in self.issues):
            return STATUS_WARN
        return STATUS_PASS

    @property
    def errors(self) -> list[ReplayIssue]:
        return [issue for issue in self.issues if issue.severity == SEVERITY_ERROR]

    @property
    def warnings(self) -> list[ReplayIssue]:
        return [issue for issue in self.issues if issue.severity == SEVERITY_WARNING]


def load_replay_manifest(path: Path) -> ReplayValidationResult:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return validate_replay_manifest_data(data, path)


def validate_replay_manifest_data(data: Any, manifest_path: Path) -> ReplayValidationResult:
    issues: list[ReplayIssue] = []
    if not isinstance(data, dict):
        return ReplayValidationResult(
            None,
            [
                ReplayIssue(
                    "replay_manifest_not_object",
                    SEVERITY_ERROR,
                    "Replay manifest must be a JSON object.",
                )
            ],
        )

    _require_fields(data, ("schema_version", "provider", "hash_policy", "cases"), issues)
    schema_version = _string_value(data.get("schema_version"))
    if schema_version and schema_version != REPLAY_MANIFEST_SCHEMA_VERSION:
        issues.append(
            ReplayIssue(
                "unsupported_schema_version",
                SEVERITY_ERROR,
                f"Unsupported replay manifest schema_version: {schema_version}",
                field="schema_version",
            )
        )

    provider = data.get("provider")
    provider_id = ""
    provider_version = ""
    if not isinstance(provider, dict):
        issues.append(
            ReplayIssue("invalid_provider", SEVERITY_ERROR, "provider must be an object.", field="provider")
        )
    else:
        _require_fields(provider, ("provider_id", "provider_version"), issues, field_prefix="provider")
        provider_id = _string_value(provider.get("provider_id"))
        provider_version = _string_value(provider.get("provider_version"))

    hash_policy = _validate_hash_policy(data.get("hash_policy"), "hash_policy", issues)
    snapshot = _load_and_validate_provider_snapshot(manifest_path, provider_id, provider_version, hash_policy, issues)

    cases_raw = data.get("cases")
    cases: list[ReplayCase] = []
    if "cases" in data and not isinstance(cases_raw, list):
        issues.append(ReplayIssue("invalid_cases", SEVERITY_ERROR, "cases must be a list.", field="cases"))
        cases_raw = []
    elif isinstance(cases_raw, list) and not cases_raw:
        issues.append(ReplayIssue("empty_cases", SEVERITY_ERROR, "cases must not be empty.", field="cases"))

    seen_case_ids: set[str] = set()
    replay_root = _replay_root(manifest_path)
    for index, case_raw in enumerate(cases_raw or []):
        case, case_issues = _validate_case(case_raw, index, replay_root, provider_id, provider_version, hash_policy)
        issues.extend(case_issues)
        case_id = _string_value(case_raw.get("case_id")) if isinstance(case_raw, dict) else ""
        if case_id:
            if case_id in seen_case_ids:
                issues.append(
                    ReplayIssue(
                        "duplicate_case_id",
                        SEVERITY_ERROR,
                        f"Duplicate replay case id: {case_id}",
                        field=f"cases[{index}].case_id",
                        case_id=case_id,
                    )
                )
            seen_case_ids.add(case_id)
        if case is not None:
            cases.append(case)

    manifest = None
    if not any(issue.severity == SEVERITY_ERROR for issue in issues):
        manifest = ReplayManifest(
            schema_version=schema_version,
            provider_id=provider_id,
            provider_version=provider_version,
            hash_policy=hash_policy,
            cases=cases,
            provider_snapshot=snapshot,
            raw=data,
        )
    return ReplayValidationResult(manifest, issues)


def _load_and_validate_provider_snapshot(
    manifest_path: Path,
    provider_id: str,
    provider_version: str,
    hash_policy: str,
    issues: list[ReplayIssue],
) -> ProviderSnapshot | None:
    if not provider_id or not provider_version:
        return None
    snapshot_path = _replay_root(manifest_path) / "provider_snapshots" / _snapshot_filename(provider_id, provider_version)
    try:
        with snapshot_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        issues.append(
            ReplayIssue(
                "provider_snapshot_missing",
                SEVERITY_ERROR,
                "Provider snapshot fixture is missing.",
                field="provider",
            )
        )
        return None
    except json.JSONDecodeError as exc:
        issues.append(
            ReplayIssue(
                "provider_snapshot_invalid_json",
                SEVERITY_ERROR,
                f"Provider snapshot must be valid JSON: {exc.msg}",
                field="provider",
            )
        )
        return None

    if not isinstance(data, dict):
        issues.append(
            ReplayIssue(
                "provider_snapshot_not_object",
                SEVERITY_ERROR,
                "Provider snapshot must be a JSON object.",
                field="provider",
            )
        )
        return None

    _require_fields(
        data,
        (
            "schema_version",
            "provider_id",
            "provider_version",
            "deterministic_capable",
            "supported_sync_modes",
            "hash_policy",
            "output_affecting_config",
        ),
        issues,
        field_prefix="provider_snapshot",
    )
    if data.get("schema_version") != PROVIDER_SNAPSHOT_SCHEMA_VERSION:
        issues.append(
            ReplayIssue(
                "provider_snapshot_schema_mismatch",
                SEVERITY_ERROR,
                "Provider snapshot schema_version is unsupported.",
                field="provider_snapshot.schema_version",
            )
        )
    if data.get("provider_id") != provider_id or data.get("provider_version") != provider_version:
        issues.append(
            ReplayIssue(
                "provider_identity_mismatch",
                SEVERITY_ERROR,
                "Provider snapshot provider_id/provider_version must match replay manifest.",
                field="provider",
            )
        )
    if hash_policy and data.get("hash_policy") != hash_policy:
        issues.append(
            ReplayIssue(
                "hash_policy_mismatch",
                SEVERITY_ERROR,
                "Provider snapshot hash_policy must match replay manifest hash policy.",
                field="provider_snapshot.hash_policy",
            )
        )
    if not isinstance(data.get("deterministic_capable"), bool):
        issues.append(
            ReplayIssue(
                "invalid_provider_snapshot",
                SEVERITY_ERROR,
                "provider snapshot deterministic_capable must be boolean.",
                field="provider_snapshot.deterministic_capable",
            )
        )
    supported_sync_modes = data.get("supported_sync_modes")
    if not isinstance(supported_sync_modes, list) or not supported_sync_modes:
        issues.append(
            ReplayIssue(
                "invalid_provider_snapshot",
                SEVERITY_ERROR,
                "provider snapshot supported_sync_modes must be a non-empty list.",
                field="provider_snapshot.supported_sync_modes",
            )
        )
        supported_sync_modes = []
    elif any(mode not in SYNC_MODE_VALUES for mode in supported_sync_modes):
        issues.append(
            ReplayIssue(
                "invalid_provider_snapshot",
                SEVERITY_ERROR,
                "provider snapshot supported_sync_modes contains unsupported values.",
                field="provider_snapshot.supported_sync_modes",
            )
        )
    if not isinstance(data.get("output_affecting_config"), dict) or not data.get("output_affecting_config"):
        issues.append(
            ReplayIssue(
                "invalid_provider_snapshot",
                SEVERITY_ERROR,
                "provider snapshot output_affecting_config must be a non-empty object.",
                field="provider_snapshot.output_affecting_config",
            )
        )

    if any(issue.severity == SEVERITY_ERROR and issue.field and issue.field.startswith("provider_snapshot") for issue in issues):
        return None
    return ProviderSnapshot(
        provider_id=str(data.get("provider_id", "")),
        provider_version=str(data.get("provider_version", "")),
        deterministic_capable=bool(data.get("deterministic_capable")),
        supported_sync_modes=[str(mode) for mode in supported_sync_modes],
        hash_policy=str(data.get("hash_policy", "")),
        raw=data,
    )


def _validate_case(
    case_raw: Any,
    index: int,
    replay_root: Path,
    provider_id: str,
    provider_version: str,
    hash_policy: str,
) -> tuple[ReplayCase | None, list[ReplayIssue]]:
    issues: list[ReplayIssue] = []
    field_prefix = f"cases[{index}]"
    if not isinstance(case_raw, dict):
        return (
            None,
            [
                ReplayIssue(
                    "replay_case_not_object",
                    SEVERITY_ERROR,
                    "Replay case must be an object.",
                    field=field_prefix,
                )
            ],
        )

    _require_fields(
        case_raw,
        ("case_id", "input_fixture", "expected_output_fixture", "replay_dimensions"),
        issues,
        field_prefix=field_prefix,
    )
    case_id = _string_value(case_raw.get("case_id"))
    input_fixture = _string_value(case_raw.get("input_fixture"))
    expected_output_fixture = _string_value(case_raw.get("expected_output_fixture"))
    replay_dimensions = case_raw.get("replay_dimensions")
    if not isinstance(replay_dimensions, list) or not replay_dimensions or not all(isinstance(item, str) and item for item in replay_dimensions):
        issues.append(
            ReplayIssue(
                "empty_replay_dimensions",
                SEVERITY_ERROR,
                "replay_dimensions must be a non-empty list of strings.",
                field=f"{field_prefix}.replay_dimensions",
                case_id=case_id or None,
            )
        )
        replay_dimensions = []

    input_path = _safe_fixture_path(replay_root, input_fixture, f"{field_prefix}.input_fixture", case_id, issues)
    output_path = _safe_fixture_path(
        replay_root,
        expected_output_fixture,
        f"{field_prefix}.expected_output_fixture",
        case_id,
        issues,
    )
    input_data = _load_fixture_json(input_path, "input", f"{field_prefix}.input_fixture", case_id, issues)
    output_data = _load_fixture_json(output_path, "output", f"{field_prefix}.expected_output_fixture", case_id, issues)
    if isinstance(input_data, dict):
        _validate_input_fixture(input_data, f"{field_prefix}.input", case_id, provider_id, provider_version, hash_policy, issues)
    if isinstance(output_data, dict):
        _validate_output_fixture(output_data, f"{field_prefix}.output", case_id, provider_id, provider_version, hash_policy, issues)
    if isinstance(input_data, dict) and isinstance(output_data, dict):
        if input_data.get("entry_id") != case_id or output_data.get("entry_id") != case_id:
            issues.append(
                ReplayIssue(
                    "replay_entry_id_mismatch",
                    SEVERITY_ERROR,
                    "case_id must match input and output entry_id.",
                    field=field_prefix,
                    case_id=case_id or None,
                )
            )

    if any(issue.severity == SEVERITY_ERROR for issue in issues):
        return None, issues
    return (
        ReplayCase(
            case_id=case_id,
            input_fixture=input_fixture,
            expected_output_fixture=expected_output_fixture,
            replay_dimensions=[str(item) for item in replay_dimensions],
            raw=case_raw,
        ),
        issues,
    )


def _validate_input_fixture(
    data: dict[str, Any],
    field_prefix: str,
    case_id: str,
    provider_id: str,
    provider_version: str,
    hash_policy: str,
    issues: list[ReplayIssue],
) -> None:
    _require_fields(data, ("schema_version", "entry_id", "manifest_entry", "source_evidence", "context", "provider", "hash_policy"), issues, field_prefix)
    if data.get("schema_version") != REAL_PREVIEW_INPUT_SCHEMA_VERSION:
        issues.append(
            ReplayIssue("input_schema_mismatch", SEVERITY_ERROR, "Input fixture schema_version is unsupported.", field=f"{field_prefix}.schema_version", case_id=case_id)
        )
    _validate_provider_ref(data.get("provider"), provider_id, provider_version, f"{field_prefix}.provider", case_id, issues)
    input_hash_policy = _validate_hash_policy(data.get("hash_policy"), f"{field_prefix}.hash_policy", issues, case_id)
    if hash_policy and input_hash_policy and input_hash_policy != hash_policy:
        issues.append(
            ReplayIssue("hash_policy_mismatch", SEVERITY_ERROR, "Input fixture hash policy must match replay manifest.", field=f"{field_prefix}.hash_policy", case_id=case_id)
        )
    manifest_entry = data.get("manifest_entry")
    if not isinstance(manifest_entry, dict):
        issues.append(
            ReplayIssue("invalid_input_manifest_entry", SEVERITY_ERROR, "Input manifest_entry must be an object.", field=f"{field_prefix}.manifest_entry", case_id=case_id)
        )
    else:
        _validate_input_manifest_entry(manifest_entry, field_prefix, case_id, issues)
    source_evidence = data.get("source_evidence")
    if not isinstance(source_evidence, dict):
        issues.append(
            ReplayIssue("missing_provenance", SEVERITY_ERROR, "Input source_evidence must be present.", field=f"{field_prefix}.source_evidence", case_id=case_id)
        )
    else:
        _validate_source_evidence(source_evidence, f"{field_prefix}.source_evidence", case_id, issues)
    _validate_hash_fields(data, field_prefix, case_id, issues)


def _validate_output_fixture(
    data: dict[str, Any],
    field_prefix: str,
    case_id: str,
    provider_id: str,
    provider_version: str,
    hash_policy: str,
    issues: list[ReplayIssue],
) -> None:
    _require_fields(
        data,
        (
            "schema_version",
            "entry_id",
            "preview_available",
            "generated_content_kind",
            "generated_bytes_hash",
            "generated_target_hash",
            "generated_managed_block_hash",
            "deterministic",
            "provider_metadata",
            "provenance",
            "unavailable_reason",
        ),
        issues,
        field_prefix,
    )
    if data.get("schema_version") != REAL_PREVIEW_OUTPUT_SCHEMA_VERSION:
        issues.append(
            ReplayIssue("output_schema_mismatch", SEVERITY_ERROR, "Output fixture schema_version is unsupported.", field=f"{field_prefix}.schema_version", case_id=case_id)
        )
    preview_available = data.get("preview_available")
    if not isinstance(preview_available, bool):
        issues.append(
            ReplayIssue("invalid_preview_available", SEVERITY_ERROR, "preview_available must be boolean.", field=f"{field_prefix}.preview_available", case_id=case_id)
        )
    deterministic = data.get("deterministic")
    if not isinstance(deterministic, bool):
        issues.append(
            ReplayIssue("invalid_deterministic_flag", SEVERITY_ERROR, "deterministic must be boolean.", field=f"{field_prefix}.deterministic", case_id=case_id)
        )
    provider_metadata = data.get("provider_metadata")
    if not isinstance(provider_metadata, dict):
        issues.append(
            ReplayIssue("missing_provider_metadata", SEVERITY_ERROR, "Output provider_metadata must be present.", field=f"{field_prefix}.provider_metadata", case_id=case_id)
        )
    else:
        _require_fields(
            provider_metadata,
            ("provider_id", "provider_version", "hash_policy", "supported_sync_mode", "output_affecting_config_ref"),
            issues,
            field_prefix=f"{field_prefix}.provider_metadata",
        )
        if provider_metadata.get("provider_id") != provider_id or provider_metadata.get("provider_version") != provider_version:
            issues.append(
                ReplayIssue("provider_identity_mismatch", SEVERITY_ERROR, "Output provider metadata must match replay manifest provider.", field=f"{field_prefix}.provider_metadata", case_id=case_id)
            )
        if hash_policy and provider_metadata.get("hash_policy") != hash_policy:
            issues.append(
                ReplayIssue("hash_policy_mismatch", SEVERITY_ERROR, "Output provider metadata hash_policy must match replay manifest.", field=f"{field_prefix}.provider_metadata.hash_policy", case_id=case_id)
            )
    provenance = data.get("provenance")
    if not isinstance(provenance, dict):
        issues.append(
            ReplayIssue("missing_provenance", SEVERITY_ERROR, "Output provenance must be present.", field=f"{field_prefix}.provenance", case_id=case_id)
        )
    else:
        _validate_provenance(provenance, f"{field_prefix}.provenance", case_id, issues)
    _validate_hash_fields(data, field_prefix, case_id, issues)

    generated_hash_fields = ("generated_bytes_hash", "generated_target_hash", "generated_managed_block_hash")
    if preview_available is True:
        if deterministic is not True:
            issues.append(
                ReplayIssue("invalid_deterministic_flag", SEVERITY_ERROR, "Available output must be deterministic.", field=f"{field_prefix}.deterministic", case_id=case_id)
            )
        if data.get("generated_bytes_hash") is None:
            issues.append(
                ReplayIssue("missing_generated_hash", SEVERITY_ERROR, "Available output must include generated_bytes_hash.", field=f"{field_prefix}.generated_bytes_hash", case_id=case_id)
            )
        if data.get("unavailable_reason") is not None:
            issues.append(
                ReplayIssue("invalid_unavailable_reason", SEVERITY_ERROR, "Available output must not include unavailable_reason.", field=f"{field_prefix}.unavailable_reason", case_id=case_id)
            )
    elif preview_available is False:
        if any(data.get(field) is not None for field in generated_hash_fields):
            issues.append(
                ReplayIssue("unavailable_generated_hash_present", SEVERITY_ERROR, "Unavailable output must have null generated hash fields.", field=field_prefix, case_id=case_id)
            )
        unavailable_reason = data.get("unavailable_reason")
        if unavailable_reason not in UNAVAILABLE_REASONS:
            issues.append(
                ReplayIssue("invalid_unavailable_reason", SEVERITY_ERROR, "Unavailable output must use a supported unavailable_reason.", field=f"{field_prefix}.unavailable_reason", case_id=case_id)
            )


def _validate_provider_ref(
    data: Any,
    provider_id: str,
    provider_version: str,
    field: str,
    case_id: str,
    issues: list[ReplayIssue],
) -> None:
    if not isinstance(data, dict):
        issues.append(ReplayIssue("invalid_provider", SEVERITY_ERROR, "provider must be an object.", field=field, case_id=case_id))
        return
    _require_fields(data, ("provider_id", "provider_version"), issues, field_prefix=field)
    if data.get("provider_id") != provider_id or data.get("provider_version") != provider_version:
        issues.append(
            ReplayIssue("provider_identity_mismatch", SEVERITY_ERROR, "Fixture provider id/version must match replay manifest.", field=field, case_id=case_id)
        )


def _validate_input_manifest_entry(
    data: dict[str, Any],
    field_prefix: str,
    case_id: str,
    issues: list[ReplayIssue],
) -> None:
    _require_fields(
        data,
        ("source_path", "source_paths", "source_hash", "target_path", "ownership", "sync_mode", "marker"),
        issues,
        field_prefix=f"{field_prefix}.manifest_entry",
    )
    if data.get("ownership") not in OWNERSHIP_VALUES:
        issues.append(
            ReplayIssue("invalid_ownership", SEVERITY_ERROR, "Input ownership is unsupported.", field=f"{field_prefix}.manifest_entry.ownership", case_id=case_id)
        )
    sync_mode = data.get("sync_mode")
    if sync_mode not in SYNC_MODE_VALUES:
        issues.append(
            ReplayIssue("invalid_sync_mode", SEVERITY_ERROR, "Input sync_mode is unsupported.", field=f"{field_prefix}.manifest_entry.sync_mode", case_id=case_id)
        )
    marker = data.get("marker")
    if sync_mode == "whole-file":
        if marker is not None:
            issues.append(
                ReplayIssue("unexpected_marker_metadata", SEVERITY_ERROR, "Whole-file replay input must not include marker metadata.", field=f"{field_prefix}.manifest_entry.marker", case_id=case_id)
            )
    elif sync_mode in {"managed-block", "mixed-boundary"}:
        if not isinstance(marker, dict):
            issues.append(
                ReplayIssue("missing_marker_metadata", SEVERITY_ERROR, "Managed replay input requires marker metadata.", field=f"{field_prefix}.manifest_entry.marker", case_id=case_id)
            )
        else:
            _require_fields(marker, ("marker_version", "marker_style", "entry_id"), issues, field_prefix=f"{field_prefix}.manifest_entry.marker")
            if marker.get("entry_id") != case_id:
                issues.append(
                    ReplayIssue("marker_entry_id_mismatch", SEVERITY_ERROR, "marker.entry_id must match case_id.", field=f"{field_prefix}.manifest_entry.marker.entry_id", case_id=case_id)
                )
            if marker.get("marker_style") not in MARKER_STYLE_VALUES:
                issues.append(
                    ReplayIssue("invalid_marker_style", SEVERITY_ERROR, "marker_style is unsupported.", field=f"{field_prefix}.manifest_entry.marker.marker_style", case_id=case_id)
                )


def _validate_source_evidence(data: dict[str, Any], field: str, case_id: str, issues: list[ReplayIssue]) -> None:
    source_paths = data.get("source_paths")
    source_hashes = data.get("source_hashes")
    if not isinstance(source_paths, list) or not source_paths or not all(isinstance(path, str) and path for path in source_paths):
        issues.append(
            ReplayIssue("missing_provenance", SEVERITY_ERROR, "source_paths must be a non-empty ordered list.", field=f"{field}.source_paths", case_id=case_id)
        )
        return
    if not isinstance(source_hashes, dict):
        issues.append(
            ReplayIssue("missing_provenance", SEVERITY_ERROR, "source_hashes must be an object.", field=f"{field}.source_hashes", case_id=case_id)
        )
        return
    if list(source_hashes.keys()) != source_paths:
        issues.append(
            ReplayIssue("source_path_order_invalid", SEVERITY_ERROR, "source_hashes key order must match source_paths.", field=field, case_id=case_id)
        )


def _validate_provenance(data: dict[str, Any], field: str, case_id: str, issues: list[ReplayIssue]) -> None:
    _require_fields(
        data,
        ("source_paths", "source_hashes", "activation_reference", "rule_context_reference", "generated_by"),
        issues,
        field_prefix=field,
    )
    _validate_source_evidence(data, field, case_id, issues)


def _validate_hash_fields(value: Any, field: str, case_id: str, issues: list[ReplayIssue]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            next_field = f"{field}.{key}"
            if isinstance(item, str) and _PLACEHOLDER_RE.search(item):
                issues.append(
                    ReplayIssue("placeholder_hash", SEVERITY_ERROR, "Fixture values must not contain placeholder hash text.", field=next_field, case_id=case_id)
                )
            if key == "source_hashes":
                if isinstance(item, dict):
                    for source_path, digest in item.items():
                        if not is_valid_hash_string(digest):
                            issues.append(
                                ReplayIssue("invalid_hash_format", SEVERITY_ERROR, "source_hashes values must use sha256:<lowercase-hex> format.", field=f"{next_field}.{source_path}", case_id=case_id)
                            )
                continue
            if key.endswith("_hash") and item is not None and not is_valid_hash_string(item):
                issues.append(
                    ReplayIssue("invalid_hash_format", SEVERITY_ERROR, f"{key} must use sha256:<lowercase-hex> format.", field=next_field, case_id=case_id)
                )
            else:
                _validate_hash_fields(item, next_field, case_id, issues)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _validate_hash_fields(item, f"{field}[{index}]", case_id, issues)


def _validate_hash_policy(data: Any, field: str, issues: list[ReplayIssue], case_id: str | None = None) -> str:
    if not isinstance(data, dict):
        issues.append(
            ReplayIssue("invalid_hash_policy", SEVERITY_ERROR, "hash_policy must be an object.", field=field, case_id=case_id)
        )
        return ""
    for key, expected in HASH_POLICY_V0.items():
        if data.get(key) != expected:
            issues.append(
                ReplayIssue(
                    "invalid_hash_policy",
                    SEVERITY_ERROR,
                    f"hash_policy.{key} must be {expected}.",
                    field=f"{field}.{key}",
                    case_id=case_id,
                )
            )
    return _string_value(data.get("version"))


def _load_fixture_json(
    path: Path | None,
    fixture_kind: str,
    field: str,
    case_id: str,
    issues: list[ReplayIssue],
) -> Any:
    if path is None:
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        issues.append(
            ReplayIssue("replay_fixture_missing", SEVERITY_ERROR, f"Replay {fixture_kind} fixture is missing.", field=field, case_id=case_id or None)
        )
    except json.JSONDecodeError as exc:
        issues.append(
            ReplayIssue("replay_fixture_invalid_json", SEVERITY_ERROR, f"Replay {fixture_kind} fixture must be valid JSON: {exc.msg}", field=field, case_id=case_id or None)
        )
    return None


def _safe_fixture_path(
    replay_root: Path,
    value: str,
    field: str,
    case_id: str,
    issues: list[ReplayIssue],
) -> Path | None:
    if not value:
        issues.append(ReplayIssue("empty_fixture_path", SEVERITY_ERROR, "Fixture path must not be empty.", field=field, case_id=case_id or None))
        return None
    candidate = Path(value)
    if candidate.is_absolute() or value.startswith("/") or value.startswith("\\") or _WINDOWS_ABSOLUTE_RE.match(value):
        issues.append(ReplayIssue("unsafe_fixture_path", SEVERITY_ERROR, "Fixture path must be relative.", field=field, case_id=case_id or None))
        return None
    if "\\" in value or ".." in candidate.parts or any(part == "" for part in value.split("/")):
        issues.append(ReplayIssue("unsafe_fixture_path", SEVERITY_ERROR, "Fixture path must be safe and use / separators.", field=field, case_id=case_id or None))
        return None
    return replay_root / candidate


def _snapshot_filename(provider_id: str, provider_version: str) -> str:
    safe_id = re.sub(r"[^A-Za-z0-9]+", "_", provider_id).strip("_").lower()
    safe_version = re.sub(r"[^A-Za-z0-9]+", "_", provider_version).strip("_")
    return f"{safe_id}_{safe_version}.json"


def _replay_root(manifest_path: Path) -> Path:
    # Expected layout: replay/manifests/replay_manifest.json.
    return manifest_path.resolve().parent.parent


def _require_fields(
    data: dict[str, Any],
    fields: tuple[str, ...],
    issues: list[ReplayIssue],
    field_prefix: str | None = None,
) -> None:
    for field_name in fields:
        if field_name not in data:
            field = f"{field_prefix}.{field_name}" if field_prefix else field_name
            issues.append(
                ReplayIssue(
                    "missing_required_field",
                    SEVERITY_ERROR,
                    f"Missing required field: {field}",
                    field=field,
                )
            )


def _string_value(value: Any) -> str:
    return value if isinstance(value, str) else ""
