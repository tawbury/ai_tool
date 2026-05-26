from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from aios.providers.sandbox_trace import (
    ALLOWED_FAILURE_CODES,
    ALLOWED_PROVIDER_MODES,
    ALLOWED_SANDBOX_MODES,
    ALLOWED_STATUSES,
    SANDBOX_TRACE_SCHEMA_VERSION,
    validate_sandbox_trace_data,
)


ROOT = Path(__file__).resolve().parents[1]
TRACES = ROOT / "tests" / "fixtures" / "providers" / "sandbox_traces"
VALID = TRACES / "valid"
INVALID = TRACES / "invalid"
EDGE = TRACES / "edge"
INVALID_FIXTURES = {
    "missing_trace_id.json": "missing_trace_id",
    "invalid_status.json": "invalid_status",
    "pass_with_failure_code.json": "pass_with_failure_code",
    "mutation_performed_true.json": "mutation_performed_true",
    "network_disabled_false.json": "network_not_disabled",
    "unsafe_observed_output_path.json": "unsafe_observed_output_ref",
    "missing_provenance.json": "missing_provenance",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def valid_trace() -> dict[str, Any]:
    return load(VALID / "successful_sandbox_trace.json")


def codes(data: Any) -> list[str]:
    return [issue.code for issue in validate_sandbox_trace_data(data).issues]


def test_sandbox_trace_constants_match_contract() -> None:
    assert SANDBOX_TRACE_SCHEMA_VERSION == "aios.sandbox_trace.v0"
    assert ALLOWED_SANDBOX_MODES == frozenset({"fixture-mock", "subprocess-temp-cwd"})
    assert ALLOWED_PROVIDER_MODES == frozenset({"fixture-mock", "subprocess-sandbox"})
    assert ALLOWED_STATUSES == frozenset({"pass", "fail", "timeout", "resource-limit"})
    assert {
        "sandbox-timeout",
        "sandbox-nonzero-exit",
        "sandbox-output-invalid",
        "sandbox-resource-limit",
        "sandbox-network-attempt",
        "sandbox-filesystem-violation",
        "sandbox-env-access-violation",
        "sandbox-nondeterministic-output",
    } <= ALLOWED_FAILURE_CODES


def test_valid_sandbox_trace_fixtures_produce_no_errors() -> None:
    for path in sorted(VALID.glob("*.json")):
        result = validate_sandbox_trace_data(load(path))

        assert result.status == "pass", path
        assert result.errors == [], path
        assert result.warnings == [], path


def test_edge_sandbox_trace_fixtures_produce_no_errors() -> None:
    for path in sorted(EDGE.glob("*.json")):
        result = validate_sandbox_trace_data(load(path))

        assert result.status == "pass", path
        assert result.errors == [], path
        assert result.warnings == [], path


def test_invalid_sandbox_trace_fixtures_return_expected_issue_code() -> None:
    for name, expected_code in INVALID_FIXTURES.items():
        result = validate_sandbox_trace_data(load(INVALID / name))

        assert result.status == "fail", name
        assert expected_code in [issue.code for issue in result.errors], (name, result.issues)


def test_request_id_mismatch_fixture_is_relationship_only_for_helper_scope() -> None:
    result = validate_sandbox_trace_data(load(INVALID / "request_id_mismatch.json"))

    assert result.status == "pass"
    assert result.errors == []


def test_schema_trace_id_request_id_and_modes_are_validated() -> None:
    data = valid_trace()
    data["schema_version"] = "aios.sandbox_trace.v9"
    assert "unsupported_schema_version" in codes(data)

    data = valid_trace()
    data["trace_id"] = ""
    assert "invalid_trace_id" in codes(data)

    data = valid_trace()
    data["request_id"] = ""
    assert "invalid_request_id" in codes(data)

    data = valid_trace()
    data["sandbox_mode"] = "host-direct"
    assert "invalid_sandbox_mode" in codes(data)

    data = valid_trace()
    data["provider_mode"] = "dynamic-plugin"
    assert "invalid_provider_mode" in codes(data)


def test_status_failure_mapping_is_validated() -> None:
    data = valid_trace()
    data["status"] = "ok"
    assert "invalid_status" in codes(data)

    data = valid_trace()
    data["failure_code"] = "not-a-code"
    assert "invalid_failure_code" in codes(data)

    data = valid_trace()
    data["failure_code"] = "sandbox-output-invalid"
    assert "pass_with_failure_code" in codes(data)

    data = valid_trace()
    data["status"] = "fail"
    data["failure_code"] = None
    assert "missing_failure_code" in codes(data)

    data = load(VALID / "timeout_sandbox_trace.json")
    data["failure_code"] = "sandbox-nonzero-exit"
    assert "invalid_timeout_failure_code" in codes(data)

    data = load(VALID / "resource_limit_sandbox_trace.json")
    data["failure_code"] = "sandbox-nonzero-exit"
    assert "invalid_resource_limit_failure_code" in codes(data)


def test_duration_timestamps_network_mutation_and_no_write_are_validated() -> None:
    data = valid_trace()
    data["duration_ms"] = -1
    assert "invalid_duration_ms" in codes(data)

    data = valid_trace()
    data["started_at"] = "not-a-timestamp"
    assert "invalid_timestamp" in codes(data)

    data = valid_trace()
    data["completed_at"] = "not-a-timestamp"
    assert "invalid_timestamp" in codes(data)

    data = valid_trace()
    data["network_disabled"] = False
    assert "network_not_disabled" in codes(data)

    data = valid_trace()
    data["mutation_performed"] = True
    assert "mutation_performed_true" in codes(data)

    data = valid_trace()
    data["no_write_confirmed"] = False
    assert "no_write_not_confirmed" in codes(data)


def test_reference_safety_is_validated() -> None:
    data = valid_trace()
    data["sandbox_policy_ref"] = "C:/absolute/policy.json"
    assert "unsafe_sandbox_policy_ref" in codes(data)

    data = valid_trace()
    data["sandbox_result_ref"] = "../sandbox_result.json"
    assert "unsafe_sandbox_result_ref" in codes(data)

    data = valid_trace()
    data["provider_trace_ref"] = "..\\trace.json"
    assert "unsafe_provider_trace_ref" in codes(data)


def test_observation_safety_and_hash_format_are_validated() -> None:
    data = valid_trace()
    data["observed_inputs"] = "not-a-list"
    assert "invalid_observed_inputs" in codes(data)

    data = valid_trace()
    data["observed_inputs"][0]["kind"] = "unknown"
    assert "invalid_observed_inputs" in codes(data)

    data = valid_trace()
    data["observed_inputs"][0]["hash"] = "sha256:UPPERCASE"
    assert "invalid_observed_inputs" in codes(data)

    data = valid_trace()
    data["observed_outputs"] = "not-a-list"
    assert "unsafe_observed_output_ref" in codes(data)

    data = valid_trace()
    data["observed_outputs"][0]["ref"] = "src/generated.json"
    assert "unsafe_observed_output_ref" in codes(data)

    data = valid_trace()
    data["observed_outputs"][0]["ref"] = "{sandbox_tmp}/../escape.json"
    assert "unsafe_observed_output_ref" in codes(data)


def test_provenance_is_validated() -> None:
    data = valid_trace()
    data["provenance"] = []
    assert "missing_provenance" in codes(data)

    data = valid_trace()
    data["provenance"]["source_refs"] = []
    assert "invalid_provenance" in codes(data)

    data = valid_trace()
    data["provenance"]["source_hashes"] = {
        "tests/fixtures/providers/traces/valid/whole_file_trace.json": "sha256:4444444444444444444444444444444444444444444444444444444444444444",
        "tests/fixtures/providers/sandbox_results/valid/successful_subprocess_result.json": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
    }
    assert "invalid_provenance" in codes(data)

    data = valid_trace()
    data["provenance"]["source_hashes"][
        "tests/fixtures/providers/sandbox_results/valid/successful_subprocess_result.json"
    ] = "sha256:UPPERCASE"
    assert "invalid_provenance" in codes(data)

    data = valid_trace()
    data["provenance"]["relationship"] = "execution-approved"
    assert "invalid_provenance" in codes(data)

    data = valid_trace()
    data["provenance"]["generated_by"] = "runtime"
    assert "invalid_provenance" in codes(data)


def test_provider_trace_ref_nullable_only_for_explicit_edge_classification() -> None:
    data = valid_trace()
    data["provider_trace_ref"] = None
    assert "provider_trace_ref_missing_without_edge" in codes(data)
    assert "provider_mode_present_without_provider_trace" in codes(data)

    data = valid_trace()
    data["provider_trace_ref"] = None
    data["provider_mode"] = None
    data["edge_classification"] = "provider-trace-ref-unavailable"
    assert validate_sandbox_trace_data(data).errors == []

    data = valid_trace()
    data["edge_classification"] = "execution-approved"
    assert "invalid_edge_classification" in codes(data)


def test_issue_dict_includes_code_severity_status_message_and_field() -> None:
    data = valid_trace()
    data["network_disabled"] = False
    issue = validate_sandbox_trace_data(data).errors[0].to_dict()

    assert issue["code"] == "network_not_disabled"
    assert issue["severity"] == "error"
    assert issue["status"] == "fail"
    assert issue["message"]
    assert issue["field"] == "network_disabled"


def test_non_object_trace_is_error() -> None:
    result = validate_sandbox_trace_data(["not", "object"])

    assert result.status == "fail"
    assert result.errors[0].code == "sandbox_trace_not_object"


def test_validator_does_not_mutate_input() -> None:
    data = valid_trace()
    before = copy.deepcopy(data)

    validate_sandbox_trace_data(data)

    assert data == before
