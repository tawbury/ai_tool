from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from aios.providers.sandbox_result import (
    ALLOWED_FAILURE_CODES,
    ALLOWED_SANDBOX_MODES,
    ALLOWED_STATUSES,
    SANDBOX_EXECUTION_RESULT_SCHEMA_VERSION,
    validate_sandbox_execution_result_data,
)


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "tests" / "fixtures" / "providers" / "sandbox_results"
VALID = RESULTS / "valid"
INVALID = RESULTS / "invalid"
EDGE = RESULTS / "edge"
INVALID_FIXTURES = {
    "missing_request_id.json": "missing_request_id",
    "mutation_performed_true.json": "mutation_performed_true",
    "no_write_false_pass.json": "no_write_not_confirmed",
    "network_disabled_false.json": "network_not_disabled",
    "pass_with_failure_code.json": "pass_with_failure_code",
    "fail_without_failure_code.json": "missing_failure_code",
    "negative_stdout_bytes.json": "invalid_byte_count",
    "malformed_no_write_evidence.json": "invalid_no_write_evidence",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def valid_result() -> dict[str, Any]:
    return load(VALID / "successful_subprocess_result.json")


def codes(data: Any) -> list[str]:
    return [issue.code for issue in validate_sandbox_execution_result_data(data).issues]


def test_sandbox_execution_result_constants_match_contract() -> None:
    assert SANDBOX_EXECUTION_RESULT_SCHEMA_VERSION == "aios.sandbox_execution_result.v0"
    assert ALLOWED_SANDBOX_MODES == frozenset({"fixture-mock", "subprocess-temp-cwd"})
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


def test_valid_sandbox_execution_result_fixtures_produce_no_errors() -> None:
    for path in sorted(VALID.glob("*.json")):
        result = validate_sandbox_execution_result_data(load(path))

        assert result.status == "pass", path
        assert result.errors == [], path
        assert result.warnings == [], path


def test_edge_sandbox_execution_result_fixtures_produce_no_errors() -> None:
    for path in sorted(EDGE.glob("*.json")):
        result = validate_sandbox_execution_result_data(load(path))

        assert result.status == "pass", path
        assert result.errors == [], path
        assert result.warnings == [], path


def test_invalid_sandbox_execution_result_fixtures_return_expected_issue_code() -> None:
    for name, expected_code in INVALID_FIXTURES.items():
        result = validate_sandbox_execution_result_data(load(INVALID / name))

        assert result.status == "fail", name
        assert expected_code in [issue.code for issue in result.errors], (name, result.issues)


def test_unsupported_schema_and_sandbox_mode_are_errors() -> None:
    data = valid_result()
    data["schema_version"] = "aios.sandbox_execution_result.v9"
    assert "unsupported_schema_version" in codes(data)

    data = valid_result()
    data["sandbox_mode"] = "host-direct"
    assert "unsupported_sandbox_mode" in codes(data)


def test_request_id_exit_code_and_status_are_validated() -> None:
    data = valid_result()
    data["request_id"] = ""
    assert "invalid_request_id" in codes(data)

    data = valid_result()
    data["exit_code"] = "0"
    assert "invalid_exit_code" in codes(data)

    data = valid_result()
    data["status"] = "ok"
    assert "invalid_status" in codes(data)


def test_invalid_failure_code_and_status_failure_mapping() -> None:
    data = load(VALID / "nonzero_exit_result.json")
    data["failure_code"] = "not-a-code"
    assert "invalid_failure_code" in codes(data)

    data = valid_result()
    data["failure_code"] = "sandbox-nonzero-exit"
    assert "pass_with_failure_code" in codes(data)

    data = load(VALID / "nonzero_exit_result.json")
    data["failure_code"] = None
    assert "missing_failure_code" in codes(data)

    data = load(VALID / "timeout_result.json")
    data["failure_code"] = "sandbox-nonzero-exit"
    assert "invalid_timeout_failure_code" in codes(data)

    data = load(VALID / "resource_limit_result.json")
    data["failure_code"] = "sandbox-nonzero-exit"
    assert "invalid_resource_limit_failure_code" in codes(data)


def test_duration_byte_counts_booleans_and_pass_output_json_are_validated() -> None:
    data = valid_result()
    data["duration_ms"] = -1
    assert "invalid_duration_ms" in codes(data)

    data = valid_result()
    data["stderr_bytes"] = -1
    assert "invalid_byte_count" in codes(data)

    data = valid_result()
    data["stdout_truncated"] = "false"
    assert "invalid_boolean_field" in codes(data)

    data = valid_result()
    data["output_json_valid"] = False
    assert "pass_output_json_invalid" in codes(data)


def test_network_mutation_and_no_write_flags_are_enforced() -> None:
    data = valid_result()
    data["network_disabled"] = False
    assert "network_not_disabled" in codes(data)

    data = valid_result()
    data["mutation_performed"] = True
    assert "mutation_performed_true" in codes(data)

    data = valid_result()
    data["no_write_confirmed"] = False
    assert "no_write_not_confirmed" in codes(data)


def test_no_write_evidence_and_hash_format_are_validated() -> None:
    data = valid_result()
    data["no_write_evidence"]["protected_roots"] = []
    assert "invalid_no_write_evidence" in codes(data)

    data = valid_result()
    data["no_write_evidence"]["post_hashes"] = {
        "target": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
        "source": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
        "manifest": "sha256:3333333333333333333333333333333333333333333333333333333333333333",
        "snapshots": "sha256:4444444444444444444444444444444444444444444444444444444444444444",
    }
    assert "invalid_no_write_evidence" in codes(data)

    data = valid_result()
    data["no_write_evidence"]["pre_hashes"]["source"] = "sha256:UPPERCASE"
    assert "invalid_hash_format" in codes(data)

    data = valid_result()
    data["no_write_evidence"]["mutation_detected"] = True
    assert "mutation_detected_true" in codes(data)

    data = valid_result()
    data["no_write_evidence"]["temp_root_cleaned"] = False
    assert "temp_root_not_cleaned" in codes(data)

    data = valid_result()
    data["no_write_evidence"]["unexpected_outputs"] = "none"
    assert "invalid_no_write_evidence" in codes(data)


def test_trace_id_resource_limit_and_edge_classification_are_validated() -> None:
    data = valid_result()
    data["trace_id"] = ""
    assert "invalid_trace_id" in codes(data)

    data = load(VALID / "resource_limit_result.json")
    data["resource_limit"] = None
    assert "invalid_resource_limit" in codes(data)

    data = load(VALID / "resource_limit_result.json")
    data["resource_limit"]["limit_bytes"] = 0
    assert "invalid_resource_limit" in codes(data)

    data = valid_result()
    data["edge_classification"] = "execution-approved"
    assert "invalid_edge_classification" in codes(data)


def test_issue_dict_includes_code_severity_status_message_and_field() -> None:
    data = valid_result()
    data["network_disabled"] = False
    issue = validate_sandbox_execution_result_data(data).errors[0].to_dict()

    assert issue["code"] == "network_not_disabled"
    assert issue["severity"] == "error"
    assert issue["status"] == "fail"
    assert issue["message"]
    assert issue["field"] == "network_disabled"


def test_non_object_result_is_error() -> None:
    result = validate_sandbox_execution_result_data(["not", "object"])

    assert result.status == "fail"
    assert result.errors[0].code == "sandbox_execution_result_not_object"


def test_validator_does_not_mutate_input() -> None:
    data = valid_result()
    before = copy.deepcopy(data)

    validate_sandbox_execution_result_data(data)

    assert data == before
