from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRACES = ROOT / "tests" / "fixtures" / "providers" / "traces"
VALID = TRACES / "valid"
INVALID = TRACES / "invalid"
EDGE_CASES = TRACES / "edge_cases"
INDEX = TRACES / "provider_trace_index.json"

SCHEMA_VERSION = "aios.provider_execution_trace.v0"
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
PROVIDER_MODES = {"fixture-mock", "subprocess-sandbox"}
FAILURE_CODES = {
    "provider-timeout",
    "nondeterministic-output",
    "provider-execution-disabled",
    "provider-isolation-violation",
    "provider-capability-missing",
    "provider-output-invalid",
    "provider-network-disabled",
    "provider-resource-limit",
}
VALID_FIXTURES = {
    "successful_fixture_mock_trace.json",
    "unavailable_fixture_mock_trace.json",
    "managed_block_trace.json",
    "whole_file_trace.json",
}
INVALID_FIXTURES = {
    "missing_trace_id.json": "missing_trace_id",
    "invalid_provider_mode.json": "invalid_provider_mode",
    "mutation_performed_true.json": "mutation_performed_true",
    "network_disabled_false.json": "network_not_disabled",
    "missing_no_write_confirmed.json": "missing_no_write_confirmed",
    "invalid_failure_code.json": "invalid_failure_code",
    "invalid_hash_format.json": "invalid_hash_format",
    "missing_provenance.json": "missing_provenance",
    "nondeterministic_execution_false.json": "nondeterministic_execution_false",
}
EDGE_FIXTURES = {
    "zero_duration_trace.json",
    "null_output_hash_unavailable.json",
    "failure_without_generated_hashes.json",
}
REQUIRED_FIELDS = {
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


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_provider_execution_trace_fixture_inventory_consistency() -> None:
    index = load(INDEX)

    assert index["schema_version"] == "aios.provider_execution_trace_fixture_index.v0"
    assert {path.name for path in VALID.glob("*.json")} == VALID_FIXTURES
    assert {path.name for path in INVALID.glob("*.json")} == set(INVALID_FIXTURES)
    assert {path.name for path in EDGE_CASES.glob("*.json")} == EDGE_FIXTURES
    assert index["contract"] == {
        "provider_execution": False,
        "sandbox_execution": False,
        "dynamic_loading": False,
        "network_access": False,
        "generated_content_creation": False,
        "mutation_performed": False,
    }

    for section, expected_parent in (
        ("valid_traces", VALID),
        ("invalid_traces", INVALID),
        ("edge_traces", EDGE_CASES),
    ):
        case_ids = [case["case_id"] for case in index[section]]
        assert len(case_ids) == len(set(case_ids)), section
        for case in index[section]:
            path = _safe_fixture_path(case["fixture"])
            assert path.is_file(), case
            assert path.parent == expected_parent, case


def test_valid_provider_execution_trace_fixtures_match_contract() -> None:
    for path in sorted(VALID.glob("*.json")) + sorted(EDGE_CASES.glob("*.json")):
        data = load(path)
        issues = _validate_trace(data)

        assert issues == [], (path, issues)
        assert REQUIRED_FIELDS <= data.keys(), path
        assert data["schema_version"] == SCHEMA_VERSION, path
        assert data["provider_mode"] in PROVIDER_MODES, path
        assert data["provider_mode"] == "fixture-mock", path
        assert data["deterministic_execution"] is True, path
        assert data["mutation_performed"] is False, path
        assert data["no_write_confirmed"] is True, path
        assert data["network_disabled"] is True, path
        assert isinstance(data["duration_ms"], int), path
        assert data["duration_ms"] >= 0, path
        _assert_hash_policy_preserves_observed_bytes(data, path)
        _assert_provenance(data["provenance"], path)


def test_invalid_provider_execution_trace_fixtures_fail_expected_assertions() -> None:
    for name, expected_issue in INVALID_FIXTURES.items():
        data = load(INVALID / name)
        issues = _validate_trace(data)

        assert expected_issue in issues, (name, issues)


def test_trace_unavailable_semantics_are_enforced() -> None:
    data = load(VALID / "unavailable_fixture_mock_trace.json")

    assert data["unavailable_reason"] == "source-missing"
    assert data["failure_code"] is None
    assert data["generated_hashes"] == {
        "generated_bytes_hash": None,
        "generated_target_hash": None,
        "generated_managed_block_hash": None,
    }


def test_trace_failure_without_generated_hashes_is_valid_edge_case() -> None:
    data = load(EDGE_CASES / "failure_without_generated_hashes.json")

    assert _validate_trace(data) == []
    assert data["failure_code"] == "provider-output-invalid"
    assert data["unavailable_reason"] == "provider-output-invalid"
    assert all(value is None for value in data["generated_hashes"].values())
    assert data["output_hash"] is None


def test_trace_hash_format_validation_covers_nested_generated_hashes() -> None:
    data = load(VALID / "managed_block_trace.json")

    assert HASH_RE.match(data["input_hash"])
    assert HASH_RE.match(data["output_hash"])
    assert HASH_RE.match(data["generated_hashes"]["generated_bytes_hash"])
    assert HASH_RE.match(data["generated_hashes"]["generated_managed_block_hash"])
    assert data["generated_hashes"]["generated_target_hash"] is None


def test_trace_fixtures_do_not_encode_normalization_assumptions() -> None:
    for path in sorted(VALID.glob("*.json")) + sorted(EDGE_CASES.glob("*.json")):
        data = load(path)

        _assert_hash_policy_preserves_observed_bytes(data, path)


def _validate_trace(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    missing = REQUIRED_FIELDS - data.keys()
    if "trace_id" in missing:
        issues.append("missing_trace_id")
    if "no_write_confirmed" in missing:
        issues.append("missing_no_write_confirmed")
    if "provenance" in missing:
        issues.append("missing_provenance")
    if missing - {"trace_id", "no_write_confirmed", "provenance"}:
        issues.append("missing_required_field")

    if data.get("schema_version") != SCHEMA_VERSION:
        issues.append("unsupported_schema_version")
    if not _non_empty_string(data.get("trace_id")) and "trace_id" in data:
        issues.append("invalid_trace_id")
    if data.get("provider_mode") not in PROVIDER_MODES:
        issues.append("invalid_provider_mode")
    if data.get("failure_code") is not None and data.get("failure_code") not in FAILURE_CODES:
        issues.append("invalid_failure_code")
    if data.get("deterministic_execution") is not True:
        issues.append("nondeterministic_execution_false")
    if data.get("mutation_performed") is not False:
        issues.append("mutation_performed_true")
    if data.get("no_write_confirmed") is not True:
        issues.append("missing_no_write_confirmed")
    if data.get("network_disabled") is not True:
        issues.append("network_not_disabled")
    if not _valid_non_negative_int(data.get("duration_ms")):
        issues.append("invalid_duration_ms")

    _validate_hash_fields(data, issues)
    _validate_generated_hashes(data, issues)
    _validate_unavailable_failure_semantics(data, issues)

    if "provenance" in data and not _valid_provenance(data["provenance"]):
        issues.append("invalid_provenance")

    return issues


def _validate_hash_fields(data: dict[str, Any], issues: list[str]) -> None:
    for key in ("input_hash", "output_hash"):
        value = data.get(key)
        if value is not None and not (isinstance(value, str) and HASH_RE.match(value)):
            issues.append("invalid_hash_format")

    generated_hashes = data.get("generated_hashes")
    if not isinstance(generated_hashes, dict):
        issues.append("invalid_generated_hashes")
        return
    required_generated = {
        "generated_bytes_hash",
        "generated_target_hash",
        "generated_managed_block_hash",
    }
    if required_generated - generated_hashes.keys():
        issues.append("invalid_generated_hashes")
    for value in generated_hashes.values():
        if value is not None and not (isinstance(value, str) and HASH_RE.match(value)):
            issues.append("invalid_hash_format")


def _validate_generated_hashes(data: dict[str, Any], issues: list[str]) -> None:
    generated_hashes = data.get("generated_hashes")
    if not isinstance(generated_hashes, dict):
        return
    if data.get("failure_code") is None and data.get("unavailable_reason") is None:
        if generated_hashes.get("generated_bytes_hash") is None:
            issues.append("missing_generated_hash")


def _validate_unavailable_failure_semantics(data: dict[str, Any], issues: list[str]) -> None:
    generated_hashes = data.get("generated_hashes")
    if not isinstance(generated_hashes, dict):
        return
    unavailable = data.get("unavailable_reason") is not None
    failed = data.get("failure_code") is not None
    if unavailable or failed:
        if data.get("unavailable_reason") is None:
            issues.append("missing_unavailable_reason")
        if any(value is not None for value in generated_hashes.values()):
            issues.append("unavailable_generated_hash_present")


def _valid_provenance(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    source_paths = value.get("source_paths")
    source_hashes = value.get("source_hashes")
    if not isinstance(source_paths, list) or not source_paths:
        return False
    if not isinstance(source_hashes, dict):
        return False
    if list(source_hashes.keys()) != source_paths:
        return False
    for digest in source_hashes.values():
        if not isinstance(digest, str) or not HASH_RE.match(digest):
            return False
    return value.get("generated_by") == "aios.mock_provider.fixture.v0"


def _assert_provenance(provenance: dict[str, Any], path: Path) -> None:
    assert _valid_provenance(provenance), path


def _assert_hash_policy_preserves_observed_bytes(data: dict[str, Any], path: Path) -> None:
    hash_policy = data.get("hash_policy")

    assert isinstance(hash_policy, dict), path
    assert hash_policy["version"] == "aios.hash_policy.v0", path
    assert hash_policy["normalization"] == "none", path
    assert hash_policy["line_endings"] == "preserve", path
    assert hash_policy["trailing_newline"] == "preserve", path


def _safe_fixture_path(relative: str) -> Path:
    candidate = Path(relative)
    assert not candidate.is_absolute(), relative
    assert ".." not in candidate.parts, relative
    assert "\\" not in relative, relative
    return TRACES / candidate


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0
