from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "tests" / "fixtures" / "providers" / "sandbox_results"
VALID = RESULTS / "valid"
INVALID = RESULTS / "invalid"
EDGE = RESULTS / "edge"
INDEX = RESULTS / "sandbox_result_index.json"

SCHEMA_VERSION = "aios.sandbox_execution_result.v0"
INDEX_SCHEMA_VERSION = "aios.sandbox_execution_result_fixture_index.v0"
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
ALLOWED_SANDBOX_MODES = {"fixture-mock", "subprocess-temp-cwd"}
ALLOWED_STATUS = {"pass", "fail", "timeout", "resource-limit"}
ALLOWED_FAILURE_CODES = {
    "sandbox-timeout",
    "sandbox-nonzero-exit",
    "sandbox-output-invalid",
    "sandbox-resource-limit",
    "sandbox-network-attempt",
    "sandbox-filesystem-violation",
    "sandbox-env-access-violation",
    "sandbox-nondeterministic-output",
}
REQUIRED_FIELDS = {
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
VALID_FIXTURES = {
    "successful_subprocess_result.json",
    "successful_fixture_mock_result.json",
    "nonzero_exit_result.json",
    "timeout_result.json",
    "resource_limit_result.json",
}
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
EDGE_FIXTURES = {
    "zero_duration_result.json",
    "truncated_stdout_result.json",
    "invalid_output_json_result.json",
}
NON_EXECUTION_FLAGS = {
    "sandbox_execution": False,
    "subprocess_execution": False,
    "provider_execution": False,
    "replay_execution": False,
    "generated_content_creation": False,
    "mutation_performed": False,
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_sandbox_execution_result_fixture_inventory_matches_contract() -> None:
    assert {path.name for path in VALID.glob("*.json")} == VALID_FIXTURES
    assert {path.name for path in INVALID.glob("*.json")} == set(INVALID_FIXTURES)
    assert {path.name for path in EDGE.glob("*.json")} == EDGE_FIXTURES

    index = load(INDEX)
    assert index["schema_version"] == INDEX_SCHEMA_VERSION
    for key, expected in NON_EXECUTION_FLAGS.items():
        assert index[key] is expected
    assert set(index["valid"]) == {f"valid/{name}" for name in VALID_FIXTURES}
    assert set(index["invalid"]) == {f"invalid/{name}" for name in INVALID_FIXTURES}
    assert set(index["edge"]) == {f"edge/{name}" for name in EDGE_FIXTURES}


def test_sandbox_execution_result_index_references_existing_fixtures() -> None:
    index = load(INDEX)

    for group in ("valid", "invalid", "edge"):
        for relative_path in index[group]:
            assert (RESULTS / relative_path).is_file(), relative_path


def test_every_sandbox_execution_result_fixture_parses() -> None:
    for path in sorted(RESULTS.glob("*/*.json")):
        data = load(path)

        assert isinstance(data, dict), path
        assert data.get("schema_version") == SCHEMA_VERSION, path


def test_valid_sandbox_execution_result_fixtures_match_contract() -> None:
    for path in sorted(VALID.glob("*.json")):
        data = load(path)
        issues = _validate_result(data)

        assert issues == [], (path, issues)
        _assert_result_invariants(data, path=path)


def test_edge_sandbox_execution_result_fixtures_are_explicitly_classified() -> None:
    for path in sorted(EDGE.glob("*.json")):
        data = load(path)
        issues = _validate_result(data)

        assert issues == [], (path, issues)
        assert isinstance(data.get("edge_classification"), str) and data["edge_classification"], path
        _assert_result_invariants(data, path=path)


def test_invalid_sandbox_execution_result_fixtures_fail_expected_assertion() -> None:
    for name, expected_code in INVALID_FIXTURES.items():
        data = load(INVALID / name)
        issues = _validate_result(data)

        assert expected_code in issues, (name, issues)


def test_sandbox_execution_result_tests_are_fixture_only() -> None:
    index = load(INDEX)

    assert index["sandbox_execution"] is False
    assert index["subprocess_execution"] is False
    assert index["provider_execution"] is False
    assert index["replay_execution"] is False
    assert index["generated_content_creation"] is False
    assert index["mutation_performed"] is False


def _assert_result_invariants(data: dict[str, Any], *, path: Path) -> None:
    assert REQUIRED_FIELDS <= data.keys(), path
    assert data["schema_version"] == SCHEMA_VERSION, path
    assert data["sandbox_mode"] in ALLOWED_SANDBOX_MODES, path
    assert data["status"] in ALLOWED_STATUS, path
    assert data["mutation_performed"] is False, path
    assert data["network_disabled"] is True, path
    assert isinstance(data["stdout_truncated"], bool), path
    assert isinstance(data["stderr_truncated"], bool), path
    assert isinstance(data["output_json_valid"], bool), path
    assert _non_negative_int(data["duration_ms"]), path
    assert _non_negative_int(data["stdout_bytes"]), path
    assert _non_negative_int(data["stderr_bytes"]), path
    assert _valid_trace_id(data["trace_id"]), path
    assert _valid_no_write_evidence(data["no_write_evidence"]), path


def _validate_result(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if "request_id" not in data:
        issues.append("missing_request_id")
    if not REQUIRED_FIELDS <= data.keys():
        issues.append("missing_required_field")
    if data.get("schema_version") != SCHEMA_VERSION:
        issues.append("unsupported_schema_version")
    if data.get("sandbox_mode") not in ALLOWED_SANDBOX_MODES:
        issues.append("unsupported_sandbox_mode")

    status = data.get("status")
    failure_code = data.get("failure_code")
    if status not in ALLOWED_STATUS:
        issues.append("invalid_status")
    if failure_code is not None and failure_code not in ALLOWED_FAILURE_CODES:
        issues.append("invalid_failure_code")
    if status == "pass" and failure_code is not None:
        issues.append("pass_with_failure_code")
    if status in {"fail", "timeout", "resource-limit"} and failure_code is None:
        issues.append("missing_failure_code")
    if status == "timeout" and failure_code != "sandbox-timeout":
        issues.append("invalid_timeout_failure_code")
    if status == "resource-limit" and failure_code != "sandbox-resource-limit":
        issues.append("invalid_resource_limit_failure_code")
    if status == "resource-limit" and not _valid_resource_limit(data.get("resource_limit")):
        issues.append("invalid_resource_limit")
    if status == "pass" and data.get("output_json_valid") is not True:
        issues.append("pass_output_json_invalid")

    if data.get("mutation_performed") is not False:
        issues.append("mutation_performed_true")
    if data.get("network_disabled") is not True:
        issues.append("network_not_disabled")
    if status == "pass" and data.get("no_write_confirmed") is not True:
        issues.append("no_write_not_confirmed")

    for field in ("duration_ms", "stdout_bytes", "stderr_bytes"):
        if not _non_negative_int(data.get(field)):
            issues.append("invalid_duration_ms" if field == "duration_ms" else "invalid_byte_count")
    for field in ("stdout_truncated", "stderr_truncated", "output_json_valid"):
        if not isinstance(data.get(field), bool):
            issues.append("invalid_boolean_flag")
    if not _valid_trace_id(data.get("trace_id")):
        issues.append("invalid_trace_id")
    if not _valid_no_write_evidence(data.get("no_write_evidence")):
        issues.append("invalid_no_write_evidence")

    return issues


def _non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _valid_trace_id(value: Any) -> bool:
    return value is None or (isinstance(value, str) and bool(value))


def _valid_resource_limit(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    if value.get("limit_kind") not in {"input", "output", "stdout", "stderr", "memory", "duration"}:
        return False
    return _positive_int(value.get("limit_bytes")) and _non_negative_int(value.get("observed_bytes"))


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _valid_no_write_evidence(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    protected_roots = value.get("protected_roots")
    pre_hashes = value.get("pre_hashes")
    post_hashes = value.get("post_hashes")
    if not isinstance(protected_roots, list) or not protected_roots:
        return False
    if not all(isinstance(item, str) and item for item in protected_roots):
        return False
    if not isinstance(pre_hashes, dict) or not isinstance(post_hashes, dict):
        return False
    if list(pre_hashes) != protected_roots or list(post_hashes) != protected_roots:
        return False
    if not all(_valid_hash(value) for value in pre_hashes.values()):
        return False
    if not all(_valid_hash(value) for value in post_hashes.values()):
        return False
    if value.get("mutation_detected") is not False:
        return False
    if value.get("temp_root_cleaned") is not True:
        return False
    return isinstance(value.get("unexpected_outputs"), list)


def _valid_hash(value: Any) -> bool:
    return isinstance(value, str) and bool(HASH_RE.fullmatch(value))
