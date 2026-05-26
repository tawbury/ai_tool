from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRACES = ROOT / "tests" / "fixtures" / "providers" / "sandbox_traces"
VALID = TRACES / "valid"
INVALID = TRACES / "invalid"
EDGE = TRACES / "edge"
INDEX = TRACES / "sandbox_trace_index.json"

SCHEMA_VERSION = "aios.sandbox_trace.v0"
INDEX_SCHEMA_VERSION = "aios.sandbox_trace_fixture_index.v0"
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
ALLOWED_SANDBOX_MODES = {"fixture-mock", "subprocess-temp-cwd"}
ALLOWED_PROVIDER_MODES = {"fixture-mock", "subprocess-sandbox", None}
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
ALLOWED_OBSERVATION_KINDS = {
    "sandbox-policy",
    "sandbox-result",
    "provider-trace",
    "input-bundle",
    "output-json",
    "stdout",
    "stderr",
}
REQUIRED_FIELDS = {
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
VALID_FIXTURES = {
    "successful_sandbox_trace.json",
    "fixture_mock_trace.json",
    "timeout_sandbox_trace.json",
    "resource_limit_sandbox_trace.json",
}
INVALID_FIXTURES = {
    "missing_trace_id.json": "missing_trace_id",
    "request_id_mismatch.json": "request_id_mismatch",
    "invalid_status.json": "invalid_status",
    "pass_with_failure_code.json": "pass_with_failure_code",
    "mutation_performed_true.json": "mutation_performed_true",
    "network_disabled_false.json": "network_not_disabled",
    "unsafe_observed_output_path.json": "unsafe_observed_output_ref",
    "missing_provenance.json": "missing_provenance",
}
EDGE_FIXTURES = {
    "trace_without_provider_trace_ref.json",
    "zero_duration_trace.json",
    "partial_observed_outputs_trace.json",
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


def test_sandbox_trace_fixture_inventory_matches_contract() -> None:
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
    assert index["expected_invalid_issues"] == {
        f"invalid/{name}": issue for name, issue in INVALID_FIXTURES.items()
    }


def test_sandbox_trace_index_references_existing_fixtures() -> None:
    index = load(INDEX)

    for group in ("valid", "invalid", "edge"):
        for relative_path in index[group]:
            assert _fixture_path(relative_path).is_file(), relative_path


def test_every_sandbox_trace_fixture_parses() -> None:
    for path in sorted(TRACES.glob("*/*.json")):
        data = load(path)

        assert isinstance(data, dict), path
        assert data.get("schema_version") == SCHEMA_VERSION, path


def test_valid_sandbox_trace_fixtures_match_contract() -> None:
    for path in sorted(VALID.glob("*.json")):
        data = load(path)
        issues = _validate_trace(data)

        assert issues == [], (path, issues)
        _assert_trace_invariants(data, path=path)
        _assert_relationship_to_sandbox_result(data, path=path)
        assert data["provider_trace_ref"] is not None, path


def test_edge_sandbox_trace_fixtures_are_explicitly_classified() -> None:
    for path in sorted(EDGE.glob("*.json")):
        data = load(path)
        issues = _validate_trace(data)

        assert issues == [], (path, issues)
        assert isinstance(data.get("edge_classification"), str) and data["edge_classification"], path
        _assert_trace_invariants(data, path=path)
        _assert_relationship_to_sandbox_result(data, path=path)


def test_invalid_sandbox_trace_fixtures_fail_expected_assertion() -> None:
    for name, expected_code in INVALID_FIXTURES.items():
        data = load(INVALID / name)
        issues = _validate_trace(data)

        assert expected_code in issues, (name, issues)


def test_provider_trace_ref_may_be_null_only_for_explicit_edge_fixture() -> None:
    for path in sorted(VALID.glob("*.json")) + sorted(INVALID.glob("*.json")):
        data = load(path)
        if "provider_trace_ref" in data:
            assert data["provider_trace_ref"] is not None, path

    edge = load(EDGE / "trace_without_provider_trace_ref.json")
    assert edge["provider_trace_ref"] is None
    assert edge["edge_classification"] == "provider-trace-ref-unavailable"


def test_sandbox_trace_tests_are_fixture_only() -> None:
    index = load(INDEX)

    assert index["sandbox_execution"] is False
    assert index["subprocess_execution"] is False
    assert index["provider_execution"] is False
    assert index["replay_execution"] is False
    assert index["generated_content_creation"] is False
    assert index["mutation_performed"] is False


def _assert_trace_invariants(data: dict[str, Any], *, path: Path) -> None:
    assert REQUIRED_FIELDS <= data.keys(), path
    assert data["schema_version"] == SCHEMA_VERSION, path
    assert _non_empty_string(data["trace_id"]), path
    assert _non_empty_string(data["request_id"]), path
    assert data["sandbox_mode"] in ALLOWED_SANDBOX_MODES, path
    assert data["provider_mode"] in ALLOWED_PROVIDER_MODES, path
    assert data["status"] in ALLOWED_STATUS, path
    assert _valid_timestamp(data["started_at"]), path
    assert _valid_timestamp(data["completed_at"]), path
    assert _non_negative_int(data["duration_ms"]), path
    assert data["network_disabled"] is True, path
    assert data["mutation_performed"] is False, path
    if data["status"] == "pass":
        assert data["no_write_confirmed"] is True, path
    assert _safe_ref(data["sandbox_policy_ref"], allow_null=True), path
    assert _safe_ref(data["sandbox_result_ref"], allow_null=False), path
    assert _safe_ref(data["provider_trace_ref"], allow_null=True), path
    assert _valid_observations(data["observed_inputs"], output=False), path
    assert _valid_observations(data["observed_outputs"], output=True), path
    assert _valid_provenance(data["provenance"]), path


def _validate_trace(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    missing = REQUIRED_FIELDS - data.keys()
    if "trace_id" in missing:
        issues.append("missing_trace_id")
    if "provenance" in missing:
        issues.append("missing_provenance")
    if missing - {"trace_id", "provenance"}:
        issues.append("missing_required_field")

    if data.get("schema_version") != SCHEMA_VERSION:
        issues.append("unsupported_schema_version")
    if "trace_id" in data and not _non_empty_string(data.get("trace_id")):
        issues.append("invalid_trace_id")
    if not _non_empty_string(data.get("request_id")):
        issues.append("invalid_request_id")
    if data.get("sandbox_mode") not in ALLOWED_SANDBOX_MODES:
        issues.append("invalid_sandbox_mode")
    if data.get("provider_mode") not in ALLOWED_PROVIDER_MODES:
        issues.append("invalid_provider_mode")

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

    if data.get("network_disabled") is not True:
        issues.append("network_not_disabled")
    if data.get("mutation_performed") is not False:
        issues.append("mutation_performed_true")
    if status == "pass" and data.get("no_write_confirmed") is not True:
        issues.append("no_write_not_confirmed")
    if not _non_negative_int(data.get("duration_ms")):
        issues.append("invalid_duration_ms")
    if not _valid_timestamp(data.get("started_at")) or not _valid_timestamp(data.get("completed_at")):
        issues.append("invalid_timestamp")

    for field in ("sandbox_policy_ref", "provider_trace_ref"):
        if not _safe_ref(data.get(field), allow_null=True):
            issues.append(f"unsafe_{field}")
    if not _safe_ref(data.get("sandbox_result_ref"), allow_null=False):
        issues.append("unsafe_sandbox_result_ref")
    if not _valid_observations(data.get("observed_inputs"), output=False):
        issues.append("invalid_observed_inputs")
    if not _valid_observations(data.get("observed_outputs"), output=True):
        issues.append("unsafe_observed_output_ref")
    if "provenance" in data and not _valid_provenance(data["provenance"]):
        issues.append("invalid_provenance")

    _validate_sandbox_result_relationship(data, issues)

    return issues


def _validate_sandbox_result_relationship(data: dict[str, Any], issues: list[str]) -> None:
    ref = data.get("sandbox_result_ref")
    if not isinstance(ref, str) or not _safe_ref(ref, allow_null=False):
        return
    result_path = ROOT / ref
    if not result_path.is_file():
        return
    result = load(result_path)
    if "trace_id" in data and result.get("trace_id") != data.get("trace_id"):
        issues.append("trace_id_mismatch")
    if result.get("request_id") != data.get("request_id"):
        issues.append("request_id_mismatch")


def _assert_relationship_to_sandbox_result(data: dict[str, Any], *, path: Path) -> None:
    issues: list[str] = []
    _validate_sandbox_result_relationship(data, issues)
    assert issues == [], (path, issues)


def _fixture_path(relative: str) -> Path:
    candidate = Path(relative)
    assert not candidate.is_absolute(), relative
    assert ".." not in candidate.parts, relative
    assert "\\" not in relative, relative
    return TRACES / candidate


def _safe_ref(value: Any, *, allow_null: bool) -> bool:
    if value is None:
        return allow_null
    if not isinstance(value, str) or not value:
        return False
    if value.startswith("{sandbox_tmp}/"):
        rest = value.removeprefix("{sandbox_tmp}/")
        return bool(rest) and _safe_parts(Path(rest))
    candidate = Path(value)
    return not candidate.is_absolute() and _safe_parts(candidate) and "\\" not in value


def _safe_parts(path: Path) -> bool:
    return ".." not in path.parts and all(part not in {"", "."} for part in path.parts)


def _valid_observations(value: Any, *, output: bool) -> bool:
    if not isinstance(value, list):
        return False
    for item in value:
        if not isinstance(item, dict):
            return False
        if item.get("kind") not in ALLOWED_OBSERVATION_KINDS:
            return False
        ref = item.get("ref")
        if not _safe_ref(ref, allow_null=False):
            return False
        if output and isinstance(ref, str) and ref.startswith(("src/", ".ai/", "docs/")):
            return False
        hash_value = item.get("hash")
        if hash_value is not None and not _valid_hash(hash_value):
            return False
    return True


def _valid_provenance(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    source_refs = value.get("source_refs")
    source_hashes = value.get("source_hashes")
    if not isinstance(source_refs, list) or not source_refs:
        return False
    if not all(_safe_ref(ref, allow_null=False) for ref in source_refs):
        return False
    if not isinstance(source_hashes, dict):
        return False
    if list(source_hashes) != source_refs:
        return False
    if not all(_valid_hash(digest) for digest in source_hashes.values()):
        return False
    return (
        value.get("relationship")
        in {"sandbox-result-to-provider-trace", "sandbox-result-without-provider-trace"}
        and value.get("generated_by") == "fixture-contract"
    )


def _valid_hash(value: Any) -> bool:
    return isinstance(value, str) and bool(HASH_RE.fullmatch(value))


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _valid_timestamp(value: Any) -> bool:
    return isinstance(value, str) and bool(TIMESTAMP_RE.fullmatch(value))
