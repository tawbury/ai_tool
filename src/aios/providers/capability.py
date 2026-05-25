from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

from ..status import SEVERITY_ERROR, SEVERITY_WARNING, STATUS_FAIL, STATUS_PASS, STATUS_WARN


PROVIDER_CAPABILITY_SCHEMA_VERSION = "aios.provider_capability.v0"
PROVIDER_HASH_POLICY = "aios.hash_policy.v0"
ALLOWED_SYNC_MODES = frozenset({"whole-file", "managed-block", "mixed-boundary"})
ALLOWED_NETWORK_POLICY = "disabled"

REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "provider_id",
        "provider_version",
        "deterministic_capable",
        "supported_sync_modes",
        "hash_policy",
        "output_affecting_config",
        "no_write_capable",
        "network_policy",
        "timeout_policy",
        "resource_policy",
        "allowed_read_roots",
        "provenance_required",
    }
)

_WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")


@dataclass(frozen=True)
class ProviderCapabilityIssue:
    code: str
    severity: str
    message: str
    field: str | None = None

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
        return data


@dataclass(frozen=True)
class ProviderCapabilityValidationResult:
    issues: list[ProviderCapabilityIssue]

    @property
    def status(self) -> str:
        if any(issue.severity == SEVERITY_ERROR for issue in self.issues):
            return STATUS_FAIL
        if any(issue.severity == SEVERITY_WARNING for issue in self.issues):
            return STATUS_WARN
        return STATUS_PASS

    @property
    def errors(self) -> list[ProviderCapabilityIssue]:
        return [issue for issue in self.issues if issue.severity == SEVERITY_ERROR]

    @property
    def warnings(self) -> list[ProviderCapabilityIssue]:
        return [issue for issue in self.issues if issue.severity == SEVERITY_WARNING]


def validate_provider_capability_data(data: Any) -> ProviderCapabilityValidationResult:
    """Validate a parsed provider capability declaration without executing a provider."""
    issues: list[ProviderCapabilityIssue] = []
    if not isinstance(data, dict):
        return ProviderCapabilityValidationResult(
            [
                ProviderCapabilityIssue(
                    "provider_capability_not_object",
                    SEVERITY_ERROR,
                    "Provider capability must be a JSON object.",
                )
            ]
        )

    missing = sorted(REQUIRED_FIELDS - data.keys())
    for field in missing:
        issues.append(
            ProviderCapabilityIssue(
                "missing_required_field",
                SEVERITY_ERROR,
                f"Missing required field: {field}",
                field=field,
            )
        )

    if data.get("schema_version") != PROVIDER_CAPABILITY_SCHEMA_VERSION:
        issues.append(
            ProviderCapabilityIssue(
                "unsupported_schema_version",
                SEVERITY_ERROR,
                "Provider capability schema_version is unsupported.",
                field="schema_version",
            )
        )

    if not _non_empty_string(data.get("provider_id")):
        issues.append(
            ProviderCapabilityIssue(
                "invalid_provider_id",
                SEVERITY_ERROR,
                "provider_id must be a non-empty string.",
                field="provider_id",
            )
        )
    if not _non_empty_string(data.get("provider_version")):
        issues.append(
            ProviderCapabilityIssue(
                "invalid_provider_version",
                SEVERITY_ERROR,
                "provider_version must be a non-empty string.",
                field="provider_version",
            )
        )

    if data.get("deterministic_capable") is not True:
        issues.append(
            ProviderCapabilityIssue(
                "deterministic_not_true",
                SEVERITY_ERROR,
                "deterministic_capable must be true for replay execution eligibility.",
                field="deterministic_capable",
            )
        )

    _validate_sync_modes(data.get("supported_sync_modes"), issues)

    if data.get("hash_policy") != PROVIDER_HASH_POLICY:
        issues.append(
            ProviderCapabilityIssue(
                "invalid_hash_policy",
                SEVERITY_ERROR,
                f"hash_policy must be {PROVIDER_HASH_POLICY}.",
                field="hash_policy",
            )
        )
    if not isinstance(data.get("output_affecting_config"), dict):
        issues.append(
            ProviderCapabilityIssue(
                "invalid_output_affecting_config",
                SEVERITY_ERROR,
                "output_affecting_config must be an object.",
                field="output_affecting_config",
            )
        )
    if data.get("no_write_capable") is not True:
        issues.append(
            ProviderCapabilityIssue(
                "no_write_not_true",
                SEVERITY_ERROR,
                "no_write_capable must be true.",
                field="no_write_capable",
            )
        )
    if data.get("network_policy") != ALLOWED_NETWORK_POLICY:
        issues.append(
            ProviderCapabilityIssue(
                "network_policy_not_disabled",
                SEVERITY_ERROR,
                "network_policy must be disabled.",
                field="network_policy",
            )
        )
    if not _valid_timeout_policy(data.get("timeout_policy")):
        issues.append(
            ProviderCapabilityIssue(
                "invalid_timeout_policy",
                SEVERITY_ERROR,
                "timeout_policy.timeout_ms must be a positive integer.",
                field="timeout_policy.timeout_ms",
            )
        )
    if not _valid_resource_policy(data.get("resource_policy")):
        issues.append(
            ProviderCapabilityIssue(
                "invalid_resource_policy",
                SEVERITY_ERROR,
                "resource_policy must include positive max_input_bytes and max_output_bytes.",
                field="resource_policy",
            )
        )
    if not _safe_relative_paths(data.get("allowed_read_roots")):
        issues.append(
            ProviderCapabilityIssue(
                "invalid_allowed_read_roots",
                SEVERITY_ERROR,
                "allowed_read_roots must be a list of safe relative paths.",
                field="allowed_read_roots",
            )
        )
    if data.get("provenance_required") is not True:
        issues.append(
            ProviderCapabilityIssue(
                "provenance_not_true",
                SEVERITY_ERROR,
                "provenance_required must be true.",
                field="provenance_required",
            )
        )

    return ProviderCapabilityValidationResult(issues)


def _validate_sync_modes(value: Any, issues: list[ProviderCapabilityIssue]) -> None:
    if not isinstance(value, list) or not value:
        issues.append(
            ProviderCapabilityIssue(
                "invalid_sync_modes",
                SEVERITY_ERROR,
                "supported_sync_modes must be a non-empty list.",
                field="supported_sync_modes",
            )
        )
        return

    if len(value) != len(set(value)):
        issues.append(
            ProviderCapabilityIssue(
                "duplicate_sync_mode",
                SEVERITY_ERROR,
                "supported_sync_modes must not contain duplicates.",
                field="supported_sync_modes",
            )
        )
    if any(mode not in ALLOWED_SYNC_MODES for mode in value):
        issues.append(
            ProviderCapabilityIssue(
                "invalid_sync_mode",
                SEVERITY_ERROR,
                "supported_sync_modes contains an unsupported value.",
                field="supported_sync_modes",
            )
        )


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_timeout_policy(value: Any) -> bool:
    return isinstance(value, dict) and _positive_int(value.get("timeout_ms"))


def _valid_resource_policy(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    if not _positive_int(value.get("max_input_bytes")):
        return False
    if not _positive_int(value.get("max_output_bytes")):
        return False
    if "max_memory_bytes" in value and not _positive_int(value.get("max_memory_bytes")):
        return False
    return True


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _safe_relative_paths(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    for item in value:
        if not isinstance(item, str):
            return False
        if item == "":
            continue
        if "\\" in item or item.startswith("/") or item.startswith("\\") or _WINDOWS_ABSOLUTE_RE.match(item):
            return False
        path = PurePosixPath(item)
        if path.is_absolute() or ".." in path.parts or any(part == "" for part in item.split("/")):
            return False
    return True
