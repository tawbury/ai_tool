from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from ..status import SEVERITY_ERROR, SEVERITY_WARNING, STATUS_FAIL, STATUS_PASS, STATUS_WARN


SANDBOX_EXECUTION_RESULT_SCHEMA_VERSION = "aios.sandbox_execution_result.v0"
ALLOWED_SANDBOX_MODES = frozenset({"fixture-mock", "subprocess-temp-cwd"})
ALLOWED_STATUSES = frozenset({"pass", "fail", "timeout", "resource-limit"})
ALLOWED_FAILURE_CODES = frozenset(
    {
        "sandbox-timeout",
        "sandbox-nonzero-exit",
        "sandbox-output-invalid",
        "sandbox-resource-limit",
        "sandbox-network-attempt",
        "sandbox-filesystem-violation",
        "sandbox-env-access-violation",
        "sandbox-nondeterministic-output",
    }
)
ALLOWED_RESOURCE_LIMIT_KINDS = frozenset({"input", "output", "stdout", "stderr", "memory", "duration"})
ALLOWED_EDGE_CLASSIFICATIONS = frozenset({"zero-duration", "truncated-stdout", "invalid-output-json"})
REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "sandbox_mode",
        "request_id",
        "exit_code",
        "status",
        "duration_ms",
        "stdout_bytes",
        "stderr_bytes",
        "stdout_truncated",
        "stderr_truncated",
        "output_json_valid",
        "failure_code",
        "failure_message",
        "resource_limit",
        "network_disabled",
        "mutation_performed",
        "no_write_confirmed",
        "no_write_evidence",
        "trace_id",
    }
)
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class SandboxExecutionResultIssue:
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
class SandboxExecutionResultValidationResult:
    issues: list[SandboxExecutionResultIssue]

    @property
    def status(self) -> str:
        if any(issue.severity == SEVERITY_ERROR for issue in self.issues):
            return STATUS_FAIL
        if any(issue.severity == SEVERITY_WARNING for issue in self.issues):
            return STATUS_WARN
        return STATUS_PASS

    @property
    def errors(self) -> list[SandboxExecutionResultIssue]:
        return [issue for issue in self.issues if issue.severity == SEVERITY_ERROR]

    @property
    def warnings(self) -> list[SandboxExecutionResultIssue]:
        return [issue for issue in self.issues if issue.severity == SEVERITY_WARNING]


def validate_sandbox_execution_result_data(data: Any) -> SandboxExecutionResultValidationResult:
    """Validate parsed sandbox execution result data without launching or running anything."""
    issues: list[SandboxExecutionResultIssue] = []
    if not isinstance(data, dict):
        return SandboxExecutionResultValidationResult(
            [
                SandboxExecutionResultIssue(
                    "sandbox_execution_result_not_object",
                    SEVERITY_ERROR,
                    "Sandbox execution result must be a JSON object.",
                )
            ]
        )

    _validate_required_fields(data, issues)

    if data.get("schema_version") != SANDBOX_EXECUTION_RESULT_SCHEMA_VERSION:
        _add(issues, "unsupported_schema_version", "schema_version must be aios.sandbox_execution_result.v0.", "schema_version")
    if data.get("sandbox_mode") not in ALLOWED_SANDBOX_MODES:
        _add(issues, "unsupported_sandbox_mode", "sandbox_mode is unsupported.", "sandbox_mode")
    if not _non_empty_string(data.get("request_id")):
        code = "missing_request_id" if "request_id" not in data else "invalid_request_id"
        _add(issues, code, "request_id must be a non-empty string.", "request_id")
    if not _integer_or_null(data.get("exit_code")):
        _add(issues, "invalid_exit_code", "exit_code must be an integer or null.", "exit_code")
    if data.get("status") not in ALLOWED_STATUSES:
        _add(issues, "invalid_status", "status is unsupported.", "status")
    if data.get("failure_code") is not None and data.get("failure_code") not in ALLOWED_FAILURE_CODES:
        _add(issues, "invalid_failure_code", "failure_code is unsupported.", "failure_code")

    _validate_status_failure_mapping(data, issues)
    _validate_integer_and_boolean_fields(data, issues)

    if data.get("status") == "pass" and data.get("output_json_valid") is not True:
        _add(issues, "pass_output_json_invalid", "pass results require output_json_valid true.", "output_json_valid")
    if data.get("network_disabled") is not True:
        _add(issues, "network_not_disabled", "network_disabled must be true.", "network_disabled")
    if data.get("mutation_performed") is not False:
        _add(issues, "mutation_performed_true", "mutation_performed must be false.", "mutation_performed")
    if data.get("status") == "pass" and data.get("no_write_confirmed") is not True:
        _add(issues, "no_write_not_confirmed", "pass results require no_write_confirmed true.", "no_write_confirmed")

    _validate_no_write_evidence(data.get("no_write_evidence"), issues, require_cleanup=data.get("status") == "pass")
    _validate_trace_id(data.get("trace_id"), issues)
    _validate_resource_limit(data.get("resource_limit"), issues, required=data.get("status") == "resource-limit")
    _validate_edge_classification(data.get("edge_classification"), issues)

    return SandboxExecutionResultValidationResult(issues)


def _validate_required_fields(data: dict[str, Any], issues: list[SandboxExecutionResultIssue]) -> None:
    for field in sorted(REQUIRED_FIELDS - data.keys()):
        code = "missing_request_id" if field == "request_id" else "missing_required_field"
        _add(issues, code, f"Missing required field: {field}", field)


def _validate_status_failure_mapping(data: dict[str, Any], issues: list[SandboxExecutionResultIssue]) -> None:
    status = data.get("status")
    failure_code = data.get("failure_code")
    if status == "pass" and failure_code is not None:
        _add(issues, "pass_with_failure_code", "pass results require failure_code null.", "failure_code")
    if status in {"fail", "timeout", "resource-limit"} and failure_code is None:
        _add(issues, "missing_failure_code", "non-pass results require failure_code.", "failure_code")
    if status == "timeout" and failure_code != "sandbox-timeout":
        _add(issues, "invalid_timeout_failure_code", "timeout results require sandbox-timeout.", "failure_code")
    if status == "resource-limit" and failure_code != "sandbox-resource-limit":
        _add(issues, "invalid_resource_limit_failure_code", "resource-limit results require sandbox-resource-limit.", "failure_code")


def _validate_integer_and_boolean_fields(data: dict[str, Any], issues: list[SandboxExecutionResultIssue]) -> None:
    for field in ("duration_ms", "stdout_bytes", "stderr_bytes"):
        if not _non_negative_int(data.get(field)):
            code = "invalid_duration_ms" if field == "duration_ms" else "invalid_byte_count"
            _add(issues, code, f"{field} must be a non-negative integer.", field)
    for field in ("stdout_truncated", "stderr_truncated", "output_json_valid"):
        if not isinstance(data.get(field), bool):
            _add(issues, "invalid_boolean_field", f"{field} must be a boolean.", field)


def _validate_no_write_evidence(value: Any, issues: list[SandboxExecutionResultIssue], *, require_cleanup: bool) -> None:
    if not isinstance(value, dict):
        _add(issues, "invalid_no_write_evidence", "no_write_evidence must be an object.", "no_write_evidence")
        return
    protected_roots = value.get("protected_roots")
    pre_hashes = value.get("pre_hashes")
    post_hashes = value.get("post_hashes")
    if not isinstance(protected_roots, list) or not protected_roots:
        _add(issues, "invalid_no_write_evidence", "protected_roots must be a non-empty ordered list.", "no_write_evidence.protected_roots")
        return
    if not all(isinstance(item, str) and item for item in protected_roots):
        _add(issues, "invalid_no_write_evidence", "protected_roots must contain non-empty strings.", "no_write_evidence.protected_roots")
    if not isinstance(pre_hashes, dict) or not isinstance(post_hashes, dict):
        _add(issues, "invalid_no_write_evidence", "pre_hashes and post_hashes must be objects.", "no_write_evidence")
        return
    if list(pre_hashes.keys()) != protected_roots:
        _add(issues, "invalid_no_write_evidence", "pre_hashes keys must match protected_roots order.", "no_write_evidence.pre_hashes")
    if list(post_hashes.keys()) != protected_roots:
        _add(issues, "invalid_no_write_evidence", "post_hashes keys must match protected_roots order.", "no_write_evidence.post_hashes")
    for root, digest in pre_hashes.items():
        if not isinstance(root, str) or not _valid_hash(digest):
            _add(issues, "invalid_hash_format", "pre_hashes values must use sha256:<lowercase-hex>.", f"no_write_evidence.pre_hashes.{root}")
    for root, digest in post_hashes.items():
        if not isinstance(root, str) or not _valid_hash(digest):
            _add(issues, "invalid_hash_format", "post_hashes values must use sha256:<lowercase-hex>.", f"no_write_evidence.post_hashes.{root}")
    if value.get("mutation_detected") is not False:
        _add(issues, "mutation_detected_true", "mutation_detected must be false.", "no_write_evidence.mutation_detected")
    if require_cleanup and value.get("temp_root_cleaned") is not True:
        _add(issues, "temp_root_not_cleaned", "pass results require temp_root_cleaned true.", "no_write_evidence.temp_root_cleaned")
    elif not isinstance(value.get("temp_root_cleaned"), bool):
        _add(issues, "invalid_no_write_evidence", "temp_root_cleaned must be a boolean.", "no_write_evidence.temp_root_cleaned")
    if not isinstance(value.get("unexpected_outputs"), list):
        _add(issues, "invalid_no_write_evidence", "unexpected_outputs must be a list.", "no_write_evidence.unexpected_outputs")


def _validate_trace_id(value: Any, issues: list[SandboxExecutionResultIssue]) -> None:
    if value is not None and not _non_empty_string(value):
        _add(issues, "invalid_trace_id", "trace_id must be null or a non-empty string.", "trace_id")


def _validate_resource_limit(value: Any, issues: list[SandboxExecutionResultIssue], *, required: bool) -> None:
    if value is None:
        if required:
            _add(issues, "invalid_resource_limit", "resource-limit results require resource_limit.", "resource_limit")
        return
    if not isinstance(value, dict):
        _add(issues, "invalid_resource_limit", "resource_limit must be an object or null.", "resource_limit")
        return
    if value.get("limit_kind") not in ALLOWED_RESOURCE_LIMIT_KINDS:
        _add(issues, "invalid_resource_limit", "resource_limit.limit_kind is unsupported.", "resource_limit.limit_kind")
    if not _positive_int(value.get("limit_bytes")):
        _add(issues, "invalid_resource_limit", "resource_limit.limit_bytes must be a positive integer.", "resource_limit.limit_bytes")
    if not _non_negative_int(value.get("observed_bytes")):
        _add(issues, "invalid_resource_limit", "resource_limit.observed_bytes must be a non-negative integer.", "resource_limit.observed_bytes")


def _validate_edge_classification(value: Any, issues: list[SandboxExecutionResultIssue]) -> None:
    if value is None:
        return
    if value not in ALLOWED_EDGE_CLASSIFICATIONS:
        _add(issues, "invalid_edge_classification", "edge_classification is unsupported.", "edge_classification")


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _integer_or_null(value: Any) -> bool:
    return value is None or (isinstance(value, int) and not isinstance(value, bool))


def _non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _valid_hash(value: Any) -> bool:
    return isinstance(value, str) and HASH_RE.match(value) is not None


def _add(issues: list[SandboxExecutionResultIssue], code: str, message: str, field: str | None = None) -> None:
    issues.append(SandboxExecutionResultIssue(code, SEVERITY_ERROR, message, field=field))
