from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

from ..status import SEVERITY_ERROR, SEVERITY_WARNING, STATUS_FAIL, STATUS_PASS, STATUS_WARN


SANDBOX_TRACE_SCHEMA_VERSION = "aios.sandbox_trace.v0"
SANDBOX_TMP_PREFIX = "{sandbox_tmp}/"
ALLOWED_SANDBOX_MODES = frozenset({"fixture-mock", "subprocess-temp-cwd"})
ALLOWED_PROVIDER_MODES = frozenset({"fixture-mock", "subprocess-sandbox"})
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
ALLOWED_OBSERVATION_KINDS = frozenset(
    {
        "sandbox-policy",
        "sandbox-result",
        "provider-trace",
        "input-bundle",
        "output-json",
        "stdout",
        "stderr",
    }
)
ALLOWED_EDGE_CLASSIFICATIONS = frozenset(
    {
        "provider-trace-ref-unavailable",
        "zero-duration-deterministic-placeholder",
        "partial-observed-outputs-after-resource-limit",
    }
)
REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "trace_id",
        "request_id",
        "sandbox_mode",
        "provider_mode",
        "sandbox_policy_ref",
        "sandbox_result_ref",
        "provider_trace_ref",
        "started_at",
        "completed_at",
        "duration_ms",
        "status",
        "failure_code",
        "network_disabled",
        "mutation_performed",
        "no_write_confirmed",
        "observed_inputs",
        "observed_outputs",
        "provenance",
    }
)
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")


@dataclass(frozen=True)
class SandboxTraceIssue:
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
class SandboxTraceValidationResult:
    issues: list[SandboxTraceIssue]

    @property
    def status(self) -> str:
        if any(issue.severity == SEVERITY_ERROR for issue in self.issues):
            return STATUS_FAIL
        if any(issue.severity == SEVERITY_WARNING for issue in self.issues):
            return STATUS_WARN
        return STATUS_PASS

    @property
    def errors(self) -> list[SandboxTraceIssue]:
        return [issue for issue in self.issues if issue.severity == SEVERITY_ERROR]

    @property
    def warnings(self) -> list[SandboxTraceIssue]:
        return [issue for issue in self.issues if issue.severity == SEVERITY_WARNING]


def validate_sandbox_trace_data(data: Any) -> SandboxTraceValidationResult:
    """Validate parsed sandbox trace data without launching or executing anything."""
    issues: list[SandboxTraceIssue] = []
    if not isinstance(data, dict):
        return SandboxTraceValidationResult(
            [
                SandboxTraceIssue(
                    "sandbox_trace_not_object",
                    SEVERITY_ERROR,
                    "Sandbox trace must be a JSON object.",
                )
            ]
        )

    _validate_required_fields(data, issues)

    if data.get("schema_version") != SANDBOX_TRACE_SCHEMA_VERSION:
        _add(issues, "unsupported_schema_version", "schema_version must be aios.sandbox_trace.v0.", "schema_version")
    if not _non_empty_string(data.get("trace_id")):
        code = "missing_trace_id" if "trace_id" not in data else "invalid_trace_id"
        _add(issues, code, "trace_id must be a non-empty string.", "trace_id")
    if not _non_empty_string(data.get("request_id")):
        code = "missing_request_id" if "request_id" not in data else "invalid_request_id"
        _add(issues, code, "request_id must be a non-empty string.", "request_id")
    if data.get("sandbox_mode") not in ALLOWED_SANDBOX_MODES:
        _add(issues, "invalid_sandbox_mode", "sandbox_mode is unsupported.", "sandbox_mode")

    provider_mode = data.get("provider_mode")
    if provider_mode is not None and provider_mode not in ALLOWED_PROVIDER_MODES:
        _add(issues, "invalid_provider_mode", "provider_mode is unsupported.", "provider_mode")

    _validate_status_failure_mapping(data, issues)
    _validate_timing_and_flags(data, issues)
    _validate_refs(data, issues)
    _validate_observations(data.get("observed_inputs"), issues, field="observed_inputs", output=False)
    _validate_observations(data.get("observed_outputs"), issues, field="observed_outputs", output=True)
    _validate_provenance(data.get("provenance"), issues)
    _validate_provider_trace_ref_policy(data, issues)
    _validate_edge_classification(data.get("edge_classification"), issues)

    return SandboxTraceValidationResult(issues)


def _validate_required_fields(data: dict[str, Any], issues: list[SandboxTraceIssue]) -> None:
    for field in sorted(REQUIRED_FIELDS - data.keys()):
        if field == "trace_id":
            code = "missing_trace_id"
        elif field == "request_id":
            code = "missing_request_id"
        elif field == "provenance":
            code = "missing_provenance"
        else:
            code = "missing_required_field"
        _add(issues, code, f"Missing required field: {field}", field)


def _validate_status_failure_mapping(data: dict[str, Any], issues: list[SandboxTraceIssue]) -> None:
    status = data.get("status")
    failure_code = data.get("failure_code")
    if status not in ALLOWED_STATUSES:
        _add(issues, "invalid_status", "status is unsupported.", "status")
    if failure_code is not None and failure_code not in ALLOWED_FAILURE_CODES:
        _add(issues, "invalid_failure_code", "failure_code is unsupported.", "failure_code")
    if status == "pass" and failure_code is not None:
        _add(issues, "pass_with_failure_code", "pass traces require failure_code null.", "failure_code")
    if status in {"fail", "timeout", "resource-limit"} and failure_code is None:
        _add(issues, "missing_failure_code", "non-pass traces require failure_code.", "failure_code")
    if status == "timeout" and failure_code != "sandbox-timeout":
        _add(issues, "invalid_timeout_failure_code", "timeout traces require sandbox-timeout.", "failure_code")
    if status == "resource-limit" and failure_code != "sandbox-resource-limit":
        _add(issues, "invalid_resource_limit_failure_code", "resource-limit traces require sandbox-resource-limit.", "failure_code")


def _validate_timing_and_flags(data: dict[str, Any], issues: list[SandboxTraceIssue]) -> None:
    if not _valid_timestamp(data.get("started_at")):
        _add(issues, "invalid_timestamp", "started_at must be an RFC3339 UTC timestamp string.", "started_at")
    if not _valid_timestamp(data.get("completed_at")):
        _add(issues, "invalid_timestamp", "completed_at must be an RFC3339 UTC timestamp string.", "completed_at")
    if not _non_negative_int(data.get("duration_ms")):
        _add(issues, "invalid_duration_ms", "duration_ms must be a non-negative integer.", "duration_ms")
    if data.get("network_disabled") is not True:
        _add(issues, "network_not_disabled", "network_disabled must be true.", "network_disabled")
    if data.get("mutation_performed") is not False:
        _add(issues, "mutation_performed_true", "mutation_performed must be false.", "mutation_performed")
    if data.get("status") == "pass" and data.get("no_write_confirmed") is not True:
        _add(issues, "no_write_not_confirmed", "pass traces require no_write_confirmed true.", "no_write_confirmed")


def _validate_refs(data: dict[str, Any], issues: list[SandboxTraceIssue]) -> None:
    if not _safe_ref(data.get("sandbox_policy_ref"), allow_null=True):
        _add(issues, "unsafe_sandbox_policy_ref", "sandbox_policy_ref must be null or a safe relative ref.", "sandbox_policy_ref")
    if not _safe_ref(data.get("sandbox_result_ref"), allow_null=False):
        _add(issues, "unsafe_sandbox_result_ref", "sandbox_result_ref must be a safe relative ref.", "sandbox_result_ref")
    if not _safe_ref(data.get("provider_trace_ref"), allow_null=True):
        _add(issues, "unsafe_provider_trace_ref", "provider_trace_ref must be null or a safe relative ref.", "provider_trace_ref")


def _validate_observations(value: Any, issues: list[SandboxTraceIssue], *, field: str, output: bool) -> None:
    if not isinstance(value, list):
        code = "unsafe_observed_output_ref" if output else "invalid_observed_inputs"
        _add(issues, code, f"{field} must be a list.", field)
        return
    for index, item in enumerate(value):
        item_field = f"{field}.{index}"
        if not isinstance(item, dict):
            code = "unsafe_observed_output_ref" if output else "invalid_observed_inputs"
            _add(issues, code, f"{item_field} must be an object.", item_field)
            continue
        if item.get("kind") not in ALLOWED_OBSERVATION_KINDS:
            code = "unsafe_observed_output_ref" if output else "invalid_observed_inputs"
            _add(issues, code, f"{item_field}.kind is unsupported.", f"{item_field}.kind")
        ref = item.get("ref")
        if not _safe_ref(ref, allow_null=False):
            code = "unsafe_observed_output_ref" if output else "invalid_observed_inputs"
            _add(issues, code, f"{item_field}.ref must be a safe relative ref.", f"{item_field}.ref")
        elif output and _is_repo_output_ref(ref):
            _add(issues, "unsafe_observed_output_ref", "observed output refs must not point at repository source/target paths.", f"{item_field}.ref")
        hash_value = item.get("hash")
        if hash_value is not None and not _valid_hash(hash_value):
            code = "unsafe_observed_output_ref" if output else "invalid_observed_inputs"
            _add(issues, code, f"{item_field}.hash must use sha256:<lowercase-hex>.", f"{item_field}.hash")


def _validate_provenance(value: Any, issues: list[SandboxTraceIssue]) -> None:
    if not isinstance(value, dict):
        _add(issues, "missing_provenance", "provenance must be an object.", "provenance")
        return
    source_refs = value.get("source_refs")
    source_hashes = value.get("source_hashes")
    if not isinstance(source_refs, list) or not source_refs:
        _add(issues, "invalid_provenance", "provenance.source_refs must be a non-empty ordered list.", "provenance.source_refs")
        return
    for index, ref in enumerate(source_refs):
        if not _safe_ref(ref, allow_null=False):
            _add(issues, "invalid_provenance", "provenance source refs must be safe relative refs.", f"provenance.source_refs.{index}")
    if not isinstance(source_hashes, dict):
        _add(issues, "invalid_provenance", "provenance.source_hashes must be an object.", "provenance.source_hashes")
        return
    if list(source_hashes.keys()) != source_refs:
        _add(issues, "invalid_provenance", "provenance.source_hashes keys must match source_refs order.", "provenance.source_hashes")
    for ref, digest in source_hashes.items():
        if not isinstance(ref, str) or not _valid_hash(digest):
            _add(issues, "invalid_provenance", "provenance source hashes must use sha256:<lowercase-hex>.", f"provenance.source_hashes.{ref}")
    if value.get("relationship") not in {"sandbox-result-to-provider-trace", "sandbox-result-without-provider-trace"}:
        _add(issues, "invalid_provenance", "provenance.relationship is unsupported.", "provenance.relationship")
    if value.get("generated_by") != "fixture-contract":
        _add(issues, "invalid_provenance", "provenance.generated_by must be fixture-contract.", "provenance.generated_by")


def _validate_provider_trace_ref_policy(data: dict[str, Any], issues: list[SandboxTraceIssue]) -> None:
    if data.get("provider_trace_ref") is not None:
        return
    if data.get("edge_classification") != "provider-trace-ref-unavailable":
        _add(
            issues,
            "provider_trace_ref_missing_without_edge",
            "provider_trace_ref may be null only for provider-trace-ref-unavailable edge fixtures.",
            "provider_trace_ref",
        )
    if data.get("provider_mode") is not None:
        _add(
            issues,
            "provider_mode_present_without_provider_trace",
            "provider_mode must be null when provider_trace_ref is null.",
            "provider_mode",
        )


def _validate_edge_classification(value: Any, issues: list[SandboxTraceIssue]) -> None:
    if value is None:
        return
    if value not in ALLOWED_EDGE_CLASSIFICATIONS:
        _add(issues, "invalid_edge_classification", "edge_classification is unsupported.", "edge_classification")


def _safe_ref(value: Any, *, allow_null: bool) -> bool:
    if value is None:
        return allow_null
    if not isinstance(value, str) or not value:
        return False
    if value.startswith(SANDBOX_TMP_PREFIX):
        return _safe_relative_path(value[len(SANDBOX_TMP_PREFIX) :])
    return _safe_relative_path(value)


def _safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if "\\" in value or value.startswith("/") or value.startswith("\\") or _WINDOWS_ABSOLUTE_RE.match(value):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and not any(part in {"", "."} for part in value.split("/"))


def _is_repo_output_ref(value: Any) -> bool:
    return isinstance(value, str) and value.startswith(("src/", ".ai/", "docs/"))


def _valid_timestamp(value: Any) -> bool:
    return isinstance(value, str) and TIMESTAMP_RE.match(value) is not None


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _valid_hash(value: Any) -> bool:
    return isinstance(value, str) and HASH_RE.match(value) is not None


def _add(issues: list[SandboxTraceIssue], code: str, message: str, field: str | None = None) -> None:
    issues.append(SandboxTraceIssue(code, SEVERITY_ERROR, message, field=field))
