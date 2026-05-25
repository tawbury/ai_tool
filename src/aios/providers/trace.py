from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from ..status import SEVERITY_ERROR, SEVERITY_WARNING, STATUS_FAIL, STATUS_PASS, STATUS_WARN


PROVIDER_EXECUTION_TRACE_SCHEMA_VERSION = "aios.provider_execution_trace.v0"
PROVIDER_HASH_POLICY = "aios.hash_policy.v0"
PROVIDER_MODES = frozenset({"fixture-mock", "subprocess-sandbox"})
FAILURE_CODES = frozenset(
    {
        "provider-timeout",
        "nondeterministic-output",
        "provider-execution-disabled",
        "provider-isolation-violation",
        "provider-capability-missing",
        "provider-output-invalid",
        "provider-network-disabled",
        "provider-resource-limit",
    }
)
REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "trace_id",
        "provider_id",
        "provider_version",
        "provider_mode",
        "case_id",
        "input_hash",
        "output_hash",
        "generated_hashes",
        "duration_ms",
        "deterministic_execution",
        "no_write_confirmed",
        "network_disabled",
        "mutation_performed",
        "unavailable_reason",
        "failure_code",
        "provenance",
    }
)
GENERATED_HASH_FIELDS = frozenset(
    {
        "generated_bytes_hash",
        "generated_target_hash",
        "generated_managed_block_hash",
    }
)
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class ProviderExecutionTraceIssue:
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
class ProviderExecutionTraceValidationResult:
    issues: list[ProviderExecutionTraceIssue]

    @property
    def status(self) -> str:
        if any(issue.severity == SEVERITY_ERROR for issue in self.issues):
            return STATUS_FAIL
        if any(issue.severity == SEVERITY_WARNING for issue in self.issues):
            return STATUS_WARN
        return STATUS_PASS

    @property
    def errors(self) -> list[ProviderExecutionTraceIssue]:
        return [issue for issue in self.issues if issue.severity == SEVERITY_ERROR]

    @property
    def warnings(self) -> list[ProviderExecutionTraceIssue]:
        return [issue for issue in self.issues if issue.severity == SEVERITY_WARNING]


def validate_provider_execution_trace_data(data: Any) -> ProviderExecutionTraceValidationResult:
    """Validate parsed provider execution trace data without running any provider."""
    issues: list[ProviderExecutionTraceIssue] = []
    if not isinstance(data, dict):
        return ProviderExecutionTraceValidationResult(
            [
                ProviderExecutionTraceIssue(
                    "provider_execution_trace_not_object",
                    SEVERITY_ERROR,
                    "Provider execution trace must be a JSON object.",
                )
            ]
        )

    _validate_required_fields(data, issues)

    if data.get("schema_version") != PROVIDER_EXECUTION_TRACE_SCHEMA_VERSION:
        _add(issues, "unsupported_schema_version", "schema_version must be aios.provider_execution_trace.v0.", "schema_version")
    if not _non_empty_string(data.get("trace_id")):
        code = "missing_trace_id" if "trace_id" not in data else "invalid_trace_id"
        _add(issues, code, "trace_id must be a non-empty string.", "trace_id")
    if not _non_empty_string(data.get("provider_id")):
        _add(issues, "invalid_provider_id", "provider_id must be a non-empty string.", "provider_id")
    if not _non_empty_string(data.get("provider_version")):
        _add(issues, "invalid_provider_version", "provider_version must be a non-empty string.", "provider_version")
    if data.get("provider_mode") not in PROVIDER_MODES:
        _add(issues, "invalid_provider_mode", "provider_mode is unsupported.", "provider_mode")
    if not _valid_hash_or_null(data.get("input_hash"), nullable=False):
        _add(issues, "invalid_hash_format", "input_hash must use sha256:<lowercase-hex>.", "input_hash")
    if not _valid_hash_or_null(data.get("output_hash"), nullable=True):
        _add(issues, "invalid_hash_format", "output_hash must be null or use sha256:<lowercase-hex>.", "output_hash")
    _validate_generated_hashes(data.get("generated_hashes"), issues)
    if not _non_negative_int(data.get("duration_ms")):
        _add(issues, "invalid_duration", "duration_ms must be a non-negative integer.", "duration_ms")
    if data.get("deterministic_execution") is not True:
        _add(issues, "nondeterministic_execution_false", "deterministic_execution must be true.", "deterministic_execution")
    if data.get("no_write_confirmed") is not True:
        code = "missing_no_write_confirmed" if "no_write_confirmed" not in data else "no_write_not_confirmed"
        _add(issues, code, "no_write_confirmed must be true.", "no_write_confirmed")
    if data.get("network_disabled") is not True:
        _add(issues, "network_not_disabled", "network_disabled must be true.", "network_disabled")
    if data.get("mutation_performed") is not False:
        _add(issues, "mutation_performed_true", "mutation_performed must be false.", "mutation_performed")
    if data.get("failure_code") is not None and data.get("failure_code") not in FAILURE_CODES:
        _add(issues, "invalid_failure_code", "failure_code is unsupported.", "failure_code")

    _validate_unavailable_failure_semantics(data, issues)
    _validate_provenance(data.get("provenance"), issues)
    _validate_hash_policy(data.get("hash_policy"), issues)

    return ProviderExecutionTraceValidationResult(issues)


def _validate_required_fields(data: dict[str, Any], issues: list[ProviderExecutionTraceIssue]) -> None:
    for field in sorted(REQUIRED_FIELDS - data.keys()):
        code = {
            "trace_id": "missing_trace_id",
            "no_write_confirmed": "missing_no_write_confirmed",
            "provenance": "missing_provenance",
        }.get(field, "missing_required_field")
        _add(issues, code, f"Missing required field: {field}", field)


def _validate_generated_hashes(value: Any, issues: list[ProviderExecutionTraceIssue]) -> None:
    if not isinstance(value, dict):
        _add(issues, "invalid_generated_hashes", "generated_hashes must be an object.", "generated_hashes")
        return
    for field in sorted(GENERATED_HASH_FIELDS - value.keys()):
        _add(issues, "invalid_generated_hashes", f"Missing generated hash field: {field}", f"generated_hashes.{field}")
    for field in sorted(GENERATED_HASH_FIELDS & value.keys()):
        if not _valid_hash_or_null(value.get(field), nullable=True):
            _add(issues, "invalid_hash_format", f"{field} must be null or use sha256:<lowercase-hex>.", f"generated_hashes.{field}")


def _validate_unavailable_failure_semantics(data: dict[str, Any], issues: list[ProviderExecutionTraceIssue]) -> None:
    generated_hashes = data.get("generated_hashes")
    generated_values = generated_hashes.values() if isinstance(generated_hashes, dict) else []
    unavailable = data.get("unavailable_reason") is not None
    failed = data.get("failure_code") is not None

    if failed and data.get("unavailable_reason") is None:
        _add(issues, "missing_unavailable_reason", "failure traces must include unavailable_reason.", "unavailable_reason")
    if (unavailable or failed) and any(value is not None for value in generated_values):
        _add(issues, "unavailable_generated_hash_present", "Unavailable or failed traces must not include generated hashes.", "generated_hashes")
    if not unavailable and not failed and isinstance(generated_hashes, dict):
        if generated_hashes.get("generated_bytes_hash") is None:
            _add(issues, "missing_generated_hash", "Successful available traces must include generated_bytes_hash.", "generated_hashes.generated_bytes_hash")


def _validate_provenance(value: Any, issues: list[ProviderExecutionTraceIssue]) -> None:
    if not isinstance(value, dict):
        code = "missing_provenance" if value is None else "invalid_provenance"
        _add(issues, code, "provenance must be an object.", "provenance")
        return
    source_paths = value.get("source_paths")
    source_hashes = value.get("source_hashes")
    if not isinstance(source_paths, list) or not source_paths or not all(isinstance(path, str) and path for path in source_paths):
        _add(issues, "invalid_provenance", "provenance.source_paths must be a non-empty list of strings.", "provenance.source_paths")
        return
    if len(source_paths) != len(set(source_paths)):
        _add(issues, "invalid_provenance", "provenance.source_paths must not contain duplicates.", "provenance.source_paths")
    if not isinstance(source_hashes, dict):
        _add(issues, "invalid_provenance", "provenance.source_hashes must be an object.", "provenance.source_hashes")
        return
    if list(source_hashes.keys()) != source_paths:
        _add(issues, "invalid_provenance", "provenance.source_hashes order must match source_paths.", "provenance.source_hashes")
    for path, digest in source_hashes.items():
        if not isinstance(path, str) or not _valid_hash_or_null(digest, nullable=False):
            _add(issues, "invalid_hash_format", "provenance source hashes must use sha256:<lowercase-hex>.", f"provenance.source_hashes.{path}")


def _validate_hash_policy(value: Any, issues: list[ProviderExecutionTraceIssue]) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        _add(issues, "invalid_hash_policy", "hash_policy must be an object when present.", "hash_policy")
        return
    expected = {
        "version": PROVIDER_HASH_POLICY,
        "normalization": "none",
        "line_endings": "preserve",
        "trailing_newline": "preserve",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            _add(issues, "invalid_hash_policy", f"hash_policy.{field} must be {expected_value}.", f"hash_policy.{field}")


def _valid_hash_or_null(value: Any, *, nullable: bool) -> bool:
    if value is None:
        return nullable
    return isinstance(value, str) and HASH_RE.match(value) is not None


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _add(issues: list[ProviderExecutionTraceIssue], code: str, message: str, field: str | None = None) -> None:
    issues.append(ProviderExecutionTraceIssue(code, SEVERITY_ERROR, message, field=field))
