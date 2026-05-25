from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

from ..status import SEVERITY_ERROR, SEVERITY_WARNING, STATUS_FAIL, STATUS_PASS, STATUS_WARN


SANDBOX_POLICY_SCHEMA_VERSION = "aios.sandbox_policy.v0"
ALLOWED_SANDBOX_MODES = frozenset({"fixture-mock", "subprocess-temp-cwd"})
ALLOWED_ENV_POLICY_MODE = "allowlist"
SANDBOX_TMP_PREFIX = "{sandbox_tmp}/"
REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "sandbox_mode",
        "timeout_ms",
        "max_input_bytes",
        "max_output_bytes",
        "stdout_limit_bytes",
        "stderr_limit_bytes",
        "allowed_read_roots",
        "allowed_output_roots",
        "network_disabled",
        "deterministic_execution",
        "no_write_required",
        "env_policy",
        "filesystem_policy",
    }
)
POSITIVE_INTEGER_FIELDS = frozenset(
    {
        "timeout_ms",
        "max_input_bytes",
        "max_output_bytes",
        "stdout_limit_bytes",
        "stderr_limit_bytes",
    }
)
ALLOWED_EDGE_CLASSIFICATIONS = frozenset(
    {
        "explicit-no-read",
        "max-limit-boundary",
        "overlapping-roots-warning",
        "minimal-env-allowlist",
        "sandbox-token-output-root",
    }
)
_WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")


@dataclass(frozen=True)
class SandboxPolicyIssue:
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
class SandboxPolicyValidationResult:
    issues: list[SandboxPolicyIssue]

    @property
    def status(self) -> str:
        if any(issue.severity == SEVERITY_ERROR for issue in self.issues):
            return STATUS_FAIL
        if any(issue.severity == SEVERITY_WARNING for issue in self.issues):
            return STATUS_WARN
        return STATUS_PASS

    @property
    def errors(self) -> list[SandboxPolicyIssue]:
        return [issue for issue in self.issues if issue.severity == SEVERITY_ERROR]

    @property
    def warnings(self) -> list[SandboxPolicyIssue]:
        return [issue for issue in self.issues if issue.severity == SEVERITY_WARNING]


def validate_sandbox_policy_data(data: Any) -> SandboxPolicyValidationResult:
    """Validate parsed sandbox policy data without launching a sandbox or subprocess."""
    issues: list[SandboxPolicyIssue] = []
    if not isinstance(data, dict):
        return SandboxPolicyValidationResult(
            [
                SandboxPolicyIssue(
                    "sandbox_policy_not_object",
                    SEVERITY_ERROR,
                    "Sandbox policy must be a JSON object.",
                )
            ]
        )

    _validate_required_fields(data, issues)

    if data.get("schema_version") != SANDBOX_POLICY_SCHEMA_VERSION:
        _add(issues, "unsupported_schema_version", "schema_version must be aios.sandbox_policy.v0.", "schema_version")
    if data.get("sandbox_mode") not in ALLOWED_SANDBOX_MODES:
        _add(issues, "unsupported_sandbox_mode", "sandbox_mode is unsupported.", "sandbox_mode")

    for field in sorted(POSITIVE_INTEGER_FIELDS):
        if not _positive_int(data.get(field)):
            _add(issues, "invalid_positive_integer", f"{field} must be a positive integer.", field)

    _validate_read_roots(data.get("allowed_read_roots"), issues)
    _validate_output_roots(data.get("allowed_output_roots"), issues)

    if data.get("network_disabled") is not True:
        _add(issues, "network_not_disabled", "network_disabled must be true.", "network_disabled")
    if data.get("deterministic_execution") is not True:
        _add(issues, "deterministic_not_true", "deterministic_execution must be true.", "deterministic_execution")
    if data.get("no_write_required") is not True:
        _add(issues, "no_write_not_true", "no_write_required must be true.", "no_write_required")

    _validate_env_policy(data.get("env_policy"), issues)
    _validate_filesystem_policy(data.get("filesystem_policy"), issues)
    _validate_edge_classification(data.get("edge_classification"), issues)

    return SandboxPolicyValidationResult(issues)


def _validate_required_fields(data: dict[str, Any], issues: list[SandboxPolicyIssue]) -> None:
    for field in sorted(REQUIRED_FIELDS - data.keys()):
        _add(issues, "missing_required_field", f"Missing required field: {field}", field)


def _validate_read_roots(value: Any, issues: list[SandboxPolicyIssue]) -> None:
    if not isinstance(value, list):
        _add(issues, "invalid_allowed_read_roots", "allowed_read_roots must be a list.", "allowed_read_roots")
        return
    if len(value) != len(set(value)):
        _add(issues, "duplicate_read_root", "allowed_read_roots must not contain duplicates.", "allowed_read_roots")
    for index, item in enumerate(value):
        if not _safe_relative_path(item):
            _add(
                issues,
                "invalid_allowed_read_roots",
                "allowed_read_roots must contain only safe relative paths.",
                f"allowed_read_roots.{index}",
            )


def _validate_output_roots(value: Any, issues: list[SandboxPolicyIssue]) -> None:
    if not isinstance(value, list) or not value:
        _add(issues, "invalid_allowed_output_roots", "allowed_output_roots must be a non-empty list.", "allowed_output_roots")
        return
    if len(value) != len(set(value)):
        _add(issues, "duplicate_output_root", "allowed_output_roots must not contain duplicates.", "allowed_output_roots")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.startswith(SANDBOX_TMP_PREFIX):
            _add(
                issues,
                "invalid_allowed_output_roots",
                "allowed_output_roots must use {sandbox_tmp}/ paths.",
                f"allowed_output_roots.{index}",
            )
            continue
        suffix = item[len("{sandbox_tmp}") :]
        if not _safe_symbolic_suffix(suffix):
            _add(
                issues,
                "invalid_allowed_output_roots",
                "allowed_output_roots must not use parent traversal, backslashes, or empty path parts.",
                f"allowed_output_roots.{index}",
            )


def _validate_env_policy(value: Any, issues: list[SandboxPolicyIssue]) -> None:
    if not isinstance(value, dict):
        _add(issues, "invalid_env_policy", "env_policy must be an object.", "env_policy")
        return
    if value.get("mode") != ALLOWED_ENV_POLICY_MODE:
        _add(issues, "invalid_env_policy", "env_policy.mode must be allowlist.", "env_policy.mode")
    allowed = value.get("allowed")
    if not isinstance(allowed, list) or not all(isinstance(item, str) for item in allowed):
        _add(issues, "invalid_env_policy", "env_policy.allowed must be a list of strings.", "env_policy.allowed")
    elif "*" in allowed:
        _add(issues, "wildcard_env_rule", "env_policy.allowed must not contain wildcard rules.", "env_policy.allowed")
    forbidden_prefixes = value.get("forbidden_prefixes")
    if not isinstance(forbidden_prefixes, list) or not all(isinstance(item, str) for item in forbidden_prefixes):
        _add(
            issues,
            "invalid_env_policy",
            "env_policy.forbidden_prefixes must be a list of strings.",
            "env_policy.forbidden_prefixes",
        )


def _validate_filesystem_policy(value: Any, issues: list[SandboxPolicyIssue]) -> None:
    if not isinstance(value, dict):
        _add(issues, "invalid_filesystem_policy", "filesystem_policy must be an object.", "filesystem_policy")
        return
    expectations = {
        "cwd": "{sandbox_tmp}",
        "temp_root_required": True,
        "symlink_policy": "reject",
        "parent_traversal": "reject",
        "absolute_paths": "reject",
    }
    for field, expected in expectations.items():
        if value.get(field) != expected:
            _add(
                issues,
                "invalid_filesystem_policy",
                f"filesystem_policy.{field} must be {expected}.",
                f"filesystem_policy.{field}",
            )
    protected_roots = value.get("protected_roots")
    if not isinstance(protected_roots, list) or not protected_roots or not all(isinstance(item, str) and item for item in protected_roots):
        _add(
            issues,
            "invalid_filesystem_policy",
            "filesystem_policy.protected_roots must be a non-empty list of strings.",
            "filesystem_policy.protected_roots",
        )


def _validate_edge_classification(value: Any, issues: list[SandboxPolicyIssue]) -> None:
    if value is None:
        return
    if value not in ALLOWED_EDGE_CLASSIFICATIONS:
        _add(
            issues,
            "invalid_edge_classification",
            "edge_classification is unsupported.",
            "edge_classification",
        )


def _safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    if value == "":
        return True
    if "\\" in value or value.startswith("/") or value.startswith("\\") or _WINDOWS_ABSOLUTE_RE.match(value):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and not any(part == "" for part in value.split("/"))


def _safe_symbolic_suffix(value: str) -> bool:
    if "\\" in value:
        return False
    if not value.startswith("/"):
        return False
    path = PurePosixPath(value.lstrip("/"))
    return ".." not in path.parts and not any(part == "" for part in value.lstrip("/").split("/"))


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _add(issues: list[SandboxPolicyIssue], code: str, message: str, field: str | None = None) -> None:
    issues.append(SandboxPolicyIssue(code, SEVERITY_ERROR, message, field=field))
