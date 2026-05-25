from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "providers" / "mock"
INPUTS = FIXTURES / "inputs"
OUTPUTS = FIXTURES / "outputs"
SNAPSHOTS = FIXTURES / "snapshots"
EXPECTED = FIXTURES / "expected"
INDEX = FIXTURES / "mock_provider_index.json"

HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
VALID_INPUTS = {
    "deterministic_available_input.json",
    "deterministic_unavailable_input.json",
    "managed_block_input.json",
    "whole_file_input.json",
}
VALID_OUTPUTS = {
    "deterministic_available_output.json",
    "deterministic_unavailable_output.json",
    "managed_block_output.json",
    "whole_file_output.json",
}
INVALID_OUTPUTS = {
    "missing_provenance_output.json": "missing_provenance",
    "hash_mismatch_output.json": "generated_hash_mismatch",
    "nondeterministic_duplicate_output.json": "nondeterministic_duplicate_output",
    "invalid_provider_version_output.json": "invalid_provider_version",
    "unavailable_with_generated_hash_output.json": "unavailable_generated_hash_present",
    "missing_no_write_confirmed_output.json": "missing_no_write_confirmed",
}
PROVIDER_ID = "aios.mock.preview.fixture"
PROVIDER_VERSION = "0.1.0"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_mock_provider_fixture_inventory_consistency() -> None:
    index = load(INDEX)

    assert index["schema_version"] == "aios.mock_provider_fixture_index.v0"
    assert {path.name for path in INPUTS.glob("*.json")} == VALID_INPUTS
    assert {path.name for path in OUTPUTS.glob("*.json")} == VALID_OUTPUTS
    assert {path.name for path in EXPECTED.glob("*.json")} == set(INVALID_OUTPUTS)
    assert (FIXTURES / index["provider_snapshot"]).is_file()

    valid_case_ids = [case["case_id"] for case in index["valid_cases"]]
    invalid_case_ids = [case["case_id"] for case in index["invalid_cases"]]
    assert len(valid_case_ids) == len(set(valid_case_ids))
    assert len(invalid_case_ids) == len(set(invalid_case_ids))

    for case in index["valid_cases"]:
        input_path = _safe_fixture_path(case["input_fixture"])
        output_path = _safe_fixture_path(case["output_fixture"])
        assert input_path.is_file(), case
        assert output_path.is_file(), case
        assert input_path.parent == INPUTS
        assert output_path.parent == OUTPUTS

    for case in index["invalid_cases"]:
        path = _safe_fixture_path(case["fixture"])
        assert path.is_file(), case
        assert path.parent == EXPECTED
        assert case["expected_issue"] in set(INVALID_OUTPUTS.values())

    assert index["contract"] == {
        "provider_execution": False,
        "sandbox_execution": False,
        "dynamic_loading": False,
        "network_access": False,
        "generated_content_creation": False,
        "mutation_performed": False,
    }


def test_mock_provider_snapshot_is_static_non_execution_contract() -> None:
    snapshot = load(SNAPSHOTS / "aios_mock_provider_0_1_0.json")

    assert snapshot["schema_version"] == "aios.mock_provider_snapshot.v0"
    assert snapshot["provider_id"] == PROVIDER_ID
    assert snapshot["provider_version"] == PROVIDER_VERSION
    assert snapshot["deterministic_capable"] is True
    assert snapshot["no_write_capable"] is True
    assert snapshot["network_policy"] == "disabled"
    assert snapshot["hash_policy"] == "aios.hash_policy.v0"
    assert set(snapshot["supported_sync_modes"]) == {"whole-file", "managed-block", "mixed-boundary"}
    assert snapshot["output_affecting_config"]["normalization"] == "none"
    assert snapshot["output_affecting_config"]["line_endings"] == "preserve"
    assert snapshot["output_affecting_config"]["trailing_newline"] == "preserve"


def test_valid_mock_provider_inputs_match_contract() -> None:
    for path in sorted(INPUTS.glob("*.json")):
        data = load(path)

        assert data["schema_version"] == "aios.mock_provider.input.v0", path
        assert data["case_id"] == data["entry_id"], path
        assert data["provider"] == {"provider_id": PROVIDER_ID, "provider_version": PROVIDER_VERSION}
        assert data["sync_mode"] in {"whole-file", "managed-block", "mixed-boundary"}, path
        assert data["hash_policy"]["version"] == "aios.hash_policy.v0", path
        assert data["hash_policy"]["normalization"] == "none", path
        assert data["hash_policy"]["line_endings"] == "preserve", path
        assert data["hash_policy"]["trailing_newline"] == "preserve", path
        assert HASH_RE.match(data["input_hash"]), path
        _assert_source_order_is_explicit(data["source_evidence"], path)
        _assert_hash_fields(data, path)


def test_valid_mock_provider_outputs_match_contract() -> None:
    for path in sorted(OUTPUTS.glob("*.json")):
        data = load(path)
        issues = _validate_mock_output(data)

        assert issues == [], (path, issues)
        assert data["schema_version"] == "aios.mock_provider.output.v0", path
        assert data["case_id"] == data["entry_id"], path
        assert data["execution_trace_id"].startswith("trace-mock-"), path
        assert data["provider_metadata"]["provider_id"] == PROVIDER_ID, path
        assert data["provider_metadata"]["provider_version"] == PROVIDER_VERSION, path
        assert data["provider_metadata"]["hash_policy"] == "aios.hash_policy.v0", path
        assert data["deterministic_execution"] is True, path
        assert data["no_write_confirmed"] is True, path
        assert data["network_disabled"] is True, path
        assert isinstance(data["duration_ms"], int) and data["duration_ms"] >= 0, path
        _assert_hash_fields(data, path)
        _assert_provenance(data["provenance"], path)


def test_valid_mock_outputs_match_indexed_inputs() -> None:
    index = load(INDEX)
    for case in index["valid_cases"]:
        input_data = load(_safe_fixture_path(case["input_fixture"]))
        output_data = load(_safe_fixture_path(case["output_fixture"]))

        assert input_data["case_id"] == case["case_id"]
        assert output_data["case_id"] == case["case_id"]
        assert output_data["input_hash"] == input_data["input_hash"]
        assert output_data["provider_metadata"]["provider_id"] == input_data["provider"]["provider_id"]
        assert output_data["provider_metadata"]["provider_version"] == input_data["provider"]["provider_version"]


def test_unavailable_output_semantics_are_enforced() -> None:
    data = load(OUTPUTS / "deterministic_unavailable_output.json")

    assert data["preview_available"] is False
    assert data["generated_content_kind"] is None
    assert data["generated_bytes_hash"] is None
    assert data["generated_target_hash"] is None
    assert data["generated_managed_block_hash"] is None
    assert data["unavailable_reason"] == "source-missing"
    assert data["deterministic_execution"] is True
    assert data["no_write_confirmed"] is True


def test_invalid_mock_provider_fixtures_fail_expected_assertions() -> None:
    for name, expected_issue in INVALID_OUTPUTS.items():
        data = load(EXPECTED / name)
        issues = _validate_mock_output(data)

        assert expected_issue in issues, (name, issues)


def test_mock_provider_fixtures_do_not_encode_normalization_assumptions() -> None:
    for path in sorted(INPUTS.glob("*.json")):
        data = load(path)
        hash_policy = data["hash_policy"]

        assert hash_policy["normalization"] == "none", path
        assert hash_policy["line_endings"] == "preserve", path
        assert hash_policy["trailing_newline"] == "preserve", path


def _validate_mock_output(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    required = {
        "schema_version",
        "case_id",
        "entry_id",
        "execution_trace_id",
        "preview_available",
        "generated_content_kind",
        "generated_bytes_hash",
        "generated_target_hash",
        "generated_managed_block_hash",
        "unavailable_reason",
        "provider_metadata",
        "deterministic_execution",
        "no_write_confirmed",
        "network_disabled",
        "input_hash",
        "output_hash",
        "duration_ms",
        "provenance",
    }
    missing = required - data.keys()
    if "provenance" in missing:
        issues.append("missing_provenance")
    if "no_write_confirmed" in missing:
        issues.append("missing_no_write_confirmed")
    if missing - {"provenance", "no_write_confirmed"}:
        issues.append("missing_required_field")

    provider_metadata = data.get("provider_metadata")
    if not isinstance(provider_metadata, dict):
        issues.append("missing_provider_metadata")
    else:
        if provider_metadata.get("provider_id") != PROVIDER_ID:
            issues.append("invalid_provider_id")
        if provider_metadata.get("provider_version") != PROVIDER_VERSION:
            issues.append("invalid_provider_version")

    if data.get("deterministic_execution") is not True:
        issues.append("nondeterministic_duplicate_output")
    if data.get("no_write_confirmed") is not True:
        issues.append("missing_no_write_confirmed")
    if data.get("network_disabled") is not True:
        issues.append("network_not_disabled")
    if not isinstance(data.get("duration_ms"), int) or isinstance(data.get("duration_ms"), bool) or data.get("duration_ms") < 0:
        issues.append("invalid_duration")

    _validate_hashes(data, issues)
    _validate_availability_semantics(data, issues)

    if "provenance" in data:
        if not _valid_provenance(data["provenance"]):
            issues.append("invalid_provenance")

    return issues


def _validate_hashes(data: dict[str, Any], issues: list[str]) -> None:
    for key in ("input_hash", "output_hash", "generated_bytes_hash", "generated_target_hash", "generated_managed_block_hash"):
        value = data.get(key)
        if value is not None and not (isinstance(value, str) and HASH_RE.match(value)):
            issues.append("invalid_hash_format")

    if data.get("preview_available") is True:
        kind = data.get("generated_content_kind")
        generated_bytes_hash = data.get("generated_bytes_hash")
        output_hash = data.get("output_hash")
        if kind == "whole-file" and data.get("generated_target_hash") != generated_bytes_hash:
            issues.append("generated_hash_mismatch")
        if kind in {"managed-block", "mixed-boundary"} and data.get("generated_managed_block_hash") != generated_bytes_hash:
            issues.append("generated_hash_mismatch")
        if output_hash != generated_bytes_hash:
            issues.append("generated_hash_mismatch")


def _validate_availability_semantics(data: dict[str, Any], issues: list[str]) -> None:
    if data.get("preview_available") is False:
        generated_fields = (
            data.get("generated_bytes_hash"),
            data.get("generated_target_hash"),
            data.get("generated_managed_block_hash"),
        )
        if any(value is not None for value in generated_fields):
            issues.append("unavailable_generated_hash_present")
        if data.get("generated_content_kind") is not None:
            issues.append("unavailable_content_kind_present")
        if not data.get("unavailable_reason"):
            issues.append("missing_unavailable_reason")
    elif data.get("preview_available") is True:
        if data.get("unavailable_reason") is not None:
            issues.append("available_unavailable_reason_present")
        if not data.get("generated_content_kind"):
            issues.append("missing_generated_content_kind")


def _valid_provenance(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    if not isinstance(value.get("source_paths"), list) or not value["source_paths"]:
        return False
    source_hashes = value.get("source_hashes")
    if not isinstance(source_hashes, dict):
        return False
    if list(source_hashes.keys()) != value["source_paths"]:
        return False
    if value.get("generated_by") != "aios.mock_provider.fixture.v0":
        return False
    for digest in source_hashes.values():
        if not isinstance(digest, str) or not HASH_RE.match(digest):
            return False
    return True


def _assert_source_order_is_explicit(source_evidence: dict[str, Any], path: Path) -> None:
    source_paths = source_evidence["source_paths"]
    source_hashes = source_evidence["source_hashes"]

    assert isinstance(source_paths, list), path
    assert source_paths, path
    assert len(source_paths) == len(set(source_paths)), path
    assert list(source_hashes.keys()) == source_paths, path


def _assert_hash_fields(value: Any, path: Path) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "source_hashes":
                assert isinstance(item, dict), path
                for digest in item.values():
                    assert HASH_RE.match(digest), (path, digest)
                continue
            if key.endswith("_hash") and item is not None:
                assert isinstance(item, str), (path, key)
                assert HASH_RE.match(item), (path, key, item)
            else:
                _assert_hash_fields(item, path)
    elif isinstance(value, list):
        for item in value:
            _assert_hash_fields(item, path)


def _assert_provenance(provenance: dict[str, Any], path: Path) -> None:
    assert _valid_provenance(provenance), path


def _safe_fixture_path(relative: str) -> Path:
    candidate = Path(relative)
    assert not candidate.is_absolute(), relative
    assert ".." not in candidate.parts, relative
    assert "\\" not in relative, relative
    return FIXTURES / candidate
