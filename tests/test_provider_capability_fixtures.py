from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES = ROOT / "tests" / "fixtures" / "providers" / "capabilities"
VALID = CAPABILITIES / "valid"
INVALID = CAPABILITIES / "invalid"
EDGE_CASES = CAPABILITIES / "edge_cases"

SCHEMA_VERSION = "aios.provider_capability.v0"
HASH_POLICY = "aios.hash_policy.v0"
ALLOWED_SYNC_MODES = {"whole-file", "managed-block", "mixed-boundary"}
REQUIRED_FIELDS = {
    "schema_version",
    "provider_id",
    "provider_version",
    "deterministic_capable",
    "supported_sync_modes",
    "hash_policy",
    "output_affecting_config",
    "no_write_capable",
    "network_policy",
    "timeout_policy",
    "resource_policy",
    "allowed_read_roots",
    "provenance_required",
}
VALID_FIXTURES = {
    "deterministic_fixture_provider.json",
    "whole_file_only_provider.json",
    "managed_block_provider.json",
}
INVALID_FIXTURES = {
    "unsupported_schema_version.json": "unsupported_schema_version",
    "invalid_sync_mode.json": "invalid_sync_mode",
    "missing_provider_version.json": "missing_required_field",
    "network_enabled.json": "network_policy_not_disabled",
    "no_write_false.json": "no_write_not_true",
    "timeout_invalid.json": "invalid_timeout_policy",
    "duplicate_sync_mode.json": "duplicate_sync_mode",
    "malformed_resource_policy.json": "invalid_resource_policy",
}
EDGE_FIXTURES = {
    "empty_allowed_read_roots.json",
    "max_timeout_boundary.json",
    "minimal_output_affecting_config.json",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_provider_capability_fixture_inventory_matches_contract() -> None:
    assert {path.name for path in VALID.glob("*.json")} == VALID_FIXTURES
    assert {path.name for path in INVALID.glob("*.json")} == set(INVALID_FIXTURES)
    assert {path.name for path in EDGE_CASES.glob("*.json")} == EDGE_FIXTURES


def test_every_provider_capability_fixture_parses() -> None:
    for path in sorted(CAPABILITIES.glob("*/*.json")):
        data = load(path)

        assert isinstance(data, dict), path


def test_valid_provider_capability_fixtures_match_contract() -> None:
    for path in sorted(VALID.glob("*.json")) + sorted(EDGE_CASES.glob("*.json")):
        data = load(path)

        assert _validate_capability(data) == [], path
        assert REQUIRED_FIELDS <= data.keys(), path
        assert data["schema_version"] == SCHEMA_VERSION, path
        assert data["hash_policy"] == HASH_POLICY, path
        assert data["network_policy"] == "disabled", path
        assert data["no_write_capable"] is True, path
        assert data["deterministic_capable"] is True, path
        assert data["provenance_required"] is True, path
        assert _paths_are_safe_relative(data["allowed_read_roots"]), path


def test_invalid_provider_capability_fixtures_fail_expected_contract_assertion() -> None:
    for name, expected_code in INVALID_FIXTURES.items():
        data = load(INVALID / name)
        issues = _validate_capability(data)

        assert expected_code in issues, (name, issues)


def _validate_capability(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        issues.append("missing_required_field")

    if data.get("schema_version") != SCHEMA_VERSION:
        issues.append("unsupported_schema_version")

    if not _non_empty_string(data.get("provider_id")):
        issues.append("invalid_provider_id")
    if not _non_empty_string(data.get("provider_version")):
        issues.append("missing_required_field")

    if data.get("deterministic_capable") is not True:
        issues.append("deterministic_not_true")

    sync_modes = data.get("supported_sync_modes")
    if not isinstance(sync_modes, list) or not sync_modes:
        issues.append("invalid_sync_modes")
    elif any(mode not in ALLOWED_SYNC_MODES for mode in sync_modes):
        issues.append("invalid_sync_mode")
    if isinstance(sync_modes, list) and len(sync_modes) != len(set(sync_modes)):
        issues.append("duplicate_sync_mode")

    if data.get("hash_policy") != HASH_POLICY:
        issues.append("invalid_hash_policy")
    if not isinstance(data.get("output_affecting_config"), dict):
        issues.append("invalid_output_affecting_config")
    if data.get("no_write_capable") is not True:
        issues.append("no_write_not_true")
    if data.get("network_policy") != "disabled":
        issues.append("network_policy_not_disabled")
    if not _valid_timeout_policy(data.get("timeout_policy")):
        issues.append("invalid_timeout_policy")
    if not _valid_resource_policy(data.get("resource_policy")):
        issues.append("invalid_resource_policy")
    if not _paths_are_safe_relative(data.get("allowed_read_roots")):
        issues.append("invalid_allowed_read_roots")
    if data.get("provenance_required") is not True:
        issues.append("provenance_not_true")

    return issues


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_timeout_policy(value: Any) -> bool:
    return isinstance(value, dict) and _positive_int(value.get("timeout_ms"))


def _valid_resource_policy(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    if not _positive_int(value.get("max_input_bytes")):
        return False
    if not _positive_int(value.get("max_output_bytes")):
        return False
    if "max_memory_bytes" in value and not _positive_int(value.get("max_memory_bytes")):
        return False
    return True


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _paths_are_safe_relative(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    for item in value:
        if not isinstance(item, str):
            return False
        path = Path(item)
        if path.is_absolute() or ".." in path.parts:
            return False
        if "\\" in item:
            return False
    return True
